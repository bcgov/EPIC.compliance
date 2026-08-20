"""Administrative penalty service."""

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, AdministrativePenaltyInspectionRequirementMap, DecisionEnum, ReferralStatusEnum)
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection import InspectionRequirement as InspectionRequirementModel
from compliance_api.services.service_utils import ServiceUtils


class AdministrativePenaltyService:
    """Administrative Penalty Service."""

    @staticmethod
    def get_all(inspection_id: int, sort_by: str = None):
        """Get all administrative penalties for an inspection."""
        if not inspection_id:
            return []
        return AdministrativePenalty.get_by_inspection_id(inspection_id, sort_by=sort_by)

    @staticmethod
    def get_by_id(administrative_penalty_id):
        """Get administrative penalty by id."""
        administrative_penalty = AdministrativePenalty.find_by_id(
            administrative_penalty_id
        )
        if not administrative_penalty:
            raise ResourceNotFoundError(
                f"Administrative Penalty with id: {administrative_penalty_id} not found"
            )
        return administrative_penalty

    @staticmethod
    def get_linked_inspections_and_requirements(administrative_penalty_id):
        """Get inspection and requirements linked to an administrative penalty.

        Args:
            administrative_penalty_id: The ID of the administrative penalty

        Returns:
            Dict containing inspection and its linked requirements
        """
        # Get the administrative penalty
        administrative_penalty = AdministrativePenalty.find_by_id(
            administrative_penalty_id
        )
        if not administrative_penalty:
            raise ResourceNotFoundError(
                f"Administrative Penalty with id: {administrative_penalty_id} not found"
            )

        # Get all active requirement maps for this administrative penalty
        requirement_maps = AdministrativePenaltyInspectionRequirementMap.query.filter(
            AdministrativePenaltyInspectionRequirementMap.administrative_penalty_id
            == administrative_penalty_id,
            AdministrativePenaltyInspectionRequirementMap.is_active.is_(True),
            AdministrativePenaltyInspectionRequirementMap.is_deleted.is_(False),
        ).all()

        # Group requirements by inspection
        inspections_data = {}
        for req_map in requirement_maps:
            inspection = req_map.inspection_requirement.inspection
            inspection_id = inspection.id

            if inspection_id not in inspections_data:
                inspections_data[inspection_id] = {
                    "inspection": inspection,
                    "requirements": [],
                }

            inspections_data[inspection_id]["requirements"].append(
                req_map.inspection_requirement
            )

        return list(inspections_data.values())

    @staticmethod
    def get_projectwise_administrative_penalties(
        case_file_id: int, include_open_aps: str = None
    ):
        """Get all administrative penalties for the project associated to the case file.

        Args:
            case_file_id: int - The case file ID
            include_open_aps: str - Flag to include only open administrative penalties
        Returns:
            List[AdministrativePenalty] - List of administrative penalties
        """
        case_file = CaseFileModel.find_by_id(case_file_id)
        if case_file is None:
            raise ResourceNotFoundError(f"Case file with ID {case_file_id} not found")
        case_file_ids_to_be_queried = [case_file.id]
        if case_file.project_id is not None:
            case_files = CaseFileModel.get_by_project(case_file.project_id)
            case_file_ids_to_be_queried = [
                case_file.id
                for case_file in case_files
                if case_file.is_active and not case_file.is_deleted
            ]

        # Convert include_open_aps to boolean
        open_aps_only = include_open_aps is not None and include_open_aps.lower() in [
            "true",
            "1",
            "yes",
        ]

        return AdministrativePenalty.get_administrative_penalties_by_case_files(
            case_file_ids_to_be_queried, open_aps_only=open_aps_only
        )

    @staticmethod
    def get_by_number(administrative_penalty_number):
        """Get administrative penalty by number."""
        administrative_penalty = (
            AdministrativePenalty.get_by_administrative_penalty_number(
                administrative_penalty_number
            )
        )
        if not administrative_penalty:
            raise ResourceNotFoundError(
                f"Administrative Penalty with number: {administrative_penalty_number} not found"
            )
        return administrative_penalty

    @classmethod
    def create_administrative_penalty(cls, administrative_penalty_data):
        """Create an administrative penalty."""
        inspection_id = administrative_penalty_data.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id=inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)

        requirement_ids = administrative_penalty_data.get(
            "inspection_requirement_ids", []
        )
        if not requirement_ids:
            raise UnprocessableEntityError(
                "Inspection requirement IDs are required to create an administrative penalty."
            )
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids,
            EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
        )

        administrative_penalty_obj = _create_ap_object(
            inspection, administrative_penalty_data
        )
        # Create administrative penalty with session scope
        with session_scope() as session:
            administrative_penalty = (
                AdministrativePenalty.create_administrative_penalty(
                    administrative_penalty_obj, session
                )
            )
            cls.insert_or_update_inspection_requirements(
                inspection_id=inspection_id,
                administrative_penalty_id=administrative_penalty.id,
                inspection_requirement_ids=administrative_penalty_data.get(
                    "inspection_requirement_ids", []
                ),
                session=session,
            )

        return administrative_penalty

    @classmethod
    def update_administrative_penalty(cls, administrative_penalty_id, update_data):
        """Update an administrative penalty."""
        administrative_penalty = AdministrativePenalty.find_by_id(
            administrative_penalty_id
        )
        if not administrative_penalty:
            raise ResourceNotFoundError(
                f"Administrative Penalty with id: {administrative_penalty_id} not found"
            )

        inspection = ServiceUtils.inspection_exist_check(
            inspection_id=update_data.get("inspection_id")
            or administrative_penalty.inspection_id
        )
        #  Primary or super user can update ap if it is not closed
        if not administrative_penalty.is_closed:
            ServiceUtils.access_check_update_for_inspection(inspection)
        #  Super user can update ap if it is closed
        if administrative_penalty.is_closed:
            ServiceUtils.access_check_for_super_user()

        requirement_ids = update_data.get("inspection_requirement_ids", [])
        if requirement_ids:
            ServiceUtils.check_requirement_for_enforcement_action(
                requirement_ids,
                EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
            )

        # Validate penalty_amount if decision is provided
        if (
            update_data.get("decision")
            and update_data.get("decision") != DecisionEnum.AP_NOT_PROCEEDING
            and not update_data.get("penalty_amount")
        ):
            if not administrative_penalty.penalty_amount:
                raise UnprocessableEntityError(
                    "Penalty amount is required when a decision is provided."
                )

        # Update administrative penalty with session scope
        with session_scope() as session:
            ap_data = _extract_ap_data(update_data)
            updated_penalty = AdministrativePenalty.update_administrative_penalty(
                administrative_penalty_id, ap_data, session
            )
            if "inspection_requirement_ids" in update_data:
                cls.insert_or_update_inspection_requirements(
                    inspection_id=inspection.id,
                    administrative_penalty_id=administrative_penalty_id,
                    inspection_requirement_ids=update_data.get(
                        "inspection_requirement_ids", []
                    ),
                    session=session,
                )

        return updated_penalty

    @classmethod
    def delete_administrative_penalty(
        cls, administrative_penalty_id, inspection_id=None
    ):
        """Delete an administrative penalty.

        Args:
            administrative_penalty_id: ID of the administrative penalty to delete
            inspection_id: Optional ID of the inspection to check
        """
        administrative_penalty = AdministrativePenalty.find_by_id(
            administrative_penalty_id
        )
        if not administrative_penalty:
            raise ResourceNotFoundError(
                f"Administrative Penalty with id: {administrative_penalty_id} not found"
            )

        ServiceUtils.access_check_update_for_inspection(
            administrative_penalty.inspection
        )
        # If administrative penalty is closed, then check the inspection status
        # No more modification possible once the AP and IR is closed
        if administrative_penalty.is_closed:
            ServiceUtils.inspection_status_check(administrative_penalty.inspection)

        # Check if the inspection belongs to the same inspection as the AP
        ap_inspection_id = administrative_penalty.inspection_id

        if inspection_id == ap_inspection_id:
            # Safe to delete the entire AP
            with session_scope() as session:
                AdministrativePenalty.update_administrative_penalty(
                    administrative_penalty_id,
                    {"is_deleted": True, "is_active": False},
                    session,
                )
                AdministrativePenaltyInspectionRequirementMap.delete_by_administrative_penalty(
                    administrative_penalty_id, session
                )
        else:
            # Different inspection - only delete the reference from the map
            with session_scope() as session:
                inspection_requirements = (
                    InspectionRequirementModel.get_by_inspection_id(inspection_id)
                )
                requirement_ids_to_be_deleted = [
                    req.id for req in inspection_requirements
                ]
                AdministrativePenaltyInspectionRequirementMap.bulk_delete(
                    administrative_penalty_id,
                    requirement_ids_to_be_deleted,
                    session,
                )

    @classmethod
    def link(cls, administrative_penalty_id, link):
        """Link an existing administrative penalty to inspection requirements.

        Args:
            administrative_penalty_id: The ID of the administrative penalty to link
            link: Dictionary containing inspection_id and inspection_requirement_ids

        Returns:
            The administrative penalty object
        """
        # Get the administrative penalty
        administrative_penalty = AdministrativePenalty.find_by_id(
            administrative_penalty_id
        )
        if not administrative_penalty:
            raise ResourceNotFoundError(
                f"Administrative Penalty with id: {administrative_penalty_id} not found"
            )

        # Get the inspection to link to
        inspection_id = link.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id=inspection_id)

        # Check that both the administrative penalty and inspection belong to the same project
        ap_project_id = administrative_penalty.inspection.case_file.project_id
        inspection_project_id = inspection.case_file.project_id

        # Handle unapproved projects (project_id is null)
        if ap_project_id is None and inspection_project_id is None:
            # For unapproved projects, compare case_file_id
            ap_case_file_id = administrative_penalty.inspection.case_file_id
            inspection_case_file_id = inspection.case_file_id
            if ap_case_file_id != inspection_case_file_id:
                raise UnprocessableEntityError(
                    "Administrative penalty and inspection must belong to the same case file for unapproved projects"
                )
        elif ap_project_id != inspection_project_id:
            raise UnprocessableEntityError(
                "Administrative penalty and inspection must belong to the same project to be linked"
            )

        # Perform access checks on the inspection
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)

        # Validate inspection requirements
        requirement_ids = link.get("inspection_requirement_ids", [])
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids,
            EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
        )
        existing_requirements = (
            AdministrativePenaltyInspectionRequirementMap.get_by_inspection_and_administrative_penalty_id(
                inspection_id, administrative_penalty_id
            )
        )
        if existing_requirements:
            raise UnprocessableEntityError(
                "Administrative penalty is already linked to inspection requirements for this inspection."
            )
        with session_scope() as session:
            cls.insert_or_update_inspection_requirements(
                inspection_id=inspection.id,
                administrative_penalty_id=administrative_penalty_id,
                inspection_requirement_ids=requirement_ids,
                session=session,
            )

        return administrative_penalty

    @classmethod
    def insert_or_update_inspection_requirements(
        cls,
        inspection_id: int,
        administrative_penalty_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert/Update inspection requirements associated with a given administrative penalty."""
        if inspection_requirement_ids is not None:
            existing_inspection_requirements = (
                InspectionRequirementModel.get_by_inspection_id(inspection_id)
            )
            existing_inspection_requirement_ids = {
                req.id for req in existing_inspection_requirements
            }
            existing_requirements = (
                AdministrativePenaltyInspectionRequirementMap.get_by_inspection_and_administrative_penalty_id(
                    inspection_id, administrative_penalty_id
                )
            )
            existing_requirement_ids = {
                req.inspection_requirement_id for req in existing_requirements
            }

            new_requirement_ids = set(inspection_requirement_ids)

            # Validate that all new requirement IDs belong to the current inspection
            invalid_requirement_ids = new_requirement_ids.difference(
                existing_inspection_requirement_ids
            )
            if invalid_requirement_ids:
                raise UnprocessableEntityError(
                    f"Requirement IDs {list(invalid_requirement_ids)} do not belong to inspection {inspection_id}"
                )

            requirement_ids_to_be_deleted = existing_requirement_ids.difference(
                new_requirement_ids
            )
            requirement_ids_to_be_added = new_requirement_ids.difference(
                existing_requirement_ids
            )

            if requirement_ids_to_be_deleted:
                AdministrativePenaltyInspectionRequirementMap.bulk_delete(
                    administrative_penalty_id,
                    list(requirement_ids_to_be_deleted),
                    session,
                )
            if requirement_ids_to_be_added:
                AdministrativePenaltyInspectionRequirementMap.bulk_insert(
                    administrative_penalty_id,
                    list(requirement_ids_to_be_added),
                    session,
                )


def _extract_ap_data(administrative_penalty_data):
    """Extract administrative penalty data."""
    return {
        "referral_status": administrative_penalty_data.get(
            "referral_status", ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO
        ),
        "date_referred": administrative_penalty_data.get("date_referred", None),
        "decision_date": administrative_penalty_data.get("decision_date", None),
        "decision": administrative_penalty_data.get("decision", None),
        "penalty_amount": administrative_penalty_data.get("penalty_amount", None),
    }


def _create_ap_object(inspection, administrative_penalty_data):
    """Create administrative penalty object."""
    # Generate administrative penalty number if not provided
    ap_number = administrative_penalty_data.get("administrative_penalty_number")
    if not ap_number:
        project_id = inspection.case_file.project_id
        case_file_id = inspection.case_file_id
        ap_number = _create_administrative_penalty_number(project_id, case_file_id)
    ap_data = _extract_ap_data(administrative_penalty_data)
    return {
        "administrative_penalty_number": ap_number,
        "inspection_id": inspection.id,
        **ap_data,
    }


def _create_administrative_penalty_number(project_id: int, case_file_id: int) -> str:
    """Generate the administrative penalty number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file don't match")

    pattern = rf"^{project_code}_{case_file.case_file_number}_AP[0-9]{{3}}$"
    count = AdministrativePenalty.get_latest_administrative_penalty_number_count(
        case_file_id, project_id, pattern
    )
    serial_number = f"{count:03}"
    return f"{project_code}_{case_file.case_file_number}_AP{serial_number}"
