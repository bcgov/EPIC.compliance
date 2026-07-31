"""enforce single active in-progress document job per user/inspection/format

Revision ID: a3f9c1d24b77
Revises: f9ce82110047
Create Date: 2026-07-24 17:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a3f9c1d24b77'
down_revision = 'f9ce82110047'
branch_labels = None
depends_on = None


INDEX_NAME = 'uq_document_jobs_active_in_progress'


def upgrade():
    op.execute(
        f"""
        CREATE UNIQUE INDEX {INDEX_NAME}
        ON document_jobs (user_id, inspection_record_id, output_format)
        WHERE is_active = true AND is_deleted = false AND status = 'In Progress'
        """
    )


def downgrade():
    op.execute(f"DROP INDEX {INDEX_NAME}")
