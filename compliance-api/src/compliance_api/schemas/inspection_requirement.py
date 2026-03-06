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
"""Inspection requirement Schema Schema."""
from marshmallow import EXCLUDE, Schema, ValidationError, fields, post_dump, pre_dump, validates_schema
from marshmallow_enum import EnumField

from compliance_api.models import (
    EnforcementActionOptionEnum, ImageTypeEnum, InspectionReqDetailDocument, InspectionReqSourceDetail,
    InspectionRequirement, InspectionRequirementImage, InspectionRequirementTypeEnum)
from compliance_api.models.inspection.inspection_req_detail_doc_image import InspectionRequirementDetailDocImage
from compliance_api.models.inspection.inspection_req_detail_image import InspectionRequirementDetailImage
from compliance_api.models.requirement_source import RequirementSourceEnum
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT

from .appendix import AppendixSchema
from .base_schema import AutoSchemaBase, BaseSchema
from .common import KeyValueSchema
from .staff_user import StaffUserSchema


class InspectionReqImageCreateSchema(BaseSchema):
    """InspectionReqImageCreateSchema."""

    original_file_name = fields.Str(
        metadata={
            "description": "The original file name given while the image is being taken"
        },
        required=True,
    )
    date_taken = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        metadata={
            "description": "The timestamp of when the image is captured in ISO 8601 format."
        },
        required=True,
        error_messages={
            "invalid": f"Not a valid datetime. Expected format: {INPUT_DATE_TIME_FORMAT}."
        },
    )
    taken_by_id = fields.Int(
        metadata={
            "description": "The unique identifier of the staff who took the image"
        },
        required=False,
        allow_none=True,
    )
    taken_by_text = fields.Str(
        metadata={
            "description": "Text description of who captured the image when not a staff member"
        },
        required=False,
        allow_none=True,
    )
    caption = fields.Str(
        metadata={"description": "The caption given to the image"}, allow_none=True
    )
    sort_order = fields.Int(
        metadata={"description": "The sort order of the image"}, required=True
    )
    relative_url = fields.Str(
        metadata={"description": "The relative url of the final uploaded image"},
        required=True,
    )


class InspectionReqImageUpdateSchema(InspectionReqImageCreateSchema):
    """InspectionReqImageUpdateSchema."""

    id = fields.Int(
        metadata={
            "description": "The unique identifier of the requirement image entity"
        },
        allow_none=True,
    )


class InspectionReqDetailImageCreateSchema(BaseSchema):
    """InspectionReqDetailImageCreateSchema."""

    original_file_name = fields.Str(
        metadata={"description": "The original filename of the uploaded image"},
        required=True,
    )
    relative_url = fields.Str(
        metadata={"description": "The actual url of the final uploaded image"},
        required=True,
    )


class InspectionReqDetailImageUpdateSchema(InspectionReqDetailImageCreateSchema):
    """InspectionReqDetailImageUpdateSchema."""

    id = fields.Int(
        metadata={
            "description": "The unique identifier of the requirement detail image"
        }
    )


class InspectionReqDetailDocImageCreateSchema(BaseSchema):
    """InspectionReqDetailDocImageCreateSchema."""

    original_file_name = fields.Str(
        metadata={"description": "The original filename of the uploaded image"},
        required=True,
    )
    relative_url = fields.Str(
        metadata={"description": "The actual url of the final uploaded image"},
        required=True,
    )


class InspectionReqDetailDocImageUpdateSchema(InspectionReqDetailDocImageCreateSchema):
    """InspectionReqDetailDocImageUpdateSchema."""

    id = fields.Int(
        metadata={
            "description": "The unique identifier of the requirement detail document image"
        }
    )


class InspectionReqDetailDocCreateSchema(BaseSchema):
    """InspectionReqDetailDocCreateSchema."""

    document_type_id = fields.Int(
        metadata={"description": "The unique identifier of the document type"},
        required=True,
    )
    document_title = fields.Str(metadata={"description": "The title of the document"})
    appendix_id = fields.Int(
        metadata={"description": "The unique identifier of the appendix"},
        allow_none=True,
    )
    description = fields.Str(
        metadata={"description": "The description of the document"}, required=True
    )
    section_number = fields.Str(
        metadata={
            "description": "The highlighted section number in the uploaded document"
        }
    )
    section_title = fields.Str(
        metadata={"description": "Additional description of the document"}
    )
    images = fields.List(
        fields.Nested(InspectionReqDetailDocImageUpdateSchema),
        allow_none=True,
        required=False,
    )


