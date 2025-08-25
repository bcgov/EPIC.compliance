"""Schema utility functions for common schema patterns."""


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
            "description": "Number of items per page",
            "type": "integer",
            "required": False,
            "default": 15,
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
