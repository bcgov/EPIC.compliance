"""Pagination schema."""

from marshmallow import fields
from marshmallow.validate import Range

from compliance_api.utils.constant import MAX_PAGE_SIZE

from .base_schema import BaseSchema


class PaginationParameterSchema(BaseSchema):
    """PaginationParameterSchema."""

    page_no = fields.Int(
        metadata={"description": "The current page to be returned."},
        missing=1,
        validate=Range(min=1),
    )
    page_size = fields.Int(
        metadata={
            "description": f"The total number of items per page (max {MAX_PAGE_SIZE})."
        },
        missing=10,
        validate=Range(min=1, max=MAX_PAGE_SIZE),
    )
