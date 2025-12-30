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
"""Complaint Schema Schema."""
from marshmallow import EXCLUDE, ValidationError, fields, post_dump, post_load, validates_schema
from marshmallow_enum import EnumField

from compliance_api.models import Complaint, ComplaintSourceContact, ComplaintStatusEnum
from compliance_api.models.complaint import ComplaintSourceEnum
from compliance_api.models.requirement_source import RequirementSourceEnum
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from .base_schema import AutoSchemaBase, BaseSchema
from .case_file import CaseFileSchema
from .common import KeyValueSchema
from .staff_user import StaffUserSchema


class RequirementSourceDetailSchema(BaseSchema):
    """RequirementSourceDetailSchema."""

    id = fields.Int(metadata={"description": "The unique identifier"})
    complaint_id = fields.Int(metadata={"description": "The complaint id"})
    order_number = fields.Str(
        metadata={"description": "The order number"}, allow_none=True
    )


class ComplaintSourceContactSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """ComplaintSourceContactSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = ComplaintSourceContact
        include_fk = True


class RequirementSourceCreateSchema(BaseSchema):
    """Requirement source create schema."""

    topic_id = fields.Int(
        metadata={"description": "The unique id of the topic"}, allow_none=True
    )
    description = fields.Str(
        metadata={"description": "The description of the requirement."},
        allow_none=True,
    )
    order_number = fields.Str(
        metadata={"description": "The order number"}, allow_none=True
    )
    amendment_number = fields.Str(
        metadata={"description": "The amendment number"}, allow_none=True
    )
    amendment_condition_number = fields.Str(
        metadata={"description": "The amendment condition number"}, allow_none=True
    )
    condition_number = fields.Str(metadata={"description": "The condition number"})


class ContactCreateSchema(BaseSchema):
    """Complaint source contact schema for create."""

    full_name = fields.Str(
        metadata={"description": "The full name of the contact person"}, allow_none=True
    )
    title = fields.Str(
        metadata={"description": "The title of the contact person"}, allow_none=True
    )
    email = fields.Str(
        metadata={"description": "The email address of the contact person"},
        allow_none=True,
    )
    phone = fields.Str(
        metadata={"description": "The phone number of the contact person"},
        allow_none=True,
    )
    description = fields.Str(
        metadata={"description": "Any description about the contact"}, allow_none=True
    )
    alliance_name = fields.Str(
        metadata={"description": "The alliance name of the First Nations alliance contact"}, allow_none=True
    )
    comment = fields.Str(metadata={"description": "Any comments"}, allow_none=True)


class ComplaintUpdateSchema(BaseSchema):
    """Complaint schema for update."""

    concern_description = fields.Str(
        metadata={"description": "The concern description of the complaint."},
        required=True,
    )
    location_description = fields.Str(
        metadata={"description": "The location details of the complaint."},
        allow_none=True,
    )
    topic_id = fields.Int(
        metadata={"description": "The unique identifier of the topic"},
        allow_none=True,
    )
    primary_officer_id = fields.Int(
        metadata={
            "description": "The unique identifier of the primary officer who created the complaint."
        },
        required=True,
    )
    date_received = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        metadata={"description": "The complaint received date in ISO 8601 format."},
        required=True,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
    )
    source_type_id = fields.Int(
        metadata={"description": "The unique identifier of complaint source"},
        required=True,
    )
    complaint_source_contact = fields.Nested(ContactCreateSchema)
    requirement_source_id = fields.Int(
        metadata={"description": "The unique identifier of requirement source"},
        allow_none=True,
    )
    requirement_source_description = fields.Str(
        metadata={"description": "The requirement source description of the complaint"},
        allow_none=True,
    )
    requirement_source_details = fields.Nested(RequirementSourceCreateSchema)
    source_agency_id = fields.Int(
        metadata={"description": "Provide agency id if the source type is AGENCY"},
        allow_none=True,
    )
    source_first_nation_id = fields.Int(
        metadata={
            "description": "Provide firstnation id if the source type is FIRSTNATION"
        },
        allow_none=True,
    )


class ComplaintCreateSchema(ComplaintUpdateSchema):
    """Complaint schema for create."""

    case_file_id = fields.Int(
        metadata={
            "description": "The unique identifier of the case file associated with the complaint."
        },
        required=True,
    )

    @validates_schema
    def validate_order(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Ensure that the order is selected if requirement source is ORDER."""
        requirement_source_id = data.get("requirement_source_id", [])
        requirement_source_details = data.get("requirement_source_details", {})
        if (
            requirement_source_id == RequirementSourceEnum.ORDER.value
            and not requirement_source_details.get("order_number", None)
        ):
            raise ValidationError(
                f"Order number is required when requirement_source {RequirementSourceEnum.ORDER.name}",
                field_name="requirement_source_details.order_number",
            )

    @validates_schema
    def validate_contact_description(
        self, data, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Ensure that the description is selected if complaint source is OTHER."""
        source_type_id = data.get("source_type_id", [])
        complaint_source_contact = data.get("complaint_source_contact", {})
        if (
            source_type_id == ComplaintSourceEnum.OTHER.value
            and not complaint_source_contact.get("description", None)
        ):
            raise ValidationError(
                f"Description is required when complaint source "
                f"{ComplaintSourceEnum.OTHER.name}",
                field_name="complaint_source_contact.description",
            )


class ComplaintSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for complaint model."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = Complaint
        include_fk = True

    case_file = fields.Nested(
        CaseFileSchema, only=("case_file_number", "id", "project", "case_file_status")
    )
    primary_officer = fields.Nested(
        StaffUserSchema,
        only=("id", "first_name", "last_name", "name", "auth_user_guid"),
    )
    source_type = fields.Nested(KeyValueSchema)
    agency = fields.Nested(KeyValueSchema)
    first_nation = fields.Nested(KeyValueSchema)
    requirement_source = fields.Nested(KeyValueSchema)
    topic = fields.Nested(KeyValueSchema)
    requirement_detail = fields.Nested(RequirementSourceDetailSchema)
    resolution = fields.Nested(KeyValueSchema)
    resolution_agency = fields.Nested(KeyValueSchema)

    @post_dump
    def post_dump_actions(
        self, data, many, **kwargs
    ):  # pylint: disable=no-self-use, unused-argument
        """Extract the value of the inspection status enum."""
        if "status" in data and data.get("status", None) is not None:
            data["status"] = ComplaintStatusEnum(data["status"]).value
        else:
            data["status"] = ""
        return data


class ComplaintFilterSchema(BaseSchema):
    """Schema for filtering complaints."""

    complaint_number = fields.Str(
        metadata={"description": "Filter by complaint number"},
        required=False,
    )
    project_ids = fields.Str(
        metadata={
            "description": "Filter by project ID(s). Can be a single value or comma-separated list"
        },
        required=False,
    )
    topic_ids = fields.Str(
        metadata={
            "description": "Filter by topic ID(s). Can be a single value or comma-separated list"
        },
        required=False,
    )
    source_type_ids = fields.Str(
        metadata={
            "description": "Filter by source type ID(s). Can be a single value or comma-separated list"
        },
        required=False,
    )
    date_received = fields.Date(
        metadata={"description": "Filter by date received"},
        required=False,
    )
    primary_officer_ids = fields.Str(
        metadata={
            "description": "Filter by primary officer ID(s). Can be a single value or comma-separated list"
        },
        required=False,
    )
    statuses = fields.Str(
        metadata={
            "description": "Filter by status(es). Can be a single value or comma-separated list"
        },
        required=False,
    )
    case_file_number = fields.Str(
        metadata={"description": "Filter by case file number"},
        required=False,
    )
    case_file_id = fields.Int(
        metadata={"description": "Filter by case file ID"},
        required=False,
    )
    resolution_ids = fields.Str(
        metadata={
            "description": "Filter by resolution ID(s). Can be a single value or comma-separated list"
        },
        required=False,
    )
    page_no = fields.Int(
        metadata={"description": "Page number for pagination"},
        required=False,
        missing=1,
    )
    page_size = fields.Int(
        metadata={"description": "Number of items per page"},
        required=False,
        missing=15,
    )
    sort_by = fields.Str(
        metadata={"description": "Field to sort by"},
        required=False,
        missing="complaint_number",
    )
    sort_order = fields.Str(
        metadata={"description": "Sort order (asc/desc)"},
        required=False,
        missing="asc",
    )


class ComplaintStatusSchema(BaseSchema):
    """Schema for changing complaint status.

    When status is 'Closed':
    - resolution_id: Required if you want to specify a resolution
    - resolution_agency_id: Optional, used when resolution type is AGENCY

    When status is 'Open':
    - Both resolution fields are automatically cleared
    - No need to provide these fields in the request
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    status = EnumField(
        ComplaintStatusEnum,
        metadata={"description": "The status of the complaint"},
        required=True,
    )
    resolution_id = fields.Int(
        metadata={
            "description": """Provide resolution id when changing status to 'Closed'.
            This field will be automatically cleared when status is changed to 'Open'.""",
        },
        allow_none=True,
    )
    resolution_agency_id = fields.Int(
        metadata={
            "description": """Provide agency id when changing status to 'Closed' and
            resolution type is AGENCY. This field will be automatically cleared when
            status is changed to 'Open'.""",
        },
        allow_none=True,
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
