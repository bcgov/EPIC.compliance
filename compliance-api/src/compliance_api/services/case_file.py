"""Service for handle CaseFile."""

# pylint: disable=too-many-lines

from datetime import datetime
from io import BytesIO

import pandas as pd
from flask import g
from sqlalchemy import String, and_, asc, case, cast, desc, func, not_, or_

from compliance_api.auth import auth
from compliance_api.exceptions import (
    PermissionDeniedError, ResourceExistsError, ResourceNotFoundError, UnprocessableEntityError)
from compliance_api.models import CaseFile as CaseFileModel
from compliance_api.models import CaseFileInitiationOption as CaseFileInitiationOptionModel
from compliance_api.models import CaseFileLink as CaseFileLinkModel
from compliance_api.models import CaseFileOfficer as CaseFileOfficerModel
from compliance_api.models import CaseFileStatusEnum
from compliance_api.models import UnapprovedProject as UnapprovedProjectModel
from compliance_api.models.administrative_penalty import AdministrativePenalty as AdministrativePenaltyModel
from compliance_api.models.charge_recommendation import ChargeDecisionEnum
from compliance_api.models.charge_recommendation import ChargeRecommendation as ChargeRecommendationModel
from compliance_api.models.charge_recommendation import ChargeRecommendationStatusEnum
from compliance_api.models.complaint import Complaint as ComplaintModel
from compliance_api.models.complaint import ComplaintStatusEnum
from compliance_api.models.db import db, session_scope
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.inspection import InspectionStatusEnum
from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderStatusEnum
from compliance_api.models.project import Project as ProjectModel
from compliance_api.models.restorative_justice import RestorativeJustice as RestorativeJusticeModel
from compliance_api.models.restorative_justice import RestorativeJusticeStatusEnum
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.models.violation_ticket import ViolationTicket as ViolationTicketModel
from compliance_api.models.violation_ticket import ViolationTicketStatusEnum
from compliance_api.models.warning_letter import WarningLetter as WarningLetterModel
from compliance_api.models.warning_letter import WarningLetterProgressEnum
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
    def get_all_with_pagination(cls, args):
        """Return all case files with pagination and filtering."""
        return _build_case_files_paginated_query(args)

    @classmethod
    def get_case_file_options(cls):
        """Return active case files as id-name pairs for dropdown options."""
        case_files = (
            CaseFileModel.query.with_entities(
                CaseFileModel.id, CaseFileModel.case_file_number.label("name")
            )
            .filter(
                CaseFileModel.is_deleted.is_(False), CaseFileModel.is_active.is_(True)
            )
            .order_by(CaseFileModel.case_file_number.asc())
            .all()
        )
        return case_files

    @classmethod
    def generate_case_files_excel(cls, filter_data):
        """Generate case files excel export."""
        # Build query without pagination to get all results
        query = _build_base_query()
        query = _apply_case_file_filters(query, filter_data)
        query = _apply_case_file_sorting(query, filter_data)

        # Get all case files without pagination
        case_files = query.all()

        # Convert to list of dictionaries for pandas
        case_files_data = []
        for case_file in case_files:
            # Get project name from the joined project or unapproved project
            project_name = ""
            if (
                case_file.project_id
                and hasattr(case_file, "project")
                and case_file.project
            ):
                project_name = case_file.project.name or ""
            elif not case_file.project_id:
                # For unapproved projects, use the name from unapproved project or case file description
                project_name = UNAPPROVED_PROJECT_NAME

            case_file_dict = {
                "Case File #": case_file.case_file_number or "",
                "Project": project_name,
                "Initiation": case_file.initiation.name or "",
                "Date Created": (
                    case_file.created_date.strftime("%Y-%m-%d")
                    if case_file.created_date
                    else ""
                ),
                "Status": (
                    case_file.case_file_status.value
                    if case_file.case_file_status
                    else ""
                ),
                "Primary": (
                    f"{case_file.primary_officer.first_name} {case_file.primary_officer.last_name}"
                    if case_file.primary_officer
                    else ""
                ),
            }
            case_files_data.append(case_file_dict)

        # Create DataFrame
        data_frame = pd.DataFrame(case_files_data)

        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            data_frame.to_excel(writer, sheet_name="Case Files", index=False)

        output.seek(0)
        return output.getvalue()

    @classmethod
    def get_by_id(cls, case_file_id: int):
        """Return case file by id."""
        case_file = CaseFileModel.find_by_id(case_file_id)
        return _set_project_parameters(case_file)

    @classmethod
    def get_other_officers(cls, case_file_id: int):
        """Return other officers associated with a given case file."""
        officers = CaseFileOfficerModel.get_all_by_case_file_id(case_file_id)
        return [
            case_file_officer.officer
            for case_file_officer in officers
            if case_file_officer.officer
        ]

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
                created_case_file.id,
                created_case_file.case_file_number,
                "created",
                [created_case_file.case_file_number],
            )
            ContinuationReportService.create(
                cr_entry, sys_generated=True, ho_session=session
            )
        return created_case_file

    @classmethod
    def update(cls, case_file_id: int, case_file_data: dict, ho_session=None):
        """Update case file."""
        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            return None
        _case_file_close_check(case_file)
        _access_check_for_update(case_file)
        case_file_obj = {
            "primary_officer_id": case_file_data.get("primary_officer_id", None),
            "project_description": case_file_data.get("project_description", None),
            "is_deleted": case_file_data.get("is_deleted", False),
            "is_active": case_file_data.get("is_active", True),
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

            if not case_file_data.get("project_id", None):
                existing_unapproved_project = (
                    UnapprovedProjectModel.get_by_case_file_id(case_file_id)
                )
                if existing_unapproved_project:
                    unapproved_project_update_data = {
                        "regulated_party": case_file_data.get(
                            "unapproved_project_regulated_party"
                        ),
                        "type": case_file_data.get("unapproved_project_type"),
                        "sub_type": case_file_data.get("unapproved_project_sub_type"),
                    }
                    existing_unapproved_project.update(
                        unapproved_project_update_data, commit=False
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
    def change_case_file_status(cls, case_file_id, status_data):
        """Change the status of the case file."""
        from .continuation_report import ContinuationReportService  # pylint: disable=import-outside-toplevel

        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            raise ResourceNotFoundError("Case file not found.")
        _access_check_for_update(case_file)
        case_file = CaseFileModel.find_by_id(case_file_id)
        status_enum = CaseFileStatusEnum(status_data.get("status"))
        if status_enum == CaseFileStatusEnum.CLOSED:
            close_check = cls.get_open_enforcement_actions(case_file_id)
            if close_check and close_check.get("has_open_items"):
                raise UnprocessableEntityError("The case file contains open items.")
        if status_enum == case_file.case_file_status:
            raise UnprocessableEntityError(
                f"The case file is already in {status_enum.value} status."
            )
        with session_scope() as session:
            CaseFileModel.change_status(case_file_id, status_enum, session)
            cr_entry = _create_cr_entry(
                case_file.id,
                case_file.case_file_number,
                "reopened" if status_enum.value == "Open" else "closed",
                [case_file.case_file_number],
            )
            ContinuationReportService.create(
                cr_entry, sys_generated=True, ho_session=session
            )

    @classmethod
    def link(cls, case_file_id, link):
        """Link the case file to another one of the same project."""
        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            raise ResourceNotFoundError(f"CaseFile with {case_file_id} not found")
        _access_check_for_update(case_file_id)
        case_file = CaseFileModel.find_by_id(case_file_id)
        link_case_file_id = link.get("link_case_file_id")
        link_to_case_file = CaseFileModel.find_by_id(link_case_file_id)
        if not link_to_case_file:
            raise ResourceNotFoundError(f"CaseFile with {link_case_file_id} not found")
        _link_case_file_checks(case_file, case_file_id)
        source_link = CaseFileLinkModel.get_links_by_source_and_target(
            source_id=case_file_id, target_id=link_case_file_id
        )
        if source_link:
            raise UnprocessableEntityError("Given link already exists")
        with session_scope() as session:
            created_link = _create_link(
                source=case_file, target=link_to_case_file, session=session
            )
            target_link = CaseFileLinkModel.get_links_by_source_and_target(
                source_id=link_case_file_id, target_id=case_file_id
            )
            if not target_link:
                _create_link(
                    source=link_to_case_file, target=case_file, session=session
                )
        return created_link

    @classmethod
    def unlink(cls, case_file_id, unlink):
        """Unlink the case file from another case file."""
        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            raise ResourceNotFoundError(f"CaseFile with {case_file_id} not found")
        _case_file_close_check(case_file)
        _access_check_for_update(case_file_id)
        unlink_case_file_id = unlink.get("case_file_to_unlink")
        case_file = CaseFileModel.find_by_id(case_file_id)
        unlink_case_file = CaseFileModel.find_by_id(unlink_case_file_id)
        if not unlink_case_file:
            raise ResourceNotFoundError(
                f"CaseFile with {unlink_case_file_id} not found"
            )
        existing_link = CaseFileLinkModel.get_links_by_source_and_target(
            source_id=case_file_id, target_id=unlink_case_file_id
        )
        if not existing_link:
            raise UnprocessableEntityError("Case file links doesn't exist")
        with session_scope() as session:
            _unlink(source=case_file, target=unlink_case_file, session=session)
            _unlink(source=unlink_case_file, target=case_file, session=session)

    @classmethod
    def get_open_enforcement_actions(cls, case_file_id: int) -> dict:
        """
        Check for any open enforcement actions for a given case file ID.

        Returns a dictionary with lists of open items for each enforcement type.
        """
        # Verify case file exists
        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            raise ResourceNotFoundError(f"Case file with id {case_file_id} not found")

        # Initialize result structure
        open_items = _initialize_open_items_structure()

        # Get case file level items (inspections + complaints)
        inspection_ids = _process_case_level_items(case_file_id, open_items)

        # Get inspection-related enforcement actions
        if inspection_ids:
            _process_enforcement_actions(inspection_ids, open_items)

        # Add summary flag
        open_items["has_open_items"] = any(
            len(items) > 0 for items in open_items.values()
        )

        return open_items

    @classmethod
    def get_linked_case_files(cls, case_file_id):
        """Get all linked case files."""
        linked_case_files = CaseFileLinkModel.get_links_by_source_id(case_file_id)
        links = [link.target for link in linked_case_files]
        return links


def _set_project_parameters(case_file):
    """Set project parameters."""
    if case_file:
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


def _access_check_for_update(case_file):
    """Access check for update."""
    auth_user_guid = g.token_info["preferred_username"]
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
        "primary_officer_id": case_file_data.get("primary_officer_id"),
        "initiation_id": case_file_data.get("initiation_id"),
        "project_description": case_file_data.get("project_description"),
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


def _create_cr_entry(case_file_id, case_file_number, action, keys):
    """Create the continuation report entry."""
    return {
        "case_file_id": case_file_id,
        "text": f"{case_file_number} is {action}",
        "rich_text": f"<p>{case_file_number} is {action}</p>",
        "date_created": datetime.utcnow().strftime(INPUT_DATE_TIME_FORMAT),
        "context_type": ContextEnum.CASE_FILE,
        "context_id": case_file_id,
        "keys": [
            {"key": case_file_number, "key_context": ContextEnum.CASE_FILE}
            for case_file_number in keys
        ],
    }


def _case_file_close_check(case_file):
    """Check and raise error if the case file is in closed status."""
    if case_file.case_file_status == CaseFileStatusEnum.CLOSED:
        raise UnprocessableEntityError(
            "No change is possible as the case file is in CLOSED status"
        )


def _build_case_files_paginated_query(args):
    """Build paginated query for case files with filtering and sorting."""
    # Base query with joins including UnapprovedProject
    query = _build_base_query()

    # Apply filters
    query = _apply_case_file_filters(query, args)

    # Apply sorting
    query = _apply_case_file_sorting(query, args)

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination
    paginated_query = _apply_case_file_pagination(query, args)

    # Execute query and get results
    case_files = paginated_query.all()

    return case_files, total_count


def _build_base_query():
    """Build the base query with all necessary joins."""
    return (
        db.session.query(CaseFileModel)
        .join(
            CaseFileInitiationOptionModel,
            CaseFileModel.initiation_id == CaseFileInitiationOptionModel.id,
        )
        .outerjoin(ProjectModel, CaseFileModel.project_id == ProjectModel.id)
        .outerjoin(
            StaffUserModel, CaseFileModel.primary_officer_id == StaffUserModel.id
        )
        .outerjoin(
            UnapprovedProjectModel,
            CaseFileModel.id == UnapprovedProjectModel.case_file_id,
        )
        .filter(CaseFileModel.is_deleted.is_(False), CaseFileModel.is_active.is_(True))
    )


def _apply_case_file_filters(query, args):
    """Apply filters to the case file query based on arguments."""
    filters = []

    # Case file number filter
    case_file_number = args.get("case_file_number")
    if case_file_number:
        filters.append(CaseFileModel.case_file_number.ilike(f"%{case_file_number}%"))

    # Project IDs filter
    if args.get("project_ids"):
        filters.append(CaseFileModel.project_id.in_(args["project_ids"].split(",")))

    # Initiation IDs filter
    if args.get("initiation_ids"):
        filters.append(
            CaseFileModel.initiation_id.in_(args["initiation_ids"].split(","))
        )

    # Statuses filter
    if args.get("statuses"):
        statuses = [s.upper().strip() for s in args["statuses"].split(",")]
        filters.append(CaseFileModel.case_file_status.in_(statuses))

    # Primary officer IDs filter
    if args.get("primary_officer_ids"):
        filters.append(
            CaseFileModel.primary_officer_id.in_(args["primary_officer_ids"].split(","))
        )

    # Date created filter
    date_created = args.get("date_created")
    if date_created:
        filters.append(func.date(CaseFileModel.date_created) == date_created)

    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))

    return query


