"""ViolationTicket Service."""

from typing import List

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection import InspectionRequirement as InspectionRequirementModel
from compliance_api.models.violation_ticket import ViolationTicket as ViolationTicketModel
from compliance_api.models.violation_ticket import \
    ViolationTicketInspectionRequirementMap as ViolationTicketInspectionRequirementMapModel
from compliance_api.models.violation_ticket import ViolationTicketStatusEnum
from compliance_api.services.service_utils import ServiceUtils


class ViolationTicketService:
    """Service layer for ViolationTicket operations."""

    @classmethod
    def get_all(cls, inspection_id: int = None) -> List[ViolationTicketModel]:
        """Get all violation tickets for an inspection."""
        if inspection_id is None:
            return ViolationTicketModel.get_all()
        return ViolationTicketModel.get_by_params(
            {"inspection_id": inspection_id}, default_filters=False
        )

    @classmethod
    def get_by_id(cls, violation_ticket_id: int) -> ViolationTicketModel:
        """Get violation ticket by id."""
        violation_ticket = ViolationTicketModel.find_by_id(violation_ticket_id)
        if violation_ticket is None:
            raise ResourceNotFoundError(
                f"Violation ticket with ID {violation_ticket_id} not found"
            )
        return violation_ticket

    @classmethod
    def get_by_vt_number(cls, vt_number: str) -> ViolationTicketModel:
        """Get violation ticket by vt number."""
        violation_tickets = ViolationTicketModel.get_by_vt_number(vt_number)
        if not violation_tickets:
            raise ResourceNotFoundError(
                f"Violation ticket with VT number {vt_number} not found"
            )
        return violation_tickets[0]

    @classmethod
    def create(cls, violation_ticket_data: dict) -> ViolationTicketModel:
        """Create a new violation ticket."""
        # Validate inspection exists and perform access/status checks
        inspection_id = violation_ticket_data.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)

        # Validate inspection requirements exist and check enforcement action
        requirement_ids = violation_ticket_data.get("inspection_requirement_ids", [])
        if not requirement_ids:
            raise UnprocessableEntityError(
                "At least one inspection requirement must be specified"
            )

        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids, EnforcementActionOptionEnum.VIOLATION_TICKET.value
        )

        # Create violation ticket object with generated VT number
        violation_ticket_obj = _create_violation_ticket_obj(
            inspection, violation_ticket_data
        )

        # Check if vt_number already exists for other entries in the database
        if ViolationTicketModel.get_by_vt_number(violation_ticket_obj["vt_number"]):
            raise UnprocessableEntityError(
                f"Violation ticket with number {violation_ticket_obj['vt_number']} already exists."
            )

        # Database operations within session scope
        with session_scope() as session:
            # Create the violation ticket
            violation_ticket = ViolationTicketModel.create(
                violation_ticket_obj, session
            )

            # Create inspection requirement mappings
            cls.insert_or_update_inspection_requirements(
                violation_ticket.id, requirement_ids, session
            )

            return violation_ticket

    @classmethod
    def update(
        cls, violation_ticket_id: int, violation_ticket_data: dict
    ) -> ViolationTicketModel:
        """Update a violation ticket."""
        # Find and validate violation ticket exists
        violation_ticket = ViolationTicketModel.find_by_id(violation_ticket_id)
        if violation_ticket is None:
            raise ResourceNotFoundError(
                f"Violation ticket with ID {violation_ticket_id} not found"
            )

        # Perform access and status checks
        ServiceUtils.access_check_update_for_inspection(violation_ticket.inspection)
        # If violation ticket is closed, then check the inspection status
        # No more modification possible once the VT and IR is closed
        if violation_ticket.is_closed:
            ServiceUtils.inspection_status_check(violation_ticket.inspection)

        # Check if violation ticket can be updated based on status
        if violation_ticket.status == ViolationTicketStatusEnum.PAID:
            raise UnprocessableEntityError(
                "Violation ticket cannot be updated as it is already PAID"
            )

        # Handle inspection requirement validation
        requirement_ids = violation_ticket_data.get("inspection_requirement_ids")
        if requirement_ids is not None:
            # Check enforcement action for requirements
            ServiceUtils.check_requirement_for_enforcement_action(
                requirement_ids, EnforcementActionOptionEnum.VIOLATION_TICKET.value
            )

            # Validate inspection requirements exist
            for req_id in requirement_ids:
                requirement = InspectionRequirementModel.find_by_id(req_id)
                if requirement is None:
                    raise ResourceNotFoundError(
                        f"Inspection requirement with ID {req_id} not found"
                    )

        # Database operations within session scope
        with session_scope() as session:
            # Handle inspection requirement updates
            violation_ticket_data_copy = violation_ticket_data.copy()
            requirement_ids = violation_ticket_data_copy.pop(
                "inspection_requirement_ids", None
            )
            if requirement_ids is not None:

                # Update inspection requirement mappings
                cls.insert_or_update_inspection_requirements(
                    violation_ticket_id, requirement_ids, session
                )

            # Update violation ticket
            updated_violation_ticket = ViolationTicketModel.update_violation_ticket(
                violation_ticket_id, violation_ticket_data_copy, session=session
            )

            return updated_violation_ticket

    @classmethod
    def delete(cls, violation_ticket_id: int) -> None:
        """Delete a violation ticket."""
        # Find and validate violation ticket exists
        violation_ticket = ViolationTicketModel.find_by_id(violation_ticket_id)
        if violation_ticket is None:
            raise ResourceNotFoundError(
                f"Violation ticket with ID {violation_ticket_id} not found"
            )

        # Perform access and status checks
        ServiceUtils.access_check_update_for_inspection(violation_ticket.inspection)
        ServiceUtils.inspection_status_check(violation_ticket.inspection)

        # Check if violation ticket can be deleted based on status
        if violation_ticket.status in ViolationTicketModel.get_non_deletable_statuses():
            raise UnprocessableEntityError(
                f"Violation ticket cannot be deleted as it is already {violation_ticket.status.value}"
            )

        # Database operations within session scope
        with session_scope() as session:
            # Update violation ticket to mark as deleted
            ViolationTicketModel.update_violation_ticket(
                violation_ticket_id, {"is_deleted": True, "is_active": False}, session
            )
            # Delete requirement mappings
            ViolationTicketInspectionRequirementMapModel.delete_by_violation_ticket_id(
                violation_ticket_id, session
            )

    @classmethod
    def insert_or_update_inspection_requirements(
        cls,
        violation_ticket_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert/Update inspection requirements associated with a given violation ticket."""
        if inspection_requirement_ids is not None:
            existing_requirements = (
                ViolationTicketInspectionRequirementMapModel.get_by_violation_ticket_id(
                    violation_ticket_id
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
                ViolationTicketInspectionRequirementMapModel.bulk_delete(
                    violation_ticket_id, list(requirement_ids_to_be_deleted), session
                )
            if requirement_ids_to_be_added:
                ViolationTicketInspectionRequirementMapModel.bulk_insert(
                    violation_ticket_id, list(requirement_ids_to_be_added), session
                )


def _create_violation_ticket_obj(inspection, violation_ticket_data: dict) -> dict:
    """
    Create a violation ticket object as a dictionary.

    Generates VT number and sets default status if not provided.
    """
    vt_number = _create_vt_number(
        inspection.case_file.project_id,
        inspection.case_file_id,
        violation_ticket_data.get("ticket_number"),
    )

    return {
        "vt_number": vt_number,
        "inspection_id": inspection.id,
        "date_issued": violation_ticket_data.get("date_issued"),
        "ticket_number": violation_ticket_data.get("ticket_number"),
        "fine_amount": violation_ticket_data.get("fine_amount"),
        "status": violation_ticket_data.get("status", ViolationTicketStatusEnum.ISSUED),
        "status_date": violation_ticket_data.get("status_date"),
    }


def _create_vt_number(project_id: int, case_file_id: int, ticket_number: int) -> str:
    """Generate the VT number."""
    project_abbreviation = ServiceUtils.get_project_abbreviation(project_id)

    # Get case file master number
    case_file = CaseFileModel.find_by_id(case_file_id)
    if case_file is None:
        raise ResourceNotFoundError(f"Case file with ID {case_file_id} not found")

    master_number = case_file.case_file_number

    return f"{project_abbreviation}_{master_number}_VT-{ticket_number}"
