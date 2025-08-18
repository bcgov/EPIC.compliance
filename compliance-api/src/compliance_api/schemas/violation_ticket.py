"""ViolationTicket Schemas."""

from marshmallow import EXCLUDE, fields, post_dump, post_load, validate
from marshmallow_enum import EnumField

from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from ..models.violation_ticket import (
    ViolationTicket, ViolationTicketInspectionRequirementMap, ViolationTicketStatusEnum)
from .base_schema import AutoSchemaBase, BaseSchema
from .inspection_requirement import InspectionRequirementSchema
from .staff_user import StaffUserSchema


class ViolationTicketCreateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Schema for violation ticket model."""

    inspection_id = fields.Integer(
        required=True, metadata={"description": "The inspection id"}
    )
    ticket_number = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "The manual ticket number"},
    )
    inspection_requirement_ids = fields.List(
        fields.Integer(),
        required=True,
        metadata={
            "description": "List of inspection requirement IDs associated with the violation ticket."
        },
    )


class ViolationTicketUpdateSchema(ViolationTicketCreateSchema):  # pylint: disable=too-many-ancestors
    """Schema for violation ticket model."""

    date_issued = fields.DateTime(
        required=False,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The date the ticket was issued"},
    )

    fine_amount = fields.Decimal(
        required=False,
        places=2,
        validate=validate.Range(min=0),
        metadata={"description": "The fine amount"},
    )
    status = EnumField(
        ViolationTicketStatusEnum,
        required=True,
        metadata={"description": "The status of the violation ticket"},
        by_value=False,
    )
    status_date = fields.DateTime(
        required=False,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The status date"},
    )


class ViolationTicketInspectionRequirementMapSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """Schema for violation ticket inspection requirement map model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta class."""

        model = ViolationTicketInspectionRequirementMap
        unknown = EXCLUDE
        include_fk = True

    inspection_requirement = fields.Nested(
        InspectionRequirementSchema(),
        only=("id", "summary"),
    )


class ViolationTicketSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for violation ticket model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta class."""

        model = ViolationTicket
        unknown = EXCLUDE
        include_fk = True

    created_by = fields.Nested(
        StaffUserSchema(),
        only=("id", "first_name", "last_name", "name", "auth_user_guid"),
    )
    fine_amount = fields.Str(
        metadata={"description": "The fine amount"},
    )
    violation_ticket_requirement_maps = fields.Nested(
        ViolationTicketInspectionRequirementMapSchema(),
        many=True,
        only=("id", "inspection_requirement_id", "inspection_requirement"),
    )
    status = fields.Raw()

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Convert the violation ticket status enum to KeyValueSchema format."""
        if "status" in data and data["status"] is not None:
            if not isinstance(data["status"], dict):
                data["status"] = {
                    "id": ViolationTicketStatusEnum(data["status"]).name,
                    "name": ViolationTicketStatusEnum(data["status"]).value,
                }
        return data


class ViolationTicketStatusSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """ViolationTicketStatusSchema."""

    status = EnumField(
        ViolationTicketStatusEnum,
        metadata={"description": "The status of the violation ticket"},
        required=True,
    )

    @post_load
    def extract_status_value(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument,no-self-use
        """Extract the value of the status enum."""
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
        return data