def _apply_case_file_sorting(query, args):
    """Apply sorting to the case file query."""
    sort_by = args.get("sort_by", "case_file_number")
    sort_order = args.get("sort_order", "asc").lower()

    if sort_by == "case_file_number":
        sort_field = CaseFileModel.case_file_number
    elif sort_by == "project":
        sort_field = ProjectModel.name
    elif sort_by == "initiation":
        sort_field = CaseFileInitiationOptionModel.name
    elif sort_by == "date_created":
        sort_field = CaseFileModel.date_created
    elif sort_by == "status":
        # Handle enum sorting with sophisticated case expression
        status_order = list(reversed([e.name for e in CaseFileStatusEnum]))
        case_file_status_case = case(
            {status: idx for idx, status in enumerate(status_order)},
            value=cast(CaseFileModel.case_file_status, String),
            else_=len(status_order),
        ).label("case_file_status_order")

        custom_order = (
            case_file_status_case.asc()
            if sort_order == "asc"
            else case_file_status_case.desc()
        )
        return query.order_by(custom_order)
    elif sort_by == "primary_officer":
        sort_field = StaffUserModel.first_name
    else:
        sort_field = CaseFileModel.case_file_number  # Default

    if sort_order == "desc":
        return query.order_by(desc(sort_field))
    return query.order_by(asc(sort_field))


