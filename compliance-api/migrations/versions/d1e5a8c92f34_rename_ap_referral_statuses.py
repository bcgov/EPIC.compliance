"""rename administrative penalty referral statuses to current terminology

Revision ID: d1e5a8c92f34
Revises: c8a2f5b31e47
Create Date: 2026-08-19 11:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd1e5a8c92f34'
down_revision = 'c8a2f5b31e47'
branch_labels = None
depends_on = None


RENAMES = [
    ('DRAFTING', 'PREPARING_REFERRAL_FOR_AEO'),
    ('REFERRED_TO_AMP_UNIT', 'REFERRED_TO_AEO'),
    ('CEB_NOT_PROCEEDING', 'AP_NOT_PROCEEDING'),
]


def upgrade():
    for old_label, new_label in RENAMES:
        op.execute(f"ALTER TYPE referralstatusenum RENAME VALUE '{old_label}' TO '{new_label}'")


def downgrade():
    for old_label, new_label in RENAMES:
        op.execute(f"ALTER TYPE referralstatusenum RENAME VALUE '{new_label}' TO '{old_label}'")
