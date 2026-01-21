"""
Modelo SQLAlchemy para DocumentoProcesado.

Representa un documento PDF procesado desde local storage.

Principios aplicados:
- SRP: Solo define la estructura de la tabla documentos_procesados
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import TipoDocumentoEnum, EstadoDocumentoProcesadoEnum


class DocumentoProcesadoModel(Base):
    """
    Modelo de base de datos para documentos procesados desde local storage.

    Attributes:
        file_id: ID único del archivo (UUID generado localmente)
        file_name: Nombre original del archivo
        storage_path: Ruta relativa donde se guardó el archivo (ej: "2026/01/18/uuid.pdf")
        tipo_documento: Tipo de documento (oficio, cav, desconocido)
        par_documento_id: FK al otro documento del par (self-referential)
        buffet_id: FK al buffet (nullable)
        oficio_id: FK al oficio creado (nullable)
        estado: Estado de procesamiento
        datos_extraidos_json: JSON con datos parseados del documento
        error_mensaje: Mensaje de error si falla el procesamiento

    Relationships:
        par_documento: Otro documento del par (self-referential)
        buffet: Buffet asociado
        oficio: Oficio creado desde este documento
    """

    __tablename__ = "documentos_procesados"

    # Identificadores de archivo local
    file_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="ID único del archivo (UUID generado localmente)",
    )
    file_name = Column(
        String(500),
        nullable=False,
        comment="Nombre original del archivo",
    )
    storage_path = Column(
        String(500),
        nullable=False,
        index=True,
        comment="Ruta relativa donde se guardó el archivo (ej: 2026/01/18/uuid.pdf)",
    )

    # Tipo y estado
    tipo_documento = Column(
        Enum(TipoDocumentoEnum, name="tipo_documento_enum", create_type=True),
        nullable=False,
        default=TipoDocumentoEnum.DESCONOCIDO,
        index=True,
        comment="Tipo de documento (oficio, cav, desconocido)",
    )
    estado = Column(
        Enum(
            EstadoDocumentoProcesadoEnum,
            name="estado_documento_procesado_enum",
            create_type=True,
        ),
        nullable=False,
        default=EstadoDocumentoProcesadoEnum.PENDIENTE,
        index=True,
        comment="Estado de procesamiento del documento",
    )

    # Relaciones
    par_documento_id = Column(
        Integer,
        ForeignKey("documentos_procesados.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del otro documento del par (self-referential)",
    )
    buffet_id = Column(
        Integer,
        ForeignKey("buffets.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del buffet asociado",
    )
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del oficio creado desde este documento",
    )

    # Datos procesados
    datos_extraidos_json = Column(
        Text,
        nullable=True,
        comment="JSON con datos extraídos del documento",
    )
    error_mensaje = Column(
        Text,
        nullable=True,
        comment="Mensaje de error si falla el procesamiento",
    )

    # Relaciones
    par_documento = relationship(
        "DocumentoProcesadoModel",
        remote_side="DocumentoProcesadoModel.id",
        backref="documento_par",
        lazy="joined",
    )
    buffet = relationship("BuffetModel", lazy="joined")
    oficio = relationship("OficioModel", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<DocumentoProcesadoModel(id={self.id}, "
            f"file_id='{self.file_id}', "
            f"tipo='{self.tipo_documento.value}', "
            f"estado='{self.estado.value}')>"
        )
