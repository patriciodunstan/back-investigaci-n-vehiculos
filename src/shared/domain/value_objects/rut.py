"""
Value Object: RUT Chileno

Representa un RUT (Rol Único Tributario) chileno con validación del dígito verificador.

Principios aplicados:
- Inmutabilidad: Una vez creado, no puede modificarse
- Validación en construcción: Si el RUT es inválido, falla al crear
- Encapsulamiento: La lógica de validación está contenida en la clase
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class RutChileno:
    """
    Value Object para RUT chileno.

    Attributes:
        valor: RUT completo con formato (ej: "12.345.678-9")
        numero: Parte numérica sin puntos (ej: 12345678)
        digito_verificador: Dígito verificador (ej: "9" o "K")

    Example:
        >>> rut = RutChileno.crear("12345678-9")
        >>> print(rut.valor)  # "12.345.678-9"
        >>> print(rut.numero)  # 12345678
    """

    valor: str
    numero: int
    digito_verificador: str

    @classmethod
    def crear(cls, rut_string: str) -> "RutChileno":
        """
        Factory method para crear un RUT validado.

        Args:
            rut_string: RUT en cualquier formato ("12345678-9", "12.345.678-9", etc.)

        Returns:
            RutChileno: Instancia validada

        Raises:
            ValueError: Si el RUT es inválido

        Example:
            >>> rut = RutChileno.crear("12345678-9")
        """
        rut_limpio = cls._limpiar(rut_string)

        if not rut_limpio:
            raise ValueError("Rut no puede estar vacío")

        numero_str = rut_limpio[:-1]
        digito = rut_limpio[-1].upper()

        if not numero_str.isdigit():
            raise ValueError(f"RUT inválido: {rut_string}")

        numero = int(numero_str)

        digito_calculado = cls._calcular_digito_verificador(numero)
        if digito != digito_calculado:
            raise ValueError(
                f"Dígito verificador inválido para RUT {rut_string}."
                f"Esperado: {digito_calculado}, Recibido: {digito}"
            )

        valor_formateado = cls._formatear(numero, digito)

        return cls(valor=valor_formateado, numero=numero, digito_verificador=digito)

    @staticmethod
    def _limpiar(rut: str) -> str:
        """Elimina puntos, guiones y espacios del RUT"""
        return re.sub(r"[.\-\s]", "", rut.strip())

    @staticmethod
    def _calcular_digito_verificador(numero: int) -> str:
        """
        Calcula el dígito verificador usando el algoritmo módulo 11.

        Args:
            numero: Parte numérica del RUT

        Returns:
            str: Dígito verificador ("0"-"9" o "K")
        """
        suma = 0
        multiplicador = 2

        for digito in reversed(str(numero)):
            suma += int(digito) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2

        resto = suma % 11
        resultado = 11 - resto

        if resultado == 11:
            return "0"
        elif resultado == 10:
            return "K"
        else:
            return str(resultado)

    @staticmethod
    def _formatear(numero: int, digito: str) -> str:
        """Formatea el RUT con puntos y guión (ej: 12.345.678-9)"""
        numero_str = str(numero)
        partes = []
        while numero_str:
            partes.append(numero_str[-3:])
            numero_str = numero_str[:-3]
        numero_formateado = ".".join(reversed(partes))
        return f"{numero_formateado}-{digito}"

    def sin_formato(self) -> str:
        """Retorna el RUT sin puntos ni guión (ej: 123456789)"""
        return f"{self.numero}{self.digito_verificador}"

    def __str__(self) -> str:
        return self.valor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RutChileno):
            return False
        return self.numero == other.numero


def es_rut_valido(rut_string: str) -> bool:
    """
    Verifica si un RUT es válido sin lanzar excepción.

    Args:
        rut_string: RUT a validar

    Returns:
        bool: True si el RUT es válido

    Example:
        >>> es_rut_valido("12345678-9")
        True
        >>> es_rut_valido("12345678-0")
        False
    """

    try:
        RutChileno.crear(rut_string)
        return True
    except ValueError:
        return False
