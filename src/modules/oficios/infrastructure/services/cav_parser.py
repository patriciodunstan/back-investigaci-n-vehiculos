"""
Parser para documentos CAV (Certificado de Inscripción y Anotaciones Vigentes).

Extrae información específica de certificados CAV de vehículos chilenos
usando regex patterns y validación de formatos.

Principios aplicados:
- SRP: Solo parsea documentos de tipo CAV
- OCP: Abierto para extensión con nuevos campos
"""

import re
import logging
from typing import Optional, Dict, Any

from src.shared.domain.value_objects.patente import Patente


logger = logging.getLogger(__name__)


class CAVParser:
    """
    Parser para extraer información de documentos CAV.
    
    Extrae:
    - Patente del vehículo
    - Marca
    - Modelo
    - Año
    - Color
    - VIN (Número de chasis)
    - Tipo de vehículo
    - Combustible
    
    Example:
        >>> parser = CAVParser()
        >>> datos = parser.parse(texto_pdf)
        >>> print(datos["patente"])
    """
    
    # Patrones regex para extracción
    PATRON_PATENTE = re.compile(
        r"(?:PATENTE|PLACA)[\s:]+([A-Z]{2,4}[\s\-]?\d{2,4})",
        re.IGNORECASE
    )
    PATRON_MARCA = re.compile(
        r"(?:MARCA)[\s:]+([A-ZÁÉÍÓÚÑ\s\-]+?)(?:\n|MODELO|$)",
        re.IGNORECASE
    )
    PATRON_MODELO = re.compile(
        r"(?:MODELO)[\s:]+([A-Z0-9ÁÉÍÓÚÑ\s\-]+?)(?:\n|AÑO|AÑO|$)",
        re.IGNORECASE
    )
    PATRON_ANO = re.compile(
        r"(?:AÑO|AÑO)[\s:]+(\d{4})",
        re.IGNORECASE
    )
    PATRON_COLOR = re.compile(
        r"(?:COLOR)[\s:]+([A-ZÁÉÍÓÚÑ\s\-]+?)(?:\n|VIN|CHASIS|TIPO|$)",
        re.IGNORECASE
    )
    PATRON_VIN = re.compile(
        r"(?:VIN|CHASIS|NÚMERO\s+CHASIS)[\s:]+([A-Z0-9]{10,17})",
        re.IGNORECASE
    )
    PATRON_TIPO = re.compile(
        r"(?:TIPO)[\s:]+([A-ZÁÉÍÓÚÑ\s\-]+?)(?:\n|COMBUSTIBLE|$)",
        re.IGNORECASE
    )
    PATRON_COMBUSTIBLE = re.compile(
        r"(?:COMBUSTIBLE)[\s:]+([A-ZÁÉÍÓÚÑ\s\-]+?)(?:\n|$)",
        re.IGNORECASE
    )
    
    # Marcas comunes para normalización
    MARCAS_NORMALIZADAS = {
        "TOYOTA": "TOYOTA",
        "CHEVROLET": "CHEVROLET",
        "CHEVY": "CHEVROLET",
        "NISSAN": "NISSAN",
        "HYUNDAI": "HYUNDAI",
        "KIA": "KIA",
        "FORD": "FORD",
        "MAZDA": "MAZDA",
        "VOLKSWAGEN": "VOLKSWAGEN",
        "VW": "VOLKSWAGEN",
        "SUZUKI": "SUZUKI",
        "PEUGEOT": "PEUGEOT",
        "RENAULT": "RENAULT",
        "FIAT": "FIAT",
        "MITSUBISHI": "MITSUBISHI",
    }
    
    def parse(self, texto: str) -> Dict[str, Any]:
        """
        Parsea un texto de documento CAV y extrae información.
        
        Args:
            texto: Texto extraído del PDF del CAV
        
        Returns:
            Dict con los datos extraídos:
            - patente: Patente del vehículo (str o None)
            - marca: Marca del vehículo (str o None)
            - modelo: Modelo del vehículo (str or None)
            - año: Año del vehículo (int or None)
            - color: Color del vehículo (str or None)
            - vin: VIN/Número de chasis (str or None)
            - tipo: Tipo de vehículo (str or None)
            - combustible: Tipo de combustible (str or None)
        """
        texto_normalizado = self._normalizar_texto(texto)
        
        datos = {
            "patente": self._extraer_patente(texto_normalizado),
            "marca": self._extraer_marca(texto_normalizado),
            "modelo": self._extraer_modelo(texto_normalizado),
            "año": self._extraer_ano(texto_normalizado),
            "color": self._extraer_color(texto_normalizado),
            "vin": self._extraer_vin(texto_normalizado),
            "tipo": self._extraer_tipo(texto_normalizado),
            "combustible": self._extraer_combustible(texto_normalizado),
        }
        
        logger.debug(
            f"CAVParser extrajo: patente={datos['patente']}, "
            f"marca={datos['marca']}, modelo={datos['modelo']}"
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
    
    def _extraer_patente(self, texto: str) -> Optional[str]:
        """
        Extrae la patente del vehículo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Patente validada y normalizada o None
        """
        match = self.PATRON_PATENTE.search(texto)
        if match:
            patente_str = match.group(1).strip()
            try:
                # Validar y normalizar usando Value Object
                patente = Patente.crear(patente_str)
                logger.debug(f"Patente extraída y validada: {patente.valor}")
                return patente.valor
            except ValueError:
                logger.warning(f"Patente encontrada pero inválida: {patente_str}")
        
        # Intentar buscar patente sin etiqueta (patrón común en CAVs)
        patron_libre = re.compile(r"\b([A-Z]{2}\d{4}|[A-Z]{4}\d{2})\b")
        matches = patron_libre.findall(texto)
        for patente_str in matches:
            try:
                patente = Patente.crear(patente_str)
                logger.debug(f"Patente extraída (sin etiqueta): {patente.valor}")
                return patente.valor
            except ValueError:
                continue
        
        return None
    
    def _extraer_marca(self, texto: str) -> Optional[str]:
        """
        Extrae la marca del vehículo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Marca normalizada o None
        """
        match = self.PATRON_MARCA.search(texto)
        if match:
            marca = match.group(1).strip().upper()
            marca = re.sub(r"\s+", " ", marca)
            marca = marca.strip(".,:-")
            
            # Normalizar usando diccionario de marcas
            marca_normalizada = self.MARCAS_NORMALIZADAS.get(marca, marca)
            if len(marca_normalizada) > 1:
                logger.debug(f"Marca extraída: {marca_normalizada}")
                return marca_normalizada
        
        return None
    
    def _extraer_modelo(self, texto: str) -> Optional[str]:
        """
        Extrae el modelo del vehículo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Modelo normalizado o None
        """
        match = self.PATRON_MODELO.search(texto)
        if match:
            modelo = match.group(1).strip()
            modelo = re.sub(r"\s+", " ", modelo)
            modelo = modelo.strip(".,:-")
            if len(modelo) > 1:
                logger.debug(f"Modelo extraído: {modelo}")
                return modelo
        
        return None
    
    def _extraer_ano(self, texto: str) -> Optional[int]:
        """
        Extrae el año del vehículo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Año como int o None
        """
        match = self.PATRON_ANO.search(texto)
        if match:
            año_str = match.group(1).strip()
            try:
                año = int(año_str)
                # Validar rango razonable (1900-2100)
                if 1900 <= año <= 2100:
                    logger.debug(f"Año extraído: {año}")
                    return año
            except ValueError:
                pass
        
        return None
    
    def _extraer_color(self, texto: str) -> Optional[str]:
        """
        Extrae el color del vehículo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Color normalizado o None
        """
        match = self.PATRON_COLOR.search(texto)
        if match:
            color = match.group(1).strip()
            color = re.sub(r"\s+", " ", color)
            color = color.strip(".,:-")
            color = color.upper()
            if len(color) > 2:
                logger.debug(f"Color extraído: {color}")
                return color
        
        return None
    
    def _extraer_vin(self, texto: str) -> Optional[str]:
        """
        Extrae el VIN (Vehicle Identification Number) o número de chasis.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            VIN normalizado (uppercase) o None
        """
        match = self.PATRON_VIN.search(texto)
        if match:
            vin = match.group(1).strip().upper()
            # VIN tiene entre 10 y 17 caracteres alfanuméricos
            if 10 <= len(vin) <= 17:
                logger.debug(f"VIN extraído: {vin}")
                return vin
        
        return None
    
    def _extraer_tipo(self, texto: str) -> Optional[str]:
        """
        Extrae el tipo de vehículo.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Tipo de vehículo normalizado o None
        """
        match = self.PATRON_TIPO.search(texto)
        if match:
            tipo = match.group(1).strip()
            tipo = re.sub(r"\s+", " ", tipo)
            tipo = tipo.strip(".,:-")
            tipo = tipo.upper()
            if len(tipo) > 2:
                logger.debug(f"Tipo extraído: {tipo}")
                return tipo
        
        return None
    
    def _extraer_combustible(self, texto: str) -> Optional[str]:
        """
        Extrae el tipo de combustible.
        
        Args:
            texto: Texto a analizar
        
        Returns:
            Tipo de combustible normalizado o None
        """
        match = self.PATRON_COMBUSTIBLE.search(texto)
        if match:
            combustible = match.group(1).strip()
            combustible = re.sub(r"\s+", " ", combustible)
            combustible = combustible.strip(".,:-")
            combustible = combustible.upper()
            if len(combustible) > 2:
                logger.debug(f"Combustible extraído: {combustible}")
                return combustible
        
        return None
