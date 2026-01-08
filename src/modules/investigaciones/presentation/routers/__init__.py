"""Routers del modulo Investigaciones"""

from .investigacion_router import router as investigacion_router
from .boostr_router import router as boostr_router

__all__ = ["investigacion_router", "boostr_router"]
