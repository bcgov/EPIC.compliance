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
"""CaseFile Schema."""
from marshmallow import EXCLUDE, Schema, fields, post_dump, post_load
from marshmallow_enum import EnumField

from compliance_api.models import CaseFile, CaseFileLink, CaseFileOfficer, CaseFileStatusEnum
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT, UNAPPROVED_PROJECT_CODE, UNAPPROVED_PROJECT_NAME

from .base_schema import AutoSchemaBase, BaseSchema
from .common import KeyValueSchema
from .project import ProjectSchema
from .staff_user import StaffUserSchema


class CaseFileOfficerSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for CaseFileOfficer."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta for CaseFileOfficer Schema."""

        unknown = EXCLUDE
        model = CaseFileOfficer
        include_fk = True

    officer = fields.Nested(StaffUserSchema, dump_only=True)


class CaseFileSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Basic schema for case file."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = CaseFile
        include_fk = True

    primary_officer = fields.Nested(StaffUserSchema, dump_only=True)
    project = fields.Nested(
        ProjectSchema,
        dump_only=True,
        exclude=["is_active"],
    )
    initiation = fields.Nested(KeyValueSchema)
    authorization = fields.Str(
        metadata={"description": "The authorization information of the project"}
    )
    regulated_party = fields.Str(
        metadata={"description": "The regulated party of the project"}
    )
    type = fields.Str(metadata={"description": "The type of the project"})
    sub_type = fields.Str(metadata={"description": "The subtype of the project"})

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of the casefile status enum."""
        if "case_file_status" in data and data["case_file_status"] is not None:
            data["case_file_status"] = CaseFileStatusEnum(
                data["case_file_status"]
            ).value
        else:
            data["case_file_status"] = ""
        if data.get("project", None) is None:
            data["project"] = {
                "name": UNAPPROVED_PROJECT_NAME,
                "abbreviation": UNAPPROVED_PROJECT_CODE,
            }
        return data


class CaseFileUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """CaseFile update Schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    primary_officer_id = fields.Int(
        metadata={"description": "The lead officer who created the case file."},
        required=True,
    )
    officer_ids = fields.List(
        fields.Int(
            metadata={
                "description": "The list of unique identifiers of the other officers associated with the case file"
            }
        )
    )
    project_description = fields.Str(
        metadata={"description": "The project description"}, allow_none=True
    )
    project_id = fields.Int(
        metadata={
            "description": "The unique identifier for the project associated with the case file."
        },
        allow_none=True,
    )
    unapproved_project_regulated_party = fields.Str(
        metadata={"description": "The regulated_party name of the unapproved project"},
        allow_none=True,
    )
    unapproved_project_type = fields.Str(
        metadata={"description": "The type of the unapproved project"}, allow_none=True
    )
    unapproved_project_sub_type = fields.Str(
        metadata={"description": "The sub type of the unapproved project"},
        allow_none=True,
    )


