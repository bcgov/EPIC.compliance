"""add deputy review complete referral status

Revision ID: c8a2f5b31e47
Revises: b7c4e91a2d58
Create Date: 2026-08-19 09:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c8a2f5b31e47'
down_revision = 'b7c4e91a2d58'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE referralstatusenum ADD VALUE IF NOT EXISTS 'DEPUTY_REVIEW_COMPLETE' AFTER 'DEPUTY_REVIEW'")
    op.execute("COMMIT;")


def downgrade():
    op.execute(
        "UPDATE administrative_penalties SET referral_status='DEPUTY_REVIEW' "
        "WHERE referral_status='DEPUTY_REVIEW_COMPLETE'"
    )
    op.execute(
        "UPDATE administrative_penalties_version SET referral_status='DEPUTY_REVIEW' "
        "WHERE referral_status='DEPUTY_REVIEW_COMPLETE'"
    )
    op.execute("ALTER TYPE referralstatusenum RENAME TO referralstatusenum_old")
    op.execute(
        "CREATE TYPE referralstatusenum AS ENUM("
        "'DRAFTING', 'REFERRED_TO_AMP_UNIT', 'DEPUTY_REVIEW', 'CEB_NOT_PROCEEDING', 'REFERRED_TO_DM')"
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
