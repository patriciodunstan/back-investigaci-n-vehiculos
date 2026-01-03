"""
Modelo SQLAlchemy para Usuario.

Representa un usuario del sistema (admin, investigador o cliente).

Principios aplicados:
- SRP: Solo define la estructura de la tabla usuarios
- Separación: Modelo de infraestructura separado de entidad de dominio
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from src.shared.infrastructure.database.base import Base
from src.shared.domain.enums import RolEnum


class UsuarioModel(Base):
    """
    Modelo de base de datos para usuarios.

    Attributes:
        email: Email único del usuario (usado para login)
        nombre: Nombre completo del usuario
        password_hash: Hash bcrypt de la contraseña
        rol: Rol del usuario (admin, investigador, cliente)
        buffet_id: FK al buffet (requerido solo para clientes)
        activo: Si el usuario está activo
        avatar_url: URL del avatar (opcional)

    Relationships:
        buffet: Buffet al que pertenece (solo clientes)
        oficios_asignados: Oficios asignados (solo investigadores)
        investigaciones: Actividades de investigación realizadas
        adjuntos: Archivos subidos por el usuario

    Business Rules:
        - Si rol = "cliente", buffet_id es obligatorio
        - Si rol = "admin" o "investigador", buffet_id debe ser NULL
    """

    __tablename__ = "usuarios"

    # Campos de autenticación
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email único para login",
    )
    nombre = Column(String(255), nullable=False, comment="Nombre completo del usuario")
    password_hash = Column(
        String(255), nullable=False, comment="Hash bcrypt de la contraseña"
    )

    # Rol y permisos
    rol = Column(
        Enum(RolEnum, name="rol_enum", create_type=True),
        nullable=False,
        default=RolEnum.CLIENTE,
        comment="Rol del usuario en el sistema",
    )

    # Relación con buffet (solo para clientes)
    buffet_id = Column(
        Integer,
        ForeignKey("buffets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID del buffet (solo para clientes)",
    )

    # Estado
    activo = Column(
        Boolean, default=True, nullable=False, comment="Si el usuario está activo"
    )

    # Perfil
    avatar_url = Column(
        String(500), nullable=True, comment="URL del avatar del usuario"
    )

    # Relaciones
    buffet = relationship("BuffetModel", back_populates="usuarios", lazy="joined")
    oficios_asignados = relationship(
        "OficioModel",
        back_populates="investigador",
        foreign_keys="OficioModel.investigador_id",
        lazy="dynamic",
    )
    investigaciones = relationship(
        "InvestigacionModel", back_populates="investigador", lazy="dynamic"
    )
    adjuntos = relationship(
        "AdjuntoModel", back_populates="investigador", lazy="dynamic"
    )
    direcciones_agregadas = relationship(
        "DireccionModel", back_populates="agregada_por", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<UsuarioModel(id={self.id}, email='{self.email}', rol='{self.rol.value}')>"

    @property
    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == RolEnum.ADMIN

    @property
    def es_investigador(self) -> bool:
        """Verifica si el usuario es investigador"""
        return self.rol == RolEnum.INVESTIGADOR

    @property
    def es_cliente(self) -> bool:
        """Verifica si el usuario es cliente"""
        return self.rol == RolEnum.CLIENTE
