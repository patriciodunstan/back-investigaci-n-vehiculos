"""
Script para cargar datos de vehículos desde CSV/Excel.

Carga los oficios, vehículos, propietarios y direcciones desde el archivo proporcionado.
"""

import sys
import csv
import re
from datetime import datetime, date

sys.path.insert(0, ".")

# Importar registry para que SQLAlchemy detecte todos los modelos
from src.shared.infrastructure.database.models_registry import *  # noqa: F401, F403
from src.shared.infrastructure.database import SessionLocal
from src.modules.buffets.infrastructure.models import BuffetModel
from src.modules.oficios.infrastructure.models import (
    OficioModel,
    VehiculoModel,
    PropietarioModel,
    DireccionModel,
)
from src.shared.domain.enums import (
    EstadoOficioEnum,
    PrioridadEnum,
    TipoPropietarioEnum,
    TipoDireccionEnum,
    ResultadoVerificacionEnum,
)


def limpiar_patente(patente: str) -> str:
    """Limpia y normaliza la patente."""
    if not patente:
        return ""
    # Eliminar puntos, guiones y espacios
    patente = re.sub(r'[.\-\s]', '', patente.strip().upper())
    return patente


def limpiar_año(año: str) -> int | None:
    """Extrae el año del campo."""
    if not año:
        return None
    try:
        # Eliminar saltos de línea y espacios
        año = año.strip().replace('\n', '')
        return int(año)
    except ValueError:
        return None


def determinar_estado(observaciones: str) -> EstadoOficioEnum:
    """Determina el estado del oficio basado en observaciones."""
    if not observaciones:
        return EstadoOficioEnum.INVESTIGACION
    
    obs_lower = observaciones.lower()
    
    if "fuera de jurisdicción" in obs_lower or "fuera de juridicción" in obs_lower:
        return EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO
    elif "prófuga" in obs_lower or "profuga" in obs_lower:
        return EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO
    elif "no se logra establecer" in obs_lower:
        return EstadoOficioEnum.INVESTIGACION
    elif "en desarrollo" in obs_lower:
        return EstadoOficioEnum.INVESTIGACION
    elif "fuera de chile" in obs_lower:
        return EstadoOficioEnum.FINALIZADO_NO_ENCONTRADO
    elif "no encontrado" in obs_lower:
        return EstadoOficioEnum.INVESTIGACION
    else:
        return EstadoOficioEnum.INVESTIGACION


