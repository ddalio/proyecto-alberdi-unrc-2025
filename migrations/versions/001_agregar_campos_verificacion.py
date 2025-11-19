"""agregar campos verificacion email

Revision ID: 001_agregar_campos_verificacion
Revises: f12da69da839
Create Date: 2025-11-19 03:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_agregar_campos_verificacion'
down_revision = 'f12da69da839'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cuenta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rol', sa.String(20), nullable=False, server_default='usuario'))
        batch_op.add_column(sa.Column('email_verificado', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('fecha_verificacion', sa.DateTime(), nullable=True))
        batch_op.alter_column('password', new_column_name='password_hash')

def downgrade():
    with op.batch_alter_table('cuenta', schema=None) as batch_op:
        batch_op.alter_column('password_hash', new_column_name='password')
        batch_op.drop_column('fecha_verificacion')
        batch_op.drop_column('email_verificado')
        batch_op.drop_column('rol')
