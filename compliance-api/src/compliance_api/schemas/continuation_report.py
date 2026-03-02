"""Schema of continuation report."""

from datetime import datetime, timedelta

from marshmallow import EXCLUDE, ValidationError, fields, post_dump, validates
from marshmallow_enum import EnumField

from compliance_api.models.continuation_report import ContinuationReport, ContinuationReportKey
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT
from compliance_api.utils.enum import ContextEnum

from .base_schema import AutoSchemaBase, BaseSchema
from .paginate import PaginationParameterSchema
from .staff_user import StaffUserSchema


class ContinuationReportKeyCreateSchema(
    BaseSchema
):  # pylint: disable=too-many-ancestors
    """ContinuationReportKeyCreateSchema."""

    key = fields.Str(
        metadata={
            "description": "The key in the report entry content which needs to be a hyperlink"
        },
    )
    key_context = EnumField(
        ContextEnum,
        metadata={
            "description": "The context in which the entry is being made. Eg: When an Inspection is created."
        },
        by_value=True,
        required=True,
    )


class ContinuationReportKeySchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """ContinuationReportKeySchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = ContinuationReportKey

    key_context = EnumField(
        ContextEnum,
        metadata={
            "description": "The context in which the entry is being made. Eg: When an Inspection is created."
        },
        by_value=True,
    )

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of key_context enum."""
        if "key_context" in data and data["key_context"] is not None:
            data["key_context"] = ContextEnum(data["key_context"]).value
        else:
            data["key_context"] = ""
        return data


class ContinuationReportSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """ContinuationReportSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = ContinuationReport
        include_fk = True

    keys = fields.List(fields.Nested(ContinuationReportKeySchema))
    context_type = EnumField(
        ContextEnum,
        metadata={
            "description": "The context in which the entry is being made. Eg: When an Inspection is created."
        },
        by_value=True,
    )
    created_by_user = fields.Nested(StaffUserSchema)

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of context enum."""
        if "context_type" in data and data["context_type"] is not None:
            data["context_type"] = ContextEnum(data["context_type"]).value
        else:
            data["context_type"] = ""
        return data


class ContinuationReportUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """ContinuationReportUpdateSchema."""

    text = fields.Str(
        metadata={"description": "The content in plane text format"},
        allow_none=True,
        required=True,
    )
    rich_text = fields.Str(
        metadata={"description": "The content in html formatted"},
        allow_none=True,
        required=True,
    )
    date_created = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        metadata={
            "description": "The continuation report entry date in ISO 8601 format."
        },
        required=True,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
    )

    @validates("date_created")
    def validate_date_created(self, value):  # pylint: disable=no-self-use
        """Validate that date_created is not later than current date + 1."""
        current_date_plus_one = datetime.utcnow() + timedelta(days=1)
        if value > current_date_plus_one:
            raise ValidationError(
                f"date_created must not be later than {current_date_plus_one.strftime(INPUT_DATE_TIME_FORMAT)}."
            )


class ContinuationReportCreateSchema(
    ContinuationReportUpdateSchema
):  # pylint: disable=too-many-ancestors
    """ContinuationReportCreateSchema."""

    case_file_id = fields.Int(
        metadata={"description": "The unique identifier of the associated case file."},
        required=True,
    )
    context_type = EnumField(
        ContextEnum,
        metadata={
            "description": "The context in which the entry is being made. Eg: When an Inspection is created."
        },
        by_value=True,
        required=True,
    )
    context_id = fields.Int(
        metadata={"description": "The unique identifier of the context type entity"},
        required=True,
    )


class CRGetQueryParamSchema(PaginationParameterSchema):
    """Query parameter for the CR query."""

    case_file_id = fields.Int(
        metadata={"description": "The case file id."}, required=True
    )
    search_text = fields.Str(metadata={"description": "The text to be searched"})


class CRExport(BaseSchema):
    """Query parameter for the CR query."""

    case_file_number = fields.String(
        metadata={"description": "The case file number."}, required=False
    )

    inspection_number = fields.String(
        metadata={"description": "The inspection number."}, required=False
    )
