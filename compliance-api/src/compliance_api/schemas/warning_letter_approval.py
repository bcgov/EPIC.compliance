"""Schema for WarningLetter Approval."""

from marshmallow import EXCLUDE, ValidationError, fields, post_dump, post_load
from marshmallow_enum import EnumField

from compliance_api.models.warning_letter_approval import WarningLetterApproval as WarningLetterApprovalModel
from compliance_api.models.warning_letter_approval import WarningLetterApprovalStatusEnum

from .base_schema import AutoSchemaBase, BaseSchema
from .staff_user import StaffUserSchema


class WarningLetterApprovalSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """WarningLetterApprovalSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = WarningLetterApprovalModel
        include_fk = True

    approved_by = fields.Nested(StaffUserSchema)

    @post_dump
    def convert_enum_to_key_value(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Convert enum to key value schema."""
        if (
            "warning_letter_status" in data
            and data["warning_letter_status"] is not None
        ):
            data["warning_letter_status"] = {
                "id": data["warning_letter_status"].name,
                "name": data["warning_letter_status"].value,
            }
        if "approval_status" in data and data["approval_status"] is not None:
            data["approval_status"] = {
                "id": data["approval_status"].name,
                "name": data["approval_status"].value,
            }
        return data


class CreateWarningLetterApprovalSchema(BaseSchema):
    """Schema for updating an WarningLetterApproval."""

    approved_by_id = fields.Integer(
        metadata={"description": "The unique id of the staff who needs to approve"},
        allow_none=True,
    )


class UpdateWarningLetterApprovalStatusSchema(BaseSchema):
    """Schema for updating the status of an WarningLetterApproval."""

    approval_status = EnumField(WarningLetterApprovalStatusEnum, by_value=False)
    approved_by_id = fields.Integer(
        metadata={"description": "The unique id of the staff who needs to approve"},
        required=True,
    )

    @post_load
    def validate_fields(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Perform custom validation for allowed fields."""
        status = data["approval_status"]
        if status == WarningLetterApprovalStatusEnum.APPROVAL_PENDING:
            raise ValidationError(f"Invalid status: {status}")

        return data
