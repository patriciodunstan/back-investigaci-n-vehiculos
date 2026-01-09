"""remove_unique_vehiculo_oficio_id

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-08 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint to allow multiple vehicles per oficio."""
    # Eliminar el índice único en oficio_id de la tabla vehiculos
    op.drop_index('ix_vehiculos_oficio_id', table_name='vehiculos')
    
    # Crear un índice normal (no único) para mantener el rendimiento
    op.create_index('ix_vehiculos_oficio_id', 'vehiculos', ['oficio_id'], unique=False)


def downgrade() -> None:
    """Restore unique constraint (1:1 relationship)."""
    op.drop_index('ix_vehiculos_oficio_id', table_name='vehiculos')
    op.create_index('ix_vehiculos_oficio_id', 'vehiculos', ['oficio_id'], unique=True)
