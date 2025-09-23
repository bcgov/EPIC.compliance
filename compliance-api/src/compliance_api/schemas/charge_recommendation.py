"""Charge Recommendation Schemas."""

from marshmallow import EXCLUDE, fields, post_dump
from marshmallow_enum import EnumField

from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from ..models.charge_recommendation import (
    ChargeDecisionEnum, ChargeRecommendation, ChargeRecommendationInspectionRequirementMap,
    ChargeRecommendationStatusEnum, JudgmentEnum)
from .base_schema import AutoSchemaBase, BaseSchema
from .inspection_requirement import InspectionRequirementSchema


class ChargeRecommendationUpdateSchema(
    BaseSchema
):  # pylint: disable=too-many-ancestors
    """Schema for charge recommendation model."""

    inspection_id = fields.Integer(
        required=True, metadata={"description": "The inspection id"}
    )
    status = EnumField(
        ChargeRecommendationStatusEnum,
        by_value=False,
        allow_none=True,
        metadata={"description": "The status of the charge recommendation"},
    )
    date_to_crown_counsel = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The date sent to crown counsel"},
    )
    charge_decision = EnumField(
        ChargeDecisionEnum,
        by_value=False,
        allow_none=True,
        metadata={"description": "The decision on the charge recommendation"},
    )
    charge_decision_date = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The charge decision date"},
    )
    court_file_number = fields.String(
        allow_none=True,
        metadata={"description": "The court file number"},
    )
    court_appearances = fields.String(
        allow_none=True,
        metadata={"description": "Court appearances details"},
    )
    judgment = EnumField(
        JudgmentEnum,
        by_value=False,
        allow_none=True,
        metadata={"description": "The judgment on the charge recommendation"},
    )
    judgment_date = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The judgment date"},
    )
    sentence_date = fields.DateTime(
        allow_none=True,
        format=INPUT_DATE_TIME_FORMAT,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
        metadata={"description": "The sentence date"},
    )
    sentence_type = fields.String(
        allow_none=True,
        metadata={"description": "The type of sentence"},
    )
    inspection_requirement_ids = fields.List(
        fields.Integer(),
        allow_none=True,
        metadata={"description": "List of inspection requirement IDs"},
    )


class ChargeRecommendationCreateSchema(
    ChargeRecommendationUpdateSchema
):  # pylint: disable=too-many-ancestors
    """Schema for charge recommendation model."""

    charge_recommendation_number = fields.String(
        allow_none=True,
        metadata={"description": "The unique charge recommendation number."},
    )


class ChargeRecommendationInspectionRequirementMapSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """Schema for charge recommendation inspection requirement map model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to auto generate schema."""

        unknown = EXCLUDE
        model = ChargeRecommendationInspectionRequirementMap
        include_fk = True

    inspection_requirement = fields.Nested(
        InspectionRequirementSchema(),
        only=("id", "summary"),
    )


class ChargeRecommendationSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for charge recommendation model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to auto generate schema."""

        model = ChargeRecommendation
        load_instance = True
        include_fk = True

    court_appearances = fields.String(
        allow_none=True,
        metadata={"description": "Court appearances details"},
    )
    charge_recommendation_requirement_maps = fields.Nested(
        ChargeRecommendationInspectionRequirementMapSchema(),
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
        # Transform enum values to objects with id and value properties
        if "status" in item and item["status"]:
            item["status"] = {
                "id": ChargeRecommendationStatusEnum(item["status"]).name,
                "name": ChargeRecommendationStatusEnum(item["status"]).value,
            }

        if "charge_decision" in item and item["charge_decision"]:
            item["charge_decision"] = {
                "id": ChargeDecisionEnum(item["charge_decision"]).name,
                "name": ChargeDecisionEnum(item["charge_decision"]).value,
            }

        if "judgment" in item and item["judgment"]:
            item["judgment"] = {
                "id": JudgmentEnum(item["judgment"]).name,
                "name": JudgmentEnum(item["judgment"]).value,
            }
