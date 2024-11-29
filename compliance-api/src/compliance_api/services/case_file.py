"""Service for handle CaseFile."""

from datetime import datetime

from flask import g

from compliance_api.auth import auth
from compliance_api.exceptions import (
    PermissionDeniedError, ResourceExistsError, ResourceNotFoundError, UnprocessableEntityError)
from compliance_api.models import CaseFile as CaseFileModel
from compliance_api.models import CaseFileInitiationOption as CaseFileInitiationOptionModel
from compliance_api.models import CaseFileOfficer as CaseFileOfficerModel
from compliance_api.models import CaseFileStatusEnum
from compliance_api.models import UnapprovedProject as UnapprovedProjectModel
from compliance_api.models.db import session_scope
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT, UNAPPROVED_PROJECT_NAME
from compliance_api.utils.enum import ContextEnum, PermissionEnum

from .epic_track_service.track_service import TrackService


class CaseFileService:
    """CaseFile Service."""

    @classmethod
    def get_initiation_options(cls):
        """Return the case file initiation options."""
        return CaseFileInitiationOptionModel.get_all(sort_by="sort_order")

    @classmethod
    def get_all(cls):
        """Return all the case files."""
        return CaseFileModel.get_all(default_filters=False)

    @classmethod
    def get_by_id(cls, case_file_id: int):
        """Return case file by id."""
        case_file = CaseFileModel.find_by_id(case_file_id)
        return _set_project_parameters(case_file)

    @classmethod
    def get_other_officers(cls, case_file_id: int):
        """Return other officers associated with a given case file."""
        officers = CaseFileOfficerModel.get_all_by_case_file_id(case_file_id)
        return [case_file_officer.officer for case_file_officer in officers]

    @classmethod
    def create(cls, case_file_data: dict):
        """Create case file."""
        from .continuation_report import ContinuationReportService  # pylint: disable=import-outside-toplevel

        case_file_obj = _create_case_file_object(case_file_data)
        _validate_existence_by_file_number(case_file_obj.get("case_file_number", None))
        with session_scope() as session:
            created_case_file = CaseFileModel.create_case_file(case_file_obj, session)
            # If Selected Project is unapproved project
            if not case_file_data.get("project_id", None):
                unapproved_project_obj = _create_unapproved_project_object(
                    case_file_data, created_case_file.id
                )
                UnapprovedProjectModel.create_project_info(
                    unapproved_project_obj, session
                )
            cls.insert_or_update_officers(
                created_case_file.id, case_file_data.get("officer_ids", []), session
            )
            cr_entry = _create_cr_entry(
                created_case_file.id, created_case_file.case_file_number
            )
            ContinuationReportService.create(
                cr_entry, sys_generated=True, ho_session=session
            )
        return created_case_file

    @classmethod
    def update(cls, case_file_id: int, case_file_data: dict, ho_session=None):
        """Update case file."""
        _access_check_for_update(case_file_id)
        case_file_obj = {
            "primary_officer_id": case_file_data.get("primary_officer_id", None),
            "project_description": case_file_data.get("project_description", None)
        }
        with session_scope() as session:
            updated_case_file = CaseFileModel.update_case_file(
                case_file_id, case_file_obj, ho_session or session
            )
            cls.insert_or_update_officers(
                case_file_id,
                case_file_data.get("officer_ids", []),
                ho_session or session,
            )
        return updated_case_file

    @classmethod
    def get_by_file_number(cls, case_file_number: int):
        """Return case file information by file number."""
        case_file = CaseFileModel.get_by_file_number(case_file_number)
        return _set_project_parameters(case_file)

    @classmethod
    def insert_or_update_officers(
        cls, case_file_id: int, officer_ids: list[int], session=None
    ):
        """Insert/Update case file officers associated with a given case file."""
        if officer_ids is not None:
            existing_officers = CaseFileOfficerModel.get_all_by_case_file_id(
                case_file_id
            )
            existing_officer_ids = {
                officer.officer_id
                for officer in existing_officers
                if officer.is_active is True
            }

            new_officer_ids = set(officer_ids)
            officer_ids_to_be_deleted = existing_officer_ids.difference(new_officer_ids)
            officer_ids_to_be_added = new_officer_ids.difference(existing_officer_ids)
            if officer_ids_to_be_deleted:
                CaseFileOfficerModel.bulk_delete(
                    case_file_id, list(officer_ids_to_be_deleted), session
                )
            if officer_ids_to_be_added:
                CaseFileOfficerModel.bulk_insert(
                    case_file_id, list(officer_ids_to_be_added), session
                )

    @classmethod
    def get_by_project(cls, project_id: int):
        """Return case files based on project id."""
        case_files = CaseFileModel.get_by_project(project_id)
        return [
            case_file
            for case_file in case_files
            if case_file.case_file_status == CaseFileStatusEnum.OPEN
        ]

    @classmethod
    def is_logged_user_primary_or_officer(cls, case_file_id):
        """Check to see if the given user is primary or other officer in the case file."""
        auth_user_guid = g.token_info["preferred_username"]
        case_file = CaseFileModel.find_by_id(case_file_id)
        #  The logged in user should be primary or officer in the associated
        #  case file
        return case_file.primary_officer.auth_user_guid == auth_user_guid or any(
            officer.officer.auth_user_guid == auth_user_guid
            for officer in case_file.case_file_officers
        )

    @classmethod
    def change_case_file_status(cls, case_file, status_data):
        """Change the status of the case file."""
        _access_check_for_update(case_file.id)
        if not case_file:
            raise ResourceNotFoundError("Case file not found.")
        status_enum = CaseFileStatusEnum(status_data.get("status"))
        if (
            case_file.case_file_status == CaseFileStatusEnum.OPEN
            and status_enum == CaseFileStatusEnum.OPEN
        ):
            raise UnprocessableEntityError("The case file is already in Open status.")
        if (
            case_file.case_file_status == CaseFileStatusEnum.CLOSED
            and status_enum == CaseFileStatusEnum.CLOSED
        ):
            raise UnprocessableEntityError("The case file is already in Open status.")
        CaseFileModel.change_status(case_file.id, status_enum)


