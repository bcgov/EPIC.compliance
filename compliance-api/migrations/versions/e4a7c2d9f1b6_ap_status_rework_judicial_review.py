"""AP status rework and judicial review (COMP-964)

Backs up administrative_penalties, clears date_referred, folds the legacy
referral statuses into REFERRED_TO_AEO, adds JUDICIAL_REVIEW and the JR columns.

Revision ID: e4a7c2d9f1b6
Revises: c9e2f4a7b1d3
Create Date: 2026-11-20 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4a7c2d9f1b6'
down_revision = 'c9e2f4a7b1d3'
branch_labels = None
depends_on = None

BACKUP_TABLE = 'administrative_penalties_backup_comp964'
AP_TABLES = ('administrative_penalties', 'administrative_penalties_version')
NEW_STATUSES = ('PREPARING_REFERRAL_FOR_AEO', 'REFERRED_TO_AEO', 'AP_NOT_PROCEEDING', 'JUDICIAL_REVIEW')
OLD_STATUSES = (
    'PREPARING_REFERRAL_FOR_AEO', 'REFERRED_TO_AEO', 'DEPUTY_REVIEW',
    'DEPUTY_REVIEW_COMPLETE', 'AP_NOT_PROCEEDING', 'REFERRED_TO_DM',
)
JR_DECISIONS = ('REVERSED', 'QUASHED_AND_REMITTED', 'SUBSTITUTED', 'UPHELD')
JR_COLUMNS = ('jr_decision_date', 'jr_decision', 'jr_new_penalty_amount', 'jr_ap_fields_edited')


def _rebuild_status_type(values, using):
    """Recreate referralstatusenum with `values`, converting rows with the `using` SQL expression."""
    labels = ', '.join(f"'{v}'" for v in values)
    op.execute("ALTER TYPE referralstatusenum RENAME TO referralstatusenum_old")
    op.execute(f"CREATE TYPE referralstatusenum AS ENUM({labels})")
    for table in AP_TABLES:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN referral_status "
            f"TYPE referralstatusenum USING ({using})::referralstatusenum"
        )
    op.execute("DROP TYPE referralstatusenum_old")


def upgrade():
    # Full before-image of every AP, kept for data verification after release.
    op.execute(f"CREATE TABLE {BACKUP_TABLE} AS TABLE administrative_penalties")
    # Text, so the backup doesn't pin the enum type being rebuilt below.
    op.execute(f"ALTER TABLE {BACKUP_TABLE} ALTER COLUMN referral_status TYPE text")
    op.execute("UPDATE administrative_penalties SET date_referred = NULL")

    _rebuild_status_type(
        NEW_STATUSES,
        "CASE WHEN referral_status::text IN ('DEPUTY_REVIEW', 'DEPUTY_REVIEW_COMPLETE', 'REFERRED_TO_DM') "
        "THEN 'REFERRED_TO_AEO' ELSE referral_status::text END",
    )

    jr_decision = sa.Enum(*JR_DECISIONS, name='judicialreviewdecisionenum')
    jr_decision.create(op.get_bind())
    for table in AP_TABLES:
        with op.batch_alter_table(table) as batch_op:
            batch_op.add_column(sa.Column('jr_decision_date', sa.DateTime(timezone=True), nullable=True,
                                          comment='Date of the judicial review decision'))
            batch_op.add_column(sa.Column('jr_decision', jr_decision, nullable=True,
                                          comment='Judicial review decision'))
            batch_op.add_column(sa.Column('jr_new_penalty_amount', sa.Numeric(precision=10, scale=2),
                                          nullable=True, comment='Penalty amount after judicial review'))
            batch_op.add_column(sa.Column('jr_ap_fields_edited', sa.Boolean(), server_default=sa.text('false'),
                                          nullable=False,
                                          comment='A superuser changed the AP fields during the judicial review'))
            if table.endswith('_version'):
                for col in JR_COLUMNS:
                    batch_op.add_column(sa.Column(f'{col}_mod', sa.Boolean(),
                                                  server_default=sa.text('false'), nullable=False))


def downgrade():
    for table in AP_TABLES:
        with op.batch_alter_table(table) as batch_op:
            for col in JR_COLUMNS:
                batch_op.drop_column(col)
                if table.endswith('_version'):
                    batch_op.drop_column(f'{col}_mod')
    op.execute("DROP TYPE judicialreviewdecisionenum")

    _rebuild_status_type(
        OLD_STATUSES,
        "CASE WHEN referral_status::text = 'JUDICIAL_REVIEW' THEN 'REFERRED_TO_AEO' "
        "ELSE referral_status::text END",
    )

    # Restore the live rows' original status and referral date from the backup.
    op.execute(
        f"UPDATE administrative_penalties ap SET referral_status = b.referral_status::text::referralstatusenum, "
        f"date_referred = b.date_referred FROM {BACKUP_TABLE} b WHERE b.id = ap.id"
    )
    op.execute(f"DROP TABLE {BACKUP_TABLE}")
