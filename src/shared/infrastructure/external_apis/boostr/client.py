"""
Cliente HTTP para la API de Boostr.

Implementa la integración con todos los endpoints relevantes
de Boostr para el sistema de investigaciones vehiculares.

Documentación: https://docs.boostr.cl/reference
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx

from src.core.config import get_settings
from .schemas import (
    BoostrResponse,
    VehicleInfo,
    VehicleExtendedInfo,
    PersonInfo,
    PersonName,
    PersonVehicle,
    PersonProperty,
    TrafficFine,
    TechnicalReview,
    SOAPInfo,
    PEPInfo,
    InterpolInfo,
    DeceasedInfo,
    InvestigacionBoostrResult,
)
from .exceptions import (
    BoostrAPIError,
    BoostrAuthenticationError,
    BoostrRateLimitError,
    BoostrNotFoundError,
    BoostrValidationError,
    BoostrTimeoutError,
    BoostrServiceUnavailableError,
)


logger = logging.getLogger(__name__)


class BoostrClient:
    """
    Cliente para la API de Boostr Chile.

    Proporciona métodos para consultar información de:
    - Vehículos por patente
    - Personas por RUT
    - Multas de tránsito
    - Revisión técnica
    - SOAP

    Attributes:
        base_url: URL base de la API
        api_key: API Key para autenticación
        timeout: Timeout en segundos para las requests

    Example:
        >>> client = BoostrClient()
        >>> vehicle = await client.get_vehicle_info("ABCD12")
        >>> print(vehicle.marca, vehicle.modelo)
    """

    # Rate limit: 5 requests cada 10 segundos
    RATE_LIMIT_REQUESTS = 5
    RATE_LIMIT_WINDOW = 10  # segundos

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Inicializa el cliente de Boostr.

        Args:
            base_url: URL base (default: desde settings)
            api_key: API Key (default: desde settings)
            timeout: Timeout en segundos (default: desde settings)
        """
        settings = get_settings()

        self.base_url = (base_url or settings.BOOSTR_API_URL or "https://api.boostr.cl").rstrip("/")
        self.api_key = api_key or settings.BOOSTR_API_KEY
        self.timeout = timeout or settings.BOOSTR_TIMEOUT or 30

        # Control de rate limiting
        self._request_times: List[datetime] = []
        self._lock = asyncio.Lock()

        # Advertencia si no hay API key
        if not self.api_key:
            logger.warning(
                "⚠️ BoostrClient inicializado SIN API KEY. "
                "Las requests fallarán. Configure BOOSTR_API_KEY en variables de entorno."
            )

        logger.info(
            f"BoostrClient inicializado: base_url={self.base_url}, "
            f"api_key={'***' + self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else 'NO CONFIGURADA'}, "
            f"timeout={self.timeout}s"
        )

    # =========================================================================
    # MÉTODOS PRIVADOS
    # =========================================================================

    def _get_headers(self) -> Dict[str, str]:
        """Retorna los headers necesarios para las requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        if self.api_key:
            # Boostr API usa Authorization Bearer con el token
            # Si el token ya tiene prefijo "Bearer", no agregarlo de nuevo
            if self.api_key.startswith("Bearer "):
                headers["Authorization"] = self.api_key
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # También agregar x-api-key por si acaso (algunas APIs lo requieren)
            headers["x-api-key"] = self.api_key
        else:
            logger.error("❌ Intentando hacer request sin API key")
        return headers

    async def _wait_for_rate_limit(self) -> None:
        """
        Espera si es necesario para respetar el rate limit.

        Boostr permite máximo 5 requests cada 10 segundos.
        """
        async with self._lock:
            now = datetime.utcnow()

            # Limpiar requests antiguas (fuera de la ventana)
            window_start = now.timestamp() - self.RATE_LIMIT_WINDOW
            self._request_times = [t for t in self._request_times if t.timestamp() > window_start]

            # Si estamos en el límite, esperar
            if len(self._request_times) >= self.RATE_LIMIT_REQUESTS:
                oldest = min(self._request_times)
                wait_time = self.RATE_LIMIT_WINDOW - (now.timestamp() - oldest.timestamp())
                if wait_time > 0:
                    logger.warning(f"Rate limit alcanzado, esperando {wait_time:.2f}s")
                    await asyncio.sleep(wait_time + 0.1)

            # Registrar esta request
            self._request_times.append(datetime.utcnow())

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Realiza una request a la API de Boostr.

        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API (sin URL base)
            params: Parámetros de query string

        Returns:
            Dict con la respuesta JSON

        Raises:
            BoostrAPIError: En caso de error
        """
        # Respetar rate limit
        await self._wait_for_rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Agregar .json si no está presente
        if not url.endswith(".json"):
            url += ".json"

        logger.debug(f"Boostr request: {method} {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    params=params,
                )

                # Manejar errores HTTP
                if response.status_code == 401:
                    raise BoostrAuthenticationError("API Key inválida o sin créditos disponibles")
                elif response.status_code == 429:
                    raise BoostrRateLimitError()
                elif response.status_code == 404:
                    raise BoostrNotFoundError(f"No se encontró: {endpoint}")
                elif response.status_code >= 500:
                    raise BoostrServiceUnavailableError()

                # Verificar que la respuesta tenga contenido antes de parsear
                if not response.content or len(response.content) == 0:
                    raise BoostrAPIError(
                        f"Respuesta vacía de Boostr API (status: {response.status_code})"
                    )

                # Intentar parsear JSON con manejo de errores
                try:
                    data = response.json()
                except Exception as json_error:
                    # Si falla el parseo, puede ser HTML o texto de error
                    content_preview = response.text[:200] if hasattr(response, "text") else "N/A"
                    content_type = response.headers.get("content-type", "N/A")
                    raise BoostrAPIError(
                        f"Boostr API devolvió respuesta inválida (status: {response.status_code}, "
                        f"Content-Type: {content_type}): {str(json_error)}. "
                        f"Respuesta: {content_preview}"
                    )

                # Verificar respuesta de error de Boostr
                if isinstance(data, dict) and data.get("status") == "error":
                    error_msg = data.get("message") or data.get("data") or "Error desconocido"
                    error_code = data.get("code", "UNKNOWN")

                    if "invalid" in error_msg.lower() or "inválido" in error_msg.lower():
                        raise BoostrValidationError(error_msg)

                    raise BoostrAPIError(error_msg, code=error_code)

                return data

        except httpx.TimeoutException:
            raise BoostrTimeoutError()
        except httpx.RequestError as e:
            raise BoostrAPIError(f"Error de conexión: {str(e)}")

    def _normalize_rut(self, rut: str) -> str:
        """
        Normaliza un RUT para la API.

        Acepta formatos: 12345678-9, 12.345.678-9
        Retorna: 12.345.678-9
        """
        # Limpiar caracteres no válidos
        rut = rut.strip().upper()
        rut = rut.replace(".", "").replace("-", "")

        if len(rut) < 2:
            return rut

        # Separar número y dígito verificador
        numero = rut[:-1]
        dv = rut[-1]

        # Formatear con puntos
        numero_formatted = ""
        for i, char in enumerate(reversed(numero)):
            if i > 0 and i % 3 == 0:
                numero_formatted = "." + numero_formatted
            numero_formatted = char + numero_formatted

        return f"{numero_formatted}-{dv}"

    def _normalize_patente(self, patente: str) -> str:
        """
        Normaliza una patente para la API.

        Elimina espacios y guiones, convierte a mayúsculas.
        """
        return patente.strip().upper().replace(" ", "").replace("-", "")

    # =========================================================================
    # ENDPOINTS DE VEHÍCULOS
    # =========================================================================

    async def get_vehicle_info(self, patente: str) -> VehicleExtendedInfo:
        """
        Obtiene información de un vehículo por patente.

        Endpoint: GET /vehicle/{patente}.json

        Args:
            patente: Patente del vehículo (ej: "ABCD12")

        Returns:
            VehicleExtendedInfo con los datos del vehículo

        Example:
            >>> info = await client.get_vehicle_info("ABCD12")
            >>> print(f"{info.marca} {info.modelo} {info.año}")
        """
        patente = self._normalize_patente(patente)
        data = await self._request("GET", f"/vehicle/{patente}")

        if data.get("status") == "success" and data.get("data"):
            vehicle_data = data["data"]
            # Mapear campos de la API a nuestro modelo
            return VehicleExtendedInfo(
                patente=patente,
                marca=vehicle_data.get("brand") or vehicle_data.get("marca"),
                modelo=vehicle_data.get("model") or vehicle_data.get("modelo"),
                año=vehicle_data.get("year") or vehicle_data.get("año"),
                tipo=vehicle_data.get("type") or vehicle_data.get("tipo"),
                color=vehicle_data.get("color"),
                vin=vehicle_data.get("chassis") or vehicle_data.get("vin"),
                combustible=vehicle_data.get("fuel") or vehicle_data.get("combustible"),
                kilometraje=vehicle_data.get("mileage") or vehicle_data.get("kilometraje"),
                fabricante=vehicle_data.get("manufacturer") or vehicle_data.get("fabricante"),
                pais_origen=vehicle_data.get("origin_country"),
                puertas=vehicle_data.get("doors"),
                version=vehicle_data.get("version"),
                motor=vehicle_data.get("engine"),
                transmision=vehicle_data.get("transmission"),
                propietario_rut=vehicle_data.get("owner_rut"),
                propietario_nombre=vehicle_data.get("owner_name"),
            )

        raise BoostrNotFoundError(f"Vehículo con patente {patente} no encontrado")

    async def get_traffic_fines(self, patente: str) -> List[TrafficFine]:
        """
        Obtiene las multas de tránsito de un vehículo.

        Endpoint: GET /vehicle/{patente}/multas.json

        Args:
            patente: Patente del vehículo

        Returns:
            Lista de multas de tránsito
        """
        patente = self._normalize_patente(patente)

        try:
            data = await self._request("GET", f"/vehicle/{patente}/multas")

            if data.get("status") == "success" and data.get("data"):
                fines_data = data["data"]
                if isinstance(fines_data, list):
                    return [TrafficFine(**fine) for fine in fines_data]
                elif isinstance(fines_data, dict) and fines_data.get("multas"):
                    return [TrafficFine(**fine) for fine in fines_data["multas"]]

            return []
        except BoostrNotFoundError:
            return []

    async def get_technical_review(self, patente: str) -> Optional[TechnicalReview]:
        """
        Obtiene información de la revisión técnica.

        Endpoint: GET /vehicle/{patente}/revision.json

        Args:
            patente: Patente del vehículo

        Returns:
            Información de revisión técnica o None
        """
        patente = self._normalize_patente(patente)

        try:
            data = await self._request("GET", f"/vehicle/{patente}/revision")

            if data.get("status") == "success" and data.get("data"):
                return TechnicalReview(**data["data"])

            return None
        except BoostrNotFoundError:
            return None

    async def get_soap_info(self, patente: str) -> Optional[SOAPInfo]:
        """
        Obtiene información del SOAP (Seguro Obligatorio).

        Endpoint: GET /vehicle/{patente}/soap.json

        Args:
            patente: Patente del vehículo

        Returns:
            Información del SOAP o None
        """
        patente = self._normalize_patente(patente)

        try:
            data = await self._request("GET", f"/vehicle/{patente}/soap")

            if data.get("status") == "success" and data.get("data"):
                return SOAPInfo(**data["data"])

            return None
        except BoostrNotFoundError:
            return None

    # =========================================================================
    # ENDPOINTS DE RUTIFICADOR
    # =========================================================================

    async def get_person_name(self, rut: str) -> PersonName:
        """
        Obtiene el nombre de una persona por RUT.

        Endpoint: GET /rut/name/{rut}.json

        Args:
            rut: RUT de la persona

        Returns:
            PersonName con el nombre
        """
        rut = self._normalize_rut(rut)
        data = await self._request("GET", f"/rut/name/{rut}")

        if data.get("status") == "success" and data.get("data"):
            person_data = data["data"]
            return PersonName(
                rut=rut,
                nombre=person_data.get("name") or person_data.get("nombre"),
                nombres=person_data.get("first_name") or person_data.get("nombres"),
                apellido_paterno=person_data.get("last_name")
                or person_data.get("apellido_paterno"),
                apellido_materno=person_data.get("mother_last_name")
                or person_data.get("apellido_materno"),
            )

        raise BoostrNotFoundError(f"Persona con RUT {rut} no encontrada")

    async def get_person_info(self, rut: str) -> PersonInfo:
        """
        Obtiene información completa de una persona por RUT.

        Endpoint: GET /rut/full/{rut}.json

        Args:
            rut: RUT de la persona

        Returns:
            PersonInfo con datos completos
        """
        rut = self._normalize_rut(rut)
        data = await self._request("GET", f"/rut/full/{rut}")

        if data.get("status") == "success" and data.get("data"):
            person_data = data["data"]
            return PersonInfo(
                rut=rut,
                nombre=person_data.get("name") or person_data.get("nombre"),
                nombres=person_data.get("first_name") or person_data.get("nombres"),
                apellido_paterno=person_data.get("last_name")
                or person_data.get("apellido_paterno"),
                apellido_materno=person_data.get("mother_last_name")
                or person_data.get("apellido_materno"),
                genero=person_data.get("gender") or person_data.get("genero"),
                nacionalidad=person_data.get("nationality") or person_data.get("nacionalidad"),
                fecha_nacimiento=person_data.get("birth_date")
                or person_data.get("fecha_nacimiento"),
                edad=person_data.get("age") or person_data.get("edad"),
                fallecido=person_data.get("deceased") or person_data.get("fallecido"),
            )

        raise BoostrNotFoundError(f"Persona con RUT {rut} no encontrada")

    async def get_person_vehicles(self, rut: str) -> List[PersonVehicle]:
        """
        Obtiene los vehículos asociados a un RUT.

        Endpoint: GET /rut/vehicles/{rut}.json

        Args:
            rut: RUT de la persona o empresa

        Returns:
            Lista de vehículos registrados
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/vehicles/{rut}")

            if data.get("status") == "success" and data.get("data"):
                vehicles_data = data["data"]
                if isinstance(vehicles_data, list):
                    return [
                        PersonVehicle(
                            patente=v.get("plate") or v.get("patente"),
                            marca=v.get("brand") or v.get("marca"),
                            modelo=v.get("model") or v.get("modelo"),
                            año=v.get("year") or v.get("año"),
                            tipo=v.get("type") or v.get("tipo"),
                        )
                        for v in vehicles_data
                    ]

            return []
        except BoostrNotFoundError:
            return []

    async def get_person_properties(self, rut: str) -> List[PersonProperty]:
        """
        Obtiene las propiedades asociadas a un RUT.

        Endpoint: GET /rut/properties/{rut}.json

        Args:
            rut: RUT de la persona o empresa

        Returns:
            Lista de propiedades
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/properties/{rut}")

            if data.get("status") == "success" and data.get("data"):
                props_data = data["data"]
                if isinstance(props_data, list):
                    return [PersonProperty(**prop) for prop in props_data]

            return []
        except BoostrNotFoundError:
            return []

    # =========================================================================
    # VERIFICACIONES ESPECIALES
    # =========================================================================

    async def check_pep(self, rut: str) -> PEPInfo:
        """
        Verifica si una persona es Políticamente Expuesta (PEP).

        Endpoint: GET /rut/pep/{rut}.json
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/pep/{rut}")

            if data.get("status") == "success" and data.get("data"):
                return PEPInfo(**data["data"])

            return PEPInfo(es_pep=False)
        except BoostrNotFoundError:
            return PEPInfo(es_pep=False)

    async def check_interpol(self, rut: str) -> InterpolInfo:
        """
        Verifica alertas de Interpol para un RUT.

        Endpoint: GET /rut/interpol/{rut}.json
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/interpol/{rut}")

            if data.get("status") == "success" and data.get("data"):
                return InterpolInfo(**data["data"])

            return InterpolInfo(tiene_alerta=False)
        except BoostrNotFoundError:
            return InterpolInfo(tiene_alerta=False)

    async def check_deceased(self, rut: str) -> DeceasedInfo:
        """
        Verifica si una persona ha fallecido.

        Endpoint: GET /rut/deceased/{rut}.json
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/deceased/{rut}")

            if data.get("status") == "success" and data.get("data"):
                return DeceasedInfo(**data["data"])

            return DeceasedInfo(fallecido=False)
        except BoostrNotFoundError:
            return DeceasedInfo(fallecido=False)

    # =========================================================================
    # MÉTODOS AGREGADOS PARA INVESTIGACIONES
    # =========================================================================

    async def investigar_vehiculo(
        self,
        patente: str,
        incluir_multas: bool = True,
        incluir_revision: bool = True,
        incluir_soap: bool = True,
    ) -> InvestigacionBoostrResult:
        """
        Realiza una investigación completa de un vehículo.

        Consulta múltiples endpoints y consolida la información.

        Args:
            patente: Patente del vehículo a investigar
            incluir_multas: Si incluir consulta de multas
            incluir_revision: Si incluir revisión técnica
            incluir_soap: Si incluir información del SOAP

        Returns:
            InvestigacionBoostrResult con toda la información
        """
        result = InvestigacionBoostrResult()
        creditos = 0

        # Obtener información del vehículo
        try:
            result.vehiculo = await self.get_vehicle_info(patente)
            creditos += 1
        except BoostrNotFoundError:
            logger.warning(f"Vehículo {patente} no encontrado en Boostr")

        # Multas (ubicaciones importantes para investigación)
        if incluir_multas:
            try:
                result.multas = await self.get_traffic_fines(patente)
                creditos += 1
            except BoostrAPIError as e:
                logger.warning(f"Error al obtener multas: {e}")

        # Revisión técnica
        if incluir_revision:
            try:
                result.revision_tecnica = await self.get_technical_review(patente)
                creditos += 1
            except BoostrAPIError as e:
                logger.warning(f"Error al obtener revisión técnica: {e}")

        # SOAP
        if incluir_soap:
            try:
                result.soap = await self.get_soap_info(patente)
                creditos += 1
            except BoostrAPIError as e:
                logger.warning(f"Error al obtener SOAP: {e}")

        result.creditos_usados = creditos
        return result

    async def investigar_propietario(
        self,
        rut: str,
        incluir_vehiculos: bool = True,
        incluir_propiedades: bool = True,
        incluir_verificaciones: bool = True,
    ) -> InvestigacionBoostrResult:
        """
        Realiza una investigación completa de un propietario.

        Args:
            rut: RUT de la persona a investigar
            incluir_vehiculos: Si incluir otros vehículos
            incluir_propiedades: Si incluir propiedades
            incluir_verificaciones: Si incluir PEP, Interpol, defunción

        Returns:
            InvestigacionBoostrResult con toda la información
        """
        result = InvestigacionBoostrResult()
        creditos = 0

        # Información de la persona
        try:
            result.propietario = await self.get_person_info(rut)
            creditos += 1
        except BoostrNotFoundError:
            logger.warning(f"Persona con RUT {rut} no encontrada")

        # Otros vehículos
        if incluir_vehiculos:
            try:
                result.otros_vehiculos = await self.get_person_vehicles(rut)
                creditos += 1
            except BoostrAPIError as e:
                logger.warning(f"Error al obtener vehículos: {e}")

        # Propiedades
        if incluir_propiedades:
            try:
                result.propiedades = await self.get_person_properties(rut)
                creditos += 1
            except BoostrAPIError as e:
                logger.warning(f"Error al obtener propiedades: {e}")

        # Verificaciones especiales
        if incluir_verificaciones:
            try:
                result.pep = await self.check_pep(rut)
                result.interpol = await self.check_interpol(rut)
                result.defuncion = await self.check_deceased(rut)
                creditos += 3
            except BoostrAPIError as e:
                logger.warning(f"Error en verificaciones: {e}")

        result.creditos_usados = creditos
        return result


# =============================================================================
# SINGLETON / DEPENDENCY INJECTION
# =============================================================================

_boostr_client: Optional[BoostrClient] = None


def get_boostr_client() -> BoostrClient:
    """
    Obtiene una instancia singleton del cliente de Boostr.

    Usar esta función para inyección de dependencias.

    Returns:
        BoostrClient configurado

    Example:
        >>> from src.shared.infrastructure.external_apis.boostr import get_boostr_client
        >>> client = get_boostr_client()
        >>> info = await client.get_vehicle_info("ABCD12")
    """
    global _boostr_client
    if _boostr_client is None:
        _boostr_client = BoostrClient()
    return _boostr_client


def reset_boostr_client() -> None:
    """Resetea el cliente singleton (útil para tests)."""
    global _boostr_client
    _boostr_client = None
