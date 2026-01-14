"""Schema for Inspection Record."""

from marshmallow import EXCLUDE, ValidationError, fields, post_dump, post_load, validate
from marshmallow_enum import EnumField

from compliance_api.models.inspection_record import InspectionRecord as InspectionRecordModel
from compliance_api.models.inspection_record import IRProgressEnum, IRStatusEnum
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from .base_schema import AutoSchemaBase, BaseSchema
from .common import KeyValueSchema
from .inspection import InspectionSchema
from .staff_user import StaffUserSchema


class InspectionRecordCreateSchema(BaseSchema):
    """Inspection Record Create Schema."""

    ir_status = EnumField(
        IRStatusEnum,
        metadata={"description": "The status of the IR to be generated"},
        required=True,
        by_value=True,
    )


class InspectionRecordSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """InspectionRecordSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionRecordModel
        include_fk = True

    inspection = fields.Nested(InspectionSchema)
    ir_status = fields.Nested(KeyValueSchema)
    record_prepared_by = fields.Nested(
        StaffUserSchema,
        only=("id", "first_name", "last_name", "name", "auth_user_guid", "position"),
    )
    record_prepared_by_position = fields.Nested(KeyValueSchema, dump_only=True)

    @post_dump(pass_original=True)
    def post_dump_actions(self, data, original, many, **kwargs):  # pylint: disable=no-self-use, unused-argument
        """Post dump actions."""
        if "ir_progress" in data and data["ir_progress"] is not None:
            data["ir_progress"] = {
                "id": data["ir_progress"].name,
                "name": data["ir_progress"].value,
            }
        else:
            data["ir_progress"] = ""
        data["is_open_for_editing"] = getattr(original, "is_open_for_editing", False)
        return data


class UpdateInspectionRecordSchema(BaseSchema):
    """Schema for updating selected fields of an InspectionRecord."""

    field_name = fields.Str(required=True, validate=validate.Length(min=1))
    value = fields.Raw(required=True)  # Allows various types of input

    @post_load
    def validate_fields(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Perform custom validation for allowed fields."""
        allowed_fields = {
            "mailing_address": fields.Str(validate=validate.Length(max=255)),
            "inspection_scope": fields.Str(),
            "preliminary_review_details": fields.Str(),
            "finding_statement": fields.Str(),
            "enforcement_summary": fields.Str(),
            "action_required_by_rp": fields.Str(),
            "record_prepared_by_id": fields.Int(),
            "record_prepared_by_position_id": fields.Int(),
            "ir_progress": EnumField(IRProgressEnum, by_value=False),
            "date_issued": fields.DateTime(
                format=INPUT_DATE_TIME_FORMAT,
                metadata={
                    "description": "Inspection record issued date in ISO 8601 format."
                },
                required=True,
                error_messages={
                    "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
                },
            ),
            "intended_issuance_date": fields.DateTime(
                format=INPUT_DATE_TIME_FORMAT,
                metadata={"description": "Intended issuance date in ISO 8601 format."},
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


class ResetInspectionRecordFieldSchema(BaseSchema):
    """Schema for resetting a field in InspectionRecord."""

    field_name = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "inspection_scope",
                "preliminary_review_details",
                "finding_statement",
                "enforcement_summary",
                "date_issued",
            ]
        ),
        metadata={"description": "The field to reset"},
    )
