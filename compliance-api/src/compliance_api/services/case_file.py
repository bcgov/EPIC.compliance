"""Service for handle CaseFile."""

from datetime import datetime
from io import BytesIO

import pandas as pd
from flask import g
from sqlalchemy import and_, or_, desc, asc, case, cast, String

from compliance_api.auth import auth
from compliance_api.exceptions import (
    PermissionDeniedError, ResourceExistsError, ResourceNotFoundError, UnprocessableEntityError)
from compliance_api.models import CaseFile as CaseFileModel
from compliance_api.models import CaseFileInitiationOption as CaseFileInitiationOptionModel
from compliance_api.models import CaseFileLink as CaseFileLinkModel
from compliance_api.models import CaseFileOfficer as CaseFileOfficerModel
from compliance_api.models import CaseFileStatusEnum
from compliance_api.models import UnapprovedProject as UnapprovedProjectModel
from compliance_api.models.db import db, session_scope
from compliance_api.models.project import Project as ProjectModel
from compliance_api.models.staff_user import StaffUser as StaffUserModel
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
    def generate_case_files_excel(cls, filter_data):
        """Generate case files excel export."""
        # Build query without pagination to get all results
        query = _build_base_query()
        query = _apply_case_file_filters(query, filter_data)
        query = _apply_case_file_sorting(query, filter_data)
        
        # Get all case files without pagination
        case_files = query.all()
        
        # # Batch set project parameters for all case files
        # _set_project_parameters_batch(case_files)
        
        # Convert to list of dictionaries for pandas
        case_files_data = []
        for case_file in case_files:
            # Get project name from the joined project or unapproved project
            project_name = ''
            if case_file.project_id and hasattr(case_file, 'project') and case_file.project:
                project_name = case_file.project.name or ''
            elif not case_file.project_id:
                # For unapproved projects, use the name from unapproved project or case file description
                project_name = UNAPPROVED_PROJECT_NAME
            
            case_file_dict = {
                'Case File #': case_file.case_file_number or '',
                'Project': project_name,
                'Initiation': case_file.initiation.name or '',
                'Date Created': case_file.created_date.strftime('%Y-%m-%d') if case_file.created_date else '',
                'Status': case_file.case_file_status.value if case_file.case_file_status else '',
                'Primary': f"{case_file.primary_officer.first_name} {case_file.primary_officer.last_name}" if case_file.primary_officer else '',
            }
            case_files_data.append(case_file_dict)
        
        # Create DataFrame
        df = pd.DataFrame(case_files_data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Case Files', index=False)
        
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
        _case_file_close_check(case_file)
        _access_check_for_update(case_file_id)
        case_file = CaseFileModel.find_by_id(case_file_id)
        link_case_file_id = link.get("link_case_file_id")
        link_to_case_file = CaseFileModel.find_by_id(link_case_file_id)
        if not link_to_case_file:
            raise ResourceNotFoundError(f"CaseFile with {link_case_file_id} not found")
        _link_case_file_checks(case_file, case_file_id)
        _link_case_file_checks(link_to_case_file, link_case_file_id)
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
    def get_linked_case_files(cls, case_file_id):
        """Get all linked case files."""
        linked_case_files = CaseFileLinkModel.get_links_by_source_id(case_file_id)
        links = [link.target for link in linked_case_files]
        return links


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
    
    # # Batch set project parameters for all case files
    # _set_project_parameters_batch(case_files)
    
    return case_files, total_count


def _build_base_query():
    """Build the base query with all necessary joins."""
    return db.session.query(CaseFileModel)\
        .join(CaseFileInitiationOptionModel, CaseFileModel.initiation_id == CaseFileInitiationOptionModel.id)\
        .outerjoin(ProjectModel, CaseFileModel.project_id == ProjectModel.id)\
        .outerjoin(StaffUserModel, CaseFileModel.primary_officer_id == StaffUserModel.id)\
        .outerjoin(UnapprovedProjectModel, CaseFileModel.id == UnapprovedProjectModel.case_file_id)


def _apply_case_file_filters(query, args):
    """Apply filters to the case file query based on arguments."""
    filters = []
    
    # Case file number filter
    case_file_number = args.get('case_file_number')
    if case_file_number:
        filters.append(CaseFileModel.case_file_number.ilike(f'%{case_file_number}%'))
    
    # Project ID filter (backward compatibility)
    project_id = args.get('project_id')
    if project_id:
        # Handle both regular projects and unapproved projects
        if str(project_id).lower() == 'null' or str(project_id).lower() == 'none':
            filters.append(CaseFileModel.project_id.is_(None))
        else:
            filters.append(CaseFileModel.project_id == project_id)
    
    # Initiation ID filter
    initiation_id = args.get('initiation_id')
    if initiation_id:
        filters.append(CaseFileModel.initiation_id == initiation_id)
    
    # Status filter
    status = args.get('status')
    if status:
        if status.upper() == 'OPEN':
            filters.append(CaseFileModel.case_file_status == CaseFileStatusEnum.OPEN)
        elif status.upper() == 'CLOSE':
            filters.append(CaseFileModel.case_file_status == CaseFileStatusEnum.CLOSED)
    
    # Primary officer filter
    primary_officer_id = args.get('primary_officer_id')
    if primary_officer_id:
        filters.append(CaseFileModel.primary_officer_id == primary_officer_id)
    
    # Date created filter
    date_created = args.get('date_created')
    if date_created:
        target_date = datetime.strptime(date_created, '%Y-%m-%d')
        filters.append(CaseFileModel.date_created == target_date)
    
    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))
    
    return query


