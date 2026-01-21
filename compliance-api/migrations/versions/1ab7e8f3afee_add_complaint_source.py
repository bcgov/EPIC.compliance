"""Add First Nations Alliance complaint source and alliance_name in complaints


Revision ID: 1ab7e8f3afee
Revises: df8eb8203cd6
Create Date: 2025-12-03 10:23:15.983007
"""

from alembic import op
from compliance_api.models.type import EncryptedType
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '1ab7e8f3afee'
down_revision = 'df8eb8203cd6'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Shift existing sort orders for Agency and Other
    op.execute("""
        UPDATE complaint_sources
        SET sort_order = sort_order + 1
        WHERE name IN ('Agency', 'Other');
    """)
    # 2. Insert the new complaint source at sort_order = 3
    insert_statement = sa.text("""
        INSERT INTO complaint_sources (
            name,
            sort_order,
            created_date,
            created_by,
            is_active,
            is_deleted
        )
        VALUES (
            :name,
            :sort_order,
            :created_date,
            :created_by,
            :is_active,
            :is_deleted
        )
    """).bindparams(
        name="First Nations Alliance",
        sort_order=3,
        created_date=datetime.utcnow(),
        created_by="system",
        is_active=True,
        is_deleted=False
    )

    op.execute(insert_statement)

        # Add title column to version table
    with op.batch_alter_table("complaint_source_contacts_version", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "alliance_name",
                EncryptedType(),
                nullable=True,
                comment="The alliance name of the First Nations alliance contact",
            )
        )
        batch_op.add_column(
            sa.Column(
                "alliance_name_mod",
                sa.Boolean(),
                nullable=True,
                comment="Modification flag for alliance_name field",
            )
        )

    # Add alliance_name column (VARCHAR, nullable)
    op.add_column(
        "complaint_source_contacts",
        sa.Column("alliance_name", sa.String(), nullable=True)
    )


def downgrade():
    # Remove alliance_name column
    op.drop_column("complaint_source_contacts", "alliance_name")
    op.drop_column("complaint_source_contacts_version", "alliance_name")
    op.drop_column("complaint_source_contacts_version", "alliance_name_mod")
    # Remove the inserted row
    op.execute("""
        DELETE FROM complaint_sources
        WHERE name = 'First Nations Alliance';
    """)

    # Shift Agency and Other back to original sort orders
    op.execute("""
        UPDATE complaint_sources
        SET sort_order = sort_order - 1
        WHERE name IN ('Agency', 'Other');
    """)


