"""adapt_documentos_procesados_to_local_storage

Revision ID: 1f60f7815f05
Revises: e198791a2934
Create Date: 2026-01-18 15:52:55.079103

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f60f7815f05"
down_revision: Union[str, None] = "e198791a2934"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema - Adaptar documentos_procesados para local storage."""
    # Eliminar índices antiguos (el índice único ya garantiza la unicidad, no hay constraint separado)
    op.drop_index("ix_documentos_procesados_drive_file_id", table_name="documentos_procesados")
    op.drop_index("ix_documentos_procesados_drive_folder_id", table_name="documentos_procesados")

    # Agregar nuevas columnas
    op.add_column(
        "documentos_procesados",
        sa.Column(
            "file_id",
            sa.String(length=255),
            nullable=True,  # Temporalmente nullable para migración
            comment="ID único del archivo (UUID generado localmente)",
        ),
    )
    op.add_column(
        "documentos_procesados",
        sa.Column(
            "file_name",
            sa.String(length=500),
            nullable=True,  # Temporalmente nullable para migración
            comment="Nombre original del archivo",
        ),
    )
    op.add_column(
        "documentos_procesados",
        sa.Column(
            "storage_path",
            sa.String(length=500),
            nullable=True,  # Temporalmente nullable para migración
            comment="Ruta relativa donde se guardó el archivo (ej: 2026/01/18/uuid.pdf)",
        ),
    )

    # Migrar datos: usar drive_file_id como file_id, drive_file_name como file_name
    # Para storage_path, generamos un path temporal basado en drive_folder_id o fecha
    op.execute(
        sa.text(
            """
        UPDATE documentos_procesados
        SET 
            file_id = drive_file_id,
            file_name = drive_file_name,
            storage_path = CONCAT('migrated/', drive_folder_id, '/', drive_file_id, '.pdf')
        WHERE file_id IS NULL
    """
        )
    )

    # Hacer columnas NOT NULL
    op.alter_column("documentos_procesados", "file_id", nullable=False)
    op.alter_column("documentos_procesados", "file_name", nullable=False)
    op.alter_column("documentos_procesados", "storage_path", nullable=False)

    # Eliminar columnas antiguas
    op.drop_column("documentos_procesados", "drive_file_id")
    op.drop_column("documentos_procesados", "drive_file_name")
    op.drop_column("documentos_procesados", "drive_folder_id")

    # Crear nuevos índices
    op.create_index(
        "ix_documentos_procesados_file_id", "documentos_procesados", ["file_id"], unique=True
    )
    op.create_index(
        "ix_documentos_procesados_storage_path",
        "documentos_procesados",
        ["storage_path"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema - Revertir a Google Drive fields."""
    # Eliminar índices nuevos
    op.drop_index("ix_documentos_procesados_storage_path", table_name="documentos_procesados")
    op.drop_index("ix_documentos_procesados_file_id", table_name="documentos_procesados")

    # Agregar columnas antiguas
    op.add_column(
        "documentos_procesados",
        sa.Column(
            "drive_file_id",
            sa.String(length=255),
            nullable=True,
            comment="ID único del archivo en Google Drive",
        ),
    )
    op.add_column(
        "documentos_procesados",
        sa.Column(
            "drive_file_name",
            sa.String(length=500),
            nullable=True,
            comment="Nombre del archivo en Google Drive",
        ),
    )
    op.add_column(
        "documentos_procesados",
        sa.Column(
            "drive_folder_id",
            sa.String(length=255),
            nullable=True,
            comment="ID de la carpeta de Google Drive",
        ),
    )

    # Migrar datos de vuelta
    op.execute(
        sa.text(
            """
        UPDATE documentos_procesados
        SET 
            drive_file_id = file_id,
            drive_file_name = file_name,
            drive_folder_id = SPLIT_PART(storage_path, '/', 2)
        WHERE drive_file_id IS NULL
    """
        )
    )

    # Hacer columnas NOT NULL
    op.alter_column("documentos_procesados", "drive_file_id", nullable=False)
    op.alter_column("documentos_procesados", "drive_file_name", nullable=False)
    op.alter_column("documentos_procesados", "drive_folder_id", nullable=False)

    # Eliminar columnas nuevas
    op.drop_column("documentos_procesados", "file_id")
    op.drop_column("documentos_procesados", "file_name")
    op.drop_column("documentos_procesados", "storage_path")

    # Crear índices antiguos
    op.create_index(
        "ix_documentos_procesados_drive_folder_id",
        "documentos_procesados",
        ["drive_folder_id"],
        unique=False,
    )
    op.create_index(
        "ix_documentos_procesados_drive_file_id",
        "documentos_procesados",
        ["drive_file_id"],
        unique=True,
    )
