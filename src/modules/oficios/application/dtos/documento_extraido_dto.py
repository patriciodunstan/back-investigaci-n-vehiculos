"""
DTOs para documentos extraídos desde local storage.

Representan los datos parseados de documentos PDF procesados.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass(frozen=True)
class OficioExtraidoDTO:
    """
    DTO para datos extraídos de un documento de Oficio.

    Contiene los datos parseados por OficioParser.
    """

    numero_oficio: Optional[str] = None
    rut_propietario: Optional[str] = None
    nombre_propietario: Optional[str] = None
    direcciones: List[str] = None
    contexto_legal: Optional[str] = None
    fecha_oficio: Optional[datetime] = None

    def __post_init__(self):
        """Normaliza valores después de la creación."""
        if self.direcciones is None:
            object.__setattr__(self, "direcciones", [])


@dataclass(frozen=True)
class CAVExtraidoDTO:
    """
    DTO para datos extraídos de un documento CAV.

    Contiene los datos parseados por CAVParser.
    """

    patente: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    año: Optional[int] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    tipo: Optional[str] = None
    combustible: Optional[str] = None


@dataclass(frozen=True)
class ParDocumentoDTO:
    """
    DTO para un par completo de documentos (Oficio + CAV).

    Contiene los datos extraídos de ambos documentos y metadatos
    para crear el oficio en el sistema.

    Attributes:
        file_id_oficio: ID único del archivo de Oficio (UUID)
        file_id_cav: ID único del archivo de CAV (UUID)
        file_name_oficio: Nombre original del archivo de Oficio
        file_name_cav: Nombre original del archivo de CAV
        storage_path_oficio: Ruta relativa donde se guardó el PDF del Oficio
        storage_path_cav: Ruta relativa donde se guardó el PDF del CAV
        oficio_extraido: Datos parseados del Oficio
        cav_extraido: Datos parseados del CAV
        buffet_id: ID del buffet asociado (opcional)
        pdf_bytes_oficio: Bytes del PDF del Oficio (para guardar como adjunto)
        pdf_bytes_cav: Bytes del PDF del CAV (para guardar como adjunto)
    """

    file_id_oficio: str
    file_id_cav: str
    file_name_oficio: str
    file_name_cav: str
    storage_path_oficio: str
    storage_path_cav: str
    oficio_extraido: OficioExtraidoDTO
    cav_extraido: CAVExtraidoDTO
    buffet_id: Optional[int] = None
    pdf_bytes_oficio: Optional[bytes] = None
    pdf_bytes_cav: Optional[bytes] = None
