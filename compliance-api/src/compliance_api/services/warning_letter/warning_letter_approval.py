"""Service method to handle warning letter approval."""

from datetime import datetime, timezone

from compliance_api.exceptions import UnprocessableEntityError
from compliance_api.models import WarningLetter as WarningLetterModel
from compliance_api.models import WarningLetterApproval as WarningLetterApprovalModel
from compliance_api.models import WarningLetterApprovalStatusEnum
from compliance_api.models.db import session_scope
from compliance_api.models.warning_letter import WarningLetterProgressEnum

from ..service_utils import ServiceUtils


class WarningLetterApprovalService:
    """Service for warning letter approval."""

    @classmethod
    def create_approval(
        cls,
        warning_letter_approval_request_data: dict,
        warning_letter_id: int,
        ho_session=None,
    ):
        """Create approval for the warning letter."""
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        inspection = warning_letter.inspection
        ServiceUtils.access_check_update_for_inspection(inspection)
        #  If the inspection is historical, then no approval is required
        approval_data = {
            "warning_letter_id": warning_letter_id,
            "approved_by_id": warning_letter_approval_request_data.get(
                "approved_by_id"
            ),
            "warning_letter_status": warning_letter.status,  # default status
            "approval_status": (
                WarningLetterApprovalStatusEnum.APPROVED
                if inspection.is_history
                else WarningLetterApprovalStatusEnum.APPROVAL_PENDING
            ),  # default status
        }
        latest_approval = (
            WarningLetterApprovalModel.get_latest_approval_by_warning_letter(
                warning_letter_id
            )
        )
        # No more approval request can be made if the latest approval is in progress
        if (
            latest_approval
            and latest_approval.approval_status
            == WarningLetterApprovalStatusEnum.APPROVAL_PENDING
        ):
            raise UnprocessableEntityError(
                "New request cannot be made as the existing one is in progress"
            )
        with session_scope() as session:
            created_approval = (
                WarningLetterApprovalModel.create_warning_letter_approval(
                    approval_data, session=ho_session or session
                )
            )
            # Update order_progress to either PRELIMINARY_DEPUTY_REVIEW or FINAL_DEPUTY_REVIEW
            WarningLetterModel.update_warning_letter(
                warning_letter_id=warning_letter_id,
                warning_letter_update_data={
                    "progress": (
                        WarningLetterProgressEnum.APPROVED
                        if inspection.is_history
                        else WarningLetterProgressEnum.DEPUTY_REVIEW
                    )
                },
                session=ho_session or session,
            )
        return created_approval

    @classmethod
    def get_all_approvals(cls, warning_letter_id: int):
        """Find all order approvals by warning_letter_id."""
        ServiceUtils.warning_letter_exist_check(warning_letter_id)
        return WarningLetterApprovalModel.get_approvals_by_warning_letter(
            warning_letter_id
        )

    @classmethod
    def update_approval_status(
        cls, warning_letter_id, approval_id, approval_status_data
    ):
        """Update approval status."""
        warning_letter = ServiceUtils.warning_letter_exist_check(warning_letter_id)
        ServiceUtils.access_check_update_for_inspection(warning_letter.inspection)
        latest_approval = (
            WarningLetterApprovalModel.get_latest_approval_by_warning_letter(
                warning_letter_id
            )
        )
        # Check if the update request for the approval is not the latest approval request
        if latest_approval.id != approval_id:
            raise UnprocessableEntityError(
                "Given approval id does not match the latest approval request"
            )
        # Check if the approval status is already in the status to be updated
        status_to_be_updated = approval_status_data.get("approval_status")
        if latest_approval.approval_status == status_to_be_updated:
            raise UnprocessableEntityError(
                f"Approval already in {status_to_be_updated.value} status"
            )
        if status_to_be_updated == WarningLetterApprovalStatusEnum.APPROVED:
            approval_status_data["approved_date"] = datetime.now(timezone.utc)
        with session_scope() as session:
            updated_approval = WarningLetterApprovalModel.update_approval(
                approval_id=approval_id,
                approval_update_data=approval_status_data,
                session=session,
            )
            WarningLetterModel.update_warning_letter(
                warning_letter_id=warning_letter_id,
                warning_letter_update_data={
                    "progress": (
                        WarningLetterProgressEnum.APPROVED
                        if status_to_be_updated
                        == WarningLetterApprovalStatusEnum.APPROVED
                        else WarningLetterProgressEnum.DRAFTING
                    )
                },
                session=session,
            )

        return updated_approval
