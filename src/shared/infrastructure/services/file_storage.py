"""
Servicio de almacenamiento de archivos local.

Proporciona funciones para guardar, leer y eliminar archivos
en el sistema de archivos local, organizados por fecha.

Principios aplicados:
- SRP: Solo maneja almacenamiento de archivos
- OCP: Abierto para extensión (S3 en el futuro)
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.config import get_settings


logger = logging.getLogger(__name__)


class FileStorageService:
    """
    Servicio para almacenar archivos en el sistema de archivos local.

    Organiza archivos en carpetas por fecha: YYYY/MM/DD/uuid.pdf
    Genera nombres únicos usando UUID para evitar colisiones.

    Attributes:
        base_path: Path base del almacenamiento
        ensure_directories: Si debe crear directorios automáticamente

    Example:
        >>> storage = FileStorageService()
        >>> path = storage.save_file(b"content", "documento.pdf")
        >>> content = storage.get_file(path)
        >>> storage.delete_file(path)
    """

    def __init__(
        self,
        base_path: Optional[str] = None,
        ensure_directories: bool = True,
    ):
        """
        Inicializa el servicio de almacenamiento.

        Args:
            base_path: Path base del almacenamiento (default: desde settings)
            ensure_directories: Si debe crear directorios automáticamente
        """
        settings = get_settings()
        self.base_path = Path(base_path or settings.STORAGE_PATH)
        self.ensure_directories = ensure_directories

        # Crear directorio base si no existe
        if self.ensure_directories:
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Storage base path: {self.base_path.absolute()}")

    def _get_date_path(self, date: Optional[datetime] = None) -> Path:
        """
        Genera el path relativo para una fecha.

        Formato: YYYY/MM/DD/

        Args:
            date: Fecha para organizar (default: fecha actual)

        Returns:
            Path relativo para la fecha
        """
        if date is None:
            date = datetime.utcnow()

        return Path(
            str(date.year),
            f"{date.month:02d}",
            f"{date.day:02d}",
        )

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Genera un nombre único para un archivo.

        Usa UUID para evitar colisiones, manteniendo la extensión original.

        Args:
            original_filename: Nombre original del archivo

        Returns:
            Nombre único generado (ej: "abc123def456.pdf")
        """
        # Obtener extensión
        original_path = Path(original_filename)
        extension = original_path.suffix or ""

        # Generar UUID y mantener extensión
        unique_id = str(uuid.uuid4()).replace("-", "")
        return f"{unique_id}{extension}"

    def save_file(
        self,
        content: bytes,
        filename: str,
        date: Optional[datetime] = None,
    ) -> str:
        """
        Guarda un archivo en el almacenamiento local.

        El archivo se guarda en: base_path/YYYY/MM/DD/uuid.ext

        Args:
            content: Contenido del archivo en bytes
            filename: Nombre original del archivo (para obtener extensión)
            date: Fecha para organizar (default: fecha actual)

        Returns:
            Path relativo del archivo guardado (ej: "2026/01/18/abc123def456.pdf")

        Raises:
            OSError: Si no se puede escribir el archivo
        """
        # Generar path relativo por fecha
        date_path = self._get_date_path(date)

        # Generar nombre único
        unique_filename = self._generate_unique_filename(filename)

        # Path completo
        full_dir = self.base_path / date_path
        full_path = full_dir / unique_filename

        # Crear directorio si no existe
        if self.ensure_directories:
            full_dir.mkdir(parents=True, exist_ok=True)

        # Escribir archivo
        try:
            full_path.write_bytes(content)
            logger.debug(f"Archivo guardado: {full_path.absolute()}")

            # Retornar path relativo desde base_path
            relative_path = date_path / unique_filename
            return str(relative_path)

        except OSError as e:
            logger.error(f"Error guardando archivo {filename}: {e}")
            raise

    def get_file(self, relative_path: str) -> bytes:
        """
        Lee un archivo del almacenamiento.

        Args:
            relative_path: Path relativo del archivo (ej: "2026/01/18/abc123def456.pdf")

        Returns:
            Contenido del archivo en bytes

        Raises:
            FileNotFoundError: Si el archivo no existe
            OSError: Si no se puede leer el archivo
        """
        full_path = self.base_path / relative_path

        if not full_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {relative_path}")

        try:
            content = full_path.read_bytes()
            logger.debug(f"Archivo leído: {full_path.absolute()} ({len(content)} bytes)")
            return content
        except OSError as e:
            logger.error(f"Error leyendo archivo {relative_path}: {e}")
            raise

    def delete_file(self, relative_path: str) -> bool:
        """
        Elimina un archivo del almacenamiento.

        Args:
            relative_path: Path relativo del archivo

        Returns:
            True si se eliminó correctamente, False si no existía

        Raises:
            OSError: Si no se puede eliminar el archivo
        """
        full_path = self.base_path / relative_path

        if not full_path.exists():
            logger.warning(f"Archivo no existe, no se puede eliminar: {relative_path}")
            return False

        try:
            full_path.unlink()
            logger.debug(f"Archivo eliminado: {full_path.absolute()}")

            # Intentar eliminar directorios vacíos (opcional, no crítico si falla)
            try:
                date_dir = full_path.parent
                if date_dir.exists() and not any(date_dir.iterdir()):
                    date_dir.rmdir()
            except OSError:
                pass  # Ignorar si no se puede eliminar el directorio

            return True
        except OSError as e:
            logger.error(f"Error eliminando archivo {relative_path}: {e}")
            raise

    def file_exists(self, relative_path: str) -> bool:
        """
        Verifica si un archivo existe.

        Args:
            relative_path: Path relativo del archivo

        Returns:
            True si el archivo existe, False en caso contrario
        """
        full_path = self.base_path / relative_path
        return full_path.exists()

    def get_file_size(self, relative_path: str) -> int:
        """
        Obtiene el tamaño de un archivo en bytes.

        Args:
            relative_path: Path relativo del archivo

        Returns:
            Tamaño del archivo en bytes

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        full_path = self.base_path / relative_path

        if not full_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {relative_path}")

        return full_path.stat().st_size


# Singleton instance
_storage_instance: Optional[FileStorageService] = None


def get_file_storage() -> FileStorageService:
    """
    Obtiene la instancia singleton del servicio de almacenamiento.

    Returns:
        Instancia de FileStorageService
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = FileStorageService()
    return _storage_instance
