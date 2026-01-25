"""
Cliente HTTP para la API de Boostr.

Implementa la integración con los endpoints de Rutificador
de Boostr para el sistema de investigaciones vehiculares.

Endpoints disponibles:
- /rut/vehicles/{rut}.json - Vehículos a nombre de un RUT
- /rut/properties/{rut}.json - Propiedades a nombre de un RUT
- /rut/deceased/{rut}.json - Estado de defunción

Documentación: https://docs.boostr.cl/reference
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx

from src.core.config import get_settings
from src.core.logging_config import (
    log_http_request,
    log_http_response,
    log_boostr_request,
    log_boostr_response,
    get_logger,
)
from .schemas import (
    PersonVehicle,
    PersonProperty,
    DeceasedInfo,
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


logger = get_logger(__name__)


class BoostrClient:
    """
    Cliente para la API de Boostr Chile (Rutificador).

    Proporciona métodos para consultar información por RUT:
    - Vehículos registrados a nombre del RUT
    - Propiedades registradas a nombre del RUT
    - Estado de defunción

    Attributes:
        base_url: URL base de la API
        api_key: API Key para autenticación
        timeout: Timeout en segundos para las requests

    Example:
        >>> client = BoostrClient()
        >>> vehicles = await client.get_person_vehicles("12.345.678-9")
        >>> print(f"Vehículos encontrados: {len(vehicles)}")
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

        if not self.api_key:
            logger.warning(
                "BoostrClient inicializado SIN API KEY. "
                "Las requests fallarán. Configure BOOSTR_API_KEY."
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
            "User-Agent": "InvestigacionesVehiculares/1.0",
        }
        if self.api_key:
            # Usar solo X-API-KEY (recomendado por Boostr)
            headers["X-API-KEY"] = self.api_key
        return headers

    async def _wait_for_rate_limit(self) -> None:
        """
        Espera si es necesario para respetar el rate limit.

        Boostr permite máximo 5 requests cada 10 segundos.
        """
        async with self._lock:
            now = datetime.utcnow()

            # Limpiar requests antiguas
            window_start = now.timestamp() - self.RATE_LIMIT_WINDOW
            self._request_times = [t for t in self._request_times if t.timestamp() > window_start]

            # Si estamos en el límite, esperar
            if len(self._request_times) >= self.RATE_LIMIT_REQUESTS:
                oldest = min(self._request_times)
                wait_time = self.RATE_LIMIT_WINDOW - (now.timestamp() - oldest.timestamp())
                if wait_time > 0:
                    logger.warning(f"Rate limit alcanzado, esperando {wait_time:.2f}s")
                    await asyncio.sleep(wait_time + 0.1)

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
        # Loguear request saliente
        rut_normalizado = endpoint.split('/')[-1].replace('.json', '') if '/rut/' in endpoint else params.get('rut', 'N/A')
        log_boostr_request(logger, endpoint, rut_normalizado, self.base_url)

        await self._wait_for_rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if not url.endswith(".json"):
            url += ".json"

        try:
            start_time = datetime.utcnow()
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    params=params,
                )
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000

                # Loguear response entrante
                log_http_response(logger, response.status_code, duration_ms, response.content)

                # Evaluar status code
                if response.status_code == 401:
                    raise BoostrAuthenticationError("API Key inválida o sin créditos disponibles")
                elif response.status_code == 429:
                    raise BoostrRateLimitError()
                elif response.status_code == 404:
                    raise BoostrNotFoundError(f"No se encontró: {endpoint}")
                elif response.status_code >= 500:
                    raise BoostrServiceUnavailableError()

                if not response.content or len(response.content) == 0:
                    raise BoostrAPIError(
                        f"Respuesta vacía de Boostr API (status: {response.status_code})"
                    )

                try:
                    data = response.json()
                except Exception as json_error:
                    content_preview = response.text[:200] if response.text else "N/A"
                    logger.error(f"❌ Error parseando JSON: {str(json_error)}. Preview: {content_preview}")
                    raise BoostrAPIError(
                        f"Respuesta inválida de Boostr (status: {response.status_code}): "
                        f"{str(json_error)}. Preview: {content_preview}"
                    )

                if isinstance(data, dict) and data.get("status") == "error":
                    error_msg = data.get("message") or data.get("data") or "Error desconocido"
                    if "invalid" in error_msg.lower() or "inválido" in error_msg.lower():
                        raise BoostrValidationError(error_msg)
                    logger.error(f"❌ Error de validación Boostr: {error_msg}")
                    raise BoostrAPIError(error_msg)

                return data

        except httpx.TimeoutException:
            logger.error(f"❌ Timeout error en request a {url}")
            raise BoostrTimeoutError()
        except httpx.RequestError as e:
            logger.error(f"❌ Connection error: {str(e)}")
            raise BoostrAPIError(f"Error de conexión: {str(e)}")

    def _normalize_rut(self, rut: str) -> str:
        """
        Normaliza un RUT para la API.

        Acepta: 12345678-9, 12.345.678-9
        Retorna: 12.345.678-9
        """
        rut = rut.strip().upper()
        rut = rut.replace(".", "").replace("-", "")

        if len(rut) < 2:
            return rut

        numero = rut[:-1]
        dv = rut[-1]

        numero_formatted = ""
        for i, char in enumerate(reversed(numero)):
            if i > 0 and i % 3 == 0:
                numero_formatted = "." + numero_formatted
            numero_formatted = char + numero_formatted

        return f"{numero_formatted}-{dv}"

    # =========================================================================
    # ENDPOINTS DISPONIBLES
    # =========================================================================

    async def get_person_vehicles(self, rut: str) -> List[PersonVehicle]:
        """
        Obtiene los vehículos registrados a nombre de un RUT.

        Endpoint: GET /rut/vehicles/{rut}.json

        Args:
            rut: RUT de la persona o empresa

        Returns:
            Lista de vehículos registrados

        Example:
            >>> vehicles = await client.get_person_vehicles("12.345.678-9")
            >>> for v in vehicles:
            ...     print(f"{v.patente} - {v.marca} {v.modelo}")
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/vehicles/{rut}")

            if data.get("status") == "success" and data.get("data"):
                vehicles_data = data["data"]
                if isinstance(vehicles_data, list):
                    vehicles = [
                        PersonVehicle(
                            patente=v.get("plate") or v.get("patente"),
                            marca=v.get("brand") or v.get("marca"),
                            modelo=v.get("model") or v.get("modelo"),
                            año=v.get("year") or v.get("año"),
                            tipo=v.get("type") or v.get("tipo"),
                        )
                        for v in vehicles_data
                    ]
                    # Loguear resultado exitoso
                    log_boostr_response(
                        logger, rut=rut, 
                        vehicles_count=len(vehicles), 
                        properties_count=0, 
                        deceased=False
                    )
                    return vehicles

            # Loguear respuesta vacía
            log_boostr_response(
                logger, rut=rut,
                vehicles_count=0,
                properties_count=0,
                deceased=False
            )
            return []
        except BoostrNotFoundError:
            logger.warning(f"⚠️ Vehículos no encontrados para RUT {rut}")
            return []

    async def get_person_properties(self, rut: str) -> List[PersonProperty]:
        """
        Obtiene las propiedades registradas a nombre de un RUT.

        Endpoint: GET /rut/properties/{rut}.json

        Args:
            rut: RUT de la persona o empresa

        Returns:
            Lista de propiedades (bienes raíces)

        Example:
            >>> props = await client.get_person_properties("12.345.678-9")
            >>> for p in props:
            ...     print(f"{p.direccion}, {p.comuna}")
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/properties/{rut}")

            if data.get("status") == "success" and data.get("data"):
                props_data = data["data"]
                if isinstance(props_data, list):
                    properties = [
                        PersonProperty(
                            rol=p.get("rol"),
                            comuna=p.get("comuna"),
                            direccion=p.get("address") or p.get("direccion"),
                            destino=p.get("destino"),
                            avaluo=p.get("avaluo"),
                        )
                        for p in props_data
                    ]
                    # Loguear resultado exitoso
                    log_boostr_response(
                        logger, rut=rut,
                        vehicles_count=0,
                        properties_count=len(properties),
                        deceased=False
                    )
                    return properties

            # Loguear respuesta vacía
            log_boostr_response(
                logger, rut=rut,
                vehicles_count=0,
                properties_count=0,
                deceased=False
            )
            return []

        except BoostrNotFoundError:
            logger.warning(f"⚠️ Propiedades no encontradas para RUT {rut}")
            return []

    async def check_deceased(self, rut: str) -> DeceasedInfo:
        """
        Verifica si una persona ha fallecido.

        Endpoint: GET /rut/deceased/{rut}.json

        Args:
            rut: RUT de la persona

        Returns:
            DeceasedInfo con estado de defunción

        Example:
            >>> info = await client.check_deceased("12.345.678-9")
            >>> if info.fallecido:
            ...     print(f"Fallecido el {info.fecha_defuncion}")
        """
        rut = self._normalize_rut(rut)

        try:
            data = await self._request("GET", f"/rut/deceased/{rut}")

            if data.get("status") == "success" and data.get("data"):
                deceased_data = data["data"]
                return DeceasedInfo(
                    fallecido=deceased_data.get("deceased")
                    or deceased_data.get("fallecido")
                    or False,
                    fecha_defuncion=deceased_data.get("death_date")
                    or deceased_data.get("fecha_defuncion"),
                )

            return DeceasedInfo(fallecido=False)
        except BoostrNotFoundError:
            return DeceasedInfo(fallecido=False)


# =============================================================================
# SINGLETON / DEPENDENCY INJECTION
# =============================================================================

_boostr_client: Optional[BoostrClient] = None


def get_boostr_client() -> BoostrClient:
    """
    Obtiene una instancia singleton del cliente de Boostr.

    Returns:
        BoostrClient configurado

    Example:
        >>> from src.shared.infrastructure.external_apis.boostr import get_boostr_client
        >>> client = get_boostr_client()
        >>> vehicles = await client.get_person_vehicles("12.345.678-9")
    """
    global _boostr_client
    if _boostr_client is None:
        _boostr_client = BoostrClient()
    return _boostr_client


def reset_boostr_client() -> None:
    """Resetea el cliente singleton (útil para tests)."""
    global _boostr_client
    _boostr_client = None