def _apply_case_file_sorting(query, args):
    """Apply sorting to the case file query."""
    sort_by = args.get('sort_by', 'case_file_number')
    sort_order = args.get('sort_order', 'asc').lower()
    
    if sort_by == 'case_file_number':
        sort_field = CaseFileModel.case_file_number
    elif sort_by == 'project':
        sort_field = ProjectModel.name
    elif sort_by == 'initiation':
        sort_field = CaseFileInitiationOptionModel.name
    elif sort_by == 'date_created':
        sort_field = CaseFileModel.date_created
    elif sort_by == 'status':
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
    elif sort_by == 'primary_officer':
        sort_field = StaffUserModel.first_name
    else:
        sort_field = CaseFileModel.case_file_number  # Default
    
    if sort_order == 'desc':
        return query.order_by(desc(sort_field))
    else:
        return query.order_by(asc(sort_field))


def _apply_case_file_pagination(query, args):
    """Apply pagination to the case file query."""
    page = int(args.get('page_no', 1))
    per_page = int(args.get('page_size', 15))
    
    return query.offset((page - 1) * per_page).limit(per_page)


def _set_project_parameters_batch(case_files):
    """Set project parameters for multiple case files efficiently."""
    if not case_files:
        return
    
    # Separate case files by project type
    approved_project_ids = []
    case_files_with_projects = []
    case_files_without_projects = []
    
    for case_file in case_files:
        if case_file.project_id:
            approved_project_ids.append(case_file.project_id)
            case_files_with_projects.append(case_file)
        else:
            case_files_without_projects.append(case_file)
    
    # Batch fetch all approved project data if any exist
    projects_lookup = {}
    if approved_project_ids:
        try:
            # Remove duplicates and fetch projects individually (TrackService doesn't have batch method)
            unique_project_ids = list(set(approved_project_ids))
            for project_id in unique_project_ids:
                try:
                    project_data = TrackService.get_project_by_id(project_id)
                    projects_lookup[project_id] = project_data
                except Exception as project_error:
                    # Log individual project fetch error but continue with others
                    print(f"Error fetching project {project_id}: {project_error}")
        except Exception as e:
            # Log error but don't fail the entire operation
            print(f"Error in project batch fetch: {e}")
    
    # Set parameters for approved projects
    for case_file in case_files_with_projects:
        project = projects_lookup.get(case_file.project_id)
        if project:
            setattr(case_file, "authorization", project.get("ea_certificate", None))
            setattr(case_file, "type", project.get("type", {}).get("name"))
            setattr(case_file, "sub_type", project.get("sub_type", {}).get("name"))
            setattr(case_file, "regulated_party", project.get("proponent", {}).get("name"))
    
    # Set parameters for unapproved projects (data already joined in query)
    for case_file in case_files_without_projects:
        # Check if unapproved project data is available from the join
        if hasattr(case_file, 'unapproved_projects') and case_file.unapproved_projects:
            unapproved_project = case_file.unapproved_projects[0]  # Should be only one
            setattr(case_file, "authorization", unapproved_project.authorization)
            setattr(case_file, "type", unapproved_project.type)
            setattr(case_file, "sub_type", unapproved_project.sub_type)
            setattr(case_file, "regulated_party", unapproved_project.regulated_party)
        else:
            # Fallback to individual query if join data not available
            unapproved_project = UnapprovedProjectModel.get_by_case_file_id(case_file.id)
            if unapproved_project:
                setattr(case_file, "authorization", unapproved_project.authorization)
                setattr(case_file, "type", unapproved_project.type)
                setattr(case_file, "sub_type", unapproved_project.sub_type)
                setattr(case_file, "regulated_party", unapproved_project.regulated_party)
