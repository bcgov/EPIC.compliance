"""Service for managing complaint."""

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.complaint import Complaint as ComplaintModel
from compliance_api.models.complaint import ComplaintReqEACDetail as ComplaintReqEACDetailModel
from compliance_api.models.complaint import ComplaintReqOrderDetail as ComplaintReqOrderDetailModel
from compliance_api.models.complaint import ComplaintReqScheduleBDetail as ComplaintReqScheduleBDetailModel
from compliance_api.models.complaint import ComplaintRequirementDetail as ComplaintRequirementDetailModel
from compliance_api.models.complaint import ComplaintRequirementSourceEnum
from compliance_api.models.complaint import ComplaintSource as ComplaintSourceModel
from compliance_api.models.complaint import ComplaintSourceContact as ComplaintSourceContactModel
from compliance_api.models.complaint import ComplaintStatusEnum
from compliance_api.models.complaint import ComplaintUnapprovedProject as ComplaintUnapprovedProjectModel
from compliance_api.models.db import session_scope
from compliance_api.services.case_file import CaseFileService
from compliance_api.services.epic_track_service.track_service import TrackService
from compliance_api.utils.constant import UNAPPROVED_PROJECT_CODE, UNAPPROVED_PROJECT_NAME


class ComplaintService:
    """Complaint Service."""

    @classmethod
    def get_complaint_sources(cls):
        """Get complaint sources."""
        return ComplaintSourceModel.get_all(sort_by="sort_order")

    @classmethod
    def get_all(cls):
        """Get all complaints."""
        return ComplaintModel.get_all(default_filters=False)

    @classmethod
    def get_by_id(cls, complaint_id):
        """Get complaint by id."""
        complaint = ComplaintModel.find_by_id(complaint_id)
        if not complaint:
            return None
        return _set_project_parameters(complaint)

    @classmethod
    def get_by_complaint_no(cls, complaint_no):
        """Get complaint details by complaint number."""
        complaint = ComplaintModel.get_by_complaint_number(complaint_no)
        if not complaint:
            return None
        return _set_project_parameters(complaint)

    @classmethod
    def get_by_case_file_id(cls, case_file_id):
        """Get all complaints by case file id."""
        return ComplaintModel.get_by_params({"case_file_id": case_file_id})

    @classmethod
    def create(cls, complaint_data: dict):
        """Create complaint."""
        complaint_obj = _create_complaint_object(complaint_data)
        with session_scope() as session:
            created_complaint = ComplaintModel.create_complaint(complaint_obj, session)
            if not _has_project(complaint_data):
                unapproved_project_obj = _create_unapproved_project_object(
                    complaint_data, created_complaint.id
                )
                ComplaintUnapprovedProjectModel.create_project_info(
                    unapproved_project_obj, session
                )
            contact_obj = _create_source_type_contact_object(
                complaint_data, created_complaint.id
            )
            ComplaintSourceContactModel.create_contact(contact_obj, session)
            if _has_requirement_source(complaint_data):
                requirement_source_obj = _create_requirement_source_detail_obj(
                    complaint_data, created_complaint.id
                )
                created_requirement_source = (
                    ComplaintRequirementDetailModel.create_detail(
                        requirement_source_obj, session
                    )
                )
                _create_requirement_source_more_details(
                    complaint_data, created_requirement_source.id, session
                )
        return created_complaint

    @classmethod
    def is_assigned_user(cls, complaint_id, auth_user_guid):
        """Check if the given user is an assigned user of the given complaint."""
        complaint = ComplaintModel.find_by_id(complaint_id)

        if not complaint:
            return False
        return complaint.primary_officer.auth_user_guid == auth_user_guid


def _set_project_parameters(complaint):
    """Set complaint project parameters."""
    project_id = complaint.project_id
    if project_id:
        project = TrackService.get_project_by_id(project_id)
        setattr(complaint, "authorization", project.get("ea_certificate", None))
        setattr(complaint, "type", project.get("type").get("name"))
        setattr(complaint, "sub_type", project.get("sub_type").get("name"))
        setattr(complaint, "regulated_party", project.get("proponent").get("name"))
    if not project_id:
        project = ComplaintUnapprovedProjectModel.get_by_complaint_id(complaint.id)
        setattr(complaint, "authorization", project.authorization)
        setattr(complaint, "type", project.type)
        setattr(complaint, "sub_type", project.sub_type)
        setattr(complaint, "regulated_party", project.regulated_party)
    return complaint


def _has_project(complaint_data):
    """Check if there is a valid project or not."""
    return complaint_data.get("project_id", None) is not None


def _has_requirement_source(complaint_data):
    """Check if requirement source selected or not."""
    return complaint_data.get("requirement_source_id", None) is not None


