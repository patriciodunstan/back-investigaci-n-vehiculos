"""add_visitas_direcciones

Revision ID: a1b2c3d4e5f6
Revises: c0820e85296d
Create Date: 2026-01-08 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'c0820e85296d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Definir el enum una vez para reutilizar
resultado_verificacion_enum = postgresql.ENUM(
    'PENDIENTE',
    'EXITOSA',
    'NO_ENCONTRADO',
    'DIRECCION_INCORRECTA',
    'SE_MUDO',
    'RECHAZO_ATENCION',
    'OTRO',
    name='resultado_verificacion_enum',
    create_type=False
)


def upgrade() -> None:
    """Upgrade database schema."""
    # Crear el enum primero (si no existe)
    connection = op.get_bind()
    connection.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE resultado_verificacion_enum AS ENUM (
                'PENDIENTE',
                'EXITOSA',
                'NO_ENCONTRADO',
                'DIRECCION_INCORRECTA',
                'SE_MUDO',
                'RECHAZO_ATENCION',
                'OTRO'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # Agregar columnas a la tabla direcciones
    op.add_column('direcciones', sa.Column(
        'resultado_verificacion',
        resultado_verificacion_enum,
        nullable=False,
        server_default='PENDIENTE',
        comment='Resultado de la verificación'
    ))
    
    op.add_column('direcciones', sa.Column(
        'verificada_por_id',
        sa.Integer(),
        nullable=True,
        comment='ID del usuario que verificó la dirección'
    ))
    
    op.add_column('direcciones', sa.Column(
        'cantidad_visitas',
        sa.Integer(),
        nullable=False,
        server_default='0',
        comment='Cantidad de visitas realizadas'
    ))
    
    # Crear FK para verificada_por_id
    op.create_foreign_key(
        'fk_direcciones_verificada_por',
        'direcciones',
        'usuarios',
        ['verificada_por_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Crear tabla visitas_direcciones
    op.create_table('visitas_direcciones',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('direccion_id', sa.Integer(), nullable=False, comment='ID de la dirección visitada'),
        sa.Column('usuario_id', sa.Integer(), nullable=False, comment='ID del usuario que realizó la visita'),
        sa.Column('fecha_visita', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Fecha y hora de la visita'),
        sa.Column('resultado', resultado_verificacion_enum, nullable=False, comment='Resultado de la visita'),
        sa.Column('notas', sa.Text(), nullable=True, comment='Notas de la visita'),
        sa.Column('latitud', sa.Float(), nullable=True, comment='Latitud GPS de la visita'),
        sa.Column('longitud', sa.Float(), nullable=True, comment='Longitud GPS de la visita'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['direccion_id'], ['direcciones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visitas_direcciones_id'), 'visitas_direcciones', ['id'], unique=False)
    op.create_index(op.f('ix_visitas_direcciones_direccion_id'), 'visitas_direcciones', ['direccion_id'], unique=False)
    op.create_index(op.f('ix_visitas_direcciones_usuario_id'), 'visitas_direcciones', ['usuario_id'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Eliminar tabla visitas_direcciones
    op.drop_index(op.f('ix_visitas_direcciones_usuario_id'), table_name='visitas_direcciones')
    op.drop_index(op.f('ix_visitas_direcciones_direccion_id'), table_name='visitas_direcciones')
    op.drop_index(op.f('ix_visitas_direcciones_id'), table_name='visitas_direcciones')
    op.drop_table('visitas_direcciones')
    
    # Eliminar FK y columnas de direcciones
    op.drop_constraint('fk_direcciones_verificada_por', 'direcciones', type_='foreignkey')
    op.drop_column('direcciones', 'cantidad_visitas')
    op.drop_column('direcciones', 'verificada_por_id')
    op.drop_column('direcciones', 'resultado_verificacion')
    
    # Eliminar enum
    sa.Enum(name='resultado_verificacion_enum').drop(op.get_bind(), checkfirst=True)
