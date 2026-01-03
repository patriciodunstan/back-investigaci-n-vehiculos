"""
Value Object: Email

Representa una dirección de email validada.

Principios aplicados:
- Inmutabilidad
- Validación en construcción
- Normalización automática (lowercase)
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """
    Value Object para direcciones de email.

    Attributes:
        valor: Email normalizado (lowercase)
        usuario: Parte antes del @
        dominio: Parte después del @

    Example:
        >>> email = Email.crear("Usuario@Example.COM")
        >>> print(email.valor)  # "usuario@example.com"
    """

    valor: str
    usuario: str
    dominio: str

    _PATRON_EMAIL = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @classmethod
    def crear(cls, email_string: str) -> "Email":
        """
        Factory method para crear un Email validado.

        Args:
            email_string: Dirección de email

        Returns:
            Email: Instancia validada y normalizada

        Raises:
            ValueError: Si el email es inválido
        """
        if not email_string:
            raise ValueError("Email no puede estar vacío")

        email_limpio = email_string.strip().lower()

        if not cls._PATRON_EMAIL.match(email_limpio):
            raise ValueError(f"Formato de email inválido: {email_string}")

        usuario, dominio = email_limpio.split("@")

        return cls(valor=email_limpio, usuario=usuario, dominio=dominio)

    def __str__(self) -> str:
        return self.valor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.valor == other.valor
