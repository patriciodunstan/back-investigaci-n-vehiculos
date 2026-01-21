"""
Parser para documentos de tipo Oficio.

Extrae información específica de documentos de oficios judiciales
usando regex patterns y validación de formatos.

Principios aplicados:
- SRP: Solo parsea documentos de tipo Oficio
- OCP: Abierto para extensión con nuevos campos
"""

import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.shared.domain.value_objects.rut import RutChileno, es_rut_valido  # noqa: F401


logger = logging.getLogger(__name__)


class OficioParser:
    """
    Parser para extraer información de documentos de tipo Oficio.

    Extrae:
    - Número de oficio
    - RUT del propietario
    - Nombre completo del propietario
    - Direcciones
    - Contexto legal/motivo
    - Fecha del oficio

    Example:
        >>> parser = OficioParser()
        >>> datos = parser.parse(texto_pdf)
        >>> print(datos["numero_oficio"])
    """

    # Patrones regex para extracción
    PATRON_NUMERO_OFICIO = re.compile(
        r"(?:OF|OFICIO|ROL)[\s\-]*(?:N[°º]?\s*)?(\d+(?:\/\d+)?)", re.IGNORECASE
    )
    PATRON_RUT = re.compile(r"(\d{1,2}\.?\d{3}\.?\d{3}[\-][\dkK])", re.IGNORECASE)
    PATRON_NOMBRE = re.compile(
        r"(?:PROPIETARIO|NOMBRE|SEÑOR[A]?|NOMBRES?)[\s:]+([A-ZÁÉÍÓÚÑ\s,\.]+)", re.IGNORECASE
    )
    PATRON_DIRECCION = re.compile(
        r"(?:DIRECCIÓN|DOMICILIO|DIR)[\s:]+([A-Z0-9\s,#\.\-\/]+(?:COMUNA|REGIÓN|REGION|CHILE)?)",
        re.IGNORECASE | re.MULTILINE,
    )
    PATRON_FECHA = re.compile(
        r"(?:FECHA|F\.)[\s:]+(\d{1,2}[\-\/]\d{1,2}[\-\/]\d{2,4})", re.IGNORECASE
    )

    def parse(self, texto: str) -> Dict[str, Any]:
        """
        Parsea un texto de documento de oficio y extrae información.

        Args:
            texto: Texto extraído del PDF del oficio

        Returns:
            Dict con los datos extraídos:
            - numero_oficio: Número del oficio (str o None)
            - rut_propietario: RUT del propietario (str o None)
            - nombre_propietario: Nombre completo (str o None)
            - direcciones: Lista de direcciones (List[str])
            - contexto_legal: Contexto/motivo del oficio (str o None)
            - fecha_oficio: Fecha del oficio (datetime o None)
        """
        texto_normalizado = self._normalizar_texto(texto)
        primeras_lineas = "\n".join(texto_normalizado.split("\n")[:30])

        datos = {
            "numero_oficio": self._extraer_numero_oficio(primeras_lineas),
            "rut_propietario": self._extraer_rut(texto_normalizado),
            "nombre_propietario": self._extraer_nombre(texto_normalizado),
            "direcciones": self._extraer_direcciones(texto_normalizado),
            "contexto_legal": self._extraer_contexto_legal(texto_normalizado),
            "fecha_oficio": self._extraer_fecha(texto_normalizado),
        }

        logger.debug(
            f"OficioParser extrajo: numero_oficio={datos['numero_oficio']}, rut={datos['rut_propietario']}"
        )

        return datos

    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza el texto para facilitar el parsing.

        Args:
            texto: Texto crudo

        Returns:
            Texto normalizado
        """
        # Reemplazar múltiples espacios por uno solo
        texto = re.sub(r"\s+", " ", texto)
        # Reemplazar múltiples saltos de línea por uno solo
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        # Limpiar caracteres no imprimibles
        texto = "".join(char for char in texto if char.isprintable() or char in "\n\t")
        return texto.strip()

    def _extraer_numero_oficio(self, texto: str) -> Optional[str]:
        """
        Extrae el número de oficio del texto.

        Args:
            texto: Texto a analizar (primeras líneas)

        Returns:
            Número de oficio o None
        """
        match = self.PATRON_NUMERO_OFICIO.search(texto)
        if match:
            numero = match.group(1)
            logger.debug(f"Numero de oficio extraído: {numero}")
            return numero
        return None

    def _extraer_rut(self, texto: str) -> Optional[str]:
        """
        Extrae el RUT del propietario.

        Args:
            texto: Texto a analizar

        Returns:
            RUT validado y formateado o None
        """
        matches = self.PATRON_RUT.findall(texto)

        # Buscar el primer RUT válido
        for rut_match in matches:
            rut_str = rut_match.strip()
            if es_rut_valido(rut_str):
                try:
                    # Validar y formatear usando Value Object
                    rut = RutChileno.crear(rut_str)
                    logger.debug(f"RUT extraído y validado: {rut.valor}")
                    return rut.valor
                except ValueError:
                    logger.warning(f"RUT encontrado pero inválido: {rut_str}")
                    continue

        return None

    def _extraer_nombre(self, texto: str) -> Optional[str]:
        """
        Extrae el nombre completo del propietario.

        Args:
            texto: Texto a analizar

        Returns:
            Nombre completo normalizado o None
        """
        match = self.PATRON_NOMBRE.search(texto)
        if match:
            nombre = match.group(1).strip()
            # Limpiar y normalizar
            nombre = re.sub(r"\s+", " ", nombre)
            nombre = nombre.strip(".,")
            if len(nombre) > 3:  # Mínimo de caracteres razonables
                logger.debug(f"Nombre extraído: {nombre}")
                return nombre
        return None

    def _extraer_direcciones(self, texto: str) -> List[str]:
        """
        Extrae direcciones del texto.

        Args:
            texto: Texto a analizar

        Returns:
            Lista de direcciones encontradas
        """
        direcciones = []
        matches = self.PATRON_DIRECCION.findall(texto)

        for match in matches:
            direccion = match.strip()
            # Limpiar
            direccion = re.sub(r"\s+", " ", direccion)
            direccion = direccion.strip(".,:")
            if len(direccion) > 10:  # Mínimo de caracteres razonables
                direcciones.append(direccion)
                logger.debug(f"Dirección extraída: {direccion}")

        return direcciones

    def _extraer_contexto_legal(self, texto: str) -> Optional[str]:
        """
        Extrae el contexto legal o motivo del oficio.

        Busca secciones como "MOTIVO:", "ASUNTO:", "ANTECEDENTES:"

        Args:
            texto: Texto a analizar

        Returns:
            Contexto legal o None
        """
        patrones_seccion = [
            r"(?:MOTIVO|ASUNTO)[\s:]+(.+?)(?:\n\n|\n[A-Z]{2,}|$)",
            r"(?:ANTECEDENTES)[\s:]+(.+?)(?:\n\n|\n[A-Z]{2,}|$)",
        ]

        for patron in patrones_seccion:
            match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
            if match:
                contexto = match.group(1).strip()
                contexto = re.sub(r"\s+", " ", contexto)
                if len(contexto) > 20:
                    logger.debug(f"Contexto legal extraído (longitud: {len(contexto)})")
                    return contexto

        return None

    def _extraer_fecha(self, texto: str) -> Optional[datetime]:
        """
        Extrae la fecha del oficio.

        Args:
            texto: Texto a analizar

        Returns:
            datetime o None
        """
        match = self.PATRON_FECHA.search(texto)
        if match:
            fecha_str = match.group(1).strip()
            # Intentar parsear diferentes formatos
            formatos = ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]
            for formato in formatos:
                try:
                    fecha = datetime.strptime(fecha_str, formato)
                    logger.debug(f"Fecha extraída: {fecha}")
                    return fecha
                except ValueError:
                    continue

        return None
