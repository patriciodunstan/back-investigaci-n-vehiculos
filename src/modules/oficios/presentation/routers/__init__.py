"""Routers del modulo Oficios"""

from .oficio_router import router as oficio_router
from .document_upload_router import router as document_upload_router
from .drive_webhook_router import router as drive_webhook_router

__all__ = ["oficio_router", "document_upload_router", "drive_webhook_router"]
