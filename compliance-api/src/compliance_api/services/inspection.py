# pylint: disable=too-many-lines
"""Service for managing Inspection."""

from io import BytesIO

import pandas as pd
from sqlalchemy import String, and_, asc, case, cast, desc, func
from sqlalchemy.orm import aliased

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
from compliance_api.models import InspectionRecordApproval as InspectionRecordApprovalModel
from compliance_api.models import InspectionReqEnforcementMap as InspectionReqEnforcementMapModel
from compliance_api.models import InspectionRequirement as InspectionRequirementModel
from compliance_api.models import InspectionStatusEnum
from compliance_api.models import InspectionType as InspectionTypeModel
from compliance_api.models import InspectionTypeOption as InspectionTypeOptionModel
from compliance_api.models import IRStatusOption as IRStatusOptionModel
from compliance_api.models import Order as OrderModel
from compliance_api.models import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models import OrderProgressEnum
from compliance_api.models import ViolationTicket as ViolationTicketModel
from compliance_api.models import WarningLetter as WarningLetterModel
from compliance_api.models import db
from compliance_api.models.administrative_penalty import AdministrativePenalty as AdministrativePenaltyModel
from compliance_api.models.administrative_penalty import \
    AdministrativePenaltyInspectionRequirementMap as AdministrativePenaltyInspectionRequirementMapModel
from compliance_api.models.case_file import CaseFile
from compliance_api.models.charge_recommendation import ChargeRecommendation as ChargeRecommendationModel
from compliance_api.models.charge_recommendation import \
    ChargeRecommendationInspectionRequirementMap as ChargeRecommendationInspectionRequirementMapModel
from compliance_api.models.compliance_finding import ComplianceFindingOptionEnum
from compliance_api.models.db import session_scope
from compliance_api.models.enforcement_action import EnforcementActionOption as EnforcementActionOptionModel
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection_record import InspectionRecord, IRProgressEnum
from compliance_api.models.order import OrderStatusEnum
from compliance_api.models.project import Project as ProjectModel
from compliance_api.models.restorative_justice import RestorativeJustice as RestorativeJusticeModel
from compliance_api.models.restorative_justice import \
    RestorativeJusticeInspectionRequirementMap as RestorativeJusticeInspectionRequirementMapModel
from compliance_api.models.staff_user import StaffUser
from compliance_api.models.violation_ticket import \
    ViolationTicketInspectionRequirementMap as ViolationTicketInspectionRequirementMapModel
from compliance_api.models.warning_letter import \
    WarningLetterInspectionRequirementMap as WarningLetterInspectionRequirementMapModel
