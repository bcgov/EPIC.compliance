"""Schema for Order Approval."""

from marshmallow import EXCLUDE, ValidationError, fields, post_dump, post_load
from marshmallow_enum import EnumField

from compliance_api.models.order_approval import OrderApproval as OrderApprovalModel
from compliance_api.models.order_approval import OrderApprovalStatusEnum

from .base_schema import AutoSchemaBase, BaseSchema
from .staff_user import StaffUserSchema


class OrderApprovalSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """OrderApprovalSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = OrderApprovalModel
        include_fk = True

    approved_by = fields.Nested(StaffUserSchema)

    @post_dump
    def convert_enum_to_key_value(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Convert enum to key value schema."""
        if "order_status" in data and data["order_status"] is not None:
            data["order_status"] = {
                "id": data["order_status"].name,
                "name": data["order_status"].value,
            }
        if "approval_status" in data and data["approval_status"] is not None:
            data["approval_status"] = {
                "id": data["approval_status"].name,
                "name": data["approval_status"].value,
            }
        return data


class CreateOrderApprovalSchema(BaseSchema):
    """Schema for updating an OrderApproval."""

    approved_by_id = fields.Integer(
        metadata={"description": "The unique id of the staff who needs to approve"},
        allow_none=True,
    )


class UpdateOrderApprovalStatusSchema(BaseSchema):
    """Schema for updating the status of an OrderApproval."""

    approval_status = EnumField(OrderApprovalStatusEnum, by_value=False)
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
        if status == OrderApprovalStatusEnum.APPROVAL_PENDING:
            raise ValidationError(f"Invalid status: {status}")

        return data