def _set_project_parameters(case_file):
    """Set project parameters."""
    project_id = case_file.project_id
    if project_id:
        project = TrackService.get_project_by_id(project_id)
        setattr(case_file, "authorization", project.get("ea_certificate", None))
        setattr(case_file, "type", project.get("type").get("name"))
        setattr(case_file, "sub_type", project.get("sub_type").get("name"))
        setattr(case_file, "regulated_party", project.get("proponent").get("name"))
    if not project_id:
        project = UnapprovedProjectModel.get_by_case_file_id(case_file.id)
        setattr(case_file, "authorization", project.authorization)
        setattr(case_file, "type", project.type)
        setattr(case_file, "sub_type", project.sub_type)
        setattr(case_file, "regulated_party", project.regulated_party)
    return case_file


def _create_unapproved_project_object(case_file_data: dict, case_file_id: int):
    """Create unapproved project object."""
    return {
        "name": UNAPPROVED_PROJECT_NAME,
        "authorization": case_file_data.get("unapproved_project_authorization"),
        "regulated_party": case_file_data.get("unapproved_project_regulated_party"),
        "type": case_file_data.get("unapproved_project_type"),
        "sub_type": case_file_data.get("unapproved_project_sub_type"),
        "case_file_id": case_file_id,
    }


def _access_check_for_update(case_file_id):
    """Access check for update."""
    auth_user_guid = g.token_info["preferred_username"]
    case_file = CaseFileModel.find_by_id(case_file_id)
    if (
        not auth.has_permission([PermissionEnum.SUPERUSER])
        and not case_file.primary_officer.auth_user_guid == auth_user_guid
    ):
        raise PermissionDeniedError(
            "You don't have the correct permission to perform this operation."
        )


def _create_case_file_object(case_file_data: dict):
    """Create a case file object."""
    case_file_obj = {
        "project_id": case_file_data.get("project_id", None),
        "date_created": case_file_data.get("date_created"),
        "primary_officer_id": case_file_data.get("primary_officer_id", None),
        "initiation_id": case_file_data.get("initiation_id"),
        "project_description": case_file_data.get("project_description", None),
        "case_file_status": CaseFileStatusEnum.OPEN,
    }
    if not case_file_data.get("case_file_number", None):
        case_file_obj["case_file_number"] = _generate_case_file_number(
            datetime.now().year
        )
    else:
        case_file_obj["case_file_number"] = case_file_data.get("case_file_number")
    return case_file_obj


def _generate_case_file_number(year):
    """Generate case file number."""
    max_number = CaseFileModel.get_max_case_file_number_by_year(year)
    return str(max_number + 1 if max_number > 0 else f"{year}{1:04d}")


def _validate_existence_by_file_number(case_file_number: int, case_file_id: int = None):
    """Check if the case file exists."""
    existing_case_file = CaseFileModel.get_by_file_number(case_file_number)
    if existing_case_file and (
        not case_file_id or existing_case_file.id != case_file_id
    ):
        raise ResourceExistsError(
            f"Case file with the number {case_file_number} exists"
        )


def _create_cr_entry(case_file_id, case_file_number):
    """Create the continuation report entry."""
    return {
        "case_file_id": case_file_id,
        "text": f"{case_file_number} is created",
        "rich_text": f"<p>{case_file_number} is created</p>",
        "date_created": datetime.utcnow().strftime(INPUT_DATE_TIME_FORMAT),
        "context_type": ContextEnum.CASE_FILE,
        "context_id": case_file_id,
        "keys": [{"key": case_file_number, "key_context": ContextEnum.CASE_FILE}],
    }
