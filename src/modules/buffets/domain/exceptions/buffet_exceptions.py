"""
Excepciones especificas del modulo Buffets.
"""

from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
)


class BuffetNotFoundException(EntityNotFoundException):
    """Buffet no encontrado."""

    def __init__(self, identifier: int | str):
        if isinstance(identifier, int):
            super().__init__("Buffet", identifier)
        else:
            self.message = f"Buffet con RUT '{identifier}' no encontrado"
            self.code = "BUFFET_NOT_FOUND"
            Exception.__init__(self, self.message)


class RutAlreadyExistsException(DuplicateEntityException):
    """RUT ya registrado en el sistema."""

    def __init__(self, rut: str):
        super().__init__("Buffet", "rut", rut)
        self.rut = rut


class BuffetInactiveException(DomainException):
    """Buffet esta inactivo."""

    def __init__(self, buffet_id: int):
        super().__init__(
            message=f"El buffet con ID {buffet_id} esta inactivo", code="BUFFET_INACTIVE"
        )
