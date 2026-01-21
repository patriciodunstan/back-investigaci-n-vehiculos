"""
Mapper para asociar carpetas de Google Drive con buffet_id.

Mapea IDs de carpetas de Google Drive a IDs de buffets en el sistema.

Principios aplicados:
- SRP: Solo mapea carpetas a buffets
- OCP: Abierto para extensión con diferentes fuentes de configuración
"""

import logging
import json
from typing import Optional, Dict
from pathlib import Path

from src.core.config import get_settings


logger = logging.getLogger(__name__)


class BuffetMapper:
    """
    Mapea carpetas de Google Drive a buffet_id.

    Estrategias de configuración:
    1. Variable de entorno (JSON string)
    2. Archivo JSON en filesystem
    3. Base de datos (futuro)

    Example:
        >>> mapper = BuffetMapper()
        >>> buffet_id = mapper.get_buffet_id("folder_id_123")
    """

    def __init__(self, mapping_config: Optional[str] = None):
        """
        Inicializa el mapper.

        Args:
            mapping_config: Configuración de mapeo (JSON string o path a archivo)
                           Si None, usa configuración desde settings
        """
        settings = get_settings()
        self._mapping: Dict[str, int] = {}

        # Obtener configuración
        config_source = mapping_config or getattr(settings, "GOOGLE_DRIVE_BUFFET_MAPPING", None)

        if config_source:
            self._load_mapping(config_source)
        else:
            logger.warning(
                "GOOGLE_DRIVE_BUFFET_MAPPING no configurado. "
                "No se podrá mapear carpetas a buffets automáticamente."
            )

    def _load_mapping(self, config_source: str) -> None:
        """
        Carga el mapeo desde una fuente de configuración.

        Args:
            config_source: JSON string o path a archivo JSON
        """
        try:
            # Intentar parsear como JSON string primero
            if config_source.strip().startswith("{"):
                mapping_dict = json.loads(config_source)
            else:
                # Asumir que es un path a archivo
                config_path = Path(config_source)
                if not config_path.exists():
                    logger.warning(f"Archivo de mapeo no encontrado: {config_source}")
                    return

                with open(config_path, "r", encoding="utf-8") as f:
                    mapping_dict = json.load(f)

            # Validar y cargar mapeo
            if isinstance(mapping_dict, dict):
                self._mapping = {
                    str(folder_id): int(buffet_id) for folder_id, buffet_id in mapping_dict.items()
                }
                logger.info(f"BuffetMapper cargado con {len(self._mapping)} mapeos de carpetas")
            else:
                logger.error("Formato de mapeo inválido: debe ser un objeto JSON")

        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de mapeo: {str(e)}")
        except Exception as e:
            logger.error(f"Error cargando mapeo de buffets: {str(e)}")

    def get_buffet_id(self, drive_folder_id: str) -> Optional[int]:
        """
        Obtiene el buffet_id asociado a una carpeta de Google Drive.

        Args:
            drive_folder_id: ID de la carpeta en Google Drive

        Returns:
            buffet_id o None si no hay mapeo

        Example:
            >>> mapper = BuffetMapper()
            >>> buffet_id = mapper.get_buffet_id("folder_123")
            >>> print(buffet_id)  # 1 o None
        """
        buffet_id = self._mapping.get(drive_folder_id)

        if buffet_id is None:
            logger.debug(
                f"No hay mapeo para carpeta {drive_folder_id}. "
                "El oficio se creará sin buffet_id."
            )

        return buffet_id

    def add_mapping(self, drive_folder_id: str, buffet_id: int) -> None:
        """
        Agrega un mapeo manualmente (útil para tests o configuración dinámica).

        Args:
            drive_folder_id: ID de la carpeta en Google Drive
            buffet_id: ID del buffet

        Note:
            Este mapeo no persiste. Para persistencia, usar configuración.
        """
        self._mapping[drive_folder_id] = buffet_id
        logger.debug(f"Mapeo agregado: {drive_folder_id} -> {buffet_id}")

    def get_all_mappings(self) -> Dict[str, int]:
        """
        Retorna todos los mapeos actuales.

        Returns:
            Dict con mapeos folder_id -> buffet_id
        """
        return self._mapping.copy()


# =============================================================================
# SINGLETON / DEPENDENCY INJECTION
# =============================================================================

_buffet_mapper: Optional[BuffetMapper] = None


def get_buffet_mapper() -> BuffetMapper:
    """
    Obtiene una instancia singleton del mapper de buffets.

    Usar esta función para inyección de dependencias.

    Returns:
        BuffetMapper configurado

    Example:
        >>> from src.modules.oficios.infrastructure.services.buffet_mapper import get_buffet_mapper
        >>> mapper = get_buffet_mapper()
        >>> buffet_id = mapper.get_buffet_id("folder_id")
    """
    global _buffet_mapper
    if _buffet_mapper is None:
        _buffet_mapper = BuffetMapper()
    return _buffet_mapper


def reset_buffet_mapper() -> None:
    """Resetea el mapper singleton (útil para tests)."""
    global _buffet_mapper
    _buffet_mapper = None