def seed_data():
    """Carga los datos del CSV."""
    print("=" * 60)
    print("CARGANDO DATOS DE VEHÍCULOS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Limpiar datos existentes
        print("\n[1/5] Limpiando datos existentes...")
        db.query(DireccionModel).delete()
        db.query(PropietarioModel).delete()
        db.query(VehiculoModel).delete()
        db.query(OficioModel).delete()
        db.commit()
        print("    ✓ Datos anteriores eliminados")
        
        # 2. Verificar que existe un buffet
        print("\n[2/5] Verificando buffet...")
        buffet = db.query(BuffetModel).first()
        if not buffet:
            print("    Creando buffet por defecto...")
            buffet = BuffetModel(
                nombre="Banco Security",
                rut="97.053.000-2",
                email_principal="contacto@security.cl",
                telefono="+56223501000",
                contacto_nombre="Departamento Legal",
                activo=True,
            )
            db.add(buffet)
            db.commit()
            db.refresh(buffet)
        print(f"    ✓ Buffet: {buffet.nombre} (ID: {buffet.id})")
        
        # 3. Leer CSV
        print("\n[3/5] Leyendo archivo CSV...")
        csv_path = "vehiculos_final.xlsx - Vehículos.csv"
        
        oficios_creados = {}
        vehiculos_count = 0
        propietarios_count = 0
        direcciones_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            print(f"    ✓ {len(rows)} registros encontrados")
            
            # 4. Procesar cada fila
            print("\n[4/5] Procesando registros...")
            
            for row in rows:
                causa_rol = row.get('Causa ROL', '').strip()
                if not causa_rol:
                    continue
                
                # Crear o recuperar oficio
                if causa_rol not in oficios_creados:
                    caratulado = row.get('Caratulado', '').strip()
                    observaciones = row.get('Observaciones', '').strip()
                    
                    oficio = OficioModel(
                        numero_oficio=causa_rol,
                        buffet_id=buffet.id,
                        estado=determinar_estado(observaciones),
                        prioridad=PrioridadEnum.MEDIA,
                        fecha_ingreso=date.today(),
                        notas_generales=f"Caratulado: {caratulado}\n\nObservaciones: {observaciones}" if observaciones else f"Caratulado: {caratulado}",
                    )
                    db.add(oficio)
                    db.flush()
                    oficios_creados[causa_rol] = oficio
                else:
                    oficio = oficios_creados[causa_rol]
                
                # Crear vehículo
                patente = limpiar_patente(row.get('Patente', ''))
                if patente:
                    # Verificar si ya existe este vehículo en el oficio
                    existe = db.query(VehiculoModel).filter(
                        VehiculoModel.oficio_id == oficio.id,
                        VehiculoModel.patente == patente
                    ).first()
                    
                    if not existe:
                        vehiculo = VehiculoModel(
                            oficio_id=oficio.id,
                            patente=patente,
                            marca=row.get('Marca', '').strip() or None,
                            modelo=row.get('Modelo', '').strip() or None,
                            año=limpiar_año(row.get('\nAño\n', '') or row.get('Año', '')),
                            color=row.get('Color', '').strip() or None,
                        )
                        db.add(vehiculo)
                        vehiculos_count += 1
                
                # Crear propietario
                propietario_nombre = row.get('Propietario', '').strip()
                if propietario_nombre:
                    # Verificar si ya existe este propietario en el oficio
                    existe = db.query(PropietarioModel).filter(
                        PropietarioModel.oficio_id == oficio.id,
                        PropietarioModel.nombre_completo == propietario_nombre
                    ).first()
                    
                    if not existe:
                        propietario = PropietarioModel(
                            oficio_id=oficio.id,
                            rut="S/I",  # Sin información de RUT en el CSV
                            nombre_completo=propietario_nombre,
                            tipo=TipoPropietarioEnum.PRINCIPAL,
                        )
                        db.add(propietario)
                        propietarios_count += 1
                
                # Crear direcciones
                domicilio_actualizado = row.get('Domicilio actualizado', '').strip()
                domicilio_decreto = row.get('Domicilio decreto', '').strip()
                
                if domicilio_actualizado and domicilio_actualizado.lower() not in ['fuera de jurisdicción', 'fuerta de jurisdicción']:
                    # Verificar si ya existe esta dirección
                    existe = db.query(DireccionModel).filter(
                        DireccionModel.oficio_id == oficio.id,
                        DireccionModel.direccion == domicilio_actualizado
                    ).first()
                    
                    if not existe:
                        direccion = DireccionModel(
                            oficio_id=oficio.id,
                            direccion=domicilio_actualizado,
                            tipo=TipoDireccionEnum.DOMICILIO,
                            resultado_verificacion=ResultadoVerificacionEnum.PENDIENTE,
                            notas="Domicilio actualizado",
                        )
                        db.add(direccion)
                        direcciones_count += 1
                
                if domicilio_decreto and domicilio_decreto != domicilio_actualizado:
                    existe = db.query(DireccionModel).filter(
                        DireccionModel.oficio_id == oficio.id,
                        DireccionModel.direccion == domicilio_decreto
                    ).first()
                    
                    if not existe:
                        direccion = DireccionModel(
                            oficio_id=oficio.id,
                            direccion=domicilio_decreto,
                            tipo=TipoDireccionEnum.DOMICILIO,
                            resultado_verificacion=ResultadoVerificacionEnum.PENDIENTE,
                            notas="Domicilio según decreto",
                        )
                        db.add(direccion)
                        direcciones_count += 1
            
            db.commit()
        
        # 5. Resumen
        print("\n[5/5] Resumen de carga:")
        print(f"    ✓ Oficios creados: {len(oficios_creados)}")
        print(f"    ✓ Vehículos creados: {vehiculos_count}")
        print(f"    ✓ Propietarios creados: {propietarios_count}")
        print(f"    ✓ Direcciones creadas: {direcciones_count}")
        
        print("\n" + "=" * 60)
        print("✅ DATOS CARGADOS EXITOSAMENTE")
        print("=" * 60)
        
        # Mostrar oficios creados
        print("\nOficios creados:")
        for i, (rol, oficio) in enumerate(oficios_creados.items(), 1):
            print(f"  {i}. {rol} - Estado: {oficio.estado.value}")
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: No se encontró el archivo CSV")
        print("   Asegúrate de que el archivo 'vehiculos_final.xlsx - Vehículos.csv' esté en la raíz del proyecto")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
