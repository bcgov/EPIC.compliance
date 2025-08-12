"""Inspection Record Preview Schema."""

from marshmallow import Schema, fields

from .appendix import AppendixSchema
from .base_schema import BaseSchema
from .department_detail import DepartmentDetailsSchema


class RequirementDocumentSchema(BaseSchema):
    """Schema for requirement source detail documents."""

    document_title = fields.String(allow_none=True)
    documents = fields.Raw()


class RequirementSourceDetailSchema(BaseSchema):
    """Schema for requirement source details."""

    appendix_no = fields.String(allow_none=True)
    requirement_source_id = fields.Integer()
    requirement_source_name = fields.String()
    requirement_source_number = fields.String()
    requirement_title = fields.String()
    requirement_source_description = fields.String(allow_none=True)
    requirement_documents = fields.List(
        fields.Nested(RequirementDocumentSchema), allow_none=True
    )


class RequirementPhotoSchema(BaseSchema):
    """Schema for requirement photos."""

    photo_caption = fields.String()
    photo_number = fields.Integer()
    photo_url = fields.String()


class RequirementFigureSchema(BaseSchema):
    """Schema for requirement figures."""

    figure_caption = fields.String()
    figure_number = fields.Integer()
    figure_url = fields.String()


class RequirementDetailSchema(BaseSchema):
    """Schema for requirement details."""

    requirement_id = fields.Integer()
    requirement_findings = fields.String(allow_none=True)
    sort_order = fields.Integer()
    compliance_finding = fields.String()
    enforcement_action = fields.String()
    requirement_summary = fields.String()
    requirement_source_details = fields.List(
        fields.Nested(RequirementSourceDetailSchema)
    )
    requirement_photos = fields.List(fields.Nested(RequirementPhotoSchema))
    requirement_figures = fields.List(fields.Nested(RequirementFigureSchema))


class RegulatoryConsiderationSchema(BaseSchema):
    """Schema for regulatory consideration."""

    findings = fields.String()
    photos = fields.List(fields.Nested(RequirementPhotoSchema))
    figures = fields.List(fields.Nested(RequirementFigureSchema))


class ProjectDetailsSchema(BaseSchema):
    """Schema for project details."""

    name = fields.Str(required=True)
    eac_certificate = fields.Str(required=True)
    certificate_label = fields.Str(required=True)
    project_state = fields.Str(required=True)
    proponent_label = fields.Str(required=True)
    proponent = fields.Str(required=True)


class InspectionDetailsSchema(BaseSchema):
    """Schema for inspection details."""

    id = fields.Int(required=True)
    inspection_type = fields.Str(required=True)
    start_date = fields.Str(required=True)
    utm = fields.Str(required=True)
    project_description = fields.Str(required=True)
    location_description = fields.Str(required=True)
    initiation = fields.Str(required=True)
    ir_number = fields.Str(required=True)


class InspectionRecordPreviewSchema(Schema):
    """Schema for inspection record preview."""

    # Status
    ir_status = fields.String()
    ir_progress = fields.String()

    # Inspection Details
    inspection_details = fields.Nested(InspectionDetailsSchema)

    # Project Details
    project_details = fields.Nested(ProjectDetailsSchema)

    # Officer Details
    officer_details = fields.Raw()
    mailing_address = fields.Str()

    # Content Fields
    inspection_scope = fields.String(allow_none=True)
    preliminary_review_details = fields.String(allow_none=True)
    finding_statement = fields.String(allow_none=True)
    enforcement_summary = fields.String(allow_none=True)
    action_required_by_rp = fields.String(allow_none=True)

    # Regulatory Consideration
    regulatory_consideration = fields.Nested(RegulatoryConsiderationSchema)

    # Requirements
    requirement_details = fields.List(fields.Nested(RequirementDetailSchema))

    # Department Details
    department_details = fields.Nested(DepartmentDetailsSchema)

    # Appendices
    appendices = fields.List(fields.Nested(AppendixSchema))
    version_date_info = fields.Raw()
    approval_info = fields.Raw()
