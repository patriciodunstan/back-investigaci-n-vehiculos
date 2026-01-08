"""
Script de prueba para verificar la conexión con la API de Boostr.

Uso:
    python scripts/test_boostr_api.py

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
    BoostrNotFoundError,
)


async def test_boostr_connection():
    """Prueba la conexión con la API de Boostr."""
    
    print("=" * 60)
    print("🚀 Test de conexión con Boostr API")
    print("=" * 60)
    
    # Crear cliente (usará las variables de entorno)
    client = BoostrClient()
    
    print(f"\n📡 URL Base: {client.base_url}")
    print(f"🔑 API Key configurada: {'Sí' if client.api_key else 'No'}")
    
    if not client.api_key:
        print("\n❌ ERROR: No hay API Key configurada.")
        print("   Configura la variable de entorno BOOSTR_API_KEY")
        return False
    
    print("\n" + "-" * 60)
    
    # Test 1: Consultar un RUT de prueba (nombre)
    print("\n📋 Test 1: Obtener nombre por RUT (16.163.631-2)")
    try:
        person = await client.get_person_name("16.163.631-2")
        print(f"   ✅ Nombre: {person.nombre}")
        print(f"   ✅ Crédito usado: 1")
    except BoostrNotFoundError:
        print("   ⚠️ RUT no encontrado (esto puede ser normal)")
    except BoostrAuthenticationError as e:
        print(f"   ❌ Error de autenticación: {e}")
        return False
    except BoostrAPIError as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "-" * 60)
    
    # Test 2: Consultar información completa de persona
    print("\n👤 Test 2: Información completa de persona")
    try:
        person_info = await client.get_person_info("16.163.631-2")
        print(f"   ✅ Nombre completo: {person_info.nombre}")
        if person_info.genero:
            print(f"   ✅ Género: {person_info.genero}")
        if person_info.nacionalidad:
            print(f"   ✅ Nacionalidad: {person_info.nacionalidad}")
        print(f"   ✅ Crédito usado: 1")
    except BoostrNotFoundError:
        print("   ⚠️ Persona no encontrada")
    except BoostrAPIError as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "-" * 60)
    
    # Test 3: Consultar vehículos de una persona
    print("\n🚗 Test 3: Vehículos asociados a un RUT")
    try:
        vehicles = await client.get_person_vehicles("7.342.646-4")
        if vehicles:
            print(f"   ✅ Vehículos encontrados: {len(vehicles)}")
            for v in vehicles[:3]:  # Mostrar máximo 3
                print(f"      - {v.patente}: {v.marca} {v.modelo} ({v.año})")
        else:
            print("   ⚠️ No se encontraron vehículos")
        print(f"   ✅ Crédito usado: 1")
    except BoostrAPIError as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "-" * 60)
    
    # Resumen
    print("\n" + "=" * 60)
    print("✅ Test de conexión completado")
    print("=" * 60)
    print("\n💡 Recuerda:")
    print("   - Rate limit: 5 requests cada 10 segundos")
    print("   - El cliente maneja automáticamente el rate limiting")
    print("   - Los créditos no expiran")
    print("\n")
    
    return True


async def test_vehicle_investigation(patente: str):
    """
    Prueba una investigación completa de vehículo.
    
    Args:
        patente: Patente del vehículo a investigar
    """
    print(f"\n🔍 Investigando vehículo: {patente}")
    print("-" * 40)
    
    client = BoostrClient()
    
    try:
        result = await client.investigar_vehiculo(patente)
        
        if result.vehiculo:
            v = result.vehiculo
            print(f"\n🚗 Vehículo encontrado:")
            print(f"   Patente: {v.patente}")
            print(f"   Marca: {v.marca}")
            print(f"   Modelo: {v.modelo}")
            print(f"   Año: {v.año}")
            if v.color:
                print(f"   Color: {v.color}")
            if v.vin:
                print(f"   VIN: {v.vin}")
        
        if result.multas:
            print(f"\n⚠️ Multas encontradas: {len(result.multas)}")
            for multa in result.multas[:3]:
                print(f"   - {multa.juzgado} ({multa.comuna})")
        
        if result.revision_tecnica:
            rt = result.revision_tecnica
            print(f"\n📋 Revisión Técnica:")
            print(f"   Estado: {rt.estado}")
            print(f"   Vencimiento: {rt.fecha_vencimiento}")
        
        if result.soap:
            print(f"\n🛡️ SOAP:")
            print(f"   Vigente: {'Sí' if result.soap.vigente else 'No'}")
        
        print(f"\n💰 Créditos usados: {result.creditos_usados}")
        
    except BoostrNotFoundError:
        print(f"   ❌ Vehículo no encontrado")
    except BoostrAPIError as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("     BOOSTR API - Script de Prueba")
    print("=" * 60 + "\n")
    
    # Verificar si hay API key en argumentos
    if len(sys.argv) > 1:
        os.environ["BOOSTR_API_KEY"] = sys.argv[1]
        print(f"✅ API Key recibida como argumento\n")
    
    # Ejecutar tests
    asyncio.run(test_boostr_connection())
    
    # Si se proporciona una patente como segundo argumento, investigarla
    if len(sys.argv) > 2:
        patente = sys.argv[2]
        asyncio.run(test_vehicle_investigation(patente))
