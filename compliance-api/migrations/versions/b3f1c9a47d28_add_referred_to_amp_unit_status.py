"""add referred to AMP unit referral status

Revision ID: b3f1c9a47d28
Revises: f71662d8e6c6
Create Date: 2026-06-17 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b3f1c9a47d28'
down_revision = 'f71662d8e6c6'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new 'REFERRED_TO_AMP_UNIT' value immediately after 'DRAFTING'
    op.execute("ALTER TYPE referralstatusenum ADD VALUE IF NOT EXISTS 'REFERRED_TO_AMP_UNIT' AFTER 'DRAFTING'")
    op.execute("COMMIT;")


def downgrade():
    # Move any rows using the new value back to DRAFTING before dropping it
    op.execute(
        "UPDATE administrative_penalties SET referral_status='DRAFTING' "
        "WHERE referral_status='REFERRED_TO_AMP_UNIT'"
    )
    op.execute(
        "UPDATE administrative_penalties_version SET referral_status='DRAFTING' "
        "WHERE referral_status='REFERRED_TO_AMP_UNIT'"
    )
    op.execute("ALTER TYPE referralstatusenum RENAME TO referralstatusenum_old")
    op.execute(
        "CREATE TYPE referralstatusenum AS ENUM("
        "'DRAFTING', 'DEPUTY_REVIEW', 'CEB_NOT_PROCEEDING', 'REFERRED_TO_DM')"
    )
    op.execute(
        "ALTER TABLE administrative_penalties "
        "ALTER COLUMN referral_status "
        "TYPE referralstatusenum "
        "USING referral_status::text::referralstatusenum"
    )
    op.execute(
        "ALTER TABLE administrative_penalties_version "
        "ALTER COLUMN referral_status "
        "TYPE referralstatusenum "
        "USING referral_status::text::referralstatusenum"
    )
    op.execute("DROP TYPE referralstatusenum_old")
