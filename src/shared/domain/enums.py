"""
Enums compartidos del dominio.

Define los valores válidos para campos de tipo enum en toda la aplicación.

Principios aplicados:
- DRY: Enums definidos una sola vez y usados en dominio e infraestructura
- Type Safety: Valores restringidos a opciones válidas
"""

from enum import Enum


class RolEnum(str, Enum):
    """
    Roles de usuario en el sistema.

    - ADMIN: Acceso completo al sistema
    - INVESTIGADOR: Puede gestionar oficios e investigaciones
    - CLIENTE: Solo puede ver oficios de su buffet (lectura)
    """

    ADMIN = "admin"
    INVESTIGADOR = "investigador"
    CLIENTE = "cliente"


class EstadoOficioEnum(str, Enum):
    """
    Estados posibles de un oficio.

    Flujo: PENDIENTE -> INVESTIGACION -> NOTIFICACION -> FINALIZADO_*
    """

    PENDIENTE = "pendiente"  # Recién ingresado
    INVESTIGACION = "investigacion"  # En proceso de investigación
    NOTIFICACION = "notificacion"  # Esperando notificación al receptor
    FINALIZADO_ENCONTRADO = "finalizado_encontrado"  # Vehículo encontrado
    FINALIZADO_NO_ENCONTRADO = "finalizado_no_encontrado"  # No se encontró


class PrioridadEnum(str, Enum):
    """
    Niveles de prioridad para oficios.
    """

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class TipoPropietarioEnum(str, Enum):
    """
    Tipos de propietario/relacionado con el vehículo.
    """

    PRINCIPAL = "principal"  # Propietario principal
    CODEUDOR = "codeudor"  # Codeudor solidario
    AVAL = "aval"  # Aval
    USUARIO = "usuario"  # Familiar que usa el vehículo


class TipoDireccionEnum(str, Enum):
    """
    Tipos de dirección.
    """

    DOMICILIO = "domicilio"  # Casa del propietario
    TRABAJO = "trabajo"  # Lugar de trabajo
    FAMILIAR = "familiar"  # Casa de familiar
    OTRO = "otro"  # Otra dirección


class TipoActividadEnum(str, Enum):
    """
    Tipos de actividad en la investigación (timeline).
    """

    CONSULTA_API = "consulta_api"  # Consulta a API externa
    NOTA = "nota"  # Nota del investigador
    LLAMADA = "llamada"  # Llamada telefónica
    TERRENO = "terreno"  # Visita en terreno


class FuenteAvistamientoEnum(str, Enum):
    """
    Fuentes de avistamientos del vehículo.
    """

    PORTICO = "portico"  # API de pórticos (Boostr, etc.)
    MULTA = "multa"  # API de multas de tránsito
    TERRENO = "terreno"  # Registrado manualmente en terreno


class TipoAdjuntoEnum(str, Enum):
    """
    Tipos de archivos adjuntos.
    """

    FOTO_VEHICULO = "foto_vehiculo"  # Foto del vehículo
    DOCUMENTO = "documento"  # PDF, Word, etc.
    EVIDENCIA = "evidencia"  # Otra evidencia


class TipoNotificacionEnum(str, Enum):
    """
    Tipos de notificación.
    """

    RECEPTOR_JUDICIAL = "receptor_judicial"  # Email a receptor judicial
    BUFFET = "buffet"  # Email a buffet cliente
    INTERNA = "interna"  # Notificación interna del sistema
