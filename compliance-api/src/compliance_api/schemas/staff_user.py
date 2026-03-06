# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Staff User Schema."""
from marshmallow import EXCLUDE, fields, post_dump, post_load
from marshmallow_enum import EnumField

from compliance_api.models.staff_user import StaffUser
from compliance_api.utils.enum import PermissionEnum

from .base_schema import AutoSchemaBase, BaseSchema
from .common import KeyValueSchema


class StaffUserSchemaSkeleton(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Basic schema for staff user."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = StaffUser
        include_fk = True

    position = fields.Nested(KeyValueSchema, dump_only=True)
    permission = fields.Raw()
    name = fields.Method("get_full_name")

    def get_full_name(self, obj):
        """Derive fullname from either an object or a dictionary."""
        if obj is None:
            return ""

        # Handle dictionary case
        if isinstance(obj, dict):
            first_name = obj.get("first_name", "")
            last_name = obj.get("last_name", "")
        # Handle StaffUser object case
        else:
            first_name = getattr(obj, "first_name", "")
            last_name = getattr(obj, "last_name", "")

        return f"{first_name} {last_name}".strip()

    @post_dump
    def nullify_nested(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Make nested objects null if the referenced ID is null."""
        if data.get("deputy_director_id") is None:
            data["deputy_director"] = None
        if data.get("supervisor_id") is None:
            data["supervisor"] = None
        if data.get("permission") in [p.name for p in PermissionEnum]:
            data["permission"] = {
                "id": getattr(PermissionEnum, data.get("permission")).name,
                "name": getattr(PermissionEnum, data.get("permission")).value,
            }
        return data


class StaffUserSchema(StaffUserSchemaSkeleton):  # pylint: disable=too-many-ancestors
    """Staff User schema."""

    deputy_director = fields.Nested(StaffUserSchemaSkeleton, dump_only=True)
    supervisor = fields.Nested(StaffUserSchemaSkeleton, dump_only=True)


class StaffUserUpdateSchema(BaseSchema):
    """StaffUser update schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    position_id = fields.Int(
        metadata={
            "description": "The unique identifier of the position of the staff user."
        },
        required=True,
    )
    deputy_director_id = fields.Int(
        metadata={"description": "The unique identifier of the deputy director."},
        allow_none=True,
    )
    supervisor_id = fields.Int(
        metadata={"description": "The unique identifier of the supervisor."},
        allow_none=True,
    )
    permission = EnumField(
        PermissionEnum,
        metadata={"description": "The permission level of the staff user."},
        required=True,
    )
    is_active = fields.Bool(
        metadata={"description": "Indicate if the staff is active or not"},
        required=True,
    )

    @post_load
    def extract_permission_value(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the permission enum."""
        permission_enum = data.get("permission")
        if permission_enum:
            data["permission"] = permission_enum.name
        return data


class StaffUserCreateSchema(BaseSchema):
    """User create Schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    position_id = fields.Int(
        metadata={
            "description": "The unique identifier of the position of the staff user."
        },
        required=True,
    )
    deputy_director_id = fields.Int(
        metadata={"description": "The unique identifier of the deputy director."},
        allow_none=True,
    )
    supervisor_id = fields.Int(
        metadata={"description": "The unique identifier of the supervisor."},
        allow_none=True,
    )
    auth_user_guid = fields.Str(
        metadata={"description": "The unique identifier from the identity provider."},
        required=True,
    )
    permission = EnumField(
        PermissionEnum,
        metadata={"description": "The permission level of the staff user."},
        required=True,
    )
    is_active = fields.Bool(
        metadata={"description": "Indicate if the staff is active or not"},
        required=True,
    )

    @post_load
    def extract_permission_value(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the permission enum."""
        permission_enum = data.get("permission")
        if permission_enum:
            data["permission"] = permission_enum.name
        return data
