"""
Value Object: Patente Vehicular

Representa una patente de vehículo chilena.

Formatos válidos:
- Antiguo: 2 letras + 4 números (ej: AB1234)
- Nuevo simple: 4 letras + 2 números (ej: ABCD12)
- Nuevo extendido: 4 letras + 2 números + 1 número/letra (ej: BPHR409, LGCR751)
- Formato mixto: 2-3 letras + 3-4 números + letra/número (ej: VYL087K, RXX0423)
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Patente:
    """
    Value Object para patentes de vehículos chilenos.

    Attributes:
        valor: Patente normalizada (uppercase, sin espacios ni guiones ni puntos)
        formato: "antiguo", "nuevo", "nuevo_extendido" o "mixto"

    Example:
        >>> patente = Patente.crear("BPHR.40-9")
        >>> print(patente.valor)  # "BPHR409"
        >>> print(patente.formato)  # "nuevo_extendido"
    """

    valor: str
    formato: str

    # Formato antiguo: 2 letras + 4 números (AB1234)
    _PATRON_ANTIGUO = re.compile(r"^[A-Z]{2}\d{4}$")
    # Formato nuevo simple: 4 letras + 2 números (ABCD12)
    _PATRON_NUEVO = re.compile(r"^[A-Z]{4}\d{2}$")
    # Formato nuevo extendido: 4 letras + 2-3 números + 1 número/letra opcional (BPHR409, LGCR751)
    _PATRON_NUEVO_EXTENDIDO = re.compile(r"^[A-Z]{4}\d{2,3}[A-Z0-9]?$")
    # Formato mixto: 2-3 letras + 3-4 números + letra/número (VYL087K, RXX0423, JZRH618)
    _PATRON_MIXTO = re.compile(r"^[A-Z]{2,4}\d{3,4}[A-Z0-9]?$")

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

        # Limpiar: remover espacios, guiones, puntos
        patente_limpia = re.sub(r"[\s\-\.]", "", patente_string.strip().upper())

        # Detectar formato
        if cls._PATRON_ANTIGUO.match(patente_limpia):
            formato = "antiguo"
        elif cls._PATRON_NUEVO.match(patente_limpia):
            formato = "nuevo"
        elif cls._PATRON_NUEVO_EXTENDIDO.match(patente_limpia):
            formato = "nuevo_extendido"
        elif cls._PATRON_MIXTO.match(patente_limpia):
            formato = "mixto"
        else:
            raise ValueError(
                f"Formato de patente inválido: {patente_string}. "
                "Formatos válidos: AB1234, ABCD12, BPHR409, VYL087K"
            )

        return cls(valor=patente_limpia, formato=formato)

    def __str__(self) -> str:
        return self.valor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Patente):
            return False
        return self.valor == other.valor
