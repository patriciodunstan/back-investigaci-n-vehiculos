"""add_duplicado_estado_documento

Revision ID: add_duplicado_estado
Revises: 1f60f7815f05
Create Date: 2026-02-04

Agrega el valor 'DUPLICADO' al enum estado_documento_procesado_enum
para identificar documentos cuyo oficio ya existía en el sistema.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_duplicado_estado'
down_revision = '1f60f7815f05'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Agrega 'DUPLICADO' al enum estado_documento_procesado_enum."""
    # PostgreSQL requiere ALTER TYPE para agregar valores a un enum existente
    op.execute("ALTER TYPE estado_documento_procesado_enum ADD VALUE IF NOT EXISTS 'DUPLICADO'")


def downgrade() -> None:
    """
    No se puede eliminar un valor de un enum en PostgreSQL fácilmente.
    Se requeriría recrear el enum completo.
    
    Para downgrade completo:
    1. Cambiar registros con DUPLICADO a ERROR
    2. Recrear enum sin DUPLICADO
    3. Actualizar columna
    
    Por simplicidad, solo convertimos los registros existentes.
    """
    # Convertir registros DUPLICADO a ERROR antes de intentar eliminar el valor
    op.execute("""
        UPDATE documentos_procesados 
        SET estado = 'ERROR', 
            error_mensaje = COALESCE(error_mensaje, '') || ' [Convertido desde DUPLICADO]'
        WHERE estado = 'DUPLICADO'
    """)
    # Nota: El valor DUPLICADO seguirá en el enum pero no se usará