def _apply_case_file_pagination(query, args):
    """Apply pagination to the case file query."""
    page = int(args.get("page_no", 1))
    per_page = int(args.get("page_size", 15))

    return query.offset((page - 1) * per_page).limit(per_page)


def _unlink(source, target, session):
    """Unlink the case file."""
    CaseFileLinkModel.delete_link(
        source_id=source.id, taget_id=target.id, session=session
    )


def _create_link(source, target, session):
    """Create case file link entry."""
    created_link = CaseFileLinkModel.create_link(
        {"source_case_id": source.id, "target_case_id": target.id}, session
    )

    return created_link


def _link_case_file_checks(case_file, case_file_id):
    """Validate case file link."""
    if not case_file:
        raise ResourceNotFoundError(f"Case file with ID: {case_file_id} not found.")
    if case_file.is_active is False or case_file.is_deleted is True:
        raise UnprocessableEntityError(
            f"Case file should be active and non-deleted. Case file number {case_file.case_file_number}"
        )
    if case_file.case_file_status == CaseFileStatusEnum.CLOSED:
        raise UnprocessableEntityError(
            f"Closed case file cannot be linked. Case file number {case_file.case_file_number}"
        )


def _build_enforcement_item(item, item_type):
    """Build a standardized enforcement action item dictionary."""
    base_item = {"id": item.id, "inspection_id": getattr(item, "inspection_id", None)}

    # Add type-specific fields using generic 'number' field
    if item_type == "inspection":
        base_item.update(
            {
                "number": item.ir_number,
                "status": item.inspection_status.value,
                "inspection_id": None,  # Inspections don't have inspection_id
            }
        )
    elif item_type == "complaint":
        status_obj = None
        if item.status:
            status_obj = {"id": item.status.name, "name": item.status.value}
        base_item.update(
            {
                "number": item.complaint_number,
                "status": status_obj,
                "inspection_id": None,  # Complaints don't have inspection_id
            }
        )
    elif item_type == "order":
        base_item.update({"number": item.order_number, "status": item.status.value})
    elif item_type == "warning_letter":
        base_item.update(
            {"number": item.warning_letter_number, "progress": item.progress.value}
        )
    elif item_type == "violation_ticket":
        base_item.update(
            {
                "number": item.violation_ticket_number,
                "status": item.status.value if item.status else "Issued",
            }
        )
    elif item_type == "administrative_penalty":
        base_item.update(
            {
                "number": item.administrative_penalty_number,
                "referral_status": (
                    item.referral_status.value if item.referral_status else "Drafting"
                ),
            }
        )
    elif item_type == "charge_recommendation":
        base_item.update(
            {"number": item.charge_recommendation_number, "status": item.status.value}
        )
    elif item_type == "restorative_justice":
        base_item.update(
            {"number": item.restorative_justice_number, "status": item.status.value}
        )

    return base_item