from compliance_api.models.warning_letter import WarningLetterStatusEnum
from compliance_api.services.case_file import CaseFileService
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.utils.constant import UNAPPROVED_PROJECT_NAME
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
        """Get inspection details with optimized bulk fetching.

        Uses a single optimized query to fetch all enforcement actions and build
        requirement details, eliminating multiple database calls and iterations.
        """
        inspections = InspectionModel.get_by_params({"case_file_id": case_file_id}, sort_by="ir_number")

        if not inspections:
            return []

        # Get all inspection IDs for bulk fetching
        inspection_ids = [inspection.id for inspection in inspections]

        # Bulk fetch all enforcement actions AND requirement details in one query
        inspection_data = _bulk_fetch_enforcement_actions_and_requirement_details(
            inspection_ids
        )

        # Attach requirement details to each inspection
        for inspection in inspections:
            data = inspection_data.get(inspection.id, {"requirement_details": []})
            setattr(inspection, "requirement_details", data["requirement_details"])
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
        #  pylint: disable=import-outside-toplevel
        from .inspection_record.inspection_record import InspectionRecordService

        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError(f"Inspection with ID {inspection_id} not found")
        ServiceUtils.inspection_status_check(inspection)
        ServiceUtils.access_check_update_for_inspection(inspection)
        inspection_obj = _create_inspection_update_obj(inspection_data)
        with session_scope() as session:
            #  If the history flag is explicitly changed, delete the inspection record if one already created
            if "is_history" in inspection_data and inspection.is_history != inspection_obj.get("is_history", False):
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

        # Check for pending items before closing inspection
        if status_enum == InspectionStatusEnum.CLOSED:
            pending_items = cls.get_pending_items(inspection_id)
            _validate_inspection_can_be_closed(pending_items)

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

        def _execute_deletion(session):
            """Execute the actual deletion logic."""
            InspectionModel.delete_by_case_file(case_file_id, session)
            InspectionAgencyModel.delete_by_case_file(case_file_id, session)
            InspectionAttendanceModel.delete_by_case_file(case_file_id, session)
            InspectionFirstnationModel.delete_by_case_file(case_file_id, session)
            InspectionOfficerModel.delete_by_case_file(case_file_id, session)
            InspectionTypeModel.delete_by_case_file(case_file_id, session)

        if ho_session:
            # Use the provided session from outer transaction
            _execute_deletion(ho_session)
        else:
            # Create own session scope when no session is provided
            with session_scope() as session:
                _execute_deletion(session)

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

    @classmethod
    def get_pending_items(cls, inspection_id: int):  # pylint: disable=too-many-locals
        """Get pending items for an inspection (optimized with single query).

        Returns a list of items (enforcement actions, inspection records) that are mapped to requirements
        or the inspection but not yet created or not in proper status.
        """
        pending_items = []
        seen_item_numbers = set()

        # Check if inspection record is pending (separate query)
        pending_inspection_record = _get_pending_inspection_record(inspection_id)
        if pending_inspection_record is not None:
            pending_items.append(pending_inspection_record)

        # OPTIMIZATION: Single query with all outer joins to fetch everything at once
        # Aliases for clarity
        req = aliased(InspectionRequirementModel)
        enf_map = aliased(InspectionReqEnforcementMapModel)
        enf_action = aliased(EnforcementActionOptionModel)
        order_map = aliased(OrderInspectionRequirementMapModel)
        order = aliased(OrderModel)
        wl_map = aliased(WarningLetterInspectionRequirementMapModel)
        warning_letter = aliased(WarningLetterModel)
        ap_map = aliased(AdministrativePenaltyInspectionRequirementMapModel)
        vt_map = aliased(ViolationTicketInspectionRequirementMapModel)
        cr_map = aliased(ChargeRecommendationInspectionRequirementMapModel)

        # Build the comprehensive query
        results = (
            db.session.query(
                req.id.label("requirement_id"),
                req.summary.label("requirement_summary"),
                enf_action.id.label("enforcement_action_id"),
                enf_action.name.label("enforcement_action_name"),
                order.order_number.label("order_number"),
                order.order_status.label("order_status"),
                warning_letter.warning_letter_number.label("warning_letter_number"),
                warning_letter.status.label("warning_letter_status"),
                order_map.id.label("order_map_id"),
                wl_map.id.label("wl_map_id"),
                ap_map.id.label("ap_map_id"),
                vt_map.id.label("vt_map_id"),
                cr_map.id.label("cr_map_id"),
            )
            .select_from(req)
            .join(
                enf_map,
                and_(
                    enf_map.requirement_id == req.id,
                    enf_map.is_active.is_(True),
                    enf_map.is_deleted.is_(False),
                ),
            )
            .join(enf_action, enf_action.id == enf_map.enforcement_action_id)
            .outerjoin(
                order_map,
                and_(
                    order_map.inspection_requirement_id == req.id,
                    enf_map.enforcement_action_id
                    == EnforcementActionOptionEnum.ORDER.value,
                    order_map.is_active.is_(True),
                    order_map.is_deleted.is_(False),
                ),
            )
            .outerjoin(order, order.id == order_map.order_id)
            .outerjoin(
                wl_map,
                and_(
                    wl_map.inspection_requirement_id == req.id,
                    enf_map.enforcement_action_id
                    == EnforcementActionOptionEnum.WARNING_LETTER.value,
                    wl_map.is_active.is_(True),
                    wl_map.is_deleted.is_(False),
                ),
            )
            .outerjoin(warning_letter, warning_letter.id == wl_map.warning_letter_id)
            .outerjoin(
                ap_map,
                and_(
                    ap_map.inspection_requirement_id == req.id,
                    enf_map.enforcement_action_id
                    == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
                    ap_map.is_active.is_(True),
                    ap_map.is_deleted.is_(False),
                ),
            )
            .outerjoin(
                vt_map,
                and_(
                    vt_map.inspection_requirement_id == req.id,
                    enf_map.enforcement_action_id
                    == EnforcementActionOptionEnum.VIOLATION_TICKET.value,
                    vt_map.is_active.is_(True),
                    vt_map.is_deleted.is_(False),
                ),
            )
            .outerjoin(
                cr_map,
                and_(
                    cr_map.inspection_requirement_id == req.id,
                    enf_map.enforcement_action_id
                    == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value,
                    cr_map.is_active.is_(True),
                    cr_map.is_deleted.is_(False),
                ),
            )
            .filter(
                req.inspection_id == inspection_id,
                req.is_active.is_(True),
                req.is_deleted.is_(False),
            )
            .all()
        )

        # Process results in-memory
        for row in results:
            enforcement_status = _process_enforcement_status(
                row.enforcement_action_id,
                row.order_map_id,
                row.order_number,
                row.order_status,
                row.wl_map_id,
                row.warning_letter_number,
                row.warning_letter_status,
                row.ap_map_id,
                row.vt_map_id,
                row.cr_map_id,
            )

            if enforcement_status is not None:
                item_number = enforcement_status.get("item_number")

                # Skip duplicates (multiple requirements can map to same order/warning letter)
                if item_number and item_number in seen_item_numbers:
                    continue

                item = {
                    "requirement": {
                        "id": row.requirement_id,
                        "summary": row.requirement_summary,
                    },
                    "item": {
                        "id": row.enforcement_action_id,
                        "name": row.enforcement_action_name,
                    },
                    "is_created": enforcement_status["is_created"],
                    "item_number": item_number,
                }
                if enforcement_status.get("is_issued", None) is not None:
                    item["is_issued"] = enforcement_status["is_issued"]

                pending_items.append(item)

                # Track this item_number to prevent duplicates
                if item_number:
                    seen_item_numbers.add(item_number)

        return pending_items


