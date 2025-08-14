"""Restorative Justice Service."""

from typing import List

from compliance_api.exceptions import BadRequestError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.restorative_justice import RestorativeJustice, RestorativeJusticeInspectionRequirementMap
from compliance_api.services.service_utils import ServiceUtils


class RestorativeJusticeService:
    """Service for restorative justice management."""

    @staticmethod
    def get_all(inspection_id):
        """Get all restorative justices for an inspection."""
        if not inspection_id:
            return []
        return RestorativeJustice.get_by_inspection_id(inspection_id)

    @staticmethod
    def get_by_id(restorative_justice_id):
        """Get restorative justice by id."""
        restorative_justice = RestorativeJustice.find_by_id(restorative_justice_id)
        if not restorative_justice:
            raise ResourceNotFoundError(
                f"Restorative justice with id: {restorative_justice_id} not found"
            )
        return restorative_justice

    @staticmethod
    def get_by_number(restorative_justice_number):
        """Get restorative justice by number."""
        restorative_justice = RestorativeJustice.get_by_restorative_justice_number(
            restorative_justice_number
        )
        if not restorative_justice:
            raise ResourceNotFoundError(
                f"Restorative justice with number: {restorative_justice_number} not found"
            )
        return restorative_justice

    @classmethod
    def create_restorative_justice(
        cls, restorative_justice_data: dict
    ) -> RestorativeJustice:
        """Create a new restorative justice."""
        # Extract inspection requirement IDs
        inspection_requirement_ids = restorative_justice_data.pop(
            "inspection_requirement_ids", []
        )

        # Validate that restorative justice doesn't already exist for these requirements
        if inspection_requirement_ids:
            exists = (
                RestorativeJustice.does_restorative_justice_exists_by_requirement_ids(
                    inspection_requirement_ids
                )
            )
            if exists:
                raise BadRequestError(
                    "A restorative justice already exists for one or more of the selected requirements"
                )

        # Generate restorative justice number if not provided
        if not restorative_justice_data.get("restorative_justice_number"):
            restorative_justice_data["restorative_justice_number"] = (
                cls._generate_restorative_justice_number(
                    restorative_justice_data["inspection_id"]
                )
            )

        # Create the restorative justice
        with session_scope() as session:
            restorative_justice = RestorativeJustice.create_restorative_justice(
                restorative_justice_data, session
            )

            # Create requirement mappings
            if inspection_requirement_ids:
                cls._create_requirement_mappings(
                    restorative_justice.id, inspection_requirement_ids, session
                )

        return restorative_justice

    @classmethod
    def update_restorative_justice(
        cls, restorative_justice_id: int, update_data: dict
    ) -> RestorativeJustice:
        """Update an existing restorative justice."""
        # Check if restorative justice exists
        cls.get_by_id(restorative_justice_id)

        # Extract inspection requirement IDs
        inspection_requirement_ids = update_data.pop("inspection_requirement_ids", None)

        # Validate requirements if provided
        if inspection_requirement_ids is not None:
            exists = (
                RestorativeJustice.does_restorative_justice_exists_by_requirement_ids(
                    inspection_requirement_ids, restorative_justice_id
                )
            )
            if exists:
                raise BadRequestError(
                    "A restorative justice already exists for one or more of the selected requirements"
                )

        with session_scope() as session:
            # Update the restorative justice
            updated_restorative_justice = RestorativeJustice.update_restorative_justice(
                restorative_justice_id, update_data, session
            )

            # Handle requirement mappings if provided
            if inspection_requirement_ids is not None:
                # Delete existing requirement mappings
                RestorativeJusticeInspectionRequirementMap.delete_by_restorative_justice_id(
                    restorative_justice_id, session
                )

                # Create new requirement mappings
                if inspection_requirement_ids:
                    cls._create_requirement_mappings(
                        restorative_justice_id, inspection_requirement_ids, session
                    )

        return updated_restorative_justice

    @classmethod
    def delete_restorative_justice(cls, restorative_justice_id: int) -> None:
        """Delete a restorative justice."""
        # Check if restorative justice exists
        cls.get_by_id(restorative_justice_id)

        with session_scope() as session:
            # Soft delete the restorative justice
            RestorativeJustice.update_restorative_justice(
                restorative_justice_id, {"is_deleted": True}, session
            )

            # Delete requirement mappings
            RestorativeJusticeInspectionRequirementMap.delete_by_restorative_justice_id(
                restorative_justice_id, session
            )

    @classmethod
    def _create_requirement_mappings(
        cls,
        restorative_justice_id: int,
        inspection_requirement_ids: List[int],
        session=None,
    ):
        """Create requirement mappings for a restorative justice."""
        for requirement_id in inspection_requirement_ids:
            mapping_data = {
                "restorative_justice_id": restorative_justice_id,
                "inspection_requirement_id": requirement_id,
            }
            RestorativeJusticeInspectionRequirementMap.create_restorative_justice_requirement_map(
                mapping_data, session
            )

    @classmethod
    def _generate_restorative_justice_number(cls, inspection_id: int) -> str:
        """Generate a unique restorative justice number."""
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError("Given inspection doesn't exist")

        project_code = ServiceUtils.get_project_abbreviation(inspection.project_id)
        case_file = CaseFileModel.find_by_id(inspection.case_file_id)
        if not case_file:
            raise ResourceNotFoundError("Given case file doesn't exist")
        if case_file.project_id != inspection.project_id:
            raise UnprocessableEntityError("Given project and case file don't match")

        count = RestorativeJustice.get_count_by_project_nd_case_file_id(
            inspection.project_id, inspection.case_file_id
        )
        serial_number = f"{count + 1:03}"
        return f"{project_code}_{case_file.case_file_number}_RJ{serial_number}"
