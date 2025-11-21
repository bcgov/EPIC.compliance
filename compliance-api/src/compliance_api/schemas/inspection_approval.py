"""Schema for Inspection Record Approval."""

from marshmallow import EXCLUDE, ValidationError, fields, post_dump, post_load, validate
from marshmallow_enum import EnumField

from compliance_api.models.inspection_record_approval import InspectionRecordApproval as InspectionRecordApprovalModel
from compliance_api.models.inspection_record_approval import IRApprovalStatusEnum
from compliance_api.schemas.common import KeyValueSchema
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from .base_schema import AutoSchemaBase, BaseSchema
from .staff_user import StaffUserSchema


class InspectionRecordApprovalSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """InspectionRecordApprovalSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionRecordApprovalModel
        include_fk = True

    approved_by = fields.Nested(StaffUserSchema)
    approved_by_position = fields.Nested(KeyValueSchema)

    @post_dump
    def convert_enum_to_key_value(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Convert enum to key value schema."""
        if "approval_status" in data and data["approval_status"] is not None:
            data["approval_status"] = {
                "id": data["approval_status"].name,
                "name": data["approval_status"].value,
            }
        return data


class CreateInspectionRecordApprovalSchema(BaseSchema):
    """Schema for updating an InspectionRecordApproval."""

    approved_by_id = fields.Integer(
        metadata={"description": "The unique id of the staff who needs to approve"},
        allow_none=True,
    )


class UpdateInspectionRecordApprovalStatusSchema(BaseSchema):
    """Schema for updating the status of an InspectionRecordApproval."""

    approval_status = EnumField(IRApprovalStatusEnum, by_value=False)
    approved_by_id = fields.Integer(
        metadata={"description": "The unique id of the staff who needs to approve"},
        required=True,
    )

    @post_load
    def validate_fields(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Perform custom validation for allowed fields."""
        status = data["approval_status"]
        if status == IRApprovalStatusEnum.APPROVAL_PENDING:
            raise ValidationError(f"Invalid status: {status}")

        return data


class UpdateInspectionRecordApprovalSchema(BaseSchema):
    """Schema for updating selected fields of an InspectionRecordApproval."""

    field_name = fields.Str(required=True, validate=validate.Length(min=1))
    value = fields.Str(required=True, allow_none=True)  # Allows various types of input

    @post_load
    def validate_fields(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Perform custom validation for allowed fields."""
        allowed_fields = {
            "date_report_sent": fields.DateTime(
                format=INPUT_DATE_TIME_FORMAT,
                metadata={
                    "description": "The date report sent to proponent in ISO 8601 format."
                },
                required=True,
                error_messages={
                    "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
                },
            ),
            "date_expected_return": fields.DateTime(
                format=INPUT_DATE_TIME_FORMAT,
                metadata={
                    "description": "The date proponent is expected to get back in ISO 8601 format."
                },
                required=True,
                error_messages={
                    "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
                },
            ),
            "date_response": fields.DateTime(
                format=INPUT_DATE_TIME_FORMAT,
                metadata={
                    "description": "The date when the actual response received from proponent in ISO 8601 format."
                },
                required=True,
                error_messages={
                    "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
                },
            ),
        }

        field_name = data["field_name"]
        if field_name not in allowed_fields:
            raise ValidationError(f"Invalid field: {field_name}")

        return data
