"""make inspection end_date nullable

Revision ID: c9e2f4a7b1d3
Revises: b7d4e1a9c2f3
Create Date: 2026-11-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9e2f4a7b1d3'
down_revision = 'b7d4e1a9c2f3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.alter_column('end_date', existing_type=sa.DateTime(timezone=True), nullable=True)


def downgrade():
    op.execute("UPDATE inspections SET end_date = start_date WHERE end_date IS NULL")
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.alter_column('end_date', existing_type=sa.DateTime(timezone=True), nullable=False)
