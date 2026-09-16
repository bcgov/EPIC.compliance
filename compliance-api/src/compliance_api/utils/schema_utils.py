"""Schema utility functions for common schema patterns."""

from compliance_api.utils.constant import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


def get_pagination_schema(default_sort_by="id"):
    """Get a reusable pagination schema dictionary.

    Args:
        default_sort_by (str): The default field to sort by

    Returns:
        dict: Pagination schema parameters
    """
    return {
        "page_no": {
            "description": "Page number for pagination",
            "type": "integer",
            "required": False,
            "default": 1,
        },
        "page_size": {
            "description": f"Number of items per page (max {MAX_PAGE_SIZE})",
            "type": "integer",
            "required": False,
            "default": DEFAULT_PAGE_SIZE,
            "maximum": MAX_PAGE_SIZE,
        },
        "sort_by": {
            "description": "Field to sort by",
            "type": "string",
            "required": False,
            "default": default_sort_by,
        },
        "sort_order": {
            "description": "Sort order (asc/desc)",
            "type": "string",
            "required": False,
            "default": "asc",
        },
    }
