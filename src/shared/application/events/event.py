"""
Clases base para eventos de dominio.

Los eventos permiten comunicación desacoplada entre módulos.

Principios aplicados:
- OCP: Nuevos eventos se crean heredando de DomainEvent
- Desacoplamiento: Módulos se comunican via eventos, no importaciones directas
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from abc import ABC, abstractmethod
from uuid import uuid4


@dataclass
class DomainEvent(ABC):
    """
    Clase base para todos los eventos de dominio.

    Attributes:
        event_id: ID único del evento
        occurred_at: Timestamp de cuando ocurrió

    Example:
        @dataclass
        class OficioCreado(DomainEvent):
            oficio_id: int

    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)

    @property
    def event_type(self) -> str:
        """Nombre del tipo de evento"""
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el evento a diccionario"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "data": {
                k: v
                for k, v in self.__dict__.items()
                if k not in ("event_id", "occurred_at")
            },
        }
