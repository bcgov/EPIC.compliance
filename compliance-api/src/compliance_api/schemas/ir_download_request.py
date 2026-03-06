"""Schema for IR Download Request."""

from marshmallow import EXCLUDE, fields, post_dump

from compliance_api.models.ir_download_request import IRDownloadRequest as IRDownloadRequestModel
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from .base_schema import AutoSchemaBase, BaseSchema


class IRDownloadRequestSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """IRDownloadRequestSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = IRDownloadRequestModel
        include_fk = True

    generated_timestamp = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT, allow_none=True
    )

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the download status enum."""
        if "download_status" in data and data["download_status"] is not None:
            data["download_status"] = {
                "id": data["download_status"].name,
                "name": data["download_status"].value,
            }
        else:
            data["download_status"] = ""
        return data


class CreateIRDownloadRequestSchema(BaseSchema):
    """Schema for creating an IR Download Request."""

    # No additional fields needed for creation
    # inspection_record_id comes from URL path
    # staff_id comes from user context


class IRDownloadRequestQuerySchema(BaseSchema):
    """Schema for querying IR Download Request."""

    created_by = fields.Str(
        required=True,
        metadata={"description": "Staff ID (GUID) of the user who created the request"},
    )
