"""
Entidad de Dominio Usuario.

Representa un usuario del sistema con su logica de negocio.

Principios aplicados:
- SRP: Solo logica de negocio del usuario
- Encapsulamiento: Validaciones internas
- Inmutabilidad: Cambios controlados
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums import RolEnum
from src.shared.domain.value_objects import Email


@dataclass
class Usuario(BaseEntity):
    """
    Entidad de dominio que representa un usuario del sistema.

    Attributes:
        email: Email validado del usuario
        nombre: Nombre completo
        password_hash: Hash de la contrasena (nunca la contrasena en texto plano)
        rol: Rol del usuario (admin, investigador, cliente)
        buffet_id: ID del buffet (solo para clientes)
        activo: Si el usuario esta activo
        avatar_url: URL del avatar (opcional)

    Business Rules:
        - El email debe ser unico (validado en repositorio)
        - Si rol es CLIENTE, buffet_id es obligatorio
        - Si rol es ADMIN o INVESTIGADOR, buffet_id debe ser None
    """

    email: Email = field(default=None)  # type: ignore
    nombre: str = ""
    password_hash: str = ""
    rol: RolEnum = RolEnum.CLIENTE
    buffet_id: Optional[int] = None
    activo: bool = True
    avatar_url: Optional[str] = None

    def __post_init__(self):
        """Validaciones post-inicializacion."""
        super().__post_init__()
        self._validar_buffet_segun_rol()

    def _validar_buffet_segun_rol(self) -> None:
        """Valida que buffet_id sea coherente con el rol."""
        if self.rol == RolEnum.CLIENTE and self.buffet_id is None:
            # Solo advertencia, puede asignarse despues
            pass
        elif self.rol in (RolEnum.ADMIN, RolEnum.INVESTIGADOR) and self.buffet_id is not None:
            raise ValueError(f"Usuario con rol {self.rol.value} no debe tener buffet_id asignado")

    @classmethod
    def crear(
        cls,
        email: str,
        nombre: str,
        password_hash: str,
        rol: RolEnum = RolEnum.CLIENTE,
        buffet_id: Optional[int] = None,
        activo: bool = True,
    ) -> "Usuario":
        """
        Factory method para crear un nuevo usuario.

        Args:
            email: Email del usuario (sera validado)
            nombre: Nombre completo
            password_hash: Hash de la contrasena
            rol: Rol del usuario
            buffet_id: ID del buffet (solo para clientes)
            activo: Si el usuario esta activo (default: True)

        Returns:
            Nueva instancia de Usuario

        Raises:
            ValueError: Si el email es invalido o las reglas de negocio no se cumplen
        """
        email_vo = Email.crear(email)

        return cls(
            email=email_vo,
            nombre=nombre.strip(),
            password_hash=password_hash,
            rol=rol,
            buffet_id=buffet_id,
            activo=activo,
        )

    def desactivar(self) -> None:
        """Desactiva el usuario (soft delete)."""
        self.activo = False
        self.marcar_actualizado()

    def activar(self) -> None:
        """Activa el usuario."""
        self.activo = True
        self.marcar_actualizado()

    def cambiar_contrasena(self, nuevo_hash: str) -> None:
        """Cambia el hash de la contraseña."""
        self.password_hash = nuevo_hash
        self.marcar_actualizado()

    def cambiar_rol(self, nuevo_rol: RolEnum, buffet_id: Optional[int] = None) -> None:
        """
        Cambia el rol del usuario.

        Args:
            nuevo_rol: Nuevo rol a asignar
            buffet_id: ID del buffet (requerido si nuevo_rol es CLIENTE)
        """
        if nuevo_rol == RolEnum.CLIENTE and buffet_id is None:
            raise ValueError("Cliente debe tener buffet_id asignado")

        if nuevo_rol in (RolEnum.ADMIN, RolEnum.INVESTIGADOR):
            self.buffet_id = None
        else:
            self.buffet_id = buffet_id

        self.rol = nuevo_rol
        self.marcar_actualizado()

    def actualizar_perfil(
        self,
        nombre: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> None:
        """Actualiza datos del perfil."""
        if nombre is not None:
            self.nombre = nombre.strip()
        if avatar_url is not None:
            self.avatar_url = avatar_url
        self.marcar_actualizado()

    @property
    def es_admin(self) -> bool:
        """Verifica si es administrador."""
        return self.rol == RolEnum.ADMIN

    @property
    def es_investigador(self) -> bool:
        """Verifica si es investigador."""
        return self.rol == RolEnum.INVESTIGADOR

    @property
    def es_cliente(self) -> bool:
        """Verifica si es cliente."""
        return self.rol == RolEnum.CLIENTE

    @property
    def email_str(self) -> str:
        """Retorna el email como string."""
        return self.email.valor if self.email else ""

    @property
    def created_at(self) -> datetime:
        """Alias para compatibilidad."""
        return self.create_at

    @property
    def updated_at(self) -> datetime:
        """Alias para compatibilidad."""
        return self.update_at

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, email='{self.email_str}', rol='{self.rol.value}')>"
