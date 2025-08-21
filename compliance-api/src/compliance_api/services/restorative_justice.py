"""Restorative Justice Service."""

from http import HTTPStatus

from compliance_api.exceptions import BadRequestError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
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
        inspection_id = restorative_justice_data.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id=inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)

        inspection_requirement_ids = restorative_justice_data.get(
            "inspection_requirement_ids", []
        )

        restorative_justice_obj = _create_rj_object(
            inspection, restorative_justice_data
        )
        # Validate requirements if provided
        if inspection_requirement_ids is not None:
            exists = (
                RestorativeJustice.does_restorative_justice_exists_by_requirement_ids(
                    inspection_requirement_ids
                )
            )
            if exists:
                raise BadRequestError(
                    "A restorative justice already exists for one or more of the selected requirements"
                )
        # Create restorative justice with session scope
        with session_scope() as session:
            restorative_justice = RestorativeJustice.create_restorative_justice(
                restorative_justice_obj, session
            )
            cls.insert_or_update_inspection_requirements(
                restorative_justice.id,
                inspection_requirement_ids,
                session,
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
                cls.insert_or_update_inspection_requirements(
                    restorative_justice_id,
                    inspection_requirement_ids,
                    session,
                )

        return updated_restorative_justice

    @classmethod
    def delete_restorative_justice(cls, restorative_justice_id: int):
        """Delete a restorative justice."""
        restorative_justice = RestorativeJustice.find_by_id(restorative_justice_id)
        if not restorative_justice:
            raise ResourceNotFoundError(
                f"Restorative Justice with id: {restorative_justice_id} not found"
            )

        ServiceUtils.access_check_update_for_inspection(restorative_justice.inspection)
        ServiceUtils.inspection_status_check(restorative_justice.inspection)

        with session_scope() as session:
            RestorativeJustice.update_restorative_justice(
                restorative_justice_id,
                {"is_deleted": True, "is_active": False},
                session,
            )
            RestorativeJusticeInspectionRequirementMap.delete_by_restorative_justice_id(
                restorative_justice_id, session
            )
        return HTTPStatus.NO_CONTENT

    @classmethod
    def insert_or_update_inspection_requirements(
        cls,
        restorative_justice_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert/Update inspection requirements associated with a given restorative justice."""
        if inspection_requirement_ids is not None:
            existing_requirements = RestorativeJusticeInspectionRequirementMap.get_by_restorative_justice_id(
                restorative_justice_id
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
                RestorativeJusticeInspectionRequirementMap.bulk_delete(
                    restorative_justice_id,
                    list(requirement_ids_to_be_deleted),
                    session,
                )
            if requirement_ids_to_be_added:
                RestorativeJusticeInspectionRequirementMap.bulk_insert(
                    restorative_justice_id,
                    list(requirement_ids_to_be_added),
                    session,
                )


def _create_rj_object(inspection, restorative_justice_data):
    """Create restorative justice object."""
    # Generate restorative justice number if not provided
    rj_number = restorative_justice_data.get("restorative_justice_number")
    if not rj_number:
        project_id = inspection.case_file.project_id
        case_file_id = inspection.case_file_id
        rj_number = _create_restorative_justice_number(project_id, case_file_id)

    return {
        "restorative_justice_number": rj_number,
        "inspection_id": inspection.id,
        "restitution_details": restorative_justice_data.get("restitution_details"),
        "date_restitution_complete": restorative_justice_data.get(
            "date_restitution_complete"
        ),
    }


def _create_restorative_justice_number(project_id: int, case_file_id: int) -> str:
    """Generate the restorative justice number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file don't match")

    count = RestorativeJustice.get_count_by_project_nd_case_file_id(
        project_id, case_file_id
    )
    serial_number = f"{count + 1:03}"
    return f"{project_code}_{case_file.case_file_number}_RJ{serial_number}"
