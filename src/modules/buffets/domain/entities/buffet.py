"""
Entidad de Dominio Buffet.

Representa un estudio juridico o empresa de cobranza cliente del sistema.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import secrets

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects import RutChileno, Email


@dataclass
class Buffet(BaseEntity):
    """
    Entidad de dominio que representa un buffet (cliente).

    Attributes:
        nombre: Nombre del estudio juridico
        rut: RUT validado del buffet
        email_principal: Email de contacto principal
        telefono: Telefono de contacto
        contacto_nombre: Nombre de la persona de contacto
        token_tablero: Token unico para acceso al tablero publico
        activo: Si el buffet esta activo
    """

    nombre: str = ""
    rut: RutChileno = field(default=None)  # type: ignore
    email_principal: Email = field(default=None)  # type: ignore
    telefono: Optional[str] = None
    contacto_nombre: Optional[str] = None
    token_tablero: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    activo: bool = True

    @classmethod
    def crear(
        cls,
        nombre: str,
        rut: str,
        email_principal: str,
        telefono: Optional[str] = None,
        contacto_nombre: Optional[str] = None,
    ) -> "Buffet":
        """
        Factory method para crear un nuevo buffet.

        Args:
            nombre: Nombre del buffet
            rut: RUT del buffet (sera validado)
            email_principal: Email de contacto
            telefono: Telefono opcional
            contacto_nombre: Nombre del contacto opcional

        Returns:
            Nueva instancia de Buffet
        """
        rut_vo = RutChileno.crear(rut)
        email_vo = Email.crear(email_principal)

        return cls(
            nombre=nombre.strip(),
            rut=rut_vo,
            email_principal=email_vo,
            telefono=telefono,
            contacto_nombre=contacto_nombre,
            activo=True,
        )

    def desactivar(self) -> None:
        """Desactiva el buffet (soft delete)."""
        self.activo = False
        self.marcar_actualizado()

    def activar(self) -> None:
        """Activa el buffet."""
        self.activo = True
        self.marcar_actualizado()

    def regenerar_token(self) -> str:
        """Regenera el token del tablero."""
        self.token_tablero = secrets.token_urlsafe(32)
        self.marcar_actualizado()
        return self.token_tablero

    def actualizar(
        self,
        nombre: Optional[str] = None,
        email_principal: Optional[str] = None,
        telefono: Optional[str] = None,
        contacto_nombre: Optional[str] = None,
    ) -> None:
        """Actualiza datos del buffet."""
        if nombre is not None:
            self.nombre = nombre.strip()
        if email_principal is not None:
            self.email_principal = Email.crear(email_principal)
        if telefono is not None:
            self.telefono = telefono
        if contacto_nombre is not None:
            self.contacto_nombre = contacto_nombre
        self.marcar_actualizado()

    @property
    def rut_str(self) -> str:
        """Retorna el RUT como string."""
        return self.rut.valor if self.rut else ""

    @property
    def email_str(self) -> str:
        """Retorna el email como string."""
        return self.email_principal.valor if self.email_principal else ""

    @property
    def created_at(self) -> datetime:
        """Alias para compatibilidad."""
        return self.create_at

    @property
    def updated_at(self) -> datetime:
        """Alias para compatibilidad."""
        return self.update_at

    def __repr__(self) -> str:
        return f"<Buffet(id={self.id}, nombre='{self.nombre}', rut='{self.rut_str}')>"
