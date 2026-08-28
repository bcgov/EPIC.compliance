"""allow multiple project statuses per inspection

Revision ID: a3f6b2c19d75
Revises: d1e5a8c92f34
Create Date: 2026-08-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f6b2c19d75'
down_revision = 'd1e5a8c92f34'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'inspection_project_statuses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='The unique identifier'),
        sa.Column('project_status_id', sa.Integer(), nullable=False,
                  comment='The unique identifier of the project status in EPIC.track'),
        sa.Column('inspection_id', sa.Integer(), nullable=False,
                  comment='The unique identifier of the inspection'),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('updated_date', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='t', nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='f', nullable=False),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'],
                                name='inspection_project_statuses_inspection_id_fkey'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'inspection_project_statuses_version',
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False, comment='The unique identifier'),
        sa.Column('project_status_id', sa.Integer(), autoincrement=False, nullable=True,
                  comment='The unique identifier of the project status in EPIC.track'),
        sa.Column('inspection_id', sa.Integer(), autoincrement=False, nullable=True,
                  comment='The unique identifier of the inspection'),
        sa.Column('created_date', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('updated_date', sa.DateTime(), autoincrement=False, nullable=True),
        sa.Column('created_by', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('updated_by', sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='t', autoincrement=False, nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='f', autoincrement=False, nullable=True),
        sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
        sa.Column('operation_type', sa.SmallInteger(), nullable=False),
        sa.Column('project_status_id_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('inspection_id_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_date_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('updated_date_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_by_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('updated_by_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_active_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_deleted_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.PrimaryKeyConstraint('id', 'transaction_id'),
    )
    op.create_index(
        op.f('ix_inspection_project_statuses_version_end_transaction_id'),
        'inspection_project_statuses_version', ['end_transaction_id'], unique=False
    )
    op.create_index(
        op.f('ix_inspection_project_statuses_version_operation_type'),
        'inspection_project_statuses_version', ['operation_type'], unique=False
    )
    op.create_index(
        op.f('ix_inspection_project_statuses_version_transaction_id'),
        'inspection_project_statuses_version', ['transaction_id'], unique=False
    )
    op.execute(
        """
        CREATE TEMP TABLE tmp_inspection_project_status_rows AS
        WITH history AS (
            SELECT
                inspections_version.id AS inspection_id,
                inspections_version.transaction_id,
                inspections_version.operation_type,
                inspections_version.is_active,
                inspections_version.is_deleted,
                inspections_version.created_by,
                inspections_version.updated_by,
                CASE
                    WHEN inspections_version.is_deleted OR inspections_version.operation_type = 2
                        THEN NULL
                    ELSE inspections_version.project_status_id
                END AS effective_project_status_id,
                LAG(
                    CASE
                        WHEN inspections_version.is_deleted OR inspections_version.operation_type = 2
                            THEN NULL
                        ELSE inspections_version.project_status_id
                    END
                ) OVER inspection_history AS previous_project_status_id
            FROM inspections_version
            WINDOW inspection_history AS (
                PARTITION BY inspections_version.id ORDER BY inspections_version.transaction_id
            )
        ),
        change_points AS (
            SELECT
                history.*,
                LEAD(history.transaction_id) OVER inspection_history AS closed_transaction_id,
                LEAD(history.operation_type) OVER inspection_history AS closed_operation_type,
                LEAD(history.is_deleted) OVER inspection_history AS closed_inspection_is_deleted
            FROM history
            WHERE history.effective_project_status_id IS DISTINCT FROM history.previous_project_status_id
              AND (
                  history.effective_project_status_id IS NOT NULL
                  OR history.previous_project_status_id IS NOT NULL
              )
            WINDOW inspection_history AS (
                PARTITION BY history.inspection_id ORDER BY history.transaction_id
            )
        )
        SELECT
            nextval('inspection_project_statuses_id_seq') AS project_status_row_id,
            change_points.inspection_id,
            change_points.effective_project_status_id AS project_status_id,
            change_points.is_active,
            change_points.transaction_id AS opened_transaction_id,
            change_points.closed_transaction_id,
            CASE WHEN change_points.closed_operation_type = 2 THEN 2 ELSE 1 END
                AS closed_operation_type,
            COALESCE(change_points.closed_inspection_is_deleted, false)
                OR change_points.closed_operation_type = 2 AS closed_by_inspection_delete,
            opened.issued_at AS opened_date,
            closed.issued_at AS closed_date,
            COALESCE(change_points.updated_by, change_points.created_by, 'system') AS opened_by
        FROM change_points
        LEFT JOIN "transaction" AS opened ON opened.id = change_points.transaction_id
        LEFT JOIN "transaction" AS closed ON closed.id = change_points.closed_transaction_id
        WHERE change_points.effective_project_status_id IS NOT NULL
        """
    )
    op.execute(
        """
        INSERT INTO inspection_project_statuses
            (id, project_status_id, inspection_id, created_date, created_by, is_active, is_deleted)
        SELECT
            COALESCE(status_rows.project_status_row_id,
                     nextval('inspection_project_statuses_id_seq')),
            inspections.project_status_id,
            inspections.id,
            COALESCE(status_rows.opened_date, inspections.created_date),
            COALESCE(status_rows.opened_by, inspections.created_by, 'system'),
            inspections.is_active,
            inspections.is_deleted
        FROM inspections
        LEFT JOIN (
            SELECT DISTINCT ON (inspection_id, project_status_id)
                inspection_id, project_status_id, project_status_row_id, opened_date, opened_by
            FROM tmp_inspection_project_status_rows
            WHERE closed_transaction_id IS NULL OR closed_by_inspection_delete
            ORDER BY inspection_id, project_status_id, opened_transaction_id DESC
        ) status_rows
            ON status_rows.inspection_id = inspections.id
           AND status_rows.project_status_id = inspections.project_status_id
        WHERE inspections.project_status_id IS NOT NULL
        """
    )
    op.execute(
        """
        INSERT INTO inspection_project_statuses
            (id, project_status_id, inspection_id, created_date, created_by, is_active, is_deleted)
        SELECT
            status_rows.project_status_row_id,
            status_rows.project_status_id,
            status_rows.inspection_id,
            COALESCE(status_rows.opened_date, now() at time zone 'utc'),
            status_rows.opened_by,
            status_rows.is_active,
            true
        FROM tmp_inspection_project_status_rows status_rows
        WHERE NOT EXISTS (
            SELECT 1 FROM inspection_project_statuses existing
            WHERE existing.id = status_rows.project_status_row_id
        )
        AND EXISTS (
            SELECT 1 FROM inspections WHERE inspections.id = status_rows.inspection_id
        )
        """
    )
    op.execute(
        """
        INSERT INTO inspection_project_statuses_version (
            id, project_status_id, inspection_id, created_date, updated_date, created_by, updated_by,
            is_active, is_deleted, transaction_id, end_transaction_id, operation_type,
            project_status_id_mod, inspection_id_mod, created_date_mod, updated_date_mod,
            created_by_mod, updated_by_mod, is_active_mod, is_deleted_mod
        )
        SELECT
            project_status_row_id,
            project_status_id,
            inspection_id,
            COALESCE(opened_date, now() at time zone 'utc'),
            NULL,
            opened_by,
            NULL,
            is_active,
            false,
            opened_transaction_id,
            closed_transaction_id,
            0,
            true, true, true, false, true, false, true, true
        FROM tmp_inspection_project_status_rows
        UNION ALL
        SELECT
            project_status_row_id,
            project_status_id,
            inspection_id,
            COALESCE(opened_date, now() at time zone 'utc'),
            COALESCE(closed_date, now() at time zone 'utc'),
            opened_by,
            'system',
            is_active,
            true,
            closed_transaction_id,
            NULL,
            CASE WHEN closed_operation_type = 2 THEN 2 ELSE 1 END,
            false, false, false, true, false, true, false, true
        FROM tmp_inspection_project_status_rows
        WHERE closed_transaction_id IS NOT NULL
        """
    )
    op.execute("DROP TABLE tmp_inspection_project_status_rows")
    op.drop_column('inspections', 'project_status_id')
    op.drop_column('inspections_version', 'project_status_id')
    op.drop_column('inspections_version', 'project_status_id_mod')


def downgrade():
    op.add_column('inspections', sa.Column('project_status_id', sa.Integer(), nullable=True))
    op.add_column('inspections_version', sa.Column('project_status_id', sa.Integer(), nullable=True))
    op.add_column(
        'inspections_version',
        sa.Column('project_status_id_mod', sa.Boolean(), server_default=sa.text('false'), nullable=False)
    )
    op.execute(
        """
        UPDATE inspections
        SET project_status_id = statuses.project_status_id
        FROM (
            SELECT DISTINCT ON (project_statuses.inspection_id)
                project_statuses.inspection_id,
                project_statuses.project_status_id
            FROM inspection_project_statuses project_statuses
            JOIN inspections ON inspections.id = project_statuses.inspection_id
            WHERE project_statuses.is_deleted IS FALSE OR inspections.is_deleted
            ORDER BY project_statuses.inspection_id, project_statuses.is_deleted,
                     project_statuses.created_date DESC, project_statuses.id DESC
        ) AS statuses
        WHERE inspections.id = statuses.inspection_id
        """
    )
    op.execute(
        """
        UPDATE inspections_version
        SET project_status_id = (
                SELECT CASE
                    WHEN status_versions.is_deleted
                        AND NOT inspections_version.is_deleted
                        AND inspections_version.operation_type <> 2 THEN NULL
                    ELSE status_versions.project_status_id
                END
                FROM inspection_project_statuses_version status_versions
                WHERE status_versions.inspection_id = inspections_version.id
                  AND status_versions.transaction_id <= inspections_version.transaction_id
                ORDER BY status_versions.transaction_id DESC,
                         status_versions.is_deleted ASC,
                         status_versions.id DESC
                LIMIT 1
            ),
            project_status_id_mod = EXISTS (
                SELECT 1
                FROM inspection_project_statuses_version status_versions
                WHERE status_versions.inspection_id = inspections_version.id
                  AND status_versions.transaction_id = inspections_version.transaction_id
            )
        """
    )
    op.drop_index(
        op.f('ix_inspection_project_statuses_version_transaction_id'),
        table_name='inspection_project_statuses_version'
    )
    op.drop_index(
        op.f('ix_inspection_project_statuses_version_operation_type'),
        table_name='inspection_project_statuses_version'
    )
    op.drop_index(
        op.f('ix_inspection_project_statuses_version_end_transaction_id'),
        table_name='inspection_project_statuses_version'
    )
    op.drop_table('inspection_project_statuses_version')
    op.drop_table('inspection_project_statuses')
