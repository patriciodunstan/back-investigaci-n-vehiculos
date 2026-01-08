"""
Registry de Modelos SQLAlchemy.

Este archivo importa TODOS los modelos para que:
1. Alembic pueda detectarlos automáticamente
2. Las relaciones entre modelos funcionen correctamente

IMPORTANTE: Importar este archivo en env.py de Alembic

Principios aplicados:
- DRY: Un solo lugar para registrar modelos
- Explícito: Listado claro de todos los modelos
"""

# Base debe importarse primero
from src.shared.infrastructure.database.base import Base  # noqa: F401

# Modelos del módulo Buffets
from src.modules.buffets.infrastructure.models.buffet_model import (
    BuffetModel,
)  # noqa: F401

# Modelos del módulo Usuarios
from src.modules.usuarios.infrastructure.models.usuario_model import (
    UsuarioModel,
)  # noqa: F401

# Modelos del módulo Oficios
from src.modules.oficios.infrastructure.models.oficio_model import (
    OficioModel,
)  # noqa: F401
from src.modules.oficios.infrastructure.models.vehiculo_model import (
    VehiculoModel,
)  # noqa: F401
from src.modules.oficios.infrastructure.models.propietario_model import (
    PropietarioModel,
)  # noqa: F401
from src.modules.oficios.infrastructure.models.direccion_model import (
    DireccionModel,
    VisitaDireccionModel,
)  # noqa: F401
from src.modules.oficios.infrastructure.models.adjunto_model import (
    AdjuntoModel,
)  # noqa: F401

# Modelos del módulo Investigaciones
from src.modules.investigaciones.infrastructure.models.investigacion_model import (
    InvestigacionModel,
)  # noqa: F401
from src.modules.investigaciones.infrastructure.models.avistamiento_model import (
    AvistamientoModel,
)  # noqa: F401

# Modelos del módulo Notificaciones
from src.modules.notificaciones.infrastructure.models.notificacion_model import (
    NotificacionModel,
)  # noqa: F401


# Lista de todos los modelos (útil para introspección)
ALL_MODELS = [
    BuffetModel,
    UsuarioModel,
    OficioModel,
    VehiculoModel,
    PropietarioModel,
    DireccionModel,
    AdjuntoModel,
    InvestigacionModel,
    AvistamientoModel,
    NotificacionModel,
]

__all__ = [
    "Base",
    "BuffetModel",
    "UsuarioModel",
    "OficioModel",
    "VehiculoModel",
    "PropietarioModel",
    "DireccionModel",
    "AdjuntoModel",
    "InvestigacionModel",
    "AvistamientoModel",
    "NotificacionModel",
    "ALL_MODELS",
]