class InspectionReqDetailDocUpdateSchema(InspectionReqDetailDocCreateSchema):
    """InspectionReqDetailDocUpdateSchema."""

    id = fields.Int(
        metadata={
            "description": "The unique identifier of the requirement detail document"
        }
    )


class InspectionReqSourceDetailCreateSchema(BaseSchema):
    """InspectionReqSourceDetailSchema."""

    requirement_source_id = fields.Int(
        metadata={"description": "The unique identifier of the requirement."},
        required=True,
    )
    source_title = fields.Str(
        metadata={"description": "The title of the requirement source detail"},
        allow_none=True,
    )
    compliance_number = fields.Str(
        metadata={
            "description": "The optional compliance number associated with requirement sources as Compliance Agreement"
        }
    )
    clause_number = fields.Str(
        metadata={
            "description": "The optional clause number associated with requirement sources as Exemption Order"
        }
    )
    regulation_number = fields.Str(
        metadata={
            "description": "The optional regulation number associated with requirement sources as Regulation"
        }
    )
    section_number = fields.Str(
        metadata={
            "description": "The optional section number associated with requirement sources"
            "(Act (2018), Schedule A, Compliance Agreement, Act (2002))"
        }
    )
    condition_number = fields.Str(
        metadata={
            "description": "The optional condition number associated with"
            "rquirement sources(Schedule B, EAC Certificate, EAC Amendment)"
        }
    )
    order_id = fields.Int(
        metadata={
            "description": "The optional order id associated with"
            "rquirement sources(Order)"
        }
    )
    amendment_number = fields.Str(
        metadata={
            "description": "The amendment number if the requirement source is EAC Amendment"
        }
    )
    title = fields.Str(
        metadata={"description": "The title of the requirement source detail"}
    )
    description = fields.Str(
        metadata={"description": "The description of the requirement source detail"},
        required=True,
    )
    appendix_id = fields.Int(
        metadata={"description": "The unique identifier of the appendix"},
        allow_none=True,
    )
    documents = fields.List(fields.Nested(InspectionReqDetailDocCreateSchema))
    images = fields.List(fields.Nested(InspectionReqDetailImageCreateSchema))

    @validates_schema
    def validate_section_number(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the section number."""
        section_number = data.get("section_number", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if section_number and RequirementSourceEnum(requirement_source_id) not in [
            RequirementSourceEnum.ACT_2002,
            RequirementSourceEnum.ACT_2018,
            RequirementSourceEnum.COMPLIANCE_AGREEMENT,
            RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION,
            RequirementSourceEnum.OTHER,
            RequirementSourceEnum.REGULATION,
        ]:
            raise ValidationError(
                "Invalid requirement source for the given section number",
                field_name="section_number",
            )

    @validates_schema
    def validate_amendment_number(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the amendment number."""
        amendment_number = data.get("amendment_number", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if (
            RequirementSourceEnum(requirement_source_id)
            == RequirementSourceEnum.EAC_AMENDMENT
            and not amendment_number
        ):
            raise ValidationError(
                "Amendment number is mandatory when the requirement source is EAC_AMENDMENT",
                field_name="amendment_number",
            )

    @validates_schema
    def validate_condition_number(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the condition number."""
        condition_number = data.get("condition_number", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if condition_number and RequirementSourceEnum(requirement_source_id) not in [
            RequirementSourceEnum.SCHEDULE_B,
            RequirementSourceEnum.EAC_CERTIFICATE,
            RequirementSourceEnum.EAC_AMENDMENT,
        ]:
            raise ValidationError(
                "Invalid requirement source for the given condition number",
                field_name="condition_number",
            )

    @validates_schema
    def validate_compliance_number(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the compliance number."""
        compliance_number = data.get("compliance_number", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if compliance_number and RequirementSourceEnum(requirement_source_id) not in [
            RequirementSourceEnum.COMPLIANCE_AGREEMENT,
        ]:
            raise ValidationError(
                "Invalid requirement source for the given compliance number",
                field_name="compliance_number",
            )

    @validates_schema
    def validate_clause_number(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the clause number."""
        clause_number = data.get("clause_number", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if clause_number and RequirementSourceEnum(requirement_source_id) not in [
            RequirementSourceEnum.EXEMPTION_ORDER,
        ]:
            raise ValidationError(
                "Invalid requirement source for the given clause number",
                field_name="clause_number",
            )

    @validates_schema
    def validate_regulation_number(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the regulation number."""
        regulation_number = data.get("regulation_number", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if regulation_number and RequirementSourceEnum(requirement_source_id) not in [
            RequirementSourceEnum.REGULATION,
        ]:
            raise ValidationError(
                "Invalid requirement source for the given regulation number",
                field_name="regulation_number",
            )

    @validates_schema
    def validate_order_id(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Ensure the correct requirement is selected for the order id."""
        order_id = data.get("order_id", [])
        requirement_source_id = data.get("requirement_source_id", None)
        if (
            RequirementSourceEnum(requirement_source_id) == RequirementSourceEnum.ORDER
            and not order_id
        ):
            raise ValidationError(
                "Order id is mandatory when the requirement source is ORDER",
                field_name="order_id",
            )


class InspectionReqSourceDetailUpdateSchema(InspectionReqSourceDetailCreateSchema):
    """InspectionRequirementUpdateSchema."""

    id = fields.Int(
        metadata={
            "description": "The unique identifier of the requirement source detail."
        }
    )
    documents = fields.List(fields.Nested(InspectionReqDetailDocUpdateSchema))
    images = fields.List(fields.Nested(InspectionReqDetailImageUpdateSchema))


class InspectionRequirementCreateSchema(BaseSchema):
    """InspectionRequirementCreateSchema."""

    req_type = EnumField(
        InspectionRequirementTypeEnum,
        metadata={"description": "The type of inspection requirement"},
        required=True,
    )
    summary = fields.Str(
        metadata={"description": "The summary of the requirement."}, required=True
    )
    topic_id = fields.Int(
        metadata={
            "description": "The unique identifier of the topic associated with the inspection"
        },
        required=True,
    )
    agency_id = fields.Int(
        metadata={
            "description": "The unique identifier of the agency only if the requirement"
            "type is regulatory considerations"
        },
        allow_none=True,
    )
    enforcement_action_ids = fields.List(
        fields.Int(metadata={"description": "The enforcement action identifier."}),
        allow_none=True,
    )
    compliance_finding_id = fields.Int(
        metadata={"description": "The unique identifier of the compliance findings."},
        allow_none=True,
    )
    findings = fields.Str(
        metadata={"description": "The requirement findings in html format."},
        required=True,
    )
    requirement_source_details = fields.List(
        fields.Nested(InspectionReqSourceDetailCreateSchema)
    )
    photos = fields.List(fields.Nested(InspectionReqImageCreateSchema))
    figures = fields.List(fields.Nested(InspectionReqImageCreateSchema))

    @validates_schema
    def validate_agency_id(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Validate the agency if the requirement type is regulatory considerations."""
        req_type = data.get("req_type")
        agency_id = data.get("agency_id", None)
        enforcement_action_ids = data.get("enforcement_action_ids")
        if (
            enforcement_action_ids
            and req_type == InspectionRequirementTypeEnum.REQ
            and (
                EnforcementActionOptionEnum.REFERRAL_TO_ANOTHER_AGENCY
                in enforcement_action_ids
                and not agency_id
            )
        ):
            raise ValidationError(
                "Agency is required if the enforcement actions include REFERRAL_TO_ANOTHER_AGENCY",
                field_name="agency_id",
            )


class InspectionRequirementUpdateSchema(InspectionRequirementCreateSchema):
    """InspectionRequirementUpdateSchema."""

    id = fields.Int(
        metadata={"description": "The unique identifier of the requirement"}
    )
    requirement_source_details = fields.List(
        fields.Nested(InspectionReqSourceDetailUpdateSchema)
    )
    photos = fields.List(fields.Nested(InspectionReqImageUpdateSchema))
    figures = fields.List(fields.Nested(InspectionReqImageUpdateSchema))


class InspectionSortOrderSchema(BaseSchema):
    """InspectionSortOrderSchema."""

    order = fields.Int(
        metadata={
            "description": "The index to which the inspection requirement should be moved."
        },
        required=True,
    )


class OrderSchema(Schema):
    """OrderSchema."""

    order_number = fields.Str(metadata={"description": "The order number"})
    id = fields.Int(metadata={"description": "The order id"})
    now_therefore = fields.Str(metadata={"description": "The now therefore"})


class InspectionReqDetailImageSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """InspectionReqDetailImageSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionRequirementDetailImage
        include_fk = True

    url = fields.Str(metadata={"description": "The signed GET url of the file"})


class InspectionReqDetailDocImageSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """InspectionReqDetailDocImageSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionRequirementDetailDocImage
        include_fk = True

    url = fields.Str(metadata={"description": "The signed GET url of the file"})


class InspectionReqDetailDocSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """InspectionReqDetailDocSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionReqDetailDocument
        include_fk = True

    document_type = fields.Nested(KeyValueSchema)
    appendix = fields.Nested(AppendixSchema)
    images = fields.List(fields.Nested(InspectionReqDetailDocImageSchema))


class InspectionReqSourceDetailSchema(
    AutoSchemaBase
):  # pylint: disable=too-many-ancestors
    """InspectionReqSourceDetailSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionReqSourceDetail
        include_fk = True

    documents = fields.List(fields.Nested(InspectionReqDetailDocSchema))
    images = fields.List(fields.Nested(InspectionReqDetailImageSchema))
    requirement_source = fields.Nested(KeyValueSchema)
    appendix = fields.Nested(AppendixSchema)
    order = fields.Nested(OrderSchema)


class InspectionRequirementSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """InspectionRequirementSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionRequirement
        include_fk = True

    requirement_source_details = fields.List(
        fields.Nested(InspectionReqSourceDetailSchema)
    )
    topic = fields.Nested(KeyValueSchema)
    compliance_finding = fields.Nested(KeyValueSchema)
    agency = fields.Nested(KeyValueSchema)
    enforcement_action_data = fields.List(fields.Nested(KeyValueSchema))

    @pre_dump
    def pre_dump_enforcement_actions(
        self, obj, many, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the enforcement actions."""
        if hasattr(obj, "enforcement_actions"):
            prepared_enforcement_actions = []
            for action in obj.enforcement_actions:
                if hasattr(action, "enforcement_action") and action.enforcement_action:
                    prepared_enforcement_actions.append(
                        {
                            "id": action.enforcement_action.id,
                            "name": action.enforcement_action.name,
                        }
                    )
            obj.enforcement_action_data = prepared_enforcement_actions
        return obj

    @post_dump
    def nullify_nested(
        self, data, **kwargs
    ):  # pylint: disable=unused-argument
        """Make nested objects null if the referenced ID is null."""
        if data.get("req_type"):
            data["req_type"] = {
                "id": data.get("req_type").name,
                "name": data.get("req_type").value,
            }
        return data


class InspectionReqImageSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """InspectionReqSourceSchema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Meta."""

        unknown = EXCLUDE
        model = InspectionRequirementImage
        include_fk = True

    taken_by = fields.Nested(StaffUserSchema)
    url = fields.Str(metadata={"description": "The signed GET url of the file"})

    @post_dump
    def post_dump_image_type(
        self, data, many, **kwargs
    ):  # pylint: disable=unused-argument
        """Extract the value of the image type enum."""
        data["image_type"] = ImageTypeEnum(data["image_type"]).value
        return data


class InspectionReqImageSortOrderSchema(BaseSchema):
    """Schema for updating image sort order."""

    image_id = fields.Int(
        metadata={"description": "The unique identifier of the image"}, required=True
    )
    sort_order = fields.Int(
        metadata={"description": "The new sort order for the image"}, required=True
    )


class InspectionReqUpdateSchema(BaseSchema):
    """Schema for updating a single inspection requirement."""

    requirement_id = fields.Int(
        metadata={"description": "The unique identifier of the requirement"},
        required=True,
    )
    findings = fields.Str(
        metadata={"description": "The findings for the requirement"}, allow_none=True
    )
    images = fields.List(
        fields.Nested(InspectionReqImageSortOrderSchema),
        metadata={"description": "List of images to update with new sort orders"},
        required=False,
    )


class InspectionRequirementBulkUpdateSchema(BaseSchema):
    """Schema for bulk updating inspection requirements."""

    requirements = fields.List(
        fields.Nested(InspectionReqUpdateSchema),
        metadata={"description": "List of requirements to update"},
        required=True,
    )
