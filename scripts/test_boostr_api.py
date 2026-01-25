"""
Script de prueba para verificar la conexión con la API de Boostr.

Uso:
    python scripts/test_boostr_api.py [API_KEY] [RUT]

Asegúrate de tener configurada la variable de entorno BOOSTR_API_KEY
o pasarla directamente al script.
"""

import asyncio
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.shared.infrastructure.external_apis.boostr import (
    BoostrClient,
    BoostrAPIError,
    BoostrAuthenticationError,
)


async def test_boostr_connection():
    """Prueba la conexión con la API de Boostr."""

    print("=" * 60)
    print("Test de conexion con Boostr API (Rutificador)")
    print("=" * 60)

    client = BoostrClient()

    print(f"\nURL Base: {client.base_url}")
    print(f"API Key configurada: {'Si' if client.api_key else 'No'}")

    if not client.api_key:
        print("\nERROR: No hay API Key configurada.")
        print("   Configura la variable de entorno BOOSTR_API_KEY")
        return False

    print("\n" + "-" * 60)

    # RUT de prueba
    test_rut = "7.342.646-4"

    # Test 1: Vehículos por RUT
    print(f"\nTest 1: Vehiculos asociados a RUT {test_rut}")
    try:
        vehicles = await client.get_person_vehicles(test_rut)
        if vehicles:
            print(f"   OK - Vehiculos encontrados: {len(vehicles)}")
            for v in vehicles[:3]:
                print(f"      - {v.patente}: {v.marca} {v.modelo} ({v.año})")
        else:
            print("   INFO - No se encontraron vehiculos")
        print("   Credito usado: 1")
    except BoostrAuthenticationError as e:
        print(f"   ERROR de autenticacion: {e}")
        return False
    except BoostrAPIError as e:
        print(f"   ERROR: {e}")

    print("\n" + "-" * 60)

    # Test 2: Propiedades por RUT
    print(f"\nTest 2: Propiedades asociadas a RUT {test_rut}")
    try:
        properties = await client.get_person_properties(test_rut)
        if properties:
            print(f"   OK - Propiedades encontradas: {len(properties)}")
            for p in properties[:3]:
                print(f"      - {p.direccion}, {p.comuna}")
        else:
            print("   INFO - No se encontraron propiedades")
        print("   Credito usado: 1")
    except BoostrAPIError as e:
        print(f"   ERROR: {e}")

    print("\n" + "-" * 60)

    # Test 3: Verificar defunción
    print(f"\nTest 3: Verificar defuncion para RUT {test_rut}")
    try:
        deceased = await client.check_deceased(test_rut)
        print(f"   OK - Fallecido: {'Si' if deceased.fallecido else 'No'}")
        if deceased.fecha_defuncion:
            print(f"   Fecha: {deceased.fecha_defuncion}")
        print("   Credito usado: 1")
    except BoostrAPIError as e:
        print(f"   ERROR: {e}")

    # Resumen
    print("\n" + "=" * 60)
    print("Test de conexion completado")
    print("=" * 60)
    print("\nRecuerda:")
    print("   - Rate limit: 5 requests cada 10 segundos")
    print("   - El cliente maneja automaticamente el rate limiting")
    print("\n")

    return True


async def test_rut_investigation(rut: str):
    """
    Prueba una investigación completa por RUT.

    Args:
        rut: RUT de la persona a investigar
    """
    print(f"\nInvestigando RUT: {rut}")
    print("-" * 40)

    client = BoostrClient()

    # Vehículos
    print("\nVehiculos:")
    try:
        vehicles = await client.get_person_vehicles(rut)
        if vehicles:
            for v in vehicles:
                print(f"   - {v.patente}: {v.marca} {v.modelo} ({v.año})")
        else:
            print("   No se encontraron vehiculos")
    except BoostrAPIError as e:
        print(f"   Error: {e}")

    # Propiedades
    print("\nPropiedades:")
    try:
        properties = await client.get_person_properties(rut)
        if properties:
            for p in properties:
                print(f"   - {p.direccion}, {p.comuna} (Avaluo: {p.avaluo})")
        else:
            print("   No se encontraron propiedades")
    except BoostrAPIError as e:
        print(f"   Error: {e}")

    # Defunción
    print("\nEstado de defuncion:")
    try:
        deceased = await client.check_deceased(rut)
        if deceased.fallecido:
            print(f"   FALLECIDO - Fecha: {deceased.fecha_defuncion}")
        else:
            print("   No registra defuncion")
    except BoostrAPIError as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("     BOOSTR API - Script de Prueba (Rutificador)")
    print("=" * 60 + "\n")

    # Verificar si hay API key en argumentos
    if len(sys.argv) > 1:
        os.environ["BOOSTR_API_KEY"] = sys.argv[1]
        print("API Key recibida como argumento\n")

    # Ejecutar tests
    asyncio.run(test_boostr_connection())

    # Si se proporciona un RUT como segundo argumento, investigarlo
    if len(sys.argv) > 2:
        rut = sys.argv[2]
        asyncio.run(test_rut_investigation(rut))
