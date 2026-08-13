"""rename executive director position to director

Revision ID: b7c4e91a2d58
Revises: d4e8a1c37b92
Create Date: 2026-08-13 10:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b7c4e91a2d58'
down_revision = 'b1d4c9e77a02'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE positions SET name='Director, Compliance & Enforcement' "
        "WHERE name='Executive Director, Compliance & Enforcement'")


def downgrade():
    op.execute(
        "UPDATE positions SET name='Executive Director, Compliance & Enforcement' "
        "WHERE name='Director, Compliance & Enforcement'")
