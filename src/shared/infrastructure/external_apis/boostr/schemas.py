"""
Esquemas de datos para respuestas de la API de Boostr.

Define modelos Pydantic para parsear y validar las respuestas
de los diferentes endpoints de Boostr.
"""

from typing import Optional, List, Any, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field


# =============================================================================
# RESPUESTA BASE
# =============================================================================

class BoostrResponse(BaseModel):
    """
    Respuesta genérica de la API de Boostr.
    
    Attributes:
        status: "success" o "error"
        data: Datos de la respuesta (puede ser dict, list o None)
        code: Código de error (solo en caso de error)
        message: Mensaje de error (solo en caso de error)
    """
    status: str
    data: Optional[Any] = None
    code: Optional[str] = None
    message: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.status == "success"
    
    @property
    def is_error(self) -> bool:
        return self.status == "error"


# =============================================================================
# VEHÍCULOS
# =============================================================================

class VehicleInfo(BaseModel):
    """
    Información básica de un vehículo por patente.
    
    Endpoint: GET /vehicle/{patente}.json
    """
    patente: str = Field(..., alias="plate", description="Patente del vehículo")
    marca: Optional[str] = Field(None, alias="brand", description="Marca del vehículo")
    modelo: Optional[str] = Field(None, alias="model", description="Modelo del vehículo")
    año: Optional[int] = Field(None, alias="year", description="Año del vehículo")
    tipo: Optional[str] = Field(None, alias="type", description="Tipo de vehículo")
    
    class Config:
        populate_by_name = True


class VehicleExtendedInfo(VehicleInfo):
    """
    Información extendida de un vehículo (requiere API Key).
    
    Incluye datos adicionales como color, VIN, kilometraje, etc.
    """
    color: Optional[str] = Field(None, description="Color del vehículo")
    vin: Optional[str] = Field(None, alias="chassis", description="Número VIN/Chasis")
    combustible: Optional[str] = Field(None, alias="fuel", description="Tipo de combustible")
    kilometraje: Optional[int] = Field(None, alias="mileage", description="Último kilometraje registrado")
    fabricante: Optional[str] = Field(None, alias="manufacturer", description="Fabricante")
    pais_origen: Optional[str] = Field(None, alias="origin_country", description="País de origen")
    puertas: Optional[int] = Field(None, alias="doors", description="Cantidad de puertas")
    version: Optional[str] = Field(None, description="Versión del vehículo")
    motor: Optional[str] = Field(None, alias="engine", description="Tamaño del motor")
    transmision: Optional[str] = Field(None, alias="transmission", description="Tipo de transmisión")
    
    # Propietario (si está disponible)
    propietario_rut: Optional[str] = Field(None, alias="owner_rut")
    propietario_nombre: Optional[str] = Field(None, alias="owner_name")
    
    class Config:
        populate_by_name = True


class TrafficFine(BaseModel):
    """
    Información de una multa de tránsito.
    
    Endpoint: GET /vehicle/{patente}/multas.json
    """
    juzgado: Optional[str] = Field(None, alias="court", description="Juzgado de Policía Local")
    comuna: Optional[str] = Field(None, description="Comuna del juzgado")
    rol: Optional[str] = Field(None, description="Rol de la causa")
    año: Optional[int] = Field(None, alias="year", description="Año de la multa")
    fecha: Optional[str] = Field(None, alias="date", description="Fecha de la multa")
    estado: Optional[str] = Field(None, alias="status", description="Estado de la multa")
    monto: Optional[float] = Field(None, alias="amount", description="Monto de la multa")
    
    class Config:
        populate_by_name = True


class TechnicalReview(BaseModel):
    """
    Información de revisión técnica.
    
    Endpoint: GET /vehicle/{patente}/revision.json
    """
    estado: Optional[str] = Field(None, alias="status", description="Estado de la revisión")
    resultado: Optional[str] = Field(None, alias="result", description="Resultado (aprobada/rechazada)")
    fecha_revision: Optional[str] = Field(None, alias="review_date", description="Fecha de última revisión")
    fecha_vencimiento: Optional[str] = Field(None, alias="expiry_date", description="Fecha de vencimiento")
    mes_renovacion: Optional[str] = Field(None, alias="renewal_month", description="Mes de renovación")
    planta: Optional[str] = Field(None, alias="plant", description="Planta de revisión")
    
    class Config:
        populate_by_name = True


class SOAPInfo(BaseModel):
    """
    Información del Seguro Obligatorio (SOAP).
    
    Endpoint: GET /vehicle/{patente}/soap.json
    """
    vigente: bool = Field(False, alias="valid", description="Si el SOAP está vigente")
    compañia: Optional[str] = Field(None, alias="company", description="Compañía de seguros")
    poliza: Optional[str] = Field(None, alias="policy", description="Número de póliza")
    fecha_inicio: Optional[str] = Field(None, alias="start_date", description="Fecha de inicio")
    fecha_termino: Optional[str] = Field(None, alias="end_date", description="Fecha de término")
    
    class Config:
        populate_by_name = True


# =============================================================================
# RUTIFICADOR - PERSONAS
# =============================================================================

