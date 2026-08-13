"""Remove orphaned enforcement action requirement maps

Requirement/enforcement action mappings were left behind when the enforcement
action of a requirement was changed while a drafting document existed. The
document itself was deleted but its mapping stayed active.

Revision ID: b1d4c9e77a02
Revises: d4e8a1c37b92
Create Date: 2026-08-13 10:49:39.349614

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b1d4c9e77a02'
down_revision = 'd4e8a1c37b92'
branch_labels = None
depends_on = None


ORPHANED_MAP_TABLES = [
    ("order_inspection_requirement_maps", "order_id", "orders"),
    (
        "warning_letter_inspection_requirement_maps",
        "warning_letter_id",
        "warning_letters",
    ),
    (
        "violation_ticket_inspection_requirement_maps",
        "violation_ticket_id",
        "violation_tickets",
    ),
    (
        "administrative_penalty_inspection_requirement_maps",
        "administrative_penalty_id",
        "administrative_penalties",
    ),
    (
        "charge_recommendation_inspection_requirement_maps",
        "charge_recommendation_id",
        "charge_recommendations",
    ),
    (
        "restorative_justice_inspection_requirement_maps",
        "restorative_justice_id",
        "restorative_justices",
    ),
]


def upgrade():
    for map_table, foreign_key, action_table in ORPHANED_MAP_TABLES:
        op.execute(
            f"""
            UPDATE {map_table} AS map_table
            SET is_active = false, is_deleted = true
            FROM {action_table} AS action_table
            WHERE action_table.id = map_table.{foreign_key}
              AND map_table.is_deleted = false
              AND (action_table.is_deleted = true OR action_table.is_active = false)
            """
        )


def downgrade():
    pass
