"""Service for managing Inspection."""

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models import Inspection as InspectionModel
from compliance_api.models import InspectionAgency as InspectionAgencyModel
from compliance_api.models import InspectionAttendance as InspectionAttendanceModel
from compliance_api.models import InspectionAttendanceOption as InspectionAttendanceOptionModel
from compliance_api.models import InspectionFirstnation as InspectionFirstnationModel
from compliance_api.models import InspectionInitiationOption as InspectionInitiationOptionModel
from compliance_api.models import InspectionOfficer as InspectionOfficerModel
from compliance_api.models import InspectionOtherAttendance as InspectionOtherAttendanceModel
from compliance_api.models import InspectionType as InspectionTypeModel
from compliance_api.models import InspectionTypeOption as InspectionTypeOptionModel
from compliance_api.models import InspectionUnapprovedProject as InspectionUnapprovedProjectModel
from compliance_api.models import IRStatusOption as IRStatusOptionModel
from compliance_api.models.db import session_scope
from compliance_api.models.inspection.inspection_enum import InspectionAttendanceOptionEnum, InspectionStatusEnum
from compliance_api.utils.constant import UNAPPROVED_PROJECT_CODE, UNAPPROVED_PROJECT_NAME

from .case_file import CaseFileService
from .epic_track_service.track_service import TrackService


