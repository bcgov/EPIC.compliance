"""ContinuationReport Service."""

from io import BytesIO

from flask import g

from compliance_api.auth import auth
from compliance_api.exceptions import PermissionDeniedError, ResourceNotFoundError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.continuation_report import ContinuationReport as ContinuationReportModel
from compliance_api.models.continuation_report import ContinuationReportKey as ContinuationReportKeyModel
from compliance_api.models.db import session_scope
from compliance_api.services.case_file import CaseFileService
from compliance_api.services.docgen_service.docgen_service import DocGenService
from compliance_api.utils.enum import PermissionEnum


class ContinuationReportService:
    """ContinuationReportService."""

    @classmethod
    def create(cls, report_entry: dict, sys_generated: bool = False, ho_session=None):
        """Create continuation report entry."""
        _access_check(report_entry)
        case_file = CaseFileModel.find_by_id(report_entry.get("case_file_id"))
        if not case_file:
            raise ResourceNotFoundError("Case file not found.")
        report_entry_obj = _create_report_entry(report_entry, sys_generated)
        with session_scope() as session:
            created_entry = ContinuationReportModel.create_entry(
                report_entry_obj, ho_session or session
            )
            keys = report_entry.get("keys", [])
            _insert_or_update_keys(created_entry.id, keys, ho_session or session)
        return created_entry

    @classmethod
    def update(cls, entry_id, report_entry: dict):
        """Update continuation report entry."""
        entry = ContinuationReportModel.find_by_id(entry_id)
        if not entry:
            return None
        _access_check_update_delete(entry.case_file_id, entry.created_by)
        with session_scope() as session:
            updated_entry = ContinuationReportModel.update_entry(
                entry_id, report_entry, session
            )
            keys = report_entry.get("keys", [])
            _insert_or_update_keys(entry_id, keys, session)
        return updated_entry

    @classmethod
    def delete(cls, entry_id):
        """Delete continuation report entry."""
        entry = ContinuationReportModel.find_by_id(entry_id)
        _access_check_update_delete(entry.case_file_id, entry.created_by)
        if not entry:
            return None
        with session_scope() as session:
            deleted_entry = ContinuationReportModel.update_entry(
                entry_id, {"is_deleted": True, "is_active": False}, session
            )
            _insert_or_update_keys(entry_id, [], session)
        return deleted_entry

    @classmethod
    def delete_by_case_file(cls, case_file_id, ho_session=None):
        """Delete continuation report entries by case file id."""

        def _execute_deletion(session):
            """Execute the actual deletion logic."""
            ContinuationReportModel.delete_by_case_file(case_file_id, session)
            ContinuationReportKeyModel.delete_keys_by_case_file(case_file_id, session)

        if ho_session:
            # Use the provided session from outer transaction
            _execute_deletion(ho_session)
        else:
            # Create own session scope when no session is provided
            with session_scope() as session:
                _execute_deletion(session)

    @classmethod
    def delete_by_context(cls, context_id, context_type, ho_session=None):
        """
        Delete continuation report entries by context.

        :param context_id: The unique ID of the context type.
        :param context_type: One of the context_type enums.
        :param ho_session: SQLAlchemy session object (optional).
        """
        with session_scope() as session:
            ContinuationReportModel.delete_by_context(context_id, context_type, session)
            ContinuationReportKeyModel.delete_keys_by_context(
                context_id, context_type, ho_session or session
            )

    @classmethod
    def get_by_case_file_id(cls, case_file_id, page_no, page_size, search_text):
        """Get all crs by case file id."""
        return ContinuationReportModel.get_by_case_file_paginated(
            case_file_id, page_no, page_size, search_text
        )

    @classmethod
    def render(cls, case_file_number):
        """Export continuation report as PDF."""
        if case_file_number is None:
            raise ValueError("Case file number must be provided.")

        if case_file_number:
            case_file = CaseFileService.get_by_file_number(case_file_number)

        if not case_file:
            raise ResourceNotFoundError("Case file not found.")

        data = _get_report_data(case_file)
        response = DocGenService.render_template("CONTINUATION_REPORT_TEMPLATE", data, "pdf")
        return BytesIO(response.content)


