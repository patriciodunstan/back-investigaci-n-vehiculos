"""
Helpers para tests.

Funciones auxiliares para facilitar la escritura de tests.
"""

from typing import Dict, Any
from datetime import datetime, date


def create_user_data(
    email: str = "test@example.com",
    nombre: str = "Test User",
    password: str = "password123",
    rol: str = "cliente",
    buffet_id: int = None,
) -> Dict[str, Any]:
    """
    Crea datos de usuario para tests.

    Args:
        email: Email del usuario
        nombre: Nombre del usuario
        password: Contraseña
        rol: Rol del usuario
        buffet_id: ID del buffet (opcional)

    Returns:
        Diccionario con datos del usuario
    """
    data = {
        "email": email,
        "nombre": nombre,
        "password": password,
        "rol": rol,
    }
    if buffet_id:
        data["buffet_id"] = buffet_id
    return data


def create_buffet_data(
    nombre: str = "Buffet Test",
    rut: str = "12345678-5",
    email_principal: str = "buffet@test.com",
    telefono: str = "+56912345678",
    contacto_nombre: str = "Contacto Test",
) -> Dict[str, Any]:
    """
    Crea datos de buffet para tests.

    Args:
        nombre: Nombre del buffet
        rut: RUT del buffet
        email_principal: Email principal
        telefono: Teléfono
        contacto_nombre: Nombre del contacto

    Returns:
        Diccionario con datos del buffet
    """
    return {
        "nombre": nombre,
        "rut": rut,
        "email_principal": email_principal,
        "telefono": telefono,
        "contacto_nombre": contacto_nombre,
    }


def create_oficio_data(
    numero_oficio: str = "OF-2026-001",
    buffet_id: int = 1,
    patente: str = "ABCD12",
    marca: str = "Toyota",
    modelo: str = "Corolla",
    color: str = "Blanco",
    prioridad: str = "media",
) -> Dict[str, Any]:
    """
    Crea datos de oficio para tests.

    Args:
        numero_oficio: Número del oficio
        buffet_id: ID del buffet
        patente: Patente del vehículo
        marca: Marca del vehículo
        modelo: Modelo del vehículo
        color: Color del vehículo
        prioridad: Prioridad del oficio

    Returns:
        Diccionario con datos del oficio
    """
    return {
        "numero_oficio": numero_oficio,
        "buffet_id": buffet_id,
        "vehiculo": {
            "patente": patente,
            "marca": marca,
            "modelo": modelo,
            "color": color,
        },
        "prioridad": prioridad,
    }
