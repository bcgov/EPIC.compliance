# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Super class to handle all operations related to base schema."""
from flask import json
from marshmallow import Schema, fields, post_dump

from compliance_api.exceptions import BadRequestError
from compliance_api.models.db import ma


class BaseSchema(Schema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """Base Schema."""

    def __init__(self, *args, **kwargs):
        """Excludes versions. Otherwise database will query <name>_versions table."""
        meta = getattr(self, "Meta", None)
        if (
            meta
            and hasattr(meta, "model")
            and hasattr(meta["model"], "versions")
            and not self.fields
        ):
            self.exclude = getattr(self.Meta, "exclude", ()) + ("versions",)
        super().__init__(*args, **kwargs)

    def handle_error(self, error, data, **kwargs):
        """Log and raise our custom exception when validation fails."""
        raise BadRequestError(json.dumps(error.messages))

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to declare any class attributes."""

        datetimeformat = "%Y-%m-%dT%H:%M:%S+00:00"  # Default output date format.

    created_by = fields.Function(
        lambda obj: (
            f"{obj.created_by.firstname} {obj.created_by.lastname}"
            if getattr(obj, "created_by", None) and hasattr(obj.created_by, "firstname")
            else obj.created_by
            if getattr(obj, "created_by", None)
            else None
        )
    )

    updated_by = fields.Function(
        lambda obj: (
            f"{obj.updated_by.firstname} {obj.updated_by.lastname}"
            if getattr(obj, "updated_by", None) and hasattr(obj.updated_by, "firstname")
            else obj.updated_by
            if getattr(obj, "updated_by", None)
            else None
        )
    )

    @post_dump(pass_many=True)
    def _remove_empty(self, data, many):  # pylint: disable=no-self-use
        """Remove all empty values and versions from the dumped dict."""
        if not many:
            for key in list(data):
                if key == "versions":
                    data.pop(key)

            return {key: value for key, value in data.items() if value is not None}
        for item in data:
            for key in list(item):
                if (key == "versions") or (item[key] is None):
                    item.pop(key)

        return data


class AutoSchemaBase(ma.SQLAlchemyAutoSchema):  # pylint: disable=too-many-ancestors
    """Representation of a base SQL alchemy auto schema with basic functions."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta information applicable to all schemas."""

        model = None
        exclude = (
            "created_date",
            "created_by",
            "updated_date",
            "updated_by",
            "is_deleted",
        )
        # abstract=True

    def on_bind_field(self, field_name, field_obj):
        """on_bind_field method."""
        # Get the SQLAlchemy column associated with this field
        column = self.Meta.model.__table__.columns.get(field_name)
        if column is not None and column.comment:
            # Set the description meta attribute to the column's comment
            field_obj.metadata["description"] = column.comment

        super().on_bind_field(field_name, field_obj)
