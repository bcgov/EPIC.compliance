# pylint: disable=too-many-lines
"""Service for managing Inspection."""

from io import BytesIO

import pandas as pd
from sqlalchemy import String, and_, asc, case, cast, desc, func

from compliance_api.auth import auth
from compliance_api.exceptions import (
    BusinessError, PermissionDeniedError, ResourceNotFoundError, UnprocessableEntityError)
from compliance_api.models import CaseFile as CaseFileModel
from compliance_api.models import CaseFileStatusEnum
from compliance_api.models import Inspection as InspectionModel
from compliance_api.models import InspectionAgency as InspectionAgencyModel
from compliance_api.models import InspectionAttendance as InspectionAttendanceModel
from compliance_api.models import InspectionAttendanceOption as InspectionAttendanceOptionModel
from compliance_api.models import InspectionAttendanceOptionEnum
from compliance_api.models import InspectionFirstnation as InspectionFirstnationModel
from compliance_api.models import InspectionInitiationOption as InspectionInitiationOptionModel
from compliance_api.models import InspectionOfficer as InspectionOfficerModel
from compliance_api.models import InspectionReqEnforcementMap as InspectionReqEnforcementMapModel
from compliance_api.models import InspectionRequirement as InspectionRequirementModel
from compliance_api.models import InspectionStatusEnum
from compliance_api.models import InspectionType as InspectionTypeModel
from compliance_api.models import InspectionTypeOption as InspectionTypeOptionModel
from compliance_api.models import IRStatusOption as IRStatusOptionModel
from compliance_api.models import Order as OrderModel
from compliance_api.models import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models import OrderProgressEnum, OrderReplaceStatusEnum
from compliance_api.models import ViolationTicket as ViolationTicketModel
from compliance_api.models import WarningLetter as WarningLetterModel
from compliance_api.models import db
from compliance_api.models.administrative_penalty import AdministrativePenalty as AdministrativePenaltyModel
from compliance_api.models.case_file import CaseFile
from compliance_api.models.charge_recommendation import ChargeRecommendation as ChargeRecommendationModel
from compliance_api.models.compliance_finding import ComplianceFindingOptionEnum
from compliance_api.models.db import session_scope
from compliance_api.models.enforcement_action import EnforcementActionOption as EnforcementActionOptionModel
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection_record import InspectionRecord, IRProgressEnum
from compliance_api.models.project import Project as ProjectModel
from compliance_api.models.restorative_justice import RestorativeJustice as RestorativeJusticeModel
from compliance_api.models.staff_user import StaffUser
from compliance_api.services.case_file import CaseFileService
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.utils.constant import UNAPPROVED_PROJECT_CODE, UNAPPROVED_PROJECT_NAME
from compliance_api.utils.enum import PermissionEnum

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
    def get_all_inspections(cls):
        """Get all inspections."""
        return InspectionModel.get_all_inspections()

    @classmethod
    def get_inspection_details(cls, case_file_id):
        """Get inspection details with optimized bulk fetching."""
        inspections = InspectionModel.get_by_params({"case_file_id": case_file_id})

        if not inspections:
            return []

        # Get all inspection IDs for bulk fetching enforcement actions
        inspection_ids = [inspection.id for inspection in inspections]

        # Bulk fetch all enforcement actions for all inspections
        enforcement_actions_data = _bulk_fetch_enforcement_actions(inspection_ids)

        # Process each inspection
        for inspection in inspections:
            requirement_details = []
            requirements = inspection.inspection_requirements or []
            enforcement_actions = enforcement_actions_data.get(
                inspection.id,
                {
                    "orders": [],
                    "warning_letters": [],
                    "violation_tickets": [],
                    "administrative_penalties": [],
                    "charge_recommendations": [],
                    "restorative_justice": [],
                },
            )
            requirement_details = _make_requirement_detail_object_optimized(
                requirements, enforcement_actions
            )
            setattr(inspection, "requirement_details", requirement_details)
        return inspections

    @classmethod
    def get_by_case_file_id(cls, case_file_id):
        """Get all inspections by case file id."""
        return InspectionModel.get_by_params({"case_file_id": case_file_id})

    @classmethod
    def get_by_id(cls, inspection_id):
        """Return inspection by id."""
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            return None
        return _set_project_status(inspection)

    @classmethod
    def get_by_ir_number(cls, ir_number):
        """Return inspection by ir number."""
        inspection = InspectionModel.get_by_ir_number(ir_number)
        if not inspection:
            raise ResourceNotFoundError(
                f"No inspection found for the given IR Number : {ir_number}"
            )
        return _set_project_status(inspection)

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
                    == InspectionAttendanceOptionEnum.ATTENDING_OFFICERS.value
                ):
                    officers = InspectionOfficerModel.get_all_by_inspection(
                        inspection_id
                    )
                    data = []
                    for officer in officers:
                        # Use stored position if available, otherwise fall back to current position
                        position_data = None
                        if officer.officer_position:
                            position_data = {
                                "id": officer.officer_position.id,
                                "name": officer.officer_position.name,
                            }
                        elif officer.officer.position:
                            position_data = {
                                "id": officer.officer.position.id,
                                "name": officer.officer.position.name,
                            }

                        data.append(
                            {
                                "id": officer.officer.id,
                                "name": f"{officer.officer.first_name} {officer.officer.last_name}",
                                "auth_user_guid": officer.officer.auth_user_guid,
                                "position": position_data,
                            }
                        )
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
                    == InspectionAttendanceOptionEnum.OTHER.value
                ):
                    if option.other:
                        data = option.other
                setattr(option, "data", data)
        return attendance_options

    @classmethod
    def create(cls, inspection_data: dict):
        """Create inspection."""
        case_file_id = inspection_data.get("case_file_id")
        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            raise UnprocessableEntityError("Case file doesn't exist")
        if case_file.case_file_status == CaseFileStatusEnum.CLOSED:
            raise UnprocessableEntityError(
                "Inspection cannot be created with closed case file"
            )
        _access_check_create(inspection_data)
        inspection_obj = _create_inspection_object(inspection_data, case_file)
        with session_scope() as session:
            created_inspection = InspectionModel.create_inspection(
                inspection_obj, session
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
                inspection_data.get("attending_officer_ids", []),
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
            if InspectionAttendanceOptionEnum.OTHER.value in attendance_option_ids:
                other_text = inspection_data.get("attendance_other")
                if other_text:
                    # Update the other field for the OTHER attendance option
                    InspectionAttendanceModel.update_other_attendance(
                        created_inspection.id, other_text, session
                    )
        return created_inspection

    @classmethod
    def update(cls, inspection_id: int, inspection_data: dict):
        """Update inspection."""
        from compliance_api.services import InspectionRecordService  # pylint: disable=import-outside-toplevel

        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError(f"Inspection with ID {inspection_id} not found")
        ServiceUtils.inspection_status_check(inspection)
        ServiceUtils.access_check_update_for_inspection(inspection)
        inspection_obj = _create_inspection_update_obj(inspection_data)
        with session_scope() as session:
            #  If the history flag is changed, delete the inspection record if one already created
            if inspection.is_history != inspection_obj.get("is_history", False):
                inspection_record = InspectionRecordService.get_by_inspection_id(
                    inspection.id
                )
                if inspection_record:
                    InspectionRecordService.delete_inspection_record(
                        inspection.id, inspection_record.id, session
                    )
            updated_case_file = InspectionModel.update_inspection(
                inspection_id, inspection_obj, session
            )
            _insert_or_update_inspection_relationship(
                inspection_id,
                inspection_data.get("attending_officer_ids", []),
                InspectionOfficerModel,
                "officer_id",
                session,
            )
            _insert_or_update_inspection_relationship(
                inspection_id,
                inspection_data.get("inspection_type_ids", []),
                InspectionTypeModel,
                "type_id",
                session,
            )
            attendance_option_ids = inspection_data.get("attendance_option_ids", [])
            _insert_or_update_inspection_relationship(
                inspection_id,
                attendance_option_ids,
                InspectionAttendanceModel,
                "attendance_option_id",
                session,
            )
            _insert_or_update_inspection_relationship(
                inspection_id,
                inspection_data.get("agency_attendance_ids", []),
                InspectionAgencyModel,
                "agency_id",
                session,
            )
            if InspectionAttendanceOptionEnum.OTHER.value in attendance_option_ids:
                other_text = inspection_data.get("attendance_other")
                if other_text:
                    # Update the other field for the OTHER attendance option
                    InspectionAttendanceModel.update_other_attendance(
                        inspection_id, other_text, session
                    )
            _insert_or_update_inspection_relationship(
                inspection_id,
                inspection_data.get("firstnation_attendance_ids", []),
                InspectionFirstnationModel,
                "firstnation_id",
                session,
            )
        return updated_case_file

    @classmethod
    def change_status(cls, inspection_id, status):
        """Close the inspection."""
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError(f"Inspection with ID {inspection_id} not found")
        ServiceUtils.access_check_update_for_inspection(inspection)
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError("Inspection not found.")
        status_enum = InspectionStatusEnum(status.get("status"))
        possible_statuses = {
            InspectionStatusEnum.OPEN: [
                InspectionStatusEnum.CLOSED,
                InspectionStatusEnum.CLOSE_AS_NOTE,
                InspectionStatusEnum.CANCELED,
            ],
            InspectionStatusEnum.CLOSED: [InspectionStatusEnum.OPEN],
            InspectionStatusEnum.CLOSE_AS_NOTE: [InspectionStatusEnum.OPEN],
        }
        if inspection.inspection_status == InspectionStatusEnum.CANCELED:
            raise UnprocessableEntityError(
                "No status change can be perforemed on CANCELED inspection"
            )
        if status_enum not in possible_statuses[inspection.inspection_status]:
            raise UnprocessableEntityError("Invalid status change")
        with session_scope() as session:
            InspectionModel.update_inspection(
                inspection_id,
                {"inspection_status": InspectionStatusEnum(status_enum.value)},
                session,
            )
            if status_enum == InspectionStatusEnum.CLOSE_AS_NOTE:
                _handle_close_as_note(inspection, session)

    @classmethod
    def delete_by_case_file(cls, case_file_id, ho_session=None):
        """Delete inspection and related entries by case file id."""
        with session_scope() as session:
            InspectionModel.delete_by_case_file(case_file_id, ho_session or session)
            InspectionAgencyModel.delete_by_case_file(
                case_file_id, ho_session or session
            )
            InspectionAttendanceModel.delete_by_case_file(
                case_file_id, ho_session or session
            )
            InspectionFirstnationModel.delete_by_case_file(
                case_file_id, ho_session or session
            )
            InspectionOfficerModel.delete_by_case_file(
                case_file_id, ho_session or session
            )
            InspectionTypeModel.delete_by_case_file(case_file_id, ho_session or session)

    @classmethod
    def delete_inspection(cls, inspection_id):
        """Delete inspection."""
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError(f"Inspection with ID {inspection_id} not found")
        with session_scope() as session:
            InspectionModel.delete_inspection(inspection_id, session)
            InspectionTypeModel.delete_inspection_type(inspection_id, session)
            InspectionOfficerModel.delete_inspection_officer(inspection_id, session)
            InspectionFirstnationModel.delete_inspection_firstnation(
                inspection_id, session
            )
            InspectionAttendanceModel.delete_inspection_attendance(
                inspection_id, session
            )
            InspectionAgencyModel.delete_inspection_agency(inspection_id)

    @classmethod
    def get_inspections_paginated(cls, args):
        """Get paginated inspections with filtering and sorting."""
        query = _build_inspections_paginated_query(args)

        # Get total count
        total_count = query.count()

        # Apply pagination
        query = _apply_inspections_pagination(query, args)

        # Execute query and process results
        results = _make_inspection_object(query.all())

        return results, total_count

    @classmethod
    def generate_inspections_excel(cls, args):
        """Generate Excel export for inspections."""
        # Get all matching inspections without pagination
        query = _build_inspections_paginated_query(args)

        # Execute query and process results
        results = _make_inspection_object(query.all())

        # Create Excel data
        excel_data = []
        for inspection in results:
            excel_data.append(
                {
                    "IR #": inspection.ir_number or "",
                    "Project": getattr(inspection, "project_name", "") or "",
                    "Start Date": (
                        inspection.start_date.strftime("%Y-%m-%d")
                        if inspection.start_date
                        else ""
                    ),
                    "Initiation": (
                        inspection.initiation.name if inspection.initiation else ""
                    ),
                    "IR Progress": (
                        inspection.ir_progress.value if inspection.ir_progress else ""
                    ),
                    "Primary": (
                        f"{inspection.primary_officer.first_name} {inspection.primary_officer.last_name}"
                        if inspection.primary_officer
                        else ""
                    ),
                    "Status": (
                        inspection.inspection_status.value
                        if inspection.inspection_status
                        else ""
                    ),
                    "Case File #": (
                        inspection.case_file.case_file_number
                        if inspection.case_file
                        else ""
                    ),
                }
            )

        # Create Excel file
        data_frame = pd.DataFrame(excel_data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            data_frame.to_excel(writer, sheet_name="Inspections", index=False)
        output.seek(0)

        return output


def _handle_close_as_note(inspection, session):
    """Handle close as note.

    Mark compliance finding as 'Not Determined' and
    Enforcement action as 'Not Applicable' unless the
    Enforcement action is 'Order' and is issued
    Args:
        inspection (InspectionModel): Inspection model.
    """
    requirements = InspectionRequirementModel.get_by_inspection_id(inspection.id)
    for requirement in requirements:
        req_enf_maps = InspectionReqEnforcementMapModel.get_all_by_requirement_id(
            requirement.id
        )
        if req_enf_maps:
            if any(
                enf_map.enforcement_action_id == EnforcementActionOptionEnum.ORDER.value
                for enf_map in req_enf_maps
            ):
                req_order_map = (
                    OrderInspectionRequirementMapModel.get_by_requirement_id(
                        requirement.id
                    )
                )
                if (
                    req_order_map
                    and req_order_map.order.order_progress == OrderProgressEnum.ISSUED
                ):
                    #  Retain the enforcement action status if the Order is issued
                    continue
            #  In all other cases, change the enforcement action to 'Not Applicable'
            #  and compliance finding to 'Not Determined'
            enf_action_ids = [enf_map.enforcement_action_id for enf_map in req_enf_maps]
            InspectionReqEnforcementMapModel.bulk_delete(
                requirement.id, enf_action_ids, session
            )
            InspectionReqEnforcementMapModel.bulk_insert(
                requirement.id,
                [EnforcementActionOptionEnum.NOT_APPLICABLE.value],
                session,
            )
            InspectionRequirementModel.update_requirement(
                requirement.id,
                {
                    "compliance_finding_id": ComplianceFindingOptionEnum.NOT_DETERMINED.value
                },
                session,
            )


def _make_inspection_object(inspections):
    """Make inspection object."""
    results = []
    for result in inspections:
        inspection = result.Inspection
        inspection.ir_progress = result.ir_progress
        if inspection.project_id is not None:
            inspection.project_name = inspection.project.name
        else:
            inspection.project_name = UNAPPROVED_PROJECT_NAME
        results.append(inspection)
    return results


def _set_warning_letter_enforcement_action_object(
    enforcement_action: dict,
    warning_letters: list,
    requirement: InspectionRequirementModel,
):
    """Make warning letter detail object."""
    requirement_warning_letters = [
        warning_letter
        for warning_letter in warning_letters
        if requirement.id
        in [
            req_map.inspection_requirement_id
            for req_map in warning_letter.warning_letter_requirement_maps
        ]
    ]
    if requirement_warning_letters:
        warning_letter = requirement_warning_letters[0]
        enforcement_action["progress"] = {
            "id": warning_letter.progress.name,
            "name": warning_letter.progress.value,
        }
        enforcement_action["status"] = {
            "id": warning_letter.status.name,
            "name": warning_letter.status.value,
        }
        if warning_letter.warning_letter_approvals:
            approval_status = warning_letter.warning_letter_approvals[0].approval_status
            enforcement_action["approval_status"] = {
                "id": approval_status.name,
                "name": approval_status.value,
            }
            enforcement_action["number"] = warning_letter.warning_letter_number
    return enforcement_action


def _set_order_enforcement_action_object(
    enforcement_action: dict, orders: list, requirement: InspectionRequirementModel
):
    """Make order detail object."""
    requirement_orders = [
        order
        for order in orders
        if requirement.id
        in [
            req_map.inspection_requirement_id
            for req_map in order.order_requirement_maps
        ]
        and order.order_replace_status == OrderReplaceStatusEnum.ORIGINAL
    ]
    if requirement_orders:
        order = requirement_orders[0]
        enforcement_action["progress"] = {
            "id": order.order_progress.name,
            "name": order.order_progress.value,
        }
        enforcement_action["status"] = {
            "id": order.order_status.name,
            "name": order.order_status.value,
        }
        if order.order_approvals:
            approval_status = order.order_approvals[0].approval_status
            enforcement_action["approval_status"] = {
                "id": approval_status.name,
                "name": approval_status.value,
            }
            enforcement_action["number"] = order.order_number
    return enforcement_action


def _set_violation_ticket_enforcement_action_object(
    enforcement_action: dict,
    violation_tickets: list,
    requirement: InspectionRequirementModel,
):
    """Make violation ticket detail object."""
    requirement_violation_tickets = [
        violation_ticket
        for violation_ticket in violation_tickets
        if requirement.id
        in [
            req_map.inspection_requirement_id
            for req_map in violation_ticket.violation_ticket_requirement_maps
        ]
    ]
    if requirement_violation_tickets:
        violation_ticket = requirement_violation_tickets[0]
        enforcement_action["status"] = (
            {
                "id": violation_ticket.status.name,
                "name": violation_ticket.status.value,
            }
            if violation_ticket.status
            else None
        )
        enforcement_action["number"] = violation_ticket.vt_number
    return enforcement_action


def _set_administrative_penalty_enforcement_action_object(
    enforcement_action: dict,
    administrative_penalties: list,
    requirement: InspectionRequirementModel,
):
    """Make administrative penalty detail object."""
    requirement_administrative_penalties = [
        administrative_penalty
        for administrative_penalty in administrative_penalties
        if requirement.id
        in [
            req_map.inspection_requirement_id
            for req_map in administrative_penalty.administrative_penalty_requirement_maps
        ]
    ]
    if requirement_administrative_penalties:
        administrative_penalty = requirement_administrative_penalties[0]
        # Use referral status as status
        enforcement_action["status"] = (
            {
                "id": administrative_penalty.referral_status.name,
                "name": administrative_penalty.referral_status.value,
            }
            if administrative_penalty.referral_status
            else None
        )
        enforcement_action["number"] = (
            administrative_penalty.administrative_penalty_number
        )
    return enforcement_action


def _access_check_create(inspection_data: dict):
    """Access check."""
    if not auth.has_permission(
        [PermissionEnum.SUPERUSER]
    ) and not CaseFileService.is_logged_user_primary_or_officer(
        inspection_data.get("case_file_id")
    ):
        raise PermissionDeniedError(
            "You don't have the correct permission to perform this operation."
        )


def _set_project_status(inspection):
    """Set inspection project parameters."""
    if inspection.project_status_id:
        project_statuses = TrackService.get_project_statuses()
        status = next(
            (
                stat
                for stat in project_statuses
                if stat["id"] == inspection.project_status_id
            ),
            None,
        )
        if not status:
            raise BusinessError(
                f"No status found with ID {inspection.project_status_id}", 500
            )
        setattr(inspection, "project_status", status)
    return inspection


def _set_first_nation_names(first_nation_list: list):
    """Set the name of the first nations from epic.track."""
    result = []
    for first_nation in first_nation_list:
        response = TrackService.get_first_nation_by_id(first_nation.firstnation_id)
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


def _create_inspection_update_obj(inspection_data: dict):
    """Create inspection update object."""
    return {
        "project_description": inspection_data.get("project_description", None),
        "location_description": inspection_data.get("location_description", None),
        "utm": inspection_data.get("utm", None),
        "primary_officer_id": inspection_data.get("primary_officer_id"),
        "start_date": inspection_data.get("start_date"),
        "is_history": inspection_data.get("is_history", False),
        "end_date": inspection_data.get("end_date"),
        "initiation_id": inspection_data.get("initiation_id"),
        "debrief_date": inspection_data.get("debrief_date", None),
        "project_status_id": inspection_data.get("project_status_id", None),
    }


def _create_inspection_object(inspection_data: dict, case_file):
    """Create inspection object."""
    return {
        "ir_number": _create_inspection_record_number(
            case_file.project_id, case_file.id
        ),
        "case_file_id": case_file.id,
        "project_id": case_file.project_id,
        "project_description": inspection_data.get("project_description", None),
        "location_description": inspection_data.get("location_description", None),
        "utm": inspection_data.get("utm", None),
        "is_history": inspection_data.get("is_history", False),
        "primary_officer_id": inspection_data.get("primary_officer_id"),
        "start_date": inspection_data.get("start_date"),
        "end_date": inspection_data.get("end_date"),
        "initiation_id": inspection_data.get("initiation_id"),
        "debrief_date": inspection_data.get("debrief_date", None),
        "project_status_id": inspection_data.get("project_status_id", None),
        "inspection_status": InspectionStatusEnum.OPEN,
    }


def _create_inspection_record_number(
    project_id: int, case_file_id
):  # pylint: disable=inconsistent-return-statements
    """Generate the inspection record number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file doesn't match")

    count = InspectionModel.get_count_by_project_nd_case_file_id(
        project_id, case_file_id
    )
    serial_number = f"{count + 1:03}"
    return f"{project_code}_{case_file.case_file_number}_IR{serial_number}"


def _build_inspections_paginated_query(args):
    """Build the base query for paginated inspections with filtering and sorting."""
    # Build base query similar to the model's get_all_inspections method
    query = (
        InspectionModel.query.outerjoin(
            InspectionRecord,
            and_(
                InspectionModel.id == InspectionRecord.inspection_id,
                InspectionRecord.is_deleted.is_(False),
                InspectionRecord.is_active.is_(True),
            ),
        )
        .filter(
            InspectionModel.is_deleted.is_(False), InspectionModel.is_active.is_(True)
        )
        .add_columns(
            InspectionRecord.ir_progress.label("ir_progress"),
        )
    )

    # Apply filters
    query = _apply_inspections_filters(query, args)

    # Apply sorting
    query = _apply_inspections_sorting(query, args)

    return query


def _get_basic_filters(args):
    """Get basic inspection filters."""
    filters = []

    # IR number filter
    if args.get("ir_number"):
        filters.append(InspectionModel.ir_number.ilike(f"%{args['ir_number']}%"))

    # Case File ID filter
    if args.get("case_file_id"):
        filters.append(InspectionModel.case_file_id == int(args["case_file_id"]))

    # Start date filter
    if args.get("start_date"):
        filters.append(func.date(InspectionModel.start_date) == args["start_date"])

    # Initiation filter
    if args.get("initiation_ids"):
        filters.append(
            InspectionModel.initiation_id.in_(args["initiation_ids"].split(","))
        )

    # Primary officer filter
    if args.get("primary_officer_ids"):
        filters.append(
            InspectionModel.primary_officer_id.in_(
                args["primary_officer_ids"].split(",")
            )
        )

    return filters


def _get_project_id_filter(args):
    """Get project ID filter with null handling."""
    if not args.get("project_ids"):
        return None

    project_ids = args["project_ids"].split(",")
    if "null" in project_ids or "none" in project_ids:
        return InspectionModel.project_id.is_(None)
    return InspectionModel.project_id.in_(project_ids)


def _get_enum_filters(args):
    """Get enum-based filters."""
    filters = []

    # IR Progress filter
    if args.get("ir_progresses"):
        ir_progress_list = [
            prog.upper().strip() for prog in args["ir_progresses"].split(",")
        ]
        filters.append(InspectionRecord.ir_progress.in_(ir_progress_list))

    # Status filter
    if args.get("statuses"):
        status_enum = [
            InspectionStatusEnum[status.upper().strip()]
            for status in args["statuses"].split(",")
        ]
        filters.append(InspectionModel.inspection_status.in_(status_enum))

    return filters


def _apply_inspections_filters(query, args):
    """Apply filters to the inspections query."""
    filters = []

    # Get basic filters
    filters.extend(_get_basic_filters(args))

    # Get project ID filter
    project_filter = _get_project_id_filter(args)
    if project_filter is not None:
        filters.append(project_filter)

    # Get enum filters
    filters.extend(_get_enum_filters(args))

    # Case file number filter (requires join)
    if args.get("case_file_number"):
        query = query.join(CaseFile, InspectionModel.case_file_id == CaseFile.id)
        filters.append(CaseFile.case_file_number.ilike(f"%{args['case_file_number']}%"))

    if filters:
        query = query.filter(and_(*filters))

    return query


def _apply_inspections_sorting(query, args):
    """Apply sorting to the inspections query."""
    sort_by = args.get("sort_by", "ir_number")
    sort_order = args.get("sort_order", "asc").lower()

    if sort_by == "ir_number":
        sort_field = InspectionModel.ir_number
    elif sort_by == "project":
        # Join with ProjectModel to sort by project name
        query = query.join(
            CaseFileModel, InspectionModel.case_file_id == CaseFileModel.id
        )
        query = query.join(ProjectModel, CaseFileModel.project_id == ProjectModel.id)
        sort_field = ProjectModel.name
    elif sort_by == "start_date":
        sort_field = InspectionModel.start_date
    elif sort_by == "initiation":
        query = query.join(
            InspectionInitiationOptionModel,
            InspectionModel.initiation_id == InspectionInitiationOptionModel.id,
        )
        sort_field = InspectionInitiationOptionModel.name
    elif sort_by == "ir_progress":
        # Handle enum sorting for IR progress - order by enum values (strings)
        progress_order = IRProgressEnum.ordered_values()

        ir_progress_case = case(
            {status: idx for idx, status in enumerate(progress_order)},
            value=func.coalesce(cast(InspectionRecord.ir_progress, String), ""),
            else_=len(progress_order),  # Default to last position (empty string)
        ).label("ir_progress_order")

        custom_order = (
            ir_progress_case.asc() if sort_order == "asc" else ir_progress_case.desc()
        )
        return query.order_by(custom_order)
    elif sort_by == "primary_officer":
        query = query.join(
            StaffUser, InspectionModel.primary_officer_id == StaffUser.id
        )
        sort_field = StaffUser.first_name
    elif sort_by == "status":
        # Handle enum sorting for inspection status
        status_order = list(reversed([e.name for e in InspectionStatusEnum]))
        inspection_status_case = case(
            {status: idx for idx, status in enumerate(status_order)},
            value=cast(InspectionModel.inspection_status, String),
            else_=len(status_order),
        ).label("inspection_status_order")

        custom_order = (
            inspection_status_case.asc()
            if sort_order == "asc"
            else inspection_status_case.desc()
        )
        return query.order_by(custom_order)
    elif sort_by == "case_file_number":
        query = query.join(CaseFile, InspectionModel.case_file_id == CaseFile.id)
        sort_field = CaseFile.case_file_number
    else:
        sort_field = InspectionModel.ir_number  # Default

    if sort_order == "desc":
        return query.order_by(desc(sort_field))
    return query.order_by(asc(sort_field))


def _apply_inspections_pagination(query, args):
    """Apply pagination to the inspections query."""
    page = int(args.get("page_no", 1))
    per_page = int(args.get("page_size", 15))

    return query.offset((page - 1) * per_page).limit(per_page)


def _get_project_abbreviation(
    project_id: int,
):  # pylint: disable=inconsistent-return-statements
    """Return the project abbreviation."""
    if project_id:
        project = TrackService.get_project_by_id(project_id)
        return project.get("abbreviation")
    return UNAPPROVED_PROJECT_CODE


def _set_charge_recommendation_enforcement_action_object(
    enforcement_action: dict,
    charge_recommendations: list,
    requirement: InspectionRequirementModel,
):
    """Make charge recommendation detail object."""
    requirement_charge_recommendations = [
        cr
        for cr in charge_recommendations
        if any(
            cr_map.inspection_requirement_id == requirement.id
            for cr_map in cr.charge_recommendation_requirement_maps
        )
    ]

    if requirement_charge_recommendations:
        charge_recommendation = requirement_charge_recommendations[0]
        enforcement_action["status"] = (
            {
                "id": charge_recommendation.status.name,
                "name": charge_recommendation.status.value,
            }
            if charge_recommendation.status
            else None
        )
        enforcement_action["number"] = (
            charge_recommendation.charge_recommendation_number
        )

    return enforcement_action


def _set_restorative_justice_enforcement_action_object(
    enforcement_action: dict,
    restorative_justice: list,
    requirement: InspectionRequirementModel,
):
    """Make restorative justice detail object."""
    requirement_restorative_justice = [
        rj
        for rj in restorative_justice
        if any(
            rj_map.inspection_requirement_id == requirement.id
            for rj_map in rj.restorative_justice_requirement_maps
        )
    ]

    if requirement_restorative_justice:
        restorative_justice_item = requirement_restorative_justice[0]
        enforcement_action["status"] = (
            {
                "id": restorative_justice_item.status.name,
                "name": restorative_justice_item.status.value,
            }
            if restorative_justice_item.status
            else None
        )
        enforcement_action["number"] = (
            restorative_justice_item.restorative_justice_number
        )

    return enforcement_action


def _bulk_fetch_enforcement_actions(inspection_ids):
    """Bulk fetch all enforcement actions for multiple inspections."""
    enforcement_data = {}

    # Initialize data structure for each inspection
    for inspection_id in inspection_ids:
        enforcement_data[inspection_id] = {
            "orders": [],
            "warning_letters": [],
            "violation_tickets": [],
            "administrative_penalties": [],
            "charge_recommendations": [],
            "restorative_justice": [],
        }

    # Bulk fetch each enforcement action type
    if inspection_ids:
        # Orders
        orders = (
            db.session.query(OrderModel)
            .filter(
                and_(
                    OrderModel.inspection_id.in_(inspection_ids),
                    OrderModel.is_active.is_(True),
                    OrderModel.is_deleted.is_(False),
                )
            )
            .all()
        )
        for order in orders:
            enforcement_data[order.inspection_id]["orders"].append(order)

        # Warning Letters
        warning_letters = (
            db.session.query(WarningLetterModel)
            .filter(
                and_(
                    WarningLetterModel.inspection_id.in_(inspection_ids),
                    WarningLetterModel.is_active.is_(True),
                    WarningLetterModel.is_deleted.is_(False),
                )
            )
            .all()
        )
        for warning_letter in warning_letters:
            enforcement_data[warning_letter.inspection_id]["warning_letters"].append(
                warning_letter
            )

        # Violation Tickets
        violation_tickets = (
            db.session.query(ViolationTicketModel)
            .filter(
                and_(
                    ViolationTicketModel.inspection_id.in_(inspection_ids),
                    ViolationTicketModel.is_active.is_(True),
                    ViolationTicketModel.is_deleted.is_(False),
                )
            )
            .all()
        )
        for violation_ticket in violation_tickets:
            enforcement_data[violation_ticket.inspection_id][
                "violation_tickets"
            ].append(violation_ticket)

        # Administrative Penalties
        admin_penalties = (
            db.session.query(AdministrativePenaltyModel)
            .filter(
                and_(
                    AdministrativePenaltyModel.inspection_id.in_(inspection_ids),
                    AdministrativePenaltyModel.is_active.is_(True),
                    AdministrativePenaltyModel.is_deleted.is_(False),
                )
            )
            .all()
        )
        for admin_penalty in admin_penalties:
            enforcement_data[admin_penalty.inspection_id][
                "administrative_penalties"
            ].append(admin_penalty)

        # Charge Recommendations
        charge_recommendations = (
            db.session.query(ChargeRecommendationModel)
            .filter(
                and_(
                    ChargeRecommendationModel.inspection_id.in_(inspection_ids),
                    ChargeRecommendationModel.is_active.is_(True),
                    ChargeRecommendationModel.is_deleted.is_(False),
                )
            )
            .all()
        )
        for charge_recommendation in charge_recommendations:
            enforcement_data[charge_recommendation.inspection_id][
                "charge_recommendations"
            ].append(charge_recommendation)

        # Restorative Justice
        restorative_justice_items = (
            db.session.query(RestorativeJusticeModel)
            .filter(
                and_(
                    RestorativeJusticeModel.inspection_id.in_(inspection_ids),
                    RestorativeJusticeModel.is_active.is_(True),
                    RestorativeJusticeModel.is_deleted.is_(False),
                )
            )
            .all()
        )
        for restorative_justice_item in restorative_justice_items:
            enforcement_data[restorative_justice_item.inspection_id][
                "restorative_justice"
            ].append(restorative_justice_item)

    return enforcement_data


def _make_requirement_detail_object_optimized(
    requirements: list, enforcement_actions_data: dict
):
    """Make requirement detail object using pre-fetched enforcement actions data."""
    requirement_details = []
    for requirement in requirements:
        if not requirement.enforcement_actions:
            continue

        for action in requirement.enforcement_actions:
            item = {
                "requirement_id": requirement.id,
                "requirement_summary": requirement.summary,
                "requirement_sort_order": requirement.sort_order,
                "enforcement_action": {
                    "id": EnforcementActionOptionModel.find_by_id(
                        action.enforcement_action_id
                    ).id,
                    "name": EnforcementActionOptionModel.find_by_id(
                        action.enforcement_action_id
                    ).name,
                },
            }
            if requirement.requirement_source_details:
                first_requirement_details = requirement.requirement_source_details[0]
                number_field = ServiceUtils.get_requirement_source_number_field(
                    first_requirement_details
                )
                item["requirement_number"] = (
                    number_field.split(" ")[1] if number_field else None
                )
                item["requirement_source_name"] = (
                    first_requirement_details.requirement_source.name
                )

            action_type = EnforcementActionOptionEnum(action.enforcement_action_id)
            if action_type == EnforcementActionOptionEnum.ORDER:
                item["enforcement_action"] = _set_order_enforcement_action_object(
                    item["enforcement_action"],
                    enforcement_actions_data.get("orders", []),
                    requirement,
                )

            elif action_type == EnforcementActionOptionEnum.WARNING_LETTER:
                item["enforcement_action"] = (
                    _set_warning_letter_enforcement_action_object(
                        item["enforcement_action"],
                        enforcement_actions_data.get("warning_letters", []),
                        requirement,
                    )
                )
            elif action_type == EnforcementActionOptionEnum.VIOLATION_TICKET:
                item["enforcement_action"] = (
                    _set_violation_ticket_enforcement_action_object(
                        item["enforcement_action"],
                        enforcement_actions_data.get("violation_tickets", []),
                        requirement,
                    )
                )
            elif (
                action_type
                == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION
            ):
                item["enforcement_action"] = (
                    _set_administrative_penalty_enforcement_action_object(
                        item["enforcement_action"],
                        enforcement_actions_data.get("administrative_penalties", []),
                        requirement,
                    )
                )
            elif action_type == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION:
                item["enforcement_action"] = (
                    _set_charge_recommendation_enforcement_action_object(
                        item["enforcement_action"],
                        enforcement_actions_data.get("charge_recommendations", []),
                        requirement,
                    )
                )
            elif action_type == EnforcementActionOptionEnum.RESTORATIVE_JUSTICE:
                item["enforcement_action"] = (
                    _set_restorative_justice_enforcement_action_object(
                        item["enforcement_action"],
                        enforcement_actions_data.get("restorative_justice", []),
                        requirement,
                    )
                )
            requirement_details.append(item)
    return requirement_details