class CaseFileCreateSchema(CaseFileUpdateSchema):  # pylint: disable=too-many-ancestors
    """CaseFile create Schema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    project_id = fields.Int(
        metadata={
            "description": "The unique identifier for the project associated with the case file."
        },
        allow_none=True,
    )
    date_created = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        metadata={"description": "The date on which the case file is created."},
        required=True,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
    )
    initiation_id = fields.Int(
        metadata={"description": "The unique identifier for the initiation options"},
        required=True,
    )
    case_file_number = fields.Str(
        metadata={
            "description": "The unique case file number. If not provided, the case file number will be auto generated."
        },
        allow_none=True,
    )
    unapproved_project_authorization = fields.Str(
        metadata={
            "description": "The authorization information of the unapproved project"
        },
        allow_none=True,
    )
    unapproved_project_regulated_party = fields.Str(
        metadata={"description": "The regulated_party name of the unapproved project"},
        allow_none=True,
    )
    unapproved_project_type = fields.Str(
        metadata={"description": "The type of the unapproved project"}, allow_none=True
    )
    unapproved_project_sub_type = fields.Str(
        metadata={"description": "The sub type of the unapproved project"},
        allow_none=True,
    )


class CaseFileStatusSchema(BaseSchema):
    """CaseFileStatusSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    status = EnumField(
        CaseFileStatusEnum,
        metadata={"description": "The status of the case file"},
        required=True,
    )

    @post_load
    def extract_status_value(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of the status enum."""
        status_enum = data.get("status")
        if status_enum:
            data["status"] = status_enum.value
        return data


class CaseFileLinkCreateSchema(BaseSchema):
    """CaseFileLinkSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    link_case_file_id = fields.Int(
        metadata={"description": "The case file to link to."}, required=True
    )


class CaseFileLinkSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """CaseFileLinkSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = CaseFileLink
        include_fk = True

    source = fields.Nested(CaseFileSchema)
    target = fields.Nested(CaseFileSchema)


class CaseFileOptionSchema(Schema):  # pylint: disable=too-many-ancestors
    """CaseFileOptionSchema."""

    id = fields.Int(metadata={"description": "The unique identifier of the case file."})
    case_file_number = fields.Str(
        metadata={"description": "The unique case file number of the case file."}
    )


class CaseFileUnlinkSchema(BaseSchema):
    """CaseFileUnlinkSchema."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    case_file_to_unlink = fields.Int(
        metadata={"description": "The case file id to unlink"}, required=True
    )


class CaseFileFilterSchema(Schema):
    """Schema to filter the case files for export and pagination."""

    case_file_number = fields.String(
        required=False,
        metadata={"description": "The case file number to filter by"},
    )
    project_ids = fields.String(
        required=False,
        metadata={
            "description": "The unique identifier of the project. Use 'null' or 'none' for unapproved projects"
        },
    )
    initiation_ids = fields.String(
        required=False,
        metadata={"description": "The initiation option ID to filter by"},
    )
    statuses = fields.String(
        required=False,
        metadata={"description": "The case file status to filter by (OPEN/CLOSE)"},
    )
    primary_officer_ids = fields.String(
        required=False,
        metadata={"description": "The primary officer ID to filter by"},
    )
    date_created = fields.String(
        required=False,
        metadata={"description": "Filter case files created on this date (YYYY-MM-DD)"},
    )
    sort_by = fields.String(
        required=False,
        metadata={
            "description": (
                "Field to sort by (case_file_number, project, initiation, "
                "date_created, status, primary_officer)"
            )
        },
    )
    sort_order = fields.String(
        required=False,
        metadata={"description": "Sort order (asc/desc)"},
    )


class EnforcementItemSchema(BaseSchema):
    """Schema for individual enforcement action items."""

    id = fields.Integer(required=True, metadata={"description": "Unique identifier"})
    inspection_id = fields.Integer(
        allow_none=True, metadata={"description": "Associated inspection ID"}
    )

    # Generic number field for all enforcement item types
    number = fields.String(
        allow_none=True,
        metadata={
            "description": "Enforcement item number (IR, complaint, order, etc.)"
        },
    )

    # Status field as key-value object
    status = fields.Nested(
        KeyValueSchema, allow_none=True, metadata={"description": "Item status"}
    )


class CaseFileOpenItemsSchema(BaseSchema):
    """Schema for case file open enforcement items response."""

    has_open_items = fields.Boolean(
        required=True,
        metadata={"description": "Indicates if any open enforcement items exist"},
    )
    inspections = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open inspections"},
    )
    complaints = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open complaints"},
    )
    orders = fields.List(
        fields.Nested(EnforcementItemSchema), metadata={"description": "Open orders"}
    )
    warning_letters = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open warning letters"},
    )
    violation_tickets = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open violation tickets"},
    )
    administrative_penalties = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open administrative penalties"},
    )
    charge_recommendations = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open charge recommendations"},
    )
    restorative_justice = fields.List(
        fields.Nested(EnforcementItemSchema),
        metadata={"description": "Open restorative justice items"},
    )
