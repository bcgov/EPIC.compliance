"""add initial and final response dates to complaints

Revision ID: b7d4e1a9c2f3
Revises: a3f6b2c19d75
Create Date: 2026-10-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7d4e1a9c2f3'
down_revision = 'a3f6b2c19d75'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('complaints', schema=None) as batch_op:
        batch_op.add_column(sa.Column('initial_response_date', sa.DateTime(timezone=True), nullable=True, comment='The date of the initial response to the complaint'))
        batch_op.add_column(sa.Column('final_response_date', sa.DateTime(timezone=True), nullable=True, comment='The date of the final response to the complaint'))

    # Continuum version table
    with op.batch_alter_table('complaints_version', schema=None) as batch_op:
        batch_op.add_column(sa.Column('initial_response_date', sa.DateTime(timezone=True), nullable=True, comment='The date of the initial response to the complaint'))
        batch_op.add_column(sa.Column('final_response_date', sa.DateTime(timezone=True), nullable=True, comment='The date of the final response to the complaint'))
        # Continuum change flags
        batch_op.add_column(sa.Column('initial_response_date_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False))
        batch_op.add_column(sa.Column('final_response_date_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade():
    with op.batch_alter_table('complaints_version', schema=None) as batch_op:
        batch_op.drop_column('final_response_date_mod')
        batch_op.drop_column('initial_response_date_mod')
        batch_op.drop_column('final_response_date')
        batch_op.drop_column('initial_response_date')

    with op.batch_alter_table('complaints', schema=None) as batch_op:
        batch_op.drop_column('final_response_date')
        batch_op.drop_column('initial_response_date')
