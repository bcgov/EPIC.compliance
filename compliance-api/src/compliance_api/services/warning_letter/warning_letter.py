"""Warning Letter Service."""

from typing import List

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.models.department_detail import DepartmentDetail as DepartmentDetailModel
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection import InspectionRequirement as InspectionRequirementModel
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.models.warning_letter import WarningLetter as WarningLetterModel
from compliance_api.models.warning_letter import \
    WarningLetterInspectionRequirementMap as WarningLetterInspectionRequirementMapModel
from compliance_api.models.warning_letter import WarningLetterProgressEnum, WarningLetterStatusEnum
from compliance_api.services.docgen_service.docgen_service import DocGenService
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.services.warning_letter.warning_letter_approval import WarningLetterApprovalService
from compliance_api.services.warning_letter.warning_letter_template_constant import WARNING_LETTER_CONTENT
from compliance_api.utils.constant import OFFICE_BRANCH, OFFICE_NAME
from compliance_api.utils.datetime import convert_to_full_month_format
from compliance_api.utils.pdf_style_converter import convert_inline_styles_for_pdf
from compliance_api.utils.template_renderer import render_template_with_data


class WarningLetterService:
    """Service layer for Warning Letter operations."""

    @classmethod
    def get_all(cls, inspection_id: int = None, sort_by: str = None) -> List[WarningLetterModel]:
        """Get all warning letters for an inspection."""
        if inspection_id is None:
            return WarningLetterModel.get_all(sort_by=sort_by)
        return WarningLetterModel.get_by_params(
            {"inspection_id": inspection_id}, default_filters=False, sort_by=sort_by
        )

    @classmethod
    def create_warning_letter(cls, warning_letter_data: dict) -> WarningLetterModel:
        """Create a new warning letter."""
        inspection_id = warning_letter_data.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id=inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        ServiceUtils.officer_check(
            warning_letter_data.get("issuing_officer_id"), inspection
        )
        requirement_ids = warning_letter_data.get("inspection_requirement_ids", [])
        if len(requirement_ids) == 0:
            raise UnprocessableEntityError("No requirement IDs provided.")
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids, EnforcementActionOptionEnum.WARNING_LETTER.value
        )
        warning_letter_obj = _create_warning_letter_obj(inspection, warning_letter_data)
        with session_scope() as session:
            # pylint: disable=import-outside-toplevel
            from compliance_api.services.warning_letter.warning_letter_approval import WarningLetterApprovalService

            created_warning_letter = WarningLetterModel.create_warning_letter(
                warning_letter_obj, session
            )
            cls.insert_or_update_inspection_requirements(
                created_warning_letter.id,
                warning_letter_data.get("inspection_requirement_ids", []),
                session,
            )
            if inspection.is_history:
                WarningLetterApprovalService.create_approval(
                    {
                        "approved_by_id": None,
                    },
                    created_warning_letter.id,
                    session,
                )
        return created_warning_letter

    @classmethod
    def get_warning_letter(cls, warning_letter_id: int) -> WarningLetterModel:
        """Retrieve a warning letter by ID."""
        return WarningLetterModel.find_by_id(warning_letter_id)

    @classmethod
    def get_warning_letter_by_warning_letter_number(
        cls, warning_letter_number: str
    ) -> WarningLetterModel:
        """Retrieve a warning letter by warning letter number."""
        return WarningLetterModel.get_by_warning_letter_number(warning_letter_number)

    @classmethod
    def update_warning_letter(
        cls, warning_letter_id: int, update_data: dict
    ) -> WarningLetterModel:
        """Update an existing warning letter."""
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        ServiceUtils.access_check_update_for_inspection(warning_letter.inspection)
        ServiceUtils.inspection_status_check(warning_letter.inspection)
        issuing_officer_id = update_data.get("issuing_officer_id")
        ServiceUtils.officer_check(issuing_officer_id, warning_letter.inspection)
        requirement_ids = update_data.get("inspection_requirement_ids", [])
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids, EnforcementActionOptionEnum.WARNING_LETTER.value
        )

        with session_scope() as session:
            updated_warning_letter = WarningLetterModel.update_warning_letter(
                warning_letter_id, update_data, session
            )
            cls.insert_or_update_inspection_requirements(
                updated_warning_letter.id,
                update_data.get("inspection_requirement_ids", []),
                session,
            )
        return updated_warning_letter

    @classmethod
    def delete_warning_letter(cls, warning_letter_id: int) -> None:
        """Delete a warning letter by ID."""
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        ServiceUtils.access_check_update_for_inspection(warning_letter.inspection)
        ServiceUtils.inspection_status_check(warning_letter.inspection)
        if warning_letter.status == WarningLetterStatusEnum.ISSUED:
            raise UnprocessableEntityError("Warning letter is in ISSUED status.")
        with session_scope() as session:
            approvals = WarningLetterApprovalService.get_all_approvals(
                warning_letter_id
            )
            for approval in approvals:
                approval.update({"is_active": False, "is_deleted": True}, session)
            WarningLetterInspectionRequirementMapModel.delete_by_warning_letter(
                warning_letter_id, session
            )
            WarningLetterModel.update_warning_letter(
                warning_letter_id,
                {"is_active": False, "is_deleted": True},
                session,
            )

    @classmethod
    def insert_or_update_inspection_requirements(
        cls, warning_letter_id: int, inspection_requirement_ids: list[int], session=None
    ):
        """Insert/Update inspection requirements associated with a given warning letter."""
        if inspection_requirement_ids is not None:
            existing_requirements = (
                WarningLetterInspectionRequirementMapModel.get_by_warning_letter_id(
                    warning_letter_id
                )
            )
            existing_requirement_ids = {
                req.inspection_requirement_id for req in existing_requirements
            }

            new_requirement_ids = set(inspection_requirement_ids)
            requirement_ids_to_be_deleted = existing_requirement_ids.difference(
                new_requirement_ids
            )
            requirement_ids_to_be_added = new_requirement_ids.difference(
                existing_requirement_ids
            )

            if requirement_ids_to_be_deleted:
                WarningLetterInspectionRequirementMapModel.bulk_delete(
                    warning_letter_id, list(requirement_ids_to_be_deleted), session
                )
            if requirement_ids_to_be_added:
                WarningLetterInspectionRequirementMapModel.bulk_insert(
                    warning_letter_id, list(requirement_ids_to_be_added), session
                )

    @classmethod
    def issue_warning_letter(cls, warning_letter_id: int, issue_data: dict) -> dict:
        """Issue a warning letter."""
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        ServiceUtils.access_check_update_for_inspection(warning_letter.inspection)
        ServiceUtils.inspection_status_check(warning_letter.inspection)
        with session_scope() as session:
            issue_data["status"] = WarningLetterStatusEnum.ISSUED
            issue_data["progress"] = WarningLetterProgressEnum.ISSUED
            updated_warning_letter = WarningLetterModel.update_warning_letter(
                warning_letter_id=warning_letter_id,
                warning_letter_update_data=issue_data,
                session=session,
            )
        return updated_warning_letter

    @classmethod
    def reset_field(cls, warning_letter_id: int, field_name: str) -> dict:
        """Reset a specific field in the warning letter.

        Currently only supports resetting the 'content' field.

        Args:
            warning_letter_id: The ID of the warning letter
            field_name: The field name to reset (must be 'content')

        Returns:
            The updated warning letter with the reset field

        Raises:
            ResourceNotFoundError: If the warning letter doesn't exist
            UnprocessableEntityError: If the warning letter is not in drafting status
            or the field_name is not supported
        """
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        ServiceUtils.access_check_update_for_inspection(warning_letter.inspection)
        ServiceUtils.inspection_status_check(warning_letter.inspection)
        # Only allow reset if warning letter is in drafting status
        if warning_letter.progress != WarningLetterProgressEnum.DRAFTING:
            raise UnprocessableEntityError(
                "Warning letter can only be reset if the progress is in drafting status"
            )

        # Supported fields for reset
        if field_name not in ["content"]:
            raise UnprocessableEntityError(
                f"Field {field_name} is not supported for reset"
            )

        update_data = {}

        if field_name == "content":
            # Get the inspection and requirement IDs to regenerate content
            inspection = warning_letter.inspection
            requirement_ids = [
                req_map.inspection_requirement_id
                for req_map in warning_letter.warning_letter_requirement_maps
            ]
            # Regenerate content using the existing method
            issuing_officer_id = warning_letter.issuing_officer_id
            new_content = _create_content(inspection, requirement_ids, issuing_officer_id)
            update_data["content"] = new_content

        # Update the warning letter with the regenerated field
        with session_scope() as session:
            updated_warning_letter = WarningLetterModel.update_warning_letter(
                warning_letter_id=warning_letter_id,
                warning_letter_update_data=update_data,
                session=session,
            )

        return updated_warning_letter

    @classmethod
    def render(cls, warning_letter_id, output_format):
        """Preview warning letter."""
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        if output_format == "pdf":
            ServiceUtils.access_check_update_for_inspection(warning_letter.inspection)
        warning_letter_data = _create_warning_letter_data(warning_letter)
        response = DocGenService.render_template(
            "WARNING_LETTER_TEMPLATE", warning_letter_data, output_format
        )
        return response, warning_letter