def _validate_inspection_can_be_closed(pending_items: list):
    """Validate that an inspection can be closed by checking for pending items.

    Args:
        pending_items (list): The list of pending items

    Raises:
        UnprocessableEntityError: If there are pending items that prevent closure
    """
    if pending_items and len(pending_items) > 0:
        # Filter items that are not created or not issued
        blocking_items = []
        for item in pending_items:
            if not item.get("is_created", True):
                blocking_items.append(f"{item['item']['name']} is not created")
            elif item.get("is_issued") is not None and not item.get("is_issued"):
                blocking_items.append(f"{item['item']['name']} is not issued")

        if blocking_items:
            blocking_message = ". ".join(blocking_items)
            raise UnprocessableEntityError(
                f"Cannot close inspection. The following items are incomplete: {blocking_message}"
            )


def _handle_close_as_note(inspection, session):
    """Handle Close as Note to File by updating requirements and inspection record.

    Mark compliance finding as 'Not Determined' and Enforcement action as 'Not Applicable' unless the
    Enforcement action is 'Order' and is issued.
    Delete the inspection record if it was created.
    Args:
        inspection (InspectionModel): Inspection model.
        session (Session): Database session.
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
    # Soft delete inspection record and approvals
    inspection_record = InspectionRecord.query.filter_by(inspection_id=inspection.id, is_active=True).first()
    if inspection_record:
        approvals = InspectionRecordApprovalModel.get_approvals_by_ir(inspection_record.id)
        if approvals:
            for approval in approvals:
                InspectionRecordApprovalModel.update_approval(
                    approval_id=approval.id,
                    approval_update_data={"is_deleted": True, "is_active": False},
                    session=session,
                )
        InspectionRecord.update_inspection_record(
            inspection_record_id=inspection_record.id,
            ir_update_data={"is_deleted": True, "is_active": False},
            session=session,
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


def _set_restorative_justice_enforcement_action_object(
    enforcement_action: dict,
    restorative_justice: RestorativeJusticeModel,
):
    """Make restorative justice detail object."""
    enforcement_action["status"] = (
        {
            "id": restorative_justice.status.name,
            "name": restorative_justice.status.value,
        }
        if restorative_justice.status
        else None
    )
    enforcement_action["number"] = restorative_justice.restorative_justice_number
    return enforcement_action


def _set_warning_letter_enforcement_action_object(
    enforcement_action: dict,
    warning_letter: WarningLetterModel,
):
    """Make warning letter detail object."""
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


def _set_order_enforcement_action_object(enforcement_action: dict, order: OrderModel):
    """Make order detail object."""
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
    violation_ticket: ViolationTicketModel,
):
    """Make violation ticket detail object."""
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
    administrative_penalty: AdministrativePenaltyModel,
):
    """Make administrative penalty detail object."""
    enforcement_action["status"] = (
        {
            "id": administrative_penalty.referral_status.name,
            "name": administrative_penalty.referral_status.value,
        }
        if administrative_penalty.referral_status
        else None
    )
    enforcement_action["number"] = administrative_penalty.administrative_penalty_number
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
        "area_inspected": inspection_data.get("area_inspected", None),
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
        "area_inspected": inspection_data.get("area_inspected", None),
    }


def _create_inspection_record_number(
    project_id: int, case_file_id
):  # pylint: disable=inconsistent-return-statements
    """Generate the inspection record number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    if project_code is None:
        raise UnprocessableEntityError(
            "Given project doesn't have an abbreviation. Check Epic.Track for more details"
        )
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file doesn't match")

    pattern = rf"^{project_code}_{case_file.case_file_number}_IR[0-9]{{3}}$"
    count = InspectionModel.get_latest_ir_number_count(
        case_file_id, project_id, pattern
    )
    serial_number = f"{count:03}"
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
            InspectionStatusEnum(status.strip())
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


