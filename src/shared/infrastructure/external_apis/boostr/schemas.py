"""
Esquemas de datos para respuestas de la API de Boostr (Rutificador).

Define modelos Pydantic para parsear y validar las respuestas
de los endpoints disponibles:
- /rut/vehicles/{rut}.json
- /rut/properties/{rut}.json
- /rut/deceased/{rut}.json
"""

from typing import Optional
from pydantic import BaseModel, Field


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


class DeceasedInfo(BaseModel):
    """
    Información de defunción.

    Endpoint: GET /rut/deceased/{rut}.json
    """

    fallecido: bool = Field(False, alias="deceased", description="Si ha fallecido")
    fecha_defuncion: Optional[str] = Field(None, alias="death_date", description="Fecha de defunción")

    class Config:
        populate_by_name = True
