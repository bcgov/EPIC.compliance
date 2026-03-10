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
"""Project Schema."""
from marshmallow import EXCLUDE, Schema, fields

from compliance_api.models.project import Project as ProjectModel

from .base_schema import AutoSchemaBase


class ProjectTypeSchema(Schema):
    """Schema for project type from EPIC.Track."""

    id = fields.Int()
    name = fields.Str()
    short_name = fields.Str(allow_none=True)
    sort_order = fields.Int(allow_none=True)
    is_active = fields.Bool()


class ProjectSubTypeSchema(Schema):
    """Schema for project sub-type from EPIC.Track."""

    id = fields.Int()
    name = fields.Str()
    short_name = fields.Str(allow_none=True)
    sort_order = fields.Int(allow_none=True)
    is_active = fields.Bool()


class ProjectProponentSchema(Schema):
    """Schema for project proponent from EPIC.Track."""

    id = fields.Int()
    name = fields.Str()
    is_active = fields.Bool()
    relationship_holder_id = fields.Int(allow_none=True)


class ProjectSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Project schema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
        model = ProjectModel
        include_fk = True


class ProjectDetailSchema(ProjectSchema):  # pylint: disable=too-many-ancestors
    """Project schema including enriched data from EPIC.Track."""

    ea_certificate = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    type = fields.Nested(ProjectTypeSchema, allow_none=True)
    sub_type = fields.Nested(ProjectSubTypeSchema, allow_none=True)
    proponent = fields.Nested(ProjectProponentSchema, allow_none=True)
