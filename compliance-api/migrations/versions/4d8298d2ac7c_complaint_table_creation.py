"""complaint table creation

Revision ID: 4d8298d2ac7c
Revises: fd7af508a4fe
Create Date: 2024-09-12 10:39:59.575107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d8298d2ac7c'
down_revision = 'fd7af508a4fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('complaints',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='The unique identifier of the complaints'),
    sa.Column('case_file_id', sa.Integer(), nullable=False, comment='The unique identifier of the case file associated with the complaint'),
    sa.Column('project_id', sa.Integer(), nullable=True, comment='The unique identifier of the project associated with the complaint'),
    sa.Column('concern_description', sa.String(), nullable=False, comment='The concern description of the complaint'),
    sa.Column('location_description', sa.String(), nullable=True, comment='The location details of the complaint'),
    sa.Column('lead_officer_id', sa.Integer(), nullable=True, comment='The lead officer who created the inspection'),
    sa.Column('date_received', sa.DateTime(timezone=True), nullable=False, comment='The complaint received date'),
    sa.Column('requirement_source_id', sa.Integer(), nullable=False, comment='The selected requirement source of the complaint'),
    sa.Column('source_id', sa.Integer(), nullable=False, comment='The selected source of the complaint'),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=False),
    sa.Column('updated_by', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='t', nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default='f', nullable=False),
    sa.ForeignKeyConstraint(['case_file_id'], ['case_files.id'], name='complaints_case_file_id_case_file_id_fkey'),
    sa.ForeignKeyConstraint(['lead_officer_id'], ['staff_users.id'], name='inspection_lead_officer_id_staff_id_fkey'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='complaints_project_id_projects_id_fkey'),
    sa.ForeignKeyConstraint(['requirement_source_id'], ['complaint_requirement_sources.id'], name='complaints_requirement_source_id_requirement_sources_id'),
    sa.ForeignKeyConstraint(['source_id'], ['complaint_sources.id'], name='complaints_source_id_complaint_sources_id'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('inspection_unapproved_projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('regulated_party', sa.String(), nullable=True, comment='The details of regulated party associated with the project'))
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               nullable=True,
               existing_comment='The description of the project')
        batch_op.alter_column('authorization',
               existing_type=sa.VARCHAR(),
               nullable=True,
               existing_comment='The details of authorization for the project')
        batch_op.drop_column('proponent_name')

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_constraint('projects_abbreviation_key', type_='unique')
        batch_op.drop_column('abbreviation')
        batch_op.drop_column('ea_certificate')
        batch_op.drop_column('proponent_name')
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('proponent_name', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('ea_certificate', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('abbreviation', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
        batch_op.create_unique_constraint('projects_abbreviation_key', ['abbreviation'])

    with op.batch_alter_table('inspection_unapproved_projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('proponent_name', sa.VARCHAR(), autoincrement=False, nullable=False, comment='The details of proponent associated with the project'))
        batch_op.alter_column('authorization',
               existing_type=sa.VARCHAR(),
               nullable=False,
               existing_comment='The details of authorization for the project')
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               nullable=False,
               existing_comment='The description of the project')
        batch_op.drop_column('regulated_party')

    op.drop_table('complaints')
    # ### end Alembic commands ###