class InspectionService:
    """Inspection Service Class."""

    @classmethod
    def get_all_attendance_options(cls):
        """Get inspection attendance options."""
        return InspectionAttendanceOptionModel.get_all(sort_by="sort_order")

    @classmethod
    def get_inspection_type_options(cls):
        """Get inspection type options."""
        return InspectionTypeOptionModel.get_all(sort_by="sort_order")

    @classmethod
    def get_initiation_options(cls):
        """Get inspection initiation options."""
        return InspectionInitiationOptionModel.get_all(sort_by="sort_order")

    @classmethod
    def get_ir_status_options(cls):
        """Get inspection record status options."""
        return IRStatusOptionModel.get_all(sort_by="sort_order")

    @classmethod
    def get_all(cls):
        """Get all inspections."""
        return InspectionModel.get_all(default_filters=False)

    @classmethod
    def get_by_case_file_id(cls, case_file_id):
        """Get all inspections by case file id"""
        return InspectionModel.get_by_params({
            "case_file_id": case_file_id
        })

    @classmethod
    def get_by_id(cls, inspection_id):
        """Return inspection by id."""
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError(
                f"No inspection found for the given ID : {inspection_id}"
            )
        return _set_inspection_project_parameters(inspection)

    @classmethod
    def get_by_ir_number(cls, ir_number):
        """Return inspection by ir number."""
        inspection = InspectionModel.get_by_ir_number(ir_number)
        return _set_inspection_project_parameters(inspection)

    @classmethod
    def get_other_officers(cls, inspection_id):
        """Return other officers associated with a given inspection."""
        officers = InspectionOfficerModel.get_all_by_inspection(inspection_id)
        return [officer.officer for officer in officers]

    @classmethod
    def get_attendance_options(cls, inspection_id):
        """Return attendances by inspection."""
        attendance_options = InspectionAttendanceModel.get_all_by_inspection(
            inspection_id
        )
        if attendance_options:
            other_attendances = InspectionOtherAttendanceModel.get_by_inspection(
                inspection_id
            )
            for option in attendance_options:
                setattr(option, "data", [])
                data = ""
                if (
                    option.attendance_option_id
                    == InspectionAttendanceOptionEnum.AGENCIES.value
                ):
                    agencies = InspectionAgencyModel.get_all_by_inspection(
                        inspection_id
                    )
                    data = [
                        {"id": agency.agency_id, "name": agency.agency.name}
                        for agency in agencies
                    ]
                if (
                    option.attendance_option_id
                    == InspectionAttendanceOptionEnum.FIRSTNATIONS.value
                ):
                    first_nations = InspectionFirstnationModel.get_all_by_inspection(
                        inspection_id
                    )
                    data = _set_first_nation_names(first_nations)
                if (
                    option.attendance_option_id
                    == InspectionAttendanceOptionEnum.MUNICIPAL.value
                ):
                    if other_attendances:
                        data = other_attendances.municipal
                if (
                    option.attendance_option_id
                    == InspectionAttendanceOptionEnum.OTHER.value
                ):
                    if other_attendances:
                        data = other_attendances.other
                setattr(option, "data", data)
        return attendance_options

    @classmethod
    def create(cls, inspection_data: dict):
        """Create inspection."""
        inspection_obj = _create_inspection_object(inspection_data)
        with session_scope() as session:
            created_inspection = InspectionModel.create_inspection(
                inspection_obj, session
            )
            # If Selected Project is unapproved project
            if not inspection_data.get("project_id", None):
                unapproved_project_obj = _create_unapproved_project_object(
                    inspection_data, created_inspection.id
                )
                InspectionUnapprovedProjectModel.create_project_info(
                    unapproved_project_obj, session
                )
            attendance_option_ids = inspection_data.get("attendance_option_ids", [])
            _insert_or_update_inspection_relationship(
                created_inspection.id,
                attendance_option_ids,
                InspectionAttendanceModel,
                "attendance_option_id",
                session,
            )
            _insert_or_update_inspection_relationship(
                created_inspection.id,
                inspection_data.get("inspection_officer_ids", []),
                InspectionOfficerModel,
                "officer_id",
                session,
            )
            _insert_or_update_inspection_relationship(
                created_inspection.id,
                inspection_data.get("agency_attendance_ids", []),
                InspectionAgencyModel,
                "agency_id",
                session,
            )
            _insert_or_update_inspection_relationship(
                created_inspection.id,
                inspection_data.get("firstnation_attendance_ids", []),
                InspectionFirstnationModel,
                "firstnation_id",
                session,
            )
            _insert_or_update_inspection_relationship(
                created_inspection.id,
                inspection_data.get("inspection_type_ids", []),
                InspectionTypeModel,
                "type_id",
                session,
            )
            if {
                InspectionAttendanceOptionEnum.MUNICIPAL.value,
                InspectionAttendanceOptionEnum.OTHER.value,
            }.intersection(attendance_option_ids):
                other_attendance_obj = _create_inspection_other_attendance_object(
                    inspection_data, created_inspection.id
                )
                InspectionOtherAttendanceModel.create_attendance(
                    other_attendance_obj, session
                )
        return created_inspection

    @classmethod
    def is_assigned_user(cls, inspection_id, auth_user_guid):
        """Check if the given user is an assigned user of the given inspection."""
        inspection = InspectionModel.find_by_id(inspection_id)

        if not inspection:
            return False

        # Check if the user is the lead officer or part of other officers
        return inspection.lead_officer.auth_user_guid == auth_user_guid or any(
            officer.officer.auth_user_guid == auth_user_guid
            for officer in inspection.other_officers
        )


def _set_inspection_project_parameters(inspection):
    """Set inspection project parameters."""
    project_id = inspection.project_id
    if project_id:
        project = TrackService.get_project_by_id(project_id)
        setattr(inspection, "authorization", project.get("ea_certificate", None))
        setattr(inspection, "type", project.get("type").get("name"))
        setattr(inspection, "sub_type", project.get("sub_type").get("name"))
        setattr(inspection, "regulated_party", project.get("proponent").get("name"))
    if not project_id:
        project = InspectionUnapprovedProjectModel.get_by_inspection_id(inspection.id)
        setattr(inspection, "authorization", project.authorization)
        setattr(inspection, "type", project.type)
        setattr(inspection, "sub_type", project.sub_type)
        setattr(inspection, "regulated_party", project.regulated_party)
    return inspection


def _set_first_nation_names(first_nation_list: list):
    """Set the name of the first nations from epic.track."""
    result = []
    for first_nation in first_nation_list:
        response = TrackService.get_first_nation_by_id(first_nation.id)
        result.append({"id": response.get("id"), "name": response.get("name")})
    return result