# Local helper functions for get_open_enforcement_actions
def _initialize_open_items_structure() -> dict:
    """Initialize the open items result structure."""
    return {
        "inspections": [],
        "complaints": [],
        "orders": [],
        "warning_letters": [],
        "violation_tickets": [],
        "administrative_penalties": [],
        "charge_recommendations": [],
        "restorative_justice": [],
    }


def _process_case_level_items(case_file_id: int, open_items: dict) -> list:
    """Process case file level items (inspections + complaints) and return inspection IDs."""
    # Query for all inspections and open complaints
    case_level_query = _build_case_level_query(case_file_id)

    all_inspection_ids = []
    processed_complaints = set()

    # Process results
    for row in case_level_query:
        if row.inspection_id:
            all_inspection_ids.append(row.inspection_id)
            # Only add to open_items if inspection is not closed, canceled, or closed as note
            if row.inspection_status not in [
                InspectionStatusEnum.CLOSED,
                InspectionStatusEnum.CANCELED,
                InspectionStatusEnum.CLOSE_AS_NOTE,
            ]:
                open_items["inspections"].append(_build_inspection_item(row))

        if row.complaint_id and row.complaint_id not in processed_complaints:
            processed_complaints.add(row.complaint_id)
            open_items["complaints"].append(_build_complaint_item(row))

    # Handle complaints-only case files
    if not all_inspection_ids:
        _process_complaints_only(case_file_id, processed_complaints, open_items)

    return all_inspection_ids


