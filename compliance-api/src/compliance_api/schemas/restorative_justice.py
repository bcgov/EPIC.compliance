"""Restorative Justice Schemas."""

from marshmallow import fields, post_dump

from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from ..models.restorative_justice import (
    RestorativeJustice, RestorativeJusticeInspectionRequirementMap, RestorativeJusticeStatusEnum)
from .base_schema import AutoSchemaBase, BaseSchema
from .inspection_requirement import InspectionRequirementSchema


class RestorativeJusticeUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Schema for restorative justice model."""

    inspection_id = fields.Integer(
        required=True, metadata={"description": "The inspection id"}
    )
    restitution_details = fields.String(
        allow_none=True,
        metadata={"description": "Restitution details"},
    )
    date_restitution_complete = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The date when restitution was completed"},
    )
    inspection_requirement_ids = fields.List(
        fields.Integer(),
        allow_none=True,
        metadata={"description": "List of inspection requirement IDs"},
    )


class RestorativeJusticeCreateSchema(
    RestorativeJusticeUpdateSchema
):  # pylint: disable=too-many-ancestors
    """Schema for restorative justice model."""

    restorative_justice_number = fields.String(
        allow_none=True,
        metadata={"description": "The unique restorative justice number."},
    )


class RestorativeJusticeInspectionRequirementMapSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """Schema for restorative justice inspection requirement map model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to auto generate schema."""

        model = RestorativeJusticeInspectionRequirementMap
        load_instance = True
        include_fk = True

    inspection_requirement = fields.Nested(
        InspectionRequirementSchema(),
        only=("id", "summary"),
    )

    inspection_requirement_id = fields.Integer()


class RestorativeJusticeSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for restorative justice model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to auto generate schema."""

        model = RestorativeJustice
        load_instance = True
        include_fk = True

    restitution_details = fields.String(
        allow_none=True,
        metadata={"description": "Restitution details"},
    )
    restorative_justice_requirement_maps = fields.Nested(
        RestorativeJusticeInspectionRequirementMapSchema(),
        many=True,
        only=("id", "inspection_requirement_id", "inspection_requirement"),
    )

    @post_dump(pass_many=True)
    def transform_data(self, data, many, **kwargs):  # pylint: disable=unused-argument
        """Transform data after serialization."""
        if many:
            for item in data:
                self._transform_single_item(item)
        else:
            self._transform_single_item(data)
        return data

    def _transform_single_item(self, item):  # pylint: disable=no-self-use
        """Transform a single item."""
        # Transform enum values to their string representation
        if "status" in item and item["status"]:
            item["status"] = {
                "id": RestorativeJusticeStatusEnum(item["status"]).name,
                "name": RestorativeJusticeStatusEnum(item["status"]).value,
            }