def _create_requirement_source_more_details(
    complaint_data: dict, requirement_id, session
):
    """Create requirement source more details."""
    requirement_source_id = complaint_data.get("requirement_source_id", None)
    if requirement_source_id:
        if requirement_source_id == ComplaintRequirementSourceEnum.SCHEDULE_B.value:
            obj = _create_schedule_b_detail_obj(complaint_data, requirement_id)
            ComplaintReqScheduleBDetailModel.create(obj, session)
        elif requirement_source_id == ComplaintRequirementSourceEnum.ORDER.value:
            obj = _create_order_detail_obj(complaint_data, requirement_id)
            ComplaintReqOrderDetailModel.create(obj, session)
        elif (
            requirement_source_id
            == ComplaintRequirementSourceEnum.EAC_CERTIFICATE.value
        ):
            obj = _create_eac_detail_obj(complaint_data, requirement_id)
            ComplaintReqEACDetailModel.create(obj, session)


def _create_requirement_source_detail_obj(complaint_data: dict, complaint_id):
    """Create requirement source detail object."""
    requirement_source_info = complaint_data.get("requirement_source_details", None)
    if not requirement_source_info:
        return {}
    return {
        "complaint_id": complaint_id,
        "topic_id": requirement_source_info.get("topic_id"),
        "description": requirement_source_info.get("description", None),
    }


def _create_source_type_contact_object(complaint_data: dict, complaint_id):
    """Create source contact info."""
    contact_info = complaint_data.get("complaint_source_contact", None)
    if not contact_info:
        return {}
    return {
        "complaint_id": complaint_id,
        "full_name": contact_info.get("full_name", None),
        "email": contact_info.get("email", None),
        "phone": contact_info.get("phone", None),
        "comment": contact_info.get("comment", None),
        "description": contact_info.get("description", None),
    }


def _create_unapproved_project_object(complaint_data: dict, complaint_id: int):
    """Create complaint unapproved project object."""
    return {
        "name": UNAPPROVED_PROJECT_NAME,
        "authorization": complaint_data.get("unapproved_project_authorization"),
        "regulated_party": complaint_data.get("unapproved_project_regulated_party"),
        "type": complaint_data.get("unapproved_project_type"),
        "sub_type": complaint_data.get("unapproved_project_sub_type"),
        "complaint_id": complaint_id,
    }


def _create_complaint_object(complaint_data: dict):
    """Create complaint object."""
    project_id = complaint_data.get("project_id", None)
    case_file_id = complaint_data.get("case_file_id")
    return {
        "complaint_number": _create_complaint_number(project_id, case_file_id),
        "case_file_id": complaint_data.get("case_file_id"),
        "project_id": project_id,
        "location_description": complaint_data.get("location_description", None),
        "project_description": complaint_data.get("project_description", None),
        "concern_description": complaint_data.get("concern_description", None),
        "primary_officer_id": complaint_data.get("primary_officer_id", None),
        "date_received": complaint_data.get("date_received"),
        "requirement_source_id": complaint_data.get("requirement_source_id", None),
        "source_type_id": complaint_data.get("source_type_id"),
        "source_agency_id": complaint_data.get("source_agency_id", None),
        "source_first_nation_id": complaint_data.get("source_first_nation_id", None),
        "status": ComplaintStatusEnum.OPEN,
    }


def _create_complaint_number(
    project_id,
    case_file_id,
):  # pylint: disable=inconsistent-return-statements
    """Generate the complaint number."""
    project_code = _get_project_abbreviation(project_id)
    case_file = CaseFileService.get_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file doesn't match")

    count = ComplaintModel.get_count_by_project_nd_case_file_id(
        project_id, case_file_id
    )
    serial_number = f"{count + 1:03}"
    return f"{project_code}_{case_file.case_file_number}_CM{serial_number}"


def _get_project_abbreviation(
    project_id: int,
):  # pylint: disable=inconsistent-return-statements
    """Return the project abbreviation."""
    if project_id:
        project = TrackService.get_project_by_id(project_id)
        return project.get("abbreviation")
    return UNAPPROVED_PROJECT_CODE


def _create_eac_detail_obj(complaint_data: dict, requirement_id):
    """Create requirement source eac detail obj."""
    req_info = complaint_data.get("requirement_source_details", {})
    return {
        "req_id": requirement_id,
        "amendment_number": req_info.get("amendment_number", None),
        "amendment_condition_number": req_info.get("amendment_condition_number", None),
    }


def _create_order_detail_obj(complaint_data: dict, requirement_id):
    """Create requirement source order detail obj."""
    req_info = complaint_data.get("requirement_source_details", {})
    return {
        "req_id": requirement_id,
        "order_number": req_info.get("order_number", None),
    }


def _create_schedule_b_detail_obj(complaint_data: dict, requirement_id):
    """Create requirement source schedule b detail obj."""
    req_info = complaint_data.get("requirement_source_details", {})
    return {
        "req_id": requirement_id,
        "condition_number": req_info.get("condition_number"),
    }
