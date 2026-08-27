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
    #  Carry the single project status of every existing inspection over to the new table
    op.execute(
        """
        INSERT INTO inspection_project_statuses
            (project_status_id, inspection_id, created_date, created_by, is_active, is_deleted)
        SELECT project_status_id, id, now() at time zone 'utc', 'system', is_active, is_deleted
        FROM inspections
        WHERE project_status_id IS NOT NULL
        """
    )
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
    #  Only a single status can be kept when rolling back
    op.execute(
        """
        UPDATE inspections
        SET project_status_id = statuses.project_status_id
        FROM (
            SELECT DISTINCT ON (inspection_id) inspection_id, project_status_id
            FROM inspection_project_statuses
            WHERE is_deleted IS FALSE
            ORDER BY inspection_id, id
        ) AS statuses
        WHERE inspections.id = statuses.inspection_id
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
