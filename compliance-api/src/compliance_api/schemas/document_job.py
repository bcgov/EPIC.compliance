"""Document Job Schema."""

from marshmallow import EXCLUDE, fields

from compliance_api.models.document_job import DocumentJob

from .base_schema import AutoSchemaBase, BaseSchema


class DocumentJobSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Document Job Schema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = DocumentJob
        include_fk = True


class DocumentJobUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Document Job Update Schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    status = fields.Str(
        metadata={"description": "The status of the document job"},
        allow_none=False,
        required=False
    )
