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
"""Requirement Source Schema."""
from marshmallow import Schema, fields


class RequirementSourceSchema(Schema):
    """Schema for requirement source."""

    id = fields.Str(metadata={"description": "Unique id in the list"})
    name = fields.Str(metadata={"description": "Name of the list item"})
    source_title = fields.Str(
        metadata={"description": "The title of the requirement source"}
    )
    sort_order = fields.Int(
        metadata={"description": "Position of the requirement source in the dropdown"}
    )