# pylint: disable=too-many-arguments
def _insert_or_update_inspection_relationship(
    inspection_id: int,
    entity_ids: list[int],
    model_class,
    entity_id_attr: str,
    session=None,
    is_active_attr: str = "is_active",
):
    """
    Insert/Update inspection relationships in a generic way.

    Args:
        inspection_id (int): The ID of the inspection.
        entity_ids (list[int]): List of IDs representing related entities (e.g., firstnations, agencies).
        model_class (Class): The model class to perform the operations (e.g., InspectionFirstnationModel).
        entity_id_attr (str): The attribute name in the model for the entity ID (e.g., 'firstnation_id').
        session: The database session to use, if applicable.
        is_active_attr (str): The attribute name for checking active entities (default is 'is_active').
    """
    # Retrieve existing relationships
    existing_entities = model_class.get_all_by_inspection(inspection_id)
    existing_entity_ids = {
        getattr(entity, entity_id_attr)
        for entity in existing_entities
        if getattr(entity, is_active_attr) is True
    }

    # Calculate the differences
    new_entity_ids = set(entity_ids)
    entity_ids_to_be_deleted = existing_entity_ids.difference(new_entity_ids)
    entity_ids_to_be_added = new_entity_ids.difference(existing_entity_ids)

    # Perform bulk delete and insert
    if entity_ids_to_be_deleted:
        model_class.bulk_delete(inspection_id, list(entity_ids_to_be_deleted), session)

    if entity_ids_to_be_added:
        model_class.bulk_insert(inspection_id, list(entity_ids_to_be_added), session)


def _create_unapproved_project_object(inspection_data: dict, inspection_id: int):
    """Create inspection unapproved project object."""
    return {
        "name": UNAPPROVED_PROJECT_NAME,
        "authorization": inspection_data.get("unapproved_project_authorization"),
        "regulated_party": inspection_data.get("unapproved_project_regulated_party"),
        "type": inspection_data.get("unapproved_project_type"),
        "sub_type": inspection_data.get("unapproved_project_sub_type"),
        "inspection_id": inspection_id,
    }


def _create_inspection_object(inspection_data: dict):
    """Create inspection object."""
    project_id = inspection_data.get("project_id", None)
    case_file_id = inspection_data.get("case_file_id")
    return {
        "ir_number": _create_inspection_record_number(project_id, case_file_id),
        "case_file_id": inspection_data.get("case_file_id"),
        "project_id": project_id,
        "project_description": inspection_data.get("project_description", None),
        "location_description": inspection_data.get("location_description", None),
        "utm": inspection_data.get("utm", None),
        "lead_officer_id": inspection_data.get("lead_officer_id"),
        "start_date": inspection_data.get("start_date"),
        "end_date": inspection_data.get("end_date"),
        "initiation_id": inspection_data.get("initiation_id"),
        "ir_status_id": inspection_data.get("ir_status_id", None),
        "project_status_id": inspection_data.get("project_status_id", None),
        "inspection_status": InspectionStatusEnum.OPEN,
    }


def _create_inspection_record_number(
    project_id: int, case_file_id
):  # pylint: disable=inconsistent-return-statements
    """Generate the inspection record number."""
    project_code = _get_project_abbreviation(project_id)
    case_file = CaseFileService.get_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file doesn't match")

    count = InspectionModel.get_count_by_project_nd_case_file_id(
        project_id, case_file_id
    )
    serial_number = f"{count + 1:03}"
    return f"{project_code}_{case_file.case_file_number}_IR{serial_number}"


def _get_project_abbreviation(
    project_id: int,
):  # pylint: disable=inconsistent-return-statements
    """Return the project abbreviation."""
    if project_id:
        project = TrackService.get_project_by_id(project_id)
        return project.get("abbreviation")
    return UNAPPROVED_PROJECT_CODE


def _create_inspection_other_attendance_object(
    inspection_data: dict, inspection_id: int
):
    """Return inspection other attendance object."""
    return {
        "municipal": inspection_data.get("attendance_municipal"),
        "other": inspection_data.get("attendance_other"),
        "inspection_id": inspection_id,
    }
