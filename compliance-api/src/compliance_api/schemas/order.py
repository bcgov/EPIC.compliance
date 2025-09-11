"""Order Schemas."""

from marshmallow import EXCLUDE, fields, post_dump, post_load, validate
from marshmallow_enum import EnumField

from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from ..models.order import Order, OrderInspectionRequirementMap, OrderStatusEnum
from .base_schema import AutoSchemaBase, BaseSchema
from .inspection_requirement import InspectionRequirementSchema
from .order_approval import OrderApprovalSchema
from .section import SectionSchema
from .staff_user import StaffUserSchema


class OrderUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Schema for order model."""

    inspection_id = fields.Integer(
        required=True, metadata={"description": "The inspection id"}
    )
    section_id = fields.Integer(
        allow_none=True, metadata={"description": "The section id"}
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
    where_as = fields.String(allow_none=True, metadata={"description": "The where as"})
    now_therefore = fields.String(
        allow_none=True, metadata={"description": "The now therefore"}
    )
    inspection_requirement_ids = fields.List(
        fields.Integer(),
        required=True,
        validate=validate.Length(
            min=1, error="At least one inspection requirement ID is required."
        ),
        metadata={
            "description": "List of inspection requirement IDs associated with the order."
        },
    )


class OrderCreateSchema(OrderUpdateSchema):  # pylint: disable=too-many-ancestors
    """Schema for order model."""

    order_number = fields.String(
        allow_none=True, metadata={"description": "The unique order number."}
    )


class OrderInspectionRequirementMapSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """Schema for order inspection requirement map model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = OrderInspectionRequirementMap
        include_fk = True

    inspection_requirement = fields.Nested(
        InspectionRequirementSchema(),
        only=("id", "summary"),
    )


class OrderSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for order model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = Order
        include_fk = True

    issuing_officer = fields.Nested(
        StaffUserSchema(),
        only=("id", "first_name", "last_name", "name", "auth_user_guid"),
    )
    section = fields.Nested(SectionSchema, only=("id", "name"))
    order_requirement_maps = fields.Nested(
        OrderInspectionRequirementMapSchema(),
        many=True,
        only=("id", "inspection_requirement_id", "inspection_requirement"),
    )
    order_approvals = fields.Nested(
        OrderApprovalSchema(),
        many=True,
        only=(
            "id",
            "order_id",
            "approved_by_id",
            "order_status",
            "approval_status",
            "approved_date",
            "created_date",
            "approved_by",
        ),
    )

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of the inspection status enum."""
        if "order_status" in data and data["order_status"] is not None:
            data["order_status"] = {
                "id": data["order_status"].name,
                "name": data["order_status"].value,
            }
        if "order_progress" in data and data["order_progress"] is not None:
            data["order_progress"] = {
                "id": data["order_progress"].name,
                "name": data["order_progress"].value,
            }
        if "order_replace_status" in data and data["order_replace_status"] is not None:
            data["order_replace_status"] = {
                "id": data["order_replace_status"].name,
                "name": data["order_replace_status"].value,
            }
        return data


class OrderStatusSchema(BaseSchema):
    """OrderStatusSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    status = EnumField(
        OrderStatusEnum,
        metadata={"description": "The status of the order"},
        required=True,
    )

    @post_load
    def extract_status_value(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of the status enum."""
        status_enum = data.get("status")
        if status_enum:
            data["status"] = status_enum.value
        return data


class OrderIssueSchema(BaseSchema):
    """OrderIssueSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    date_issued = fields.DateTime(
        required=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The date the order was issued"},
    )


class ResetOrderFieldSchema(BaseSchema):
    """Schema for validating fields that can be reset in orders."""

    field_names = fields.List(
        fields.Str(
            validate=validate.OneOf(
                [
                    "where_as",
                    "now_therefore",
                ]
            ),
            metadata={"description": "The name of the field to reset"},
        )
    )


class OrderReplaceSchema(BaseSchema):
    """Schema for order replacement."""

    replacement_order_number = fields.String(
        allow_none=True,
        metadata={
            "description": "The order number for the replacement order. "
            "If not provided, a new number will be generated."
        },
    )
