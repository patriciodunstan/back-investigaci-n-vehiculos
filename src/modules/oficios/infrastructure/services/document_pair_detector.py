"""
Detector de pares de documentos (Oficio + CAV).

Identifica si un documento nuevo tiene un par relacionado basándose
en múltiples estrategias de matching.

Principios aplicados:
- SRP: Solo identifica pares de documentos
- Strategy Pattern: Múltiples estrategias de matching
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.oficios.infrastructure.models.documento_procesado_model import (
    DocumentoProcesadoModel,
)
from src.shared.domain.enums import TipoDocumentoEnum, EstadoDocumentoProcesadoEnum
from src.core.config import get_settings


logger = logging.getLogger(__name__)


class DocumentPairDetector:
    """
    Detecta pares de documentos (Oficio + CAV) relacionados.

    Estrategias de matching:
    1. Por buffet_id y tipo complementario
    2. Por fecha (dentro de timeout)
    3. Por estado ESPERANDO_PAR
    4. Por contenido extraído (número de oficio, patente)

    Example:
        >>> detector = DocumentPairDetector(session)
        >>> par = await detector.find_pair(file_id, tipo_documento, buffet_id)
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el detector.

        Args:
            session: Sesión de SQLAlchemy para queries
        """
        self._session = session
        settings = get_settings()
        # Timeout en horas (default: 24 horas)
        self._timeout_hours = getattr(settings, "DOCUMENT_PAIR_TIMEOUT_HOURS", 24)

    async def find_pair(
        self,
        file_id: str,
        tipo_documento: TipoDocumentoEnum,
        buffet_id: Optional[int] = None,
        fecha_subida: Optional[datetime] = None,
    ) -> Optional[DocumentoProcesadoModel]:
        """
        Busca un documento par para el documento dado.

        Args:
            file_id: ID único del archivo (UUID)
            tipo_documento: Tipo del documento (OFICIO o CAV)
            buffet_id: ID del buffet (opcional, para filtrar por buffet)
            fecha_subida: Fecha en que se subió el documento (opcional)

        Returns:
            DocumentoProcesadoModel del par encontrado o None
        """
        # Determinar el tipo complementario
        tipo_complementario = (
            TipoDocumentoEnum.CAV
            if tipo_documento == TipoDocumentoEnum.OFICIO
            else TipoDocumentoEnum.OFICIO
        )

        # Construir query base
        conditions = [
            DocumentoProcesadoModel.file_id != file_id,
            DocumentoProcesadoModel.tipo_documento == tipo_complementario,
            or_(
                DocumentoProcesadoModel.estado == EstadoDocumentoProcesadoEnum.ESPERANDO_PAR,
                DocumentoProcesadoModel.estado == EstadoDocumentoProcesadoEnum.PENDIENTE,
            ),
        ]

        # Filtrar por buffet_id si está disponible
        if buffet_id is not None:
            conditions.append(DocumentoProcesadoModel.buffet_id == buffet_id)

        stmt = select(DocumentoProcesadoModel).where(and_(*conditions))

        # Filtrar por fecha si se proporciona
        if fecha_subida:
            fecha_limite_inferior = fecha_subida - timedelta(hours=self._timeout_hours)
            fecha_limite_superior = fecha_subida + timedelta(hours=self._timeout_hours)

            stmt = stmt.where(
                and_(
                    DocumentoProcesadoModel.created_at >= fecha_limite_inferior,
                    DocumentoProcesadoModel.created_at <= fecha_limite_superior,
                )
            )

        # Ordenar por fecha de creación (más reciente primero)
        stmt = stmt.order_by(DocumentoProcesadoModel.created_at.desc())
        stmt = stmt.limit(10)  # Limitar resultados para performance

        result = await self._session.execute(stmt)
        candidatos = list(result.unique().scalars().all())

        if candidatos:
            # Por ahora, retornar el más reciente
            # En el futuro, se podría implementar scoring basado en contenido
            par = candidatos[0]
            logger.info(
                f"Par encontrado: {par.file_id} ({par.tipo_documento.value}) "
                f"para {file_id} ({tipo_documento.value})"
            )
            return par

        logger.debug(f"No se encontró par para {file_id} ({tipo_documento.value})")
        return None

    async def find_pair_by_content(
        self,
        file_id: str,
        tipo_documento: TipoDocumentoEnum,
        datos_extraidos: dict,
        buffet_id: Optional[int] = None,
    ) -> Optional[DocumentoProcesadoModel]:
        """
        Busca un par basándose en contenido extraído (número de oficio o patente).

        Args:
            file_id: ID único del archivo (UUID)
            tipo_documento: Tipo del documento (OFICIO o CAV)
            datos_extraidos: Datos extraídos del documento
            buffet_id: ID del buffet (opcional, para filtrar por buffet)

        Returns:
            DocumentoProcesadoModel del par encontrado o None
        """
        tipo_complementario = (
            TipoDocumentoEnum.CAV
            if tipo_documento == TipoDocumentoEnum.OFICIO
            else TipoDocumentoEnum.OFICIO
        )

        # Si es OFICIO, buscar por número de oficio en CAVs que puedan tenerlo
        # Si es CAV, buscar por patente en OFICIOS que puedan tenerla
        # Por ahora, esta es una búsqueda básica
        # En el futuro, se podría parsear datos_extraidos_json de otros documentos

        conditions = [
            DocumentoProcesadoModel.file_id != file_id,
            DocumentoProcesadoModel.tipo_documento == tipo_complementario,
            or_(
                DocumentoProcesadoModel.estado == EstadoDocumentoProcesadoEnum.ESPERANDO_PAR,
                DocumentoProcesadoModel.estado == EstadoDocumentoProcesadoEnum.PENDIENTE,
            ),
        ]

        # Filtrar por buffet_id si está disponible
        if buffet_id is not None:
            conditions.append(DocumentoProcesadoModel.buffet_id == buffet_id)

        stmt = select(DocumentoProcesadoModel).where(and_(*conditions))

        stmt = stmt.order_by(DocumentoProcesadoModel.created_at.desc())
        stmt = stmt.limit(10)

        result = await self._session.execute(stmt)
        candidatos = list(result.unique().scalars().all())

        if candidatos:
            # Por ahora, retornar el más reciente
            # En el futuro, se podría comparar datos_extraidos_json
            return candidatos[0]

        return None