def _set_charge_recommendation_enforcement_action_object(
    enforcement_action: dict, charge_recommendation: ChargeRecommendationModel
):
    """Make charge recommendation detail object."""
    enforcement_action["status"] = (
        {
            "id": charge_recommendation.status.name,
            "name": charge_recommendation.status.value,
        }
        if charge_recommendation.status
        else None
    )
    enforcement_action["number"] = charge_recommendation.charge_recommendation_number
    return enforcement_action


def _build_query_for_enforcement_actions_and_requirement_details(inspection_ids):
    """Build the query for bulk fetching enforcement actions and requirement details."""
    # pylint: disable=invalid-name,too-many-locals
    # Create aliases for mapping tables
    order_map_alias = aliased(OrderInspectionRequirementMapModel)
    warning_letter_map_alias = aliased(WarningLetterInspectionRequirementMapModel)
    violation_ticket_map_alias = aliased(ViolationTicketInspectionRequirementMapModel)
    administrative_penalty_map_alias = aliased(
        AdministrativePenaltyInspectionRequirementMapModel
    )
    charge_recommendation_map_alias = aliased(
        ChargeRecommendationInspectionRequirementMapModel
    )
    restorative_justice_map_alias = aliased(
        RestorativeJusticeInspectionRequirementMapModel
    )

    # Create alias for enforcement action mapping
    enforcement_action_map_alias = aliased(InspectionReqEnforcementMapModel)

    # Create alias for enforcement action option (to get the name)
    enforcement_action_option_alias = aliased(EnforcementActionOptionModel)

    # Create aliases for enforcement tables
    order_alias = aliased(OrderModel)
    warning_letter_alias = aliased(WarningLetterModel)
    violation_ticket_alias = aliased(ViolationTicketModel)
    administrative_penalty_alias = aliased(AdministrativePenaltyModel)
    charge_recommendation_alias = aliased(ChargeRecommendationModel)
    restorative_justice_alias = aliased(RestorativeJusticeModel)

    # Single query starting from InspectionRequirement as the main entity
    # We'll access inspection_id from the requirement object itself
    results = (
        db.session.query(InspectionRequirementModel)
        .add_columns(
            enforcement_action_map_alias.enforcement_action_id.label(
                "enforcement_action_id"
            ),
            enforcement_action_option_alias.name.label("enforcement_action_name"),
            order_alias,  # Model objects cannot use .label()
            warning_letter_alias,
            violation_ticket_alias,
            administrative_penalty_alias,
            charge_recommendation_alias,
            restorative_justice_alias,
        )
        .filter(
            InspectionRequirementModel.inspection_id.in_(inspection_ids),
            InspectionRequirementModel.is_active.is_(True),
            InspectionRequirementModel.is_deleted.is_(False),
        )
        .outerjoin(
            enforcement_action_map_alias,
            and_(
                enforcement_action_map_alias.requirement_id
                == InspectionRequirementModel.id,
                enforcement_action_map_alias.is_active.is_(True),
                enforcement_action_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            enforcement_action_option_alias,
            and_(
                enforcement_action_option_alias.id
                == enforcement_action_map_alias.enforcement_action_id,
                enforcement_action_option_alias.is_active.is_(True),
                enforcement_action_option_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            order_map_alias,
            and_(
                order_map_alias.inspection_requirement_id
                == InspectionRequirementModel.id,
                order_map_alias.is_active.is_(True),
                order_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            order_alias,
            and_(
                order_alias.id == order_map_alias.order_id,
                order_alias.is_active.is_(True),
                order_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            warning_letter_map_alias,
            and_(
                warning_letter_map_alias.inspection_requirement_id
                == InspectionRequirementModel.id,
                warning_letter_map_alias.is_active.is_(True),
                warning_letter_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            warning_letter_alias,
            and_(
                warning_letter_alias.id == warning_letter_map_alias.warning_letter_id,
                warning_letter_alias.is_active.is_(True),
                warning_letter_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            violation_ticket_map_alias,
            and_(
                violation_ticket_map_alias.inspection_requirement_id
                == InspectionRequirementModel.id,
                violation_ticket_map_alias.is_active.is_(True),
                violation_ticket_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            violation_ticket_alias,
            and_(
                violation_ticket_alias.id
                == violation_ticket_map_alias.violation_ticket_id,
                violation_ticket_alias.is_active.is_(True),
                violation_ticket_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            administrative_penalty_map_alias,
            and_(
                administrative_penalty_map_alias.inspection_requirement_id
                == InspectionRequirementModel.id,
                administrative_penalty_map_alias.is_active.is_(True),
                administrative_penalty_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            administrative_penalty_alias,
            and_(
                administrative_penalty_alias.id
                == administrative_penalty_map_alias.administrative_penalty_id,
                administrative_penalty_alias.is_active.is_(True),
                administrative_penalty_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            charge_recommendation_map_alias,
            and_(
                charge_recommendation_map_alias.inspection_requirement_id
                == InspectionRequirementModel.id,
                charge_recommendation_map_alias.is_active.is_(True),
                charge_recommendation_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            charge_recommendation_alias,
            and_(
                charge_recommendation_alias.id
                == charge_recommendation_map_alias.charge_recommendation_id,
                charge_recommendation_alias.is_active.is_(True),
                charge_recommendation_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            restorative_justice_map_alias,
            and_(
                restorative_justice_map_alias.inspection_requirement_id
                == InspectionRequirementModel.id,
                restorative_justice_map_alias.is_active.is_(True),
                restorative_justice_map_alias.is_deleted.is_(False),
            ),
        )
        .outerjoin(
            restorative_justice_alias,
            and_(
                restorative_justice_alias.id
                == restorative_justice_map_alias.restorative_justice_id,
                restorative_justice_alias.is_active.is_(True),
                restorative_justice_alias.is_deleted.is_(False),
            ),
        )
        .all()
    )
    return results


def initialize_result_data(inspection_ids):
    """Initialize the result data structure for _bulk_fetch_enforcement_actions_and_requirement_details."""
    result_data = {}
    # Initialize data structure for each inspection
    for inspection_id in inspection_ids:
        result_data[inspection_id] = {
            "enforcement_actions": {
                "orders": [],
                "warning_letters": [],
                "violation_tickets": [],
                "administrative_penalties": [],
                "charge_recommendations": [],
                "restorative_justice": [],
            },
            "requirement_details": [],
        }
    return result_data


def _bulk_fetch_enforcement_actions_and_requirement_details(
    inspection_ids,
):  # pylint: disable=too-many-locals,too-many-branches
    """Bulk fetch all enforcement actions and build requirement details in a single optimized query.

    Returns a dict with two keys per inspection:
    - 'enforcement_actions': dict of enforcement lists (orders, warning_letters, etc.)
    - 'requirement_details': list of requirement detail objects
    """
    result_data = initialize_result_data(inspection_ids)

    if not inspection_ids:
        return result_data

    results = _build_query_for_enforcement_actions_and_requirement_details(
        inspection_ids
    )

    for row in results:
        requirement = row[0]  # InspectionRequirementModel
        enforcement_action_id = row.enforcement_action_id
        enforcement_action_name = row.enforcement_action_name
        order = row[3]  # OrderAlias
        warning_letter = row[4]  # WarningLetterAlias
        violation_ticket = row[5]  # ViolationTicketAlias
        administrative_penalty = row[6]  # AdministrativePenaltyAlias
        charge_recommendation = row[7]  # ChargeRecommendationAlias
        restorative_justice = row[8]  # RestorativeJusticeAlias

        inspection_id = requirement.inspection_id

        enforcement_data = result_data[inspection_id]["enforcement_actions"]

        if order is not None and order not in enforcement_data["orders"]:
            enforcement_data["orders"].append(order)

        if (
            warning_letter is not None
            and warning_letter not in enforcement_data["warning_letters"]
        ):
            enforcement_data["warning_letters"].append(warning_letter)

        if (
            violation_ticket is not None
            and violation_ticket not in enforcement_data["violation_tickets"]
        ):
            enforcement_data["violation_tickets"].append(violation_ticket)

        if (
            administrative_penalty is not None
            and administrative_penalty
            not in enforcement_data["administrative_penalties"]
        ):
            enforcement_data["administrative_penalties"].append(administrative_penalty)

        if (
            charge_recommendation is not None
            and charge_recommendation not in enforcement_data["charge_recommendations"]
        ):
            enforcement_data["charge_recommendations"].append(charge_recommendation)

        if (
            restorative_justice is not None
            and restorative_justice not in enforcement_data["restorative_justice"]
        ):
            enforcement_data["restorative_justice"].append(restorative_justice)

        # Build base requirement detail item
        item = {
            "requirement_id": requirement.id,
            "requirement_summary": requirement.summary,
            "requirement_sort_order": requirement.sort_order,
            "enforcement_action": {
                "id": enforcement_action_id,
                "name": enforcement_action_name,  # From query join, no DB call needed!
            },
        }

        # Add requirement source details if available
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

        # Set enforcement-specific details based on type (if available)
        action_type = None
        if enforcement_action_id is not None:
            action_type = EnforcementActionOptionEnum(enforcement_action_id)

        if action_type == EnforcementActionOptionEnum.ORDER and order:
            item["enforcement_action"] = _set_order_enforcement_action_object(
                item["enforcement_action"], order
            )
        elif (
            action_type == EnforcementActionOptionEnum.WARNING_LETTER and warning_letter
        ):
            item["enforcement_action"] = _set_warning_letter_enforcement_action_object(
                item["enforcement_action"], warning_letter
            )
        elif (
            action_type == EnforcementActionOptionEnum.VIOLATION_TICKET
            and violation_ticket
        ):
            item["enforcement_action"] = (
                _set_violation_ticket_enforcement_action_object(
                    item["enforcement_action"], violation_ticket
                )
            )
        elif (
            action_type
            == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION
            and administrative_penalty
        ):
            item["enforcement_action"] = (
                _set_administrative_penalty_enforcement_action_object(
                    item["enforcement_action"], administrative_penalty
                )
            )
        elif (
            action_type == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION
            and charge_recommendation
        ):
            item["enforcement_action"] = (
                _set_charge_recommendation_enforcement_action_object(
                    item["enforcement_action"], charge_recommendation
                )
            )
        elif (
            action_type == EnforcementActionOptionEnum.RESTORATIVE_JUSTICE
            and restorative_justice
        ):
            item["enforcement_action"] = (
                _set_restorative_justice_enforcement_action_object(
                    item["enforcement_action"], restorative_justice
                )
            )

        result_data[inspection_id]["requirement_details"].append(item)
    # Sort requirement details by sort order
    for inspection_id, data in result_data.items():
        data["requirement_details"].sort(
            key=lambda x: (
                x["requirement_sort_order"] is None,
                x["requirement_sort_order"],
            )
        )
    return result_data


def _process_enforcement_status(  # pylint: disable=too-many-return-statements,too-many-branches
    enforcement_action_id: int,
    order_map_id,
    order_number,
    order_status,
    wl_map_id,
    warning_letter_number,
    warning_letter_status,
    ap_map_id,
    vt_map_id,
    cr_map_id,
):
    """Process enforcement status from query results (optimized in-memory processing).

    Args:
        enforcement_action_id: ID of the enforcement action
        order_map_id: Order mapping ID (None if not mapped)
        order_number: Order number (None if no order)
        order_status: Order status (None if no order)
        wl_map_id: Warning letter mapping ID (None if not mapped)
        warning_letter_number: Warning letter number (None if no warning letter)
        warning_letter_status: Warning letter status (None if no warning letter)
        ap_map_id: Administrative penalty mapping ID (None if not mapped)
        vt_map_id: Violation ticket mapping ID (None if not mapped)
        cr_map_id: Charge recommendation mapping ID (None if not mapped)

    Returns:
        Dict with status info or None if not a pending item
    """
    if enforcement_action_id == EnforcementActionOptionEnum.ORDER.value:
        if not order_map_id:
            return {"is_created": False, "item_number": None}
        if not order_number:
            return {"is_created": False, "item_number": None}
        if order_status in [OrderStatusEnum.CLOSED, OrderStatusEnum.RESCINDED]:
            return None
        if order_status != OrderStatusEnum.OPEN:
            return {"is_created": True, "item_number": order_number, "is_issued": False}
        return None

    if enforcement_action_id == EnforcementActionOptionEnum.WARNING_LETTER.value:
        if not wl_map_id:
            return {"is_created": False, "item_number": None}
        if not warning_letter_number:
            return {"is_created": False, "item_number": None}
        if warning_letter_status != WarningLetterStatusEnum.ISSUED:
            return {
                "is_created": True,
                "item_number": warning_letter_number,
                "is_issued": False,
            }
        return None

    if (
        enforcement_action_id
        == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value
    ):
        if not ap_map_id:
            return {"is_created": False, "item_number": None}
        return None

    if enforcement_action_id == EnforcementActionOptionEnum.VIOLATION_TICKET.value:
        if not vt_map_id:
            return {"is_created": False, "item_number": None}
        return None

    if (
        enforcement_action_id == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value
    ):
        if not cr_map_id:
            return {"is_created": False, "item_number": None}
        return None

    return None


def _check_inspection_record_status(inspection_id: int):
    """Check inspection record status for an inspection."""
    inspection_record = InspectionRecord.get_by_inspection_id(inspection_id)

    if not inspection_record:
        return {
            "is_created": False,
            "ir_number": None,
            "ir_id": None,
        }

    # Check if inspection record is issued (IRProgressEnum.ISSUED)
    is_issued = inspection_record.ir_progress == IRProgressEnum.ISSUED

    return {
        "is_created": True,
        "is_issued": is_issued,
        "ir_number": getattr(inspection_record.inspection, "ir_number", None),
        "ir_id": inspection_record.id,
    }


def _get_pending_inspection_record(inspection_id: int):
    """Get pending inspection record if not issued."""
    inspection_record_status = _check_inspection_record_status(inspection_id)

    return {
        "requirement": None,  # Inspection record applies to the whole inspection
        "item": {
            "id": inspection_record_status.get("ir_id"),
            "name": "Inspection Record",
        },
        "is_created": inspection_record_status.get("is_created"),
        "is_issued": inspection_record_status.get("is_issued", None),
        "item_number": inspection_record_status.get("ir_number"),
    }