def _create_warning_letter_data(warning_letter):
    """Create warning letter data."""
    department_details = DepartmentDetailModel.query.filter_by(
        is_active=True, is_deleted=False
    ).first()
    return {
        "warning_letter": {
            "warning_letter_number": warning_letter.warning_letter_number,
            "issue_date": (
                warning_letter.date_issued.strftime("%Y-%m-%d")
                if warning_letter.date_issued
                else (
                    warning_letter.intended_issuance_date.strftime("%Y-%m-%d")
                    if warning_letter.intended_issuance_date
                    else None
                )
            ),
            "content": convert_inline_styles_for_pdf(warning_letter.content),
        },
        "officer_details": {
            "officer_name": warning_letter.issuing_officer.first_name
            + " "
            + warning_letter.issuing_officer.last_name,
            "officer_position": warning_letter.issuing_officer.position.name,
        },
        "department_details": {
            "logo_url": department_details.logo_url,
            "email": department_details.email,
            "address_line1": department_details.address_line1,
            "address_line2": department_details.address_line2,
            "phone": department_details.phone,
            "website": department_details.website,
            "office_name": OFFICE_NAME,
            "office_branch": OFFICE_BRANCH,
        },
    }


def _create_warning_letter_obj(inspection, warning_letter_data: dict) -> dict:
    """
    Create a warning letter object as a dictionary.

    If content is not provided, it will be generated.
    If issuing_officer_id is not provided, it will be set to the primary officer of the inspection.
    """
    requirement_ids = warning_letter_data.get("inspection_requirement_ids", None)
    warning_letter_number = warning_letter_data.get("warning_letter_number", None)
    if not warning_letter_number:
        warning_letter_number = _create_warning_letter_number(
            inspection.case_file.project_id, inspection.case_file.id
        )

    issuing_officer_id = warning_letter_data.get(
        "issuing_officer_id", inspection.primary_officer_id
    )

    content = warning_letter_data.get("content")
    if not content:
        content = _create_content(
            inspection, requirement_ids, issuing_officer_id
        )

    return {
        "warning_letter_number": warning_letter_number,
        "inspection_id": inspection.id,
        "issuing_officer_id": issuing_officer_id,
        "content": content,
        "intended_issuance_date": warning_letter_data.get("intended_issuance_date"),
        "status": WarningLetterStatusEnum.CREATED,
        "progress": WarningLetterProgressEnum.DRAFTING,
    }


