"""
Value Objects compartidos del dominio.

Estos objetos son inmutables y se definen por su valor, no por su identidad.
"""

from .rut import RutChileno, es_rut_valido
from .email import Email
from .patente import Patente

__all__ = [
    "RutChileno",
    "es_rut_valido",
    "Email",
    "Patente",
]
