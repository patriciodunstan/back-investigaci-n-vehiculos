"""
Interface y implementación del Event Bus.

El Event Bus permite publicar y suscribirse a eventos de forma desacoplada.

Principios aplicados:
- DIP: Los módulos dependen de la interface, no de la implementación
- OCP: Nuevos handlers se agregan sin modificar código existente
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type
from .event import DomainEvent


class IEventBus(ABC):
    """
    Interface para el Event Bus.

    Define operaciones para publicar y suscribirse a eventos.
    """

    @abstractmethod
    async def public(self, event: DomainEvent) -> None:
        """
        Publica un evento para que los suscriptores lo procesen.

        Args:
            event: Evento a publicar
        """
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handles: callable) -> None:
        """
        Suscribe un handler a un tipo de evento.

        Args:
            event_type: Tipo de evento a escuchar
            handler: Función que procesa el evento
        """
        pass


class InMemoryEventBus(IEventBus):
    """
    Implementación en memoria del Event Bus.

    Útil para desarrollo y testing. En producción se puede reemplazar
    por RabbitMQ, Kafka, etc. sin cambiar el código de los módulos.

    Example:
        bus = InMemoryEventBus()

        # Suscribir handler
        @bus.subscribe(OficioCreado)
        async def handle_oficio_creado(event: OficioCreado):
            print(f"Nuevo oficio: {event.oficio_id}")

        # Publicar evento
        await bus.publish(OficioCreado(oficio_id=1, patente="ABCD12"))
    """

    def __init__(self):
        self._handlers: Dict[str, List[callable]] = {}

    async def public(self, event: DomainEvent) -> None:
        """Publica evento a todos los handlers suscritos"""
        event_type = event.event_type
        handlers = self._handlers.get(event_type, [])

        for handler in handlers:
            try:

                result = handler(event)
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:

                print(f"Error en handler para {event_type}: {e}")

    def subscribe(self, event_type: Type[DomainEvent], handler: callable) -> None:
        """Registra un handler para un tipo de evento"""
        event_name = event_type.__name__
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def subscribe_decorator(self, event_type: Type[DomainEvent]):
        """
        Decorador para suscribir handlers.

        Example:
            @event_bus.subscribe_decorator(OficioCreado)
            async def handle_oficio(event):
                pass
        """

        def decorator(handler: callable) -> callable:
            self.subscribe(event_type, handler)
            return handler

        return decorator


event_bus = InMemoryEventBus()