def _create_content(inspection, requirement_ids, issuing_officer_id):
    """Create where_as and now_therefore."""
    department_details = DepartmentDetailModel.query.filter_by(
        is_active=True, is_deleted=False
    ).first()
    requirements = InspectionRequirementModel.get_requirement_by_ids(requirement_ids)
    requirement_details = ServiceUtils.get_formatted_requirement_details(requirements)
    issuing_officer = StaffUserModel.find_by_id(issuing_officer_id)
    requirements = []
    for requirement in requirement_details:
        if len(requirement["requirement_source_details"]) > 0:
            requirements.append(
                {
                    "requirement_summary": requirement["requirement_summary"],
                    "requirement_source_number": requirement[
                        "requirement_source_details"
                    ][0]["requirement_source_number"],
                    "requirement_source_name": requirement[
                        "requirement_source_details"
                    ][0]["requirement_source_name"],
                }
            )
    if len(requirements) == 0:
        raise UnprocessableEntityError("No requirement details found.")
    # Create condition_line by grouping requirements by source name
    condition_lines = []
    grouped_requirements = {}

    # Group requirements by source name
    for requirement in requirements:
        source_name = requirement["requirement_source_name"]
        if source_name not in grouped_requirements:
            grouped_requirements[source_name] = []
        grouped_requirements[source_name].append(
            {"number": requirement["requirement_source_number"]}
        )

    # Create condition line for each source
    for source_name, reqs in grouped_requirements.items():
        numbers = ", ".join(req["number"] for req in reqs if req["number"])
        condition_lines.append(f"{numbers} of {source_name}")
    warning_letter_content = {
        "project_details": ServiceUtils.get_project_details(
            inspection.case_file.project_id, inspection.case_file.id
        ),
        "inspection_details": {
            "id": inspection.id,
            "inspection_type": " and ".join(
                [inspection_type.type.name for inspection_type in inspection.types]
            ),
            "start_date": convert_to_full_month_format(inspection.start_date),
            "end_date": (
                convert_to_full_month_format(inspection.end_date)
                if inspection.end_date
                else ""
            ),
            "ir_number": ServiceUtils.strip_project_code(inspection.ir_number),
            "primary_officer_name": f"{inspection.primary_officer.first_name} {inspection.primary_officer.last_name}",
            "officer_name": f"{issuing_officer.first_name} {issuing_officer.last_name}",
            "officer_position": issuing_officer.position.name,
        },
        "department_details": {
            "email": department_details.email,
            "phone": department_details.phone,
        },
        "requirement_details": requirements,
        "requirement_sources": ", ".join(
            [requirement["requirement_source_name"] for requirement in requirements]
        ),
        "condition_lines": condition_lines,
    }

    content = render_template_with_data(
        "WARNING_LETTER_CONTENT", WARNING_LETTER_CONTENT, warning_letter_content
    )
    return content


def _create_warning_letter_number(project_id: int, case_file_id: int) -> str:
    """Generate the warning letter number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file don't match")
    pattern = rf"^{project_code}_{case_file.case_file_number}_WN[0-9]{{3}}$"
    count = WarningLetterModel.get_latest_warning_letter_number_count(
        case_file_id, project_id, pattern
    )
    serial_number = f"{count:03}"
    return f"{project_code}_{case_file.case_file_number}_WN{serial_number}"
