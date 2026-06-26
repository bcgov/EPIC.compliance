"""Case file aggregate service."""

from compliance_api.models import UnapprovedProject
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.services import CaseFileService, ComplaintService, ContinuationReportService, InspectionService


class CaseFileAggregateService:
    """Case file aggregate service."""

    @classmethod
    def delete_case_file(cls, case_file_id):
        """Delete a case file an all its associated dependecies."""
        case_file = CaseFileModel.find_by_id(case_file_id)
        if not case_file:
            return None
        with session_scope() as session:
            case_file = session.merge(case_file)
            CaseFileService.update(
                case_file_id,
                {"is_deleted": True, "is_active": False, "officer_ids": []},
                session,
            )
            UnapprovedProject.delete_by_case_file(case_file_id, session)
            ContinuationReportService.delete_by_case_file(case_file_id, session)
            InspectionService.delete_by_case_file(case_file_id, session)
            ComplaintService.delete_by_case_file(case_file_id, session)
            CaseFileService.unlink_all(case_file, session)
        return case_file
