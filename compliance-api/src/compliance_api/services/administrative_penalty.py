"""Administrative Penalty Service."""

from http import HTTPStatus

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, AdministrativePenaltyInspectionRequirementMap, DecisionEnum, ReferralStatusEnum)
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.services.service_utils import ServiceUtils


class AdministrativePenaltyService:
    """Administrative Penalty Service."""

    @staticmethod
    def get_all(inspection_id):
        """Get all administrative penalties for an inspection."""
        if not inspection_id:
            return []
        return AdministrativePenalty.get_by_inspection_id(inspection_id)

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
    def get_projectwise_administrative_penalties(case_file_id: int):
        """Get all administrative penalties for the project associated to the case file.

        Args:
            case_file_id: int - The case file ID
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
        return AdministrativePenalty.get_administrative_penalties_by_case_files(
            case_file_ids_to_be_queried
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
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids,
            EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
        )

        # Check if administrative penalty already exists for the given requirements
        if AdministrativePenalty.does_administrative_penalty_exists_by_requirement_ids(
            administrative_penalty_data.get("inspection_requirement_ids", []),
        ):
            raise UnprocessableEntityError(
                "Administrative Penalty already exists for these requirements."
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
                administrative_penalty.id,
                administrative_penalty_data.get("inspection_requirement_ids", []),
                session,
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
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)

        requirement_ids = update_data.get("inspection_requirement_ids", [])
        if requirement_ids:
            ServiceUtils.check_requirement_for_enforcement_action(
                requirement_ids,
                EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
            )

        # Check if administrative penalty already exists for the given requirements
        if (
            requirement_ids
            and AdministrativePenalty.does_administrative_penalty_exists_by_requirement_ids(
                requirement_ids, administrative_penalty_id
            )
        ):
            raise UnprocessableEntityError(
                "Administrative Penalty already exists for these requirements."
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
                    administrative_penalty_id,
                    update_data.get("inspection_requirement_ids", []),
                    session,
                )

        return updated_penalty

    @classmethod
    def delete_administrative_penalty(cls, administrative_penalty_id):
        """Delete an administrative penalty."""
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
        ServiceUtils.inspection_status_check(administrative_penalty.inspection)

        with session_scope() as session:
            AdministrativePenalty.update_administrative_penalty(
                administrative_penalty_id,
                {"is_deleted": True, "is_active": False},
                session,
            )
            AdministrativePenaltyInspectionRequirementMap.delete_by_administrative_penalty(
                administrative_penalty_id, session
            )
        return HTTPStatus.NO_CONTENT

    @classmethod
    def insert_or_update_inspection_requirements(
        cls,
        administrative_penalty_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert/Update inspection requirements associated with a given administrative penalty."""
        if inspection_requirement_ids is not None:
            existing_requirements = AdministrativePenaltyInspectionRequirementMap.get_by_administrative_penalty_id(
                administrative_penalty_id
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
        "inspection_id": administrative_penalty_data.get("inspection_id", None),
        "referral_status": administrative_penalty_data.get(
            "referral_status", ReferralStatusEnum.DRAFTING
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
    return {"administrative_penalty_number": ap_number, **ap_data}


def _create_administrative_penalty_number(project_id: int, case_file_id: int) -> str:
    """Generate the administrative penalty number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file don't match")

    count = AdministrativePenalty.get_count_by_project_nd_case_file_id(
        project_id, case_file_id
    )
    serial_number = f"{count + 1:03}"
    return f"{project_code}_{case_file.case_file_number}_AP{serial_number}"
