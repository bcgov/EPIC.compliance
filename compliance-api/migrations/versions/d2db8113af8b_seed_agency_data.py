"""see agency data

Revision ID: d2db8113af8b
Revises: 31ce9015c9b0
Create Date: 2024-10-23 15:24:10.938966
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2db8113af8b'
down_revision = '31ce9015c9b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(sa.text("TRUNCATE agencies RESTART IDENTITY CASCADE"))
    agencies = [
        {
            "name": "BC Energy Regulator",
            "abbreviation": "BCER"
        },
        {
            "name": "Canada Energy Regulator",
            "abbreviation": "CER"
        },
        {
            "name": "Education Dept",
            "abbreviation": "ED"
        },
        {
            "name": "Environment and Climate Change Canada",
            "abbreviation": "ECC"
        },
        {
            "name": "Fisheries and Oceans Canada",
            "abbreviation": "DFO"
        },
        {
            "name": "Impact Assessment Agency of Canada",
            "abbreviation": "IAAC"
        }
    ]

    # Add your insertion logic here (e.g., inserting into an 'agencies' table).
    for agency in agencies:
        op.execute(
            f"""
            INSERT INTO agencies (name, abbreviation,created_date, created_by)
            VALUES ('{agency["name"]}', '{agency["abbreviation"]}',now() at time zone 'utc', 'system')
            """
        )
    op.execute("UPDATE inspection_attendance_options SET sort_order=8 WHERE sort_order=8")
    op.execute("INSERT INTO inspection_attendance_options(id, name, sort_order, created_by, created_date)VALUES(8, 'Attending Officers', 7, 'system',now() at time zone 'utc')")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(sa.text("TRUNCATE agencies RESTART IDENTITY CASCADE"))
    op.execute("UPDATE inspection_attendance_options SET sort_order=7 WHERE sort_order=8")
    op.execute("DELETE from inspection_attendance_options WHERE name='Attending Officers'")
    # ### end Alembic commands ###
