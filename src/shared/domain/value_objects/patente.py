"""
Value Object: Patente Vehicular

Representa una patente de vehículo chilena.

Formatos válidos:
- Antiguo: 2 letras + 4 números (ej: AB1234)
- Nuevo: 4 letras + 2 números (ej: ABCD12)
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Patente:
    """
    Value Object para patentes de vehículos chilenos.

    Attributes:
        valor: Patente normalizada (uppercase, sin espacios)
        formato: "antiguo" o "nuevo"

    Example:
        >>> patente = Patente.crear("abcd-12")
        >>> print(patente.valor)  # "ABCD12"
        >>> print(patente.formato)  # "nuevo"
    """

    valor: str
    formato: str

    _PATRON_ANTIGUO = re.compile(r"^[A-Z]{2}\d{4}$")
    _PATRON_NUEVO = re.compile(r"^[A-Z]{4}\d{2}$")

    @classmethod
    def crear(cls, patente_string: str) -> "Patente":
        """
        Factory method para crear una Patente validada.

        Args:
            patente_string: Patente en cualquier formato

        Returns:
            Patente: Instancia validada y normalizada

        Raises:
            ValueError: Si la patente es inválida
        """
        if not patente_string:
            raise ValueError("Patente no puede estar vacía")

        patente_limpia = re.sub(r"[\s\-]", "", patente_string.strip().upper())

        if cls._PATRON_NUEVO.match(patente_limpia):
            formato = "nuevo"
        elif cls._PATRON_ANTIGUO.match(patente_limpia):
            formato = "antiguo"
        else:
            raise ValueError(
                f"Formato de patente inválido: {patente_string}."
                "Formatos válidos: AB1234 (antiguo) o ABC12 (nuevo)"
            )

        return cls(valor=patente_limpia, formato=formato)

    def __str__(self) -> str:
        return self.valor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Patente):
            return False
        return self.valor == other.valor