def _build_case_level_query(case_file_id: int):
    """Build the case file level query for all inspections and open complaints."""
    return (
        db.session.query(
            InspectionModel.id.label("inspection_id"),
            InspectionModel.ir_number,
            InspectionModel.inspection_status,
            ComplaintModel.id.label("complaint_id"),
            ComplaintModel.complaint_number,
            ComplaintModel.status.label("complaint_status"),
        )
        .select_from(InspectionModel)
        .outerjoin(
            ComplaintModel,
            and_(
                ComplaintModel.case_file_id == case_file_id,
                ComplaintModel.status != ComplaintStatusEnum.CLOSED,
                ComplaintModel.is_active.is_(True),
                ComplaintModel.is_deleted.is_(False),
            ),
        )
        .filter(
            and_(
                InspectionModel.case_file_id == case_file_id,
                InspectionModel.is_active.is_(True),
                InspectionModel.is_deleted.is_(False),
            )
        )
        .all()
    )


def _process_complaints_only(
    case_file_id: int, processed_complaints: set, open_items: dict
):
    """Handle case files that have only complaints (no inspections)."""
    complaints_only_query = ComplaintModel.query.filter(
        and_(
            ComplaintModel.case_file_id == case_file_id,
            ComplaintModel.status != ComplaintStatusEnum.CLOSED,
            ComplaintModel.is_active.is_(True),
            ComplaintModel.is_deleted.is_(False),
        )
    ).all()

    for complaint in complaints_only_query:
        if complaint.id not in processed_complaints:
            open_items["complaints"].append(
                _build_enforcement_item(complaint, "complaint")
            )


