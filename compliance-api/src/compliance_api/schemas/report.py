"""Schema for report generation parameters."""
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from compliance_api.models.report_enum import ReportTypeEnum


class ReportGenerationSchema(Schema):
    """Schema to filter the case files for export and pagination."""

    report_type = EnumField(
        ReportTypeEnum,
        metadata={"description": "Type of report to generate"},
        by_value=True,
        required=True,
    )

    project_id = fields.Int(
        required=False,
        allow_none=True,
        metadata={"description": "Project ID for report"},
    )

    officer_ids = fields.List(
        fields.Int(),
        required=False,
        allow_none=True,
        metadata={"description": "List of officer IDs for report"},
    )

    first_nation_id = fields.Int(
        required=False,
        allow_none=True,
        metadata={"description": "First Nation Alliance ID for report"},
    )

    start_date = fields.DateTime(
        required=False,
        allow_none=True,
        metadata={"description": "Start date for report"},
    )

    end_date = fields.DateTime(
        required=False,
        allow_none=True,
        metadata={"description": "End date for report"},
    )
