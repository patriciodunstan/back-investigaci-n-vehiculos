"""
Excepciones especificas del modulo Usuarios.

Principios aplicados:
- SRP: Excepciones solo para usuarios
- Herencia: Extiende excepciones base del dominio
"""

from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
    UnauthorizedException,
)


class UsuarioNotFoundException(EntityNotFoundException):
    """Usuario no encontrado."""

    def __init__(self, identifier: str | int):
        if isinstance(identifier, int):
            super().__init__("Usuario", identifier)
        else:
            self.message = f"Usuario con email '{identifier}' no encontrado"
            self.code = "USER_NOT_FOUND"
            Exception.__init__(self, self.message)


class EmailAlreadyExistsException(DuplicateEntityException):
    """Email ya registrado en el sistema."""

    def __init__(self, email: str):
        super().__init__("Usuario", "email", email)
        self.email = email


class InvalidCredentialsException(UnauthorizedException):
    """Credenciales invalidas (email o password incorrectos)."""

    def __init__(self):
        super().__init__("Credenciales invalidas")
        self.code = "INVALID_CREDENTIALS"


class InactiveUserException(DomainException):
    """Usuario esta inactivo."""

    def __init__(self, email: str):
        super().__init__(
            message=f"El usuario '{email}' esta inactivo", code="INACTIVE_USER"
        )
        self.email = email


class InvalidTokenException(UnauthorizedException):
    """Token JWT invalido o expirado."""

    def __init__(self, reason: str = "Token invalido o expirado"):
        super().__init__(reason)
        self.code = "INVALID_TOKEN"


class InsufficientPermissionsException(UnauthorizedException):
    """Usuario no tiene permisos suficientes."""

    def __init__(self, required_role: str):
        super().__init__(f"Se requiere rol '{required_role}' para esta accion")
        self.code = "INSUFFICIENT_PERMISSIONS"
        self.required_role = required_role
