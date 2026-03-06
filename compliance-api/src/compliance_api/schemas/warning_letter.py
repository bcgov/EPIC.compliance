"""Warning Letter Schemas."""

from marshmallow import EXCLUDE, fields, post_dump, post_load, validate
from marshmallow_enum import EnumField

from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from ..models.warning_letter import WarningLetter, WarningLetterInspectionRequirementMap, WarningLetterStatusEnum
from .base_schema import AutoSchemaBase, BaseSchema
from .inspection_requirement import InspectionRequirementSchema
from .staff_user import StaffUserSchema
from .warning_letter_approval import WarningLetterApprovalSchema


class WarningLetterUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Schema for warning letter model."""

    inspection_id = fields.Integer(
        required=True, metadata={"description": "The inspection id"}
    )
    issuing_officer_id = fields.Integer(
        allow_none=True, metadata={"description": "The issuing officer id"}
    )
    intended_issuance_date = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The intended issuance date"},
    )
    content = fields.String(allow_none=True, metadata={"description": "The content"})
    inspection_requirement_ids = fields.List(
        fields.Integer(),
        required=True,
        metadata={
            "description": "List of inspection requirement IDs associated with the order."
        },
    )


class WarningLetterCreateSchema(
    WarningLetterUpdateSchema
):  # pylint: disable=too-many-ancestors
    """Schema for warning letter model."""

    warning_letter_number = fields.String(
        allow_none=True, metadata={"description": "The unique warning letter number."}
    )


class WarningLetterInspectionRequirementMapSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """Schema for warning letter inspection requirement map model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = WarningLetterInspectionRequirementMap
        include_fk = True

    inspection_requirement = fields.Nested(
        InspectionRequirementSchema(),
        only=("id", "summary", "requirement_source_details"),
    )


class WarningLetterSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for warning letter model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = WarningLetter
        include_fk = True

    issuing_officer = fields.Nested(
        StaffUserSchema(),
        only=("id", "first_name", "last_name", "name", "auth_user_guid"),
    )
    warning_letter_requirement_maps = fields.Nested(
        WarningLetterInspectionRequirementMapSchema(),
        many=True,
        only=("id", "inspection_requirement_id", "inspection_requirement"),
    )
    warning_letter_approvals = fields.Nested(
        WarningLetterApprovalSchema(),
        many=True,
        only=(
            "id",
            "warning_letter_id",
            "approved_by_id",
            "warning_letter_status",
            "approval_status",
            "approved_date",
            "created_date",
            "approved_by",
        ),
    )

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the inspection status enum."""
        if "progress" in data and data["progress"] is not None:
            data["progress"] = {
                "id": data["progress"].name,
                "name": data["progress"].value,
            }
        if "status" in data and data["status"] is not None:
            data["status"] = {
                "id": data["status"].name,
                "name": data["status"].value,
            }
        return data


class WarningLetterStatusSchema(BaseSchema):
    """WarningLetterStatusSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    status = EnumField(
        WarningLetterStatusEnum,
        metadata={"description": "The status of the warning letter"},
        required=True,
    )

    @post_load
    def extract_status_value(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the status enum."""
        status_enum = data.get("status")
        if status_enum:
            data["status"] = status_enum.value
        return data


class WarningLetterIssueSchema(BaseSchema):
    """WarningLetterIssueSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    date_issued = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The date the warning letter was issued"},
    )


class ResetWarningLetterFieldSchema(BaseSchema):
    """Schema for resetting warning letter fields."""

    field_name = fields.Str(
        required=True,
        validate=validate.OneOf(["content"]),
    )