def _access_check(report_entry: dict):
    """Access check."""
    if not auth.has_permission(
        [PermissionEnum.SUPERUSER]
    ) and not _is_logged_user_primary_or_officer(report_entry.get("case_file_id")):
        raise PermissionDeniedError(
            "You don't have the correct permission to perform this operation."
        )


def _access_check_update_delete(case_file_id, created_by):
    """Access check for update."""
    auth_user_guid = g.token_info["preferred_username"]
    if auth.has_permission([PermissionEnum.SUPERUSER]):
        return
    if auth_user_guid == created_by and _is_logged_user_primary_or_officer(
        case_file_id
    ):
        return
    raise PermissionDeniedError(
        "You don't have the correct permission to perform this operation."
    )


def _is_logged_user_primary_or_officer(case_file_id):
    """Check to see if the given user is primary or other officer in the case file."""
    auth_user_guid = g.token_info["preferred_username"]
    case_file = CaseFileModel.find_by_id(case_file_id)
    #  The logged in user should be primary or officer in the associated
    #  case file
    return case_file.primary_officer.auth_user_guid == auth_user_guid or any(
        officer.officer.auth_user_guid == auth_user_guid
        for officer in case_file.case_file_officers
    )


def _insert_or_update_keys(report_id, keys, session=None):
    """Insert or update keys for continuatino report."""
    existing_keys = ContinuationReportKeyModel.get_by_report_id(report_id)
    existing_keys = {entry.key for entry in existing_keys if entry.is_active is True}

    new_keys = {key.get("key") for key in keys}
    keys_to_be_deleted = existing_keys.difference(new_keys)
    keysto_be_added = new_keys.difference(existing_keys)
    if keys_to_be_deleted:
        ContinuationReportKeyModel.bulk_delete(
            report_id, list(keys_to_be_deleted), session
        )
    if keysto_be_added:
        key_objects = [key for key in keys if key.get("key") in keysto_be_added]
        ContinuationReportKeyModel.bulk_insert(report_id, key_objects, session)


def _create_report_entry(report_entry_data: dict, sys_generated: bool = False):
    """Create the report entry object."""
    text = report_entry_data.get("text")
    return {
        "case_file_id": report_entry_data.get("case_file_id"),
        "text": text,
        "rich_text": report_entry_data.get("rich_text"),
        "date_created": report_entry_data.get("date_created"),
        "system_generated": sys_generated,
        "context_type": report_entry_data.get("context_type"),
        "context_id": report_entry_data.get("context_id"),
    }


def _get_report_data(case_file):
    """Get the data for continuation report."""
    continuation_report = ContinuationReportModel.get_all_by_case_file(case_file.id)
    data = {
        "project_name": case_file.project.name if case_file.project else "",
        "case_file_number": case_file.case_file_number,
        "primary_officer": (
            f"{case_file.primary_officer.first_name} {case_file.primary_officer.last_name}"
            if case_file.primary_officer
            else ""
        ),
        "authorization": case_file.authorization,
        "other_officers": [
            f"{cfo.officer.first_name} {cfo.officer.last_name}" for cfo in case_file.case_file_officers
        ],
        "continuation_report_entries": [
            {
                "date": entry.date_created.strftime("%Y-%m-%d"),
                "time": entry.date_created.strftime("%H:%M"),
                "action": _build_action_text(entry),
            }
            for entry in continuation_report
        ]
    }
    return data


def _build_action_text(entry):
    """Build action text with creator info if not system-generated."""
    action = entry.text
    if not entry.system_generated and entry.created_by_user:
        action += f" <i>Created by {entry.created_by_user.first_name} {entry.created_by_user.last_name}</i>"
    return action
