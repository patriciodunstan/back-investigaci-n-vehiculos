"""
Excepciones especificas del modulo Oficios.
"""

from src.shared.domain.exceptions import (
    DomainException,
    EntityNotFoundException,
    DuplicateEntityException,
)


class OficioNotFoundException(EntityNotFoundException):
    """Oficio no encontrado."""

    def __init__(self, identifier: int | str):
        if isinstance(identifier, int):
            super().__init__("Oficio", identifier)
        else:
            self.message = f"Oficio con numero '{identifier}' no encontrado"
            self.code = "OFICIO_NOT_FOUND"
            Exception.__init__(self, self.message)


class NumeroOficioAlreadyExistsException(DuplicateEntityException):
    """Numero de oficio ya registrado."""

    def __init__(self, numero_oficio: str):
        super().__init__("Oficio", "numero_oficio", numero_oficio)


class OficioYaFinalizadoException(DomainException):
    """Oficio ya esta finalizado."""

    def __init__(self, oficio_id: int):
        super().__init__(
            message=f"El oficio con ID {oficio_id} ya esta finalizado", code="OFICIO_FINALIZADO"
        )


class VehiculoNotFoundException(EntityNotFoundException):
    """Vehiculo no encontrado."""

    def __init__(self, identifier: int):
        super().__init__("Vehiculo", identifier)


class PropietarioNotFoundException(EntityNotFoundException):
    """Propietario no encontrado."""

    def __init__(self, identifier: int):
        super().__init__("Propietario", identifier)


class DireccionNotFoundException(EntityNotFoundException):
    """Direccion no encontrada."""

    def __init__(self, identifier: int):
        super().__init__("Direccion", identifier)
