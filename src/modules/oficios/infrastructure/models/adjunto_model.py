"""
Modelo SQLAlchemy para Adjunto.

Representa un archivo adjunto (foto, documento) de un oficio.

Principios aplicados:
- SRP: Solo define la estructura de la tabla adjuntos
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import TipoAdjuntoEnum


class AdjuntoModel(Base):
    """
    Modelo de base de datos para adjuntos.

    Attributes:
        oficio_id: FK al oficio
        investigador_id: FK al usuario que lo subió
        tipo: Tipo de adjunto
        filename: Nombre del archivo
        url: Path o URL del archivo
        mime_type: Tipo MIME del archivo
        tamaño_bytes: Tamaño en bytes
        descripcion: Descripción del adjunto
        fecha_subida: Fecha y hora de subida
        metadata_json: Metadata adicional (GPS, EXIF, etc.)

    Relationships:
        oficio: Oficio al que pertenece
        investigador: Usuario que lo subió
    """

    __tablename__ = "adjuntos"

    # Relaciones
    oficio_id = Column(
        Integer,
        ForeignKey("oficios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del oficio",
    )
    investigador_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID del usuario que subió el adjunto",
    )

    # Datos del archivo
    tipo = Column(
        Enum(TipoAdjuntoEnum, name="tipo_adjunto_enum", create_type=True),
        nullable=False,
        default=TipoAdjuntoEnum.FOTO_VEHICULO,
        comment="Tipo de adjunto",
    )
    filename = Column(String(255), nullable=False, comment="Nombre del archivo")
    url = Column(String(500), nullable=False, comment="Path o URL del archivo")
    mime_type = Column(String(100), nullable=True, comment="Tipo MIME del archivo")
    tamaño_bytes = Column(Integer, nullable=True, comment="Tamaño en bytes")
    descripcion = Column(Text, nullable=True, comment="Descripción del adjunto")
    fecha_subida = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora de subida",
    )
    metadata_json = Column(
        Text, nullable=True, comment="Metadata adicional en JSON (GPS, EXIF)"
    )

    # Relaciones
    oficio = relationship("OficioModel", back_populates="adjuntos", lazy="joined")
    investigador = relationship(
        "UsuarioModel", back_populates="adjuntos", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<AdjuntoModel(id={self.id}, filename='{self.filename}', tipo='{self.tipo.value}')>"
