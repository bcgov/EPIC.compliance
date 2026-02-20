"""adding project components and area inspected to inspecton model

Revision ID: f71662d8e6c6
Revises: 36db02e529a3
Create Date: 2026-02-19 14:04:12.318696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f71662d8e6c6'
down_revision = '36db02e529a3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('inspections', sa.Column('area_inspected', sa.String(), nullable=True))
    op.add_column('inspections_version', sa.Column('area_inspected', sa.String(), nullable=True))
    op.add_column('inspections_version', sa.Column('area_inspected_mod', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('inspections', 'area_inspected')
    op.drop_column('inspections_version', 'area_inspected')
    op.drop_column('inspections_version', 'area_inspected_mod')