def _build_inspection_item(row) -> dict:
    """Build inspection item following schema."""
    status_obj = None
    if row.inspection_status:
        status_obj = {
            "id": row.inspection_status.name,
            "name": row.inspection_status.value,
        }

    return {
        "id": row.inspection_id,
        "inspection_id": row.inspection_id,
        "number": row.ir_number,
        "status": status_obj,
    }


def _build_complaint_item(row) -> dict:
    """Build complaint item following schema."""
    status_obj = None
    if row.complaint_status:
        status_obj = {
            "id": row.complaint_status.name,
            "name": row.complaint_status.value,
        }

    return {
        "id": row.complaint_id,
        "inspection_id": None,
        "number": row.complaint_number,
        "status": status_obj,
    }


def _process_enforcement_actions(inspection_ids: list, open_items: dict):
    """Process all inspection-related enforcement actions."""
    enforcement_query = _build_enforcement_query(inspection_ids)

    processed_items = {
        "orders": set(),
        "warning_letters": set(),
        "violation_tickets": set(),
        "administrative_penalties": set(),
        "charge_recommendations": set(),
        "restorative_justice": set(),
    }

    for row in enforcement_query:
        _process_enforcement_row(row, processed_items, open_items)


def _build_enforcement_query(inspection_ids: list):
    """Build the enforcement actions query with all joins."""
    return (
        db.session.query(
            # Inspection
            InspectionModel.ir_number,
            # Orders
            OrderModel.id.label("order_id"),
            OrderModel.order_number,
            OrderModel.order_status,
            OrderModel.inspection_id.label("order_inspection_id"),
            # Warning Letters
            WarningLetterModel.id.label("warning_letter_id"),
            WarningLetterModel.warning_letter_number,
            WarningLetterModel.progress.label("warning_letter_progress"),
            WarningLetterModel.inspection_id.label("warning_letter_inspection_id"),
            # Violation Tickets
            ViolationTicketModel.id.label("violation_ticket_id"),
            ViolationTicketModel.vt_number,
            ViolationTicketModel.status.label("violation_ticket_status"),
            ViolationTicketModel.inspection_id.label("violation_ticket_inspection_id"),
            # Administrative Penalties
            AdministrativePenaltyModel.id.label("admin_penalty_id"),
            AdministrativePenaltyModel.administrative_penalty_number,
            AdministrativePenaltyModel.referral_status.label(
                "admin_penalty_referral_status"
            ),
            AdministrativePenaltyModel.inspection_id.label(
                "admin_penalty_inspection_id"
            ),
            # Charge Recommendations
            ChargeRecommendationModel.id.label("charge_rec_id"),
            ChargeRecommendationModel.charge_recommendation_number,
            ChargeRecommendationModel.status.label("charge_rec_status"),
            ChargeRecommendationModel.inspection_id.label("charge_rec_inspection_id"),
            # Restorative Justice
            RestorativeJusticeModel.id.label("restorative_justice_id"),
            RestorativeJusticeModel.restorative_justice_number,
            RestorativeJusticeModel.status.label("restorative_justice_status"),
            RestorativeJusticeModel.inspection_id.label(
                "restorative_justice_inspection_id"
            ),
        )
        .select_from(InspectionModel)
        .outerjoin(
            OrderModel,
            and_(
                OrderModel.inspection_id == InspectionModel.id,
                OrderModel.order_status.notin_(
                    [OrderStatusEnum.OPEN, OrderStatusEnum.CLOSED, OrderStatusEnum.RESCINDED]
                ),
                OrderModel.is_active.is_(True),
                OrderModel.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            WarningLetterModel,
            and_(
                WarningLetterModel.inspection_id == InspectionModel.id,
                WarningLetterModel.progress != WarningLetterProgressEnum.ISSUED,
                WarningLetterModel.is_active.is_(True),
                WarningLetterModel.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            ViolationTicketModel,
            and_(
                ViolationTicketModel.inspection_id == InspectionModel.id,
                ViolationTicketModel.status.notin_(
                    [
                        ViolationTicketStatusEnum.PAID,
                        ViolationTicketStatusEnum.DISPUTED,
                        ViolationTicketStatusEnum.DEEMED_GUILTY,
                    ]
                ),
                ViolationTicketModel.is_active.is_(True),
                ViolationTicketModel.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            AdministrativePenaltyModel,
            and_(
                AdministrativePenaltyModel.inspection_id == InspectionModel.id,
                # Use centralized open AP filter condition
                AdministrativePenaltyModel.get_open_ap_filter_condition(),
                AdministrativePenaltyModel.is_active.is_(True),
                AdministrativePenaltyModel.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            ChargeRecommendationModel,
            and_(
                ChargeRecommendationModel.inspection_id == InspectionModel.id,
                not_(
                    or_(
                        ChargeRecommendationModel.status
                        == ChargeRecommendationStatusEnum.CEB_NOT_PROCEEDING,
                        and_(
                            ChargeRecommendationModel.charge_decision.isnot(None),
                            ChargeRecommendationModel.charge_decision
                            == ChargeDecisionEnum.NOT_PROCEEDING,
                        ),
                        ChargeRecommendationModel.sentence_date.isnot(None),
                    )
                ),
                ChargeRecommendationModel.is_active.is_(True),
                ChargeRecommendationModel.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            RestorativeJusticeModel,
            and_(
                RestorativeJusticeModel.inspection_id == InspectionModel.id,
                RestorativeJusticeModel.status != RestorativeJusticeStatusEnum.CLOSED,
                RestorativeJusticeModel.is_active.is_(True),
                RestorativeJusticeModel.is_deleted.is_(False),
            ),
        )
        .filter(InspectionModel.id.in_(inspection_ids))
        .all()
    )


def _process_enforcement_row(row, processed_items: dict, open_items: dict):
    """Process a single row from the enforcement query."""
    # Process Orders
    if row.order_id and row.order_id not in processed_items["orders"]:
        processed_items["orders"].add(row.order_id)
        open_items["orders"].append(_build_order_item(row))

    # Process Warning Letters
    if (
        row.warning_letter_id
        and row.warning_letter_id not in processed_items["warning_letters"]
    ):
        processed_items["warning_letters"].add(row.warning_letter_id)
        open_items["warning_letters"].append(_build_warning_letter_item(row))

    # Process Violation Tickets
    if (
        row.violation_ticket_id
        and row.violation_ticket_id not in processed_items["violation_tickets"]
    ):
        open_items["violation_tickets"].append(_build_violation_ticket_item(row))

    # Process Administrative Penalties
    if (
        row.admin_penalty_id
        and row.admin_penalty_id not in processed_items["administrative_penalties"]
    ):
        processed_items["administrative_penalties"].add(row.admin_penalty_id)
        open_items["administrative_penalties"].append(_build_admin_penalty_item(row))

    # Process Charge Recommendations
    if (
        row.charge_rec_id
        and row.charge_rec_id not in processed_items["charge_recommendations"]
    ):
        processed_items["charge_recommendations"].add(row.charge_rec_id)
        open_items["charge_recommendations"].append(_build_charge_rec_item(row))

    # Process Restorative Justice
    if (
        row.restorative_justice_id
        and row.restorative_justice_id not in processed_items["restorative_justice"]
    ):
        processed_items["restorative_justice"].add(row.restorative_justice_id)
        open_items["restorative_justice"].append(_build_restorative_justice_item(row))


def _build_order_item(row) -> dict:
    """Build order item following schema."""
    status_obj = None
    if row.order_status:
        status_obj = {"id": row.order_status.name, "name": row.order_status.value}

    return {
        "id": row.order_id,
        "inspection_id": row.order_inspection_id,
        "ir_number": row.ir_number,
        "number": row.order_number,
        "status": status_obj,
    }


def _build_warning_letter_item(row) -> dict:
    """Build warning letter item following schema."""
    status_obj = None
    if row.warning_letter_progress:
        status_obj = {
            "id": row.warning_letter_progress.name,
            "name": row.warning_letter_progress.value,
        }

    return {
        "id": row.warning_letter_id,
        "inspection_id": row.warning_letter_inspection_id,
        "ir_number": row.ir_number,
        "number": row.warning_letter_number,
        "status": status_obj,
    }


def _build_violation_ticket_item(row) -> dict:
    """Build violation ticket item following schema."""
    status_obj = None
    if row.violation_ticket_status:
        status_obj = {
            "id": row.violation_ticket_status.name,
            "name": row.violation_ticket_status.value,
        }

    return {
        "id": row.violation_ticket_id,
        "inspection_id": row.violation_ticket_inspection_id,
        "ir_number": row.ir_number,
        "number": row.vt_number,
        "status": status_obj,
    }


def _build_admin_penalty_item(row) -> dict:
    """Build administrative penalty item following schema."""
    status_obj = None
    if row.admin_penalty_referral_status:
        status_obj = {
            "id": row.admin_penalty_referral_status.name,
            "name": row.admin_penalty_referral_status.value,
        }

    return {
        "id": row.admin_penalty_id,
        "inspection_id": row.admin_penalty_inspection_id,
        "ir_number": row.ir_number,
        "number": row.administrative_penalty_number,
        "status": status_obj,
    }


def _build_charge_rec_item(row) -> dict:
    """Build charge recommendation item following schema."""
    status_obj = None
    if row.charge_rec_status:
        status_obj = {
            "id": row.charge_rec_status.name,
            "name": row.charge_rec_status.value,
        }

    return {
        "id": row.charge_rec_id,
        "inspection_id": row.charge_rec_inspection_id,
        "ir_number": row.ir_number,
        "number": row.charge_recommendation_number,
        "status": status_obj,
    }


def _build_restorative_justice_item(row) -> dict:
    """Build restorative justice item following schema."""
    status_obj = None
    if row.restorative_justice_status:
        status_obj = {
            "id": row.restorative_justice_status.name,
            "name": row.restorative_justice_status.value,
        }

    return {
        "id": row.restorative_justice_id,
        "inspection_id": row.restorative_justice_inspection_id,
        "ir_number": row.ir_number,
        "number": row.restorative_justice_number,
        "status": status_obj,
    }
