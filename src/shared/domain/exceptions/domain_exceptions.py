"""
Excepciones de dominio.

Define excepciones específicas del negocio que son independientes
de la infraestructura (HTTP, DB, etc.)

Principios aplicados:
- SRP: Cada excepción representa un error específico
- Separación de capas: Excepciones de dominio != excepciones HTTP
"""


class DomainException(Exception):
    """
    Excepción base para errores de dominio.

    Attributes:
        message: Mensaje descriptivo del error
        code: Código de error para identificación
    """

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """
    Se lanza cuando no se encuentra una entidad.

    Example:
        >>> raise EntityNotFoundException("Buffet", 123)
        EntityNotFoundException: Buffet con ID 123 no encontrado
    """

    def __init__(self, entity_name: str, entity_id: int):
        super().__init__(
            message=f"{entity_name} con ID {entity_id} no encontrado",
            code="ENTITY_NOT_FOUND",
        )
        self.entity_name = entity_name
        self.entity_id = entity_id


class DuplicateEntityException(DomainException):
    """
    Se lanza cuando se intenta crear una entidad duplicada.

    Example:
        >>> raise DuplicateEntityException("Usuario", "email", "test@test.com")
    """

    def __init__(self, entity_name: str, field: str, value: str):
        super().__init__(
            message=f"Ya existe un {entity_name} con {field}: {value}",
            code="DUPLICATE_ENTITY",
        )
        self.entity_name = entity_name
        self.field = field
        self.value = value


class ValidationException(DomainException):
    """
    Se lanza cuando hay errores de validación de negocio.

    Example:
        >>> raise ValidationException("El RUT no es válido")
    """

    def __init__(self, message: str, field: str = None):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class BusinessRuleException(DomainException):
    """
    Se lanza cuando se viola una regla de negocio.

    Example:
        >>> raise BusinessRuleException("No se puede eliminar un buffet con oficios activos")
    """

    def __init__(self, message: str):
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION")


class UnauthorizedException(DomainException):
    """
    Se lanza cuando el usuario no tiene permisos.

    Example:
        >>> raise UnauthorizedException("No tiene permisos para ver este oficio")
    """

    def __init__(self, message: str = "No autorizado"):
        super().__init__(message=message, code="UNAUTHORIZED")
