"""Service for inspection record."""

from compliance_api.exceptions import ResourceExistsError, UnprocessableEntityError
from compliance_api.models import Inspection as InspectionModel
from compliance_api.models import InspectionRecord as InspectionRecordModel
from compliance_api.models import InspectionRecordApproval as InspectionRecordApprovalModel
from compliance_api.models import InspectionStatusEnum, IRApprovalStatusEnum
from compliance_api.models.case_file import CaseFileOfficer
from compliance_api.models.db import session_scope
from compliance_api.models.inspection_record import IRProgressEnum, IRStatusEnum
from compliance_api.models.staff_user import StaffUser
from compliance_api.schemas import InspectionRecordPreviewSchema
from compliance_api.services.inspection_record.inspection_record_builder import InspectionRecordDataBuilder
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.utils.pdf_style_converter import convert_inline_styles_for_pdf

from ..docgen_service.docgen_service import DocGenService
from ..inspection import InspectionService


class InspectionRecordService:
    """InspectionRecordService."""

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Find all inspection records by inspection id."""
        return InspectionRecordModel.get_by_inspection_id(inspection_id)

    @classmethod
    def get_by_id(cls, inspection_record_id):
        """Find inspection record by id."""
        return InspectionRecordModel.find_by_id(inspection_record_id)

    @classmethod
    def create(cls, ir_request_data: dict, inspection_id):
        """Create inspection record."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        existing_ir = InspectionRecordModel.get_by_inspection_id(inspection_id)
        #  Raise error, if ir exists and the request is to create another ir of the same status
        if existing_ir:
            raise ResourceExistsError("IR for the given inspection already exists.")
        ir_status = ir_request_data.get("ir_status")
        ir_builder = InspectionRecordDataBuilder(
            inspection=inspection, ir_status=ir_status.value
        )
        ir_data = (
            ir_builder.build_inspection_scope()
            .build_preliminary_review_details()
            .build_finding_statement()
            .build_enforcement_summary()
            .build_action_required_by_rp()
            .build()
        )
        ir_obj = _create_ir_object(ir_data, ir_status, inspection_id)
        with session_scope() as session:
            # pylint: disable=import-outside-toplevel
            from compliance_api.services.inspection_record.inspection_record_approval import (
                InspectionRecordApprovalService)

            created_ir = InspectionRecordModel.create_inspection_record(
                ir_obj, session=session
            )
            if inspection.is_history:
                InspectionRecordApprovalService.create_approval(
                    ir_approval_request_data={"approved_by_id": None},
                    inspection_id=inspection_id,
                    inspection_record_id=created_ir.id,
                    ho_session=session,
                )
        return created_ir

    @classmethod
    def update(cls, inspection_id, inspection_record_id, ir_update_data: dict):
        """Update the inspection record."""
        field_name = ir_update_data.get("field_name")
        value = ir_update_data.get("value", None)
        ir_update_data = {field_name: value}
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        change_track_required_fields = {
            "inspection_scope",
            "preliminary_review_details",
            "finding_statement",
        }
        if field_name in change_track_required_fields:
            #  This check is to make sure the value has actually changed
            if getattr(inspection_record, field_name) != value:
                change_info = dict(inspection_record.field_change_info or {})
                change_info[f"{field_name}_changed"] = True
                ir_update_data["field_change_info"] = change_info
        with session_scope() as session:
            # Update the IR progress to ISSUED if date_issued is updated
            # Update the inspection status to be closed if date_issued is updated
            if field_name == "date_issued" and value:
                approvals = InspectionRecordApprovalModel.get_approvals_by_ir(
                    inspection_record_id=inspection_record_id
                )
                if not approvals:
                    raise UnprocessableEntityError(
                        "IR cannot be issued without approval"
                    )
                latest_approval = approvals[0]
                if latest_approval.approval_status != IRApprovalStatusEnum.APPROVED:
                    raise UnprocessableEntityError("Pending review for this IR")
                ir_update_data["ir_progress"] = IRProgressEnum.ISSUED
                # Validate that the inspection can be closed before closing it
                pending_items = InspectionService.get_pending_items(inspection_id)
                if pending_items and len(pending_items) > 0:
                    items_expect_ir = [
                        item
                        for item in pending_items
                        if item.get("item").get("name", None) != "Inspection Record"
                    ]
                    # Update the inspection status to be closed only if there are
                    # no pending enforcement actions present
                    if len(items_expect_ir) == 0:
                        InspectionModel.update_inspection(
                            inspection_id=inspection_id,
                            inspection_data={
                                "inspection_status": InspectionStatusEnum.CLOSED
                            },
                            session=session,
                        )
            if field_name == "record_prepared_by_id" and value:
                # Validate the record prepared by id and add record_prepared_by_position_id to ir_update_data
                _validate_record_prepared_by_value(
                    inspection_record, value, ir_update_data
                )
            updated_inspection_record = InspectionRecordModel.update_inspection_record(
                inspection_record_id=inspection_record_id,
                ir_update_data=ir_update_data,
                session=session,
            )
        return updated_inspection_record

    @classmethod
    def delete_inspection_record(
        cls, inspection_id, inspection_record_id, ho_session=None
    ):
        """Delete inspection record."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        if inspection_record.ir_progress == IRProgressEnum.ISSUED:
            raise UnprocessableEntityError("Issued IR cannot be deleted")
        approvals = InspectionRecordApprovalModel.get_approvals_by_ir(
            inspection_record_id=inspection_record_id
        )
        with session_scope() as session:
            if approvals:
                for approval in approvals:
                    InspectionRecordApprovalModel.update_approval(
                        approval_id=approval.id,
                        approval_update_data={"is_deleted": True, "is_active": False},
                        session=ho_session or session,
                    )
            InspectionRecordModel.update_inspection_record(
                inspection_record_id=inspection_record_id,
                ir_update_data={"is_deleted": True, "is_active": False},
                session=ho_session or session,
            )

    @classmethod
    def switch_to_final(cls, inspection_id, inspection_record_id):
        """Update the IR status to FINAL."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        approvals = InspectionRecordApprovalModel.get_approvals_by_ir(
            inspection_record_id=inspection_record_id
        )
        if not approvals:
            raise UnprocessableEntityError("IR cannot be FINAL without approval")
        latest_approval = approvals[0]
        if latest_approval.approval_status != IRApprovalStatusEnum.APPROVED:
            raise UnprocessableEntityError("Pending review for this IR")
        ir_builder = InspectionRecordDataBuilder(
            inspection=inspection,
            ir_status=IRStatusEnum.FINAL.value,
            existing_ir=inspection_record,
        )
        ir_data = (
            ir_builder.build_preliminary_review_details()
            .build_enforcement_summary()
            .build()
        )
        update_data = {
            "preliminary_review_details": ir_data.get(
                "preliminary_review_details", None
            ),
            "enforcement_summary": ir_data.get("enforcement_summary", None),
            "action_required_by_rp": None,  # This field should be NONE when you switch to final
            "ir_status_id": IRStatusEnum.FINAL.value,
            "ir_progress": IRProgressEnum.FINALIZING_RECORD,
        }
        updated_ir = InspectionRecordModel.update_inspection_record(
            inspection_record_id, update_data
        )
        return updated_ir

    @classmethod
    def reset_field(
        cls, inspection_id: int, inspection_record_id: int, field_name: str
    ):
        """Reset a specific field in the inspection record to its default generated state.

        Args:
            inspection_id: The ID of the inspection
            inspection_record_id: The ID of the inspection record
            field_name: The field to reset (inspection_scope, preliminary_review_details, etc.)

        Returns:
            Updated inspection record object

        Raises:
            ResourceNotFoundError: If inspection or inspection record not found
            PermissionDeniedError: If user doesn't have permission
        """
        # Check if inspection exists
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        # Check user permissions
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        # Create builder with existing inspection and status
        ir_builder = InspectionRecordDataBuilder(
            inspection=inspection, ir_status=inspection_record.ir_status_id
        )
        ir_data = None
        change_info = dict(inspection_record.field_change_info)
        # Build only the requested field
        if field_name == "inspection_scope":
            ir_data = ir_builder.build_inspection_scope().build()
        elif field_name == "preliminary_review_details":
            ir_data = ir_builder.build_preliminary_review_details().build()
        elif field_name == "finding_statement":
            ir_data = ir_builder.build_finding_statement().build()
        elif field_name == "enforcement_summary":
            ir_data = ir_builder.build_enforcement_summary().build()
        change_info[f"{field_name}_changed"] = False
        update_data = {
            field_name: ir_data.get(field_name),
            "field_change_info": change_info,
        }
        # Update the inspection record with the reset field
        updated_inspection_record = InspectionRecordModel.update_inspection_record(
            inspection_record_id=inspection_record_id, ir_update_data=update_data
        )

        return updated_inspection_record

    @classmethod
    def render(cls, inspection_id, inspection_record_id, output_format):
        """Preview inspection record."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        if output_format == "pdf":
            ServiceUtils.access_check_update_for_inspection(inspection)
            ServiceUtils.inspection_status_check(inspection)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        if inspection.id != inspection_record.inspection_id:
            raise UnprocessableEntityError(
                "Inspection and inspection record do not match"
            )
        ir_builder = InspectionRecordDataBuilder(
            inspection=inspection,
            ir_status=inspection_record.ir_status_id,
            existing_ir=inspection_record,
        )
        ir_data = (
            ir_builder.build_project_details()
            .build_officer_details()
            .build_appendices()
            .build_department_details()
            .build_inspection_scope()
            .build_preliminary_review_details()
            .build_finding_statement()
            .build_enforcement_summary()
            .build_action_required_by_rp()
            .build_requirement_details()
            .build_regulatory_considerations()
            .build_version_date_info()
            .build_approval_info()
            .build()
        )
        preview_data = InspectionRecordPreviewSchema().dump(ir_data)

        # Apply style conversion to HTML fields (similar to order.py and warning_letter.py)
        if preview_data.get("inspection_scope"):
            preview_data["inspection_scope"] = convert_inline_styles_for_pdf(
                preview_data["inspection_scope"]
            )
        if preview_data.get("preliminary_review_details"):
            preview_data["preliminary_review_details"] = convert_inline_styles_for_pdf(
                preview_data["preliminary_review_details"]
            )
        if preview_data.get("finding_statement"):
            preview_data["finding_statement"] = convert_inline_styles_for_pdf(
                preview_data["finding_statement"]
            )
        if preview_data.get("enforcement_summary"):
            preview_data["enforcement_summary"] = convert_inline_styles_for_pdf(
                preview_data["enforcement_summary"]
            )
        if preview_data.get("action_required_by_rp"):
            preview_data["action_required_by_rp"] = convert_inline_styles_for_pdf(
                preview_data["action_required_by_rp"]
            )

        # Apply style conversion to requirement findings and nested descriptions (may contain tables)
        if preview_data.get("requirement_details"):
            for requirement in preview_data["requirement_details"]:
                # Findings
                if requirement.get("requirement_findings"):
                    requirement["requirement_findings"] = convert_inline_styles_for_pdf(
                        requirement["requirement_findings"]
                    )
                # Requirement source descriptions
                if requirement.get("requirement_source_details"):
                    for source in requirement["requirement_source_details"]:
                        if source.get("requirement_source_description"):
                            source["requirement_source_description"] = (
                                convert_inline_styles_for_pdf(
                                    source["requirement_source_description"]
                                )
                            )
                        # Document descriptions nested within sources
                        if source.get("requirement_documents"):
                            for doc_group in source["requirement_documents"]:
                                if doc_group.get("documents"):
                                    for doc in doc_group["documents"]:
                                        if doc.get("description"):
                                            doc["description"] = (
                                                convert_inline_styles_for_pdf(
                                                    doc["description"]
                                                )
                                            )

        # Apply style conversion to regulatory consideration findings
        if preview_data.get("regulatory_consideration") and preview_data[
            "regulatory_consideration"
        ].get("findings"):
            preview_data["regulatory_consideration"]["findings"] = (
                convert_inline_styles_for_pdf(
                    preview_data["regulatory_consideration"]["findings"]
                )
            )

        response = DocGenService.render_template(
            "IR_TEMPLATE", preview_data, output_format
        )
        return response, inspection


def _create_ir_object(ir_data, ir_status, inspection_id):
    """
    Create the inspection record object to be persisted.

    :param ir_request_data: The input payload for the endpoint.
    :param ir_data: The inspection record builder output.
    """
    return {
        "inspection_id": inspection_id,
        "ir_status_id": ir_status.value,
        "record_prepared_by_id": ir_data.get("record_prepared_by_id"),
        "record_prepared_by_position_id": ir_data.get("record_prepared_by_position_id"),
        "inspection_scope": ir_data.get("inspection_scope"),
        "finding_statement": ir_data.get("finding_statement"),
        "enforcement_summary": ir_data.get("enforcement_summary", None),
        "ir_progress": ir_data.get("ir_progress"),
        "action_required_by_rp": ir_data.get("action_required_by_rp", None),
        "field_change_info": {
            "inspection_scope_changed": False,
            "preliminary_review_details_changed": False,
            "finding_statement_changed": False,
        },
    }


def _validate_record_prepared_by_value(
    inspection_record, record_prepared_by_id, ir_update_data
):
    """
    Validate that the provided staff member is authorized to prepare the inspection record.

    Authorized staff includes:
    - Primary officer on inspection
    - Primary officer on case file
    - Other officers on case file

    Also updates the position ID of the record prepared by staff.
    """
    # Get the inspection and case file
    inspection = inspection_record.inspection
    case_file = inspection.case_file

    # Get the staff member
    staff_member = StaffUser.find_by_id(record_prepared_by_id)
    if not staff_member:
        raise UnprocessableEntityError(
            f"Staff member with id {record_prepared_by_id} not found"
        )

    # Check if staff member is authorized
    authorized_officer_ids = set()

    # Add primary officer on inspection
    if inspection.primary_officer_id:
        authorized_officer_ids.add(inspection.primary_officer_id)

    # Add primary officer on case file
    if case_file.primary_officer_id:
        authorized_officer_ids.add(case_file.primary_officer_id)

    # Add other officers on case file
    case_file_officers = CaseFileOfficer.get_all_by_case_file_id(case_file.id)
    for case_file_officer in case_file_officers:
        authorized_officer_ids.add(case_file_officer.officer_id)

    # Validate the staff member is authorized
    if int(record_prepared_by_id) not in authorized_officer_ids:
        raise UnprocessableEntityError(
            "The selected staff member is not authorized to prepare this inspection record. "
            "Only the primary officer on inspection, primary officer on case file, "
            "or other officers on case file are allowed."
        )

    # Set the position ID of the record prepared by staff
    if staff_member.position_id:
        ir_update_data["record_prepared_by_position_id"] = staff_member.position_id
