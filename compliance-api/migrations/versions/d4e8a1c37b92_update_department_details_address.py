"""update department details mailing address

Revision ID: d4e8a1c37b92
Revises: a3f9c1d24b77
Create Date: 2026-08-05 16:05:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd4e8a1c37b92'
down_revision = 'a3f9c1d24b77'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE department_details SET address_line1 = 'PO Box 9347 Stn Prov Govt', "
        "address_line2 = 'Victoria BC  V8W 9M1' "
        "WHERE is_active = true AND is_deleted = false")


def downgrade():
    op.execute(
        "UPDATE department_details SET address_line1 = 'PO Box 9426 Stn Prov Govt', "
        "address_line2 = 'Victoria, BC V8W 9V1' "
        "WHERE is_active = true AND is_deleted = false")
