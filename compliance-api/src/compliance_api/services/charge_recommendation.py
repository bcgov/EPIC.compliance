"""Charge Recommendation Service."""

from typing import List

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.charge_recommendation import (
    ChargeRecommendation, ChargeRecommendationInspectionRequirementMap)
from compliance_api.models.cr_sentence_type_mapping import CRSentenceTypeMapping
from compliance_api.models.db import session_scope
from compliance_api.services.service_utils import ServiceUtils


class ChargeRecommendationService:
    """Service for charge recommendation management."""

    @staticmethod
    def get_all(inspection_id, sort_by: str = None) -> List[ChargeRecommendation]:
        """Get all charge recommendations for an inspection."""
        if not inspection_id:
            return []
        return ChargeRecommendation.get_by_inspection_id(inspection_id, sort_by=sort_by)

    @staticmethod
    def get_by_id(charge_recommendation_id):
        """Get charge recommendation by id."""
        charge_recommendation = ChargeRecommendation.find_by_id(
            charge_recommendation_id
        )
        if not charge_recommendation:
            raise ResourceNotFoundError(
                f"Charge recommendation with id: {charge_recommendation_id} not found"
            )
        return charge_recommendation

    @staticmethod
    def get_by_number(charge_recommendation_number):
        """Get charge recommendation by number."""
        charge_recommendation = (
            ChargeRecommendation.get_by_charge_recommendation_number(
                charge_recommendation_number
            )
        )
        if not charge_recommendation:
            raise ResourceNotFoundError(
                f"Charge recommendation with number: {charge_recommendation_number} not found"
            )
        return charge_recommendation

    @classmethod
    def create_charge_recommendation(
        cls, charge_recommendation_data: dict
    ) -> ChargeRecommendation:
        """Create a new charge recommendation."""
        inspection_id = charge_recommendation_data.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id=inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        charge_recommendation_obj = _create_cr_object(
            inspection, charge_recommendation_data
        )
        # Create charge recommendation with session scope
        with session_scope() as session:
            charge_recommendation = ChargeRecommendation.create_charge_recommendation(
                charge_recommendation_obj, session
            )
            cls.insert_or_update_inspection_requirements(
                charge_recommendation.id,
                charge_recommendation_data.get("inspection_requirement_ids", []),
                session,
            )
            cls.insert_or_update_sentence_type_mappings(
                charge_recommendation.id,
                charge_recommendation_data.get("sentence_type_option_ids", []),
                session,
            )

        return charge_recommendation

    @classmethod
    def update_charge_recommendation(
        cls, charge_recommendation_id: int, update_data: dict
    ) -> ChargeRecommendation:
        """Update an existing charge recommendation."""
        charge_recommendation = cls.get_by_id(charge_recommendation_id)
        inspection = ServiceUtils.inspection_exist_check(
            inspection_id=update_data.get("inspection_id")
        )
        # Primary or super user can update CR if it is not closed
        if not charge_recommendation.is_closed:
            ServiceUtils.access_check_update_for_inspection(inspection)
        # Super user can update CR if it is closed
        if charge_recommendation.is_closed:
            ServiceUtils.access_check_for_super_user()
        requirement_ids = update_data.get("inspection_requirement_ids", [])
        with session_scope() as session:
            extracted_update_data = _extract_cr_data(update_data)
            updated_charge_recommendation = (
                ChargeRecommendation.update_charge_recommendation(
                    charge_recommendation_id, extracted_update_data, session
                )
            )
            cls.insert_or_update_inspection_requirements(
                updated_charge_recommendation.id,
                requirement_ids,
                session,
            )
            sentence_type_ids = update_data.get("sentence_type_option_ids", [])
            cls.insert_or_update_sentence_type_mappings(
                updated_charge_recommendation.id,
                sentence_type_ids,
                session,
            )
        return updated_charge_recommendation

    @classmethod
    def delete_charge_recommendation(cls, charge_recommendation_id: int) -> None:
        """Delete a charge recommendation."""
        # Check if charge recommendation exists
        charge_recommendation = cls.get_by_id(charge_recommendation_id)
        ServiceUtils.access_check_update_for_inspection(
            charge_recommendation.inspection
        )

        # If charge recommendation is closed, then check the inspection status
        # No more modification possible once the CR and IR is closed
        if charge_recommendation.is_closed:
            ServiceUtils.inspection_status_check(charge_recommendation.inspection)

        with session_scope() as session:
            # Soft delete the charge recommendation
            ChargeRecommendation.update_charge_recommendation(
                charge_recommendation_id, {"is_deleted": True}, session
            )

            # Delete requirement mappings
            ChargeRecommendationInspectionRequirementMap.delete_by_charge_recommendation_id(
                charge_recommendation_id, session
            )

    @classmethod
    def insert_or_update_inspection_requirements(
        cls,
        charge_recommendation_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert/Update inspection requirements associated with a given charge recommendation."""
        if inspection_requirement_ids is not None:
            existing_requirements = ChargeRecommendationInspectionRequirementMap.get_by_charge_recommendation_id(
                charge_recommendation_id
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
                ChargeRecommendationInspectionRequirementMap.bulk_delete(
                    charge_recommendation_id,
                    list(requirement_ids_to_be_deleted),
                    session,
                )
            if requirement_ids_to_be_added:
                ChargeRecommendationInspectionRequirementMap.bulk_insert(
                    charge_recommendation_id,
                    list(requirement_ids_to_be_added),
                    session,
                )

    @classmethod
    def insert_or_update_sentence_type_mappings(
        cls,
        charge_recommendation_id: int,
        sentence_type_option_ids: List[int],
        session=None,
    ):
        """Insert or update sentence type mappings for a charge recommendation."""
        existing_mappings = CRSentenceTypeMapping.get_by_charge_recommendation_id(
            charge_recommendation_id, session
        )
        existing_sentence_type_ids = {
            mapping.sentence_type_option_id for mapping in existing_mappings
        }
        new_sentence_type_ids = set(sentence_type_option_ids)

        # Find IDs to be added and deleted
        sentence_type_ids_to_be_added = (
            new_sentence_type_ids - existing_sentence_type_ids
        )
        sentence_type_ids_to_be_deleted = (
            existing_sentence_type_ids - new_sentence_type_ids
        )

        # Delete mappings that are no longer needed
        if sentence_type_ids_to_be_deleted:
            CRSentenceTypeMapping.bulk_delete(
                charge_recommendation_id,
                list(sentence_type_ids_to_be_deleted),
                session,
            )

        # Add new mappings
        if sentence_type_ids_to_be_added:
            CRSentenceTypeMapping.bulk_insert(
                charge_recommendation_id,
                list(sentence_type_ids_to_be_added),
                session,
            )

    @classmethod
    def _create_requirement_mappings(
        cls,
        charge_recommendation_id: int,
        inspection_requirement_ids: List[int],
        session=None,
    ):
        """Create requirement mappings for a charge recommendation."""
        for requirement_id in inspection_requirement_ids:
            mapping_data = {
                "charge_recommendation_id": charge_recommendation_id,
                "inspection_requirement_id": requirement_id,
            }
            ChargeRecommendationInspectionRequirementMap.create_charge_recommendation_requirement_map(
                mapping_data, session
            )


def _extract_cr_data(charge_recommendation_data):
    """Extract charge recommendation data."""
    return {
        "inspection_id": charge_recommendation_data.get("inspection_id"),
        "status": charge_recommendation_data.get("status", "DRAFTING"),
        "date_to_crown_counsel": charge_recommendation_data.get(
            "date_to_crown_counsel", None
        ),
        "charge_decision": charge_recommendation_data.get("charge_decision", None),
        "charge_decision_date": charge_recommendation_data.get(
            "charge_decision_date", None
        ),
        "court_file_number": charge_recommendation_data.get("court_file_number", None),
        "court_decision": charge_recommendation_data.get("court_decision", None),
        "court_decision_date": charge_recommendation_data.get(
            "court_decision_date", None
        ),
        "sentence_date": charge_recommendation_data.get("sentence_date", None),
        "sentence_description": charge_recommendation_data.get(
            "sentence_description", None
        ),
    }


def _create_cr_object(inspection, charge_recommendation_data):
    """Create charge recommendation object."""
    # Generate charge recommendation number if not provided
    cr_number = charge_recommendation_data.get("charge_recommendation_number")
    if not cr_number:
        project_id = inspection.case_file.project_id
        case_file_id = inspection.case_file_id
        cr_number = _create_charge_recommendation_number(project_id, case_file_id)
    return {
        "charge_recommendation_number": cr_number,
        **_extract_cr_data(charge_recommendation_data),
    }


def _create_charge_recommendation_number(project_id: int, case_file_id: int) -> str:
    """Generate the charge recommendation number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file don't match")
    pattern = rf"^{project_code}_{case_file.case_file_number}_CR[0-9]{{3}}$"
    count = ChargeRecommendation.get_latest_charge_recommendation_number_count(
        case_file_id, project_id, pattern
    )
    serial_number = f"{count:03}"
    return f"{project_code}_{case_file.case_file_number}_CR{serial_number}"