class PersonInfo(BaseModel):
    """
    Información de una persona por RUT.
    
    Endpoint: GET /rut/full/{rut}.json
    """
    rut: str = Field(..., description="RUT de la persona")
    nombre: Optional[str] = Field(None, alias="name", description="Nombre completo")
    nombres: Optional[str] = Field(None, alias="first_name", description="Nombres")
    apellido_paterno: Optional[str] = Field(None, alias="last_name", description="Apellido paterno")
    apellido_materno: Optional[str] = Field(None, alias="mother_last_name", description="Apellido materno")
    genero: Optional[str] = Field(None, alias="gender", description="Género")
    nacionalidad: Optional[str] = Field(None, alias="nationality", description="Nacionalidad")
    fecha_nacimiento: Optional[str] = Field(None, alias="birth_date", description="Fecha de nacimiento")
    edad: Optional[int] = Field(None, alias="age", description="Edad")
    fallecido: Optional[bool] = Field(None, alias="deceased", description="Si la persona ha fallecido")
    
    class Config:
        populate_by_name = True


class PersonName(BaseModel):
    """
    Nombre de una persona por RUT.
    
    Endpoint: GET /rut/name/{rut}.json
    """
    rut: str
    nombre: Optional[str] = Field(None, alias="name")
    nombres: Optional[str] = Field(None, alias="first_name")
    apellido_paterno: Optional[str] = Field(None, alias="last_name")
    apellido_materno: Optional[str] = Field(None, alias="mother_last_name")
    
    class Config:
        populate_by_name = True


class PersonVehicle(BaseModel):
    """
    Vehículo asociado a una persona.
    
    Endpoint: GET /rut/vehicles/{rut}.json
    """
    patente: str = Field(..., alias="plate", description="Patente del vehículo")
    marca: Optional[str] = Field(None, alias="brand", description="Marca")
    modelo: Optional[str] = Field(None, alias="model", description="Modelo")
    año: Optional[int] = Field(None, alias="year", description="Año")
    tipo: Optional[str] = Field(None, alias="type", description="Tipo de vehículo")
    
    class Config:
        populate_by_name = True


class PersonProperty(BaseModel):
    """
    Propiedad asociada a una persona.
    
    Endpoint: GET /rut/properties/{rut}.json
    """
    rol: Optional[str] = Field(None, description="Rol de la propiedad")
    comuna: Optional[str] = Field(None, description="Comuna")
    direccion: Optional[str] = Field(None, alias="address", description="Dirección")
    destino: Optional[str] = Field(None, description="Destino (habitacional, comercial, etc.)")
    avaluo: Optional[float] = Field(None, description="Avalúo fiscal")
    
    class Config:
        populate_by_name = True


# =============================================================================
# VERIFICACIONES ESPECIALES
# =============================================================================

class PEPInfo(BaseModel):
    """
    Información de Persona Políticamente Expuesta.
    
    Endpoint: GET /rut/pep/{rut}.json
    """
    es_pep: bool = Field(False, alias="is_pep", description="Si es PEP")
    cargo: Optional[str] = Field(None, alias="position", description="Cargo público")
    institucion: Optional[str] = Field(None, alias="institution", description="Institución")
    vigente: Optional[bool] = Field(None, alias="active", description="Si el cargo está vigente")
    
    class Config:
        populate_by_name = True


class InterpolInfo(BaseModel):
    """
    Información de búsqueda en Interpol.
    
    Endpoint: GET /rut/interpol/{rut}.json
    """
    tiene_alerta: bool = Field(False, alias="has_alert", description="Si tiene alerta Interpol")
    tipo_alerta: Optional[str] = Field(None, alias="alert_type", description="Tipo de alerta")
    
    class Config:
        populate_by_name = True


class DeceasedInfo(BaseModel):
    """
    Información de defunción.
    
    Endpoint: GET /rut/deceased/{rut}.json
    """
    fallecido: bool = Field(False, alias="deceased", description="Si ha fallecido")
    fecha_defuncion: Optional[str] = Field(None, alias="death_date", description="Fecha de defunción")
    
    class Config:
        populate_by_name = True


# =============================================================================
# RESPUESTAS AGREGADAS PARA EL PROYECTO
# =============================================================================

class InvestigacionBoostrResult(BaseModel):
    """
    Resultado consolidado de una consulta a Boostr para investigaciones.
    
    Agrupa toda la información relevante obtenida de múltiples endpoints.
    """
    # Datos del vehículo
    vehiculo: Optional[VehicleExtendedInfo] = None
    revision_tecnica: Optional[TechnicalReview] = None
    soap: Optional[SOAPInfo] = None
    multas: List[TrafficFine] = Field(default_factory=list)
    
    # Datos del propietario
    propietario: Optional[PersonInfo] = None
    otros_vehiculos: List[PersonVehicle] = Field(default_factory=list)
    propiedades: List[PersonProperty] = Field(default_factory=list)
    
    # Verificaciones
    pep: Optional[PEPInfo] = None
    interpol: Optional[InterpolInfo] = None
    defuncion: Optional[DeceasedInfo] = None
    
    # Metadata
    fecha_consulta: datetime = Field(default_factory=datetime.utcnow)
    fuente: str = "boostr"
    creditos_usados: int = 0
