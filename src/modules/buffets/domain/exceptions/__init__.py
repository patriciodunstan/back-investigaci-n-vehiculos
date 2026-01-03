"""Excepciones del modulo Buffets"""

from .buffet_exceptions import (
    BuffetNotFoundException,
    RutAlreadyExistsException,
    BuffetInactiveException,
)

__all__ = [
    "BuffetNotFoundException",
    "RutAlreadyExistsException",
    "BuffetInactiveException",
]
