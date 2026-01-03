"""
Entidad de Dominio Investigacion.

Representa una actividad en el timeline de investigacion.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums import TipoActividadEnum, FuenteAvistamientoEnum


@dataclass
class Investigacion(BaseEntity):
    """
    Entidad que representa una actividad de investigacion.

    Attributes:
        oficio_id: ID del oficio relacionado
        investigador_id: ID del investigador que realizo la actividad
        tipo_actividad: Tipo de actividad
        descripcion: Descripcion de la actividad
        resultado: Resultado obtenido
        api_externa: Nombre de la API externa si aplica
        datos_json: Datos adicionales en JSON
        fecha_actividad: Fecha y hora de la actividad
    """

    oficio_id: int = 0
    investigador_id: Optional[int] = None
    tipo_actividad: TipoActividadEnum = TipoActividadEnum.NOTA_INVESTIGADOR
    descripcion: str = ""
    resultado: Optional[str] = None
    api_externa: Optional[str] = None
    datos_json: Optional[str] = None
    fecha_actividad: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def crear_nota(
        cls,
        oficio_id: int,
        investigador_id: int,
        descripcion: str,
        resultado: Optional[str] = None,
    ) -> "Investigacion":
        """Crea una nota de investigador."""
        return cls(
            oficio_id=oficio_id,
            investigador_id=investigador_id,
            tipo_actividad=TipoActividadEnum.NOTA_INVESTIGADOR,
            descripcion=descripcion,
            resultado=resultado,
        )

    @classmethod
    def crear_consulta_api(
        cls,
        oficio_id: int,
        investigador_id: int,
        api_externa: str,
        descripcion: str,
        resultado: str,
        datos_json: Optional[str] = None,
    ) -> "Investigacion":
        """Crea una consulta a API externa."""
        return cls(
            oficio_id=oficio_id,
            investigador_id=investigador_id,
            tipo_actividad=TipoActividadEnum.CONSULTA_API,
            descripcion=descripcion,
            resultado=resultado,
            api_externa=api_externa,
            datos_json=datos_json,
        )


@dataclass
class Avistamiento(BaseEntity):
    """
    Entidad que representa un avistamiento del vehiculo.

    Attributes:
        oficio_id: ID del oficio relacionado
        fuente: Fuente del avistamiento (boostr, multas, terreno)
        fecha_hora: Fecha y hora del avistamiento
        ubicacion: Ubicacion textual
        latitud: Coordenada latitud
        longitud: Coordenada longitud
        api_response_id: ID de respuesta de API si aplica
        datos_json: Datos adicionales
        notas: Notas adicionales
    """

    oficio_id: int = 0
    fuente: FuenteAvistamientoEnum = FuenteAvistamientoEnum.TERRENO
    fecha_hora: datetime = field(default_factory=datetime.utcnow)
    ubicacion: str = ""
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    api_response_id: Optional[str] = None
    datos_json: Optional[str] = None
    notas: Optional[str] = None

    @classmethod
    def crear(
        cls,
        oficio_id: int,
        fuente: FuenteAvistamientoEnum,
        ubicacion: str,
        fecha_hora: Optional[datetime] = None,
        latitud: Optional[float] = None,
        longitud: Optional[float] = None,
        notas: Optional[str] = None,
    ) -> "Avistamiento":
        """Crea un nuevo avistamiento."""
        return cls(
            oficio_id=oficio_id,
            fuente=fuente,
            fecha_hora=fecha_hora or datetime.utcnow(),
            ubicacion=ubicacion,
            latitud=latitud,
            longitud=longitud,
            notas=notas,
        )
