"""Service method to handle inspection record approval."""

from datetime import datetime, timedelta, timezone

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models import InspectionRecord as InspectionRecordModel
from compliance_api.models import InspectionRecordApproval as InspectionRecordApprovalModel
from compliance_api.models import IRApprovalStatusEnum, IRProgressEnum
from compliance_api.models.db import session_scope
from compliance_api.models.inspection_record import IRStatusEnum
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.services.inspection_record.inspection_record_builder import InspectionRecordDataBuilder

from ..service_utils import ServiceUtils


class InspectionRecordApprovalService:
    """Service for inspection record approval."""

    @classmethod
    def create_approval(
        cls,
        ir_approval_request_data: dict,
        inspection_id: int,
        inspection_record_id: int,
        ho_session=None,
    ):
        """Create approval for the inspection record."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        # for historical inspection record, the approval status is set to
        # approved by default as no explicit approval is required
        approval_data = {
            "inspection_record_id": inspection_record_id,
            "approved_by_id": ir_approval_request_data.get("approved_by_id", None),
            "ir_status_id": inspection_record.ir_status_id,
            "approval_status": (
                IRApprovalStatusEnum.APPROVED
                if inspection.is_history
                else IRApprovalStatusEnum.APPROVAL_PENDING
            ),  # default status
        }
        # No more approval request can be made if the IR is in the following statuses
        if inspection_record.ir_progress in {
            IRProgressEnum.PRELIMINARY_DEPUTY_REVIEW,
            IRProgressEnum.FINAL_DEPUTY_REVIEW,
            IRProgressEnum.ISSUED,
            IRProgressEnum.FINAL_APPROVED,
        }:
            raise UnprocessableEntityError(
                f"New approval request cannot be perforemed as the IR already in {inspection_record.ir_progress.value}"
            )
        latest_approval = InspectionRecordApprovalModel.get_latest_approval_by_ir(
            inspection_record_id
        )
        # No more approval request can be made if the latest approval is in progress
        if (
            latest_approval
            and latest_approval.approval_status == IRApprovalStatusEnum.APPROVAL_PENDING
        ):
            raise UnprocessableEntityError(
                "New request cannot be made as the existing one is in progress"
            )
        with session_scope() as session:
            created_approval = (
                InspectionRecordApprovalModel.create_inspection_record_approval(
                    approval_data, session=ho_session or session
                )
            )
            # Update ir_progress to either PRELIMINARY_DEPUTY_REVIEW or FINAL_DEPUTY_REVIEW
            ir_progress = (
                IRProgressEnum.PRELIMINARY_DEPUTY_REVIEW
                if inspection_record.ir_status_id == IRStatusEnum.PRELIMINARY.value
                else IRProgressEnum.FINAL_DEPUTY_REVIEW
            )
            # for historical inspection record, the ir_progress is set to FINAL_APPROVED
            if inspection.is_history:
                ir_progress = IRProgressEnum.FINAL_APPROVED
            InspectionRecordModel.update_inspection_record(
                inspection_record_id=inspection_record_id,
                ir_update_data={"ir_progress": ir_progress},
                session=ho_session or session,
            )
        return created_approval

    @classmethod
    def get_all_approvals(cls, inspection_record_id: int):
        """Find all inspection record approvals by inspection_record_id."""
        return InspectionRecordApprovalModel.get_approvals_by_ir(inspection_record_id)

    @classmethod
    def update_approval(
        cls, inspection_id, inspection_record_id, approval_id, approval_update_data
    ):
        """Update inspection record approval."""
        field_name = approval_update_data.get("field_name")
        value = approval_update_data.get("value", None)
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        inspection_record = ServiceUtils.inspection_record_exist_check(
            inspection_record_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        latest_approval = InspectionRecordApprovalModel.get_latest_approval_by_ir(
            inspection_record_id
        )
        if latest_approval.id != approval_id:
            raise UnprocessableEntityError(
                "Given approval id does not match the latest approval request"
            )

        # Convert date fields to datetime objects
        date_fields = ["date_report_sent", "date_expected_return", "date_response"]
        if field_name in date_fields and value and isinstance(value, str):
            # Convert string date to datetime object
            approval_update_data[field_name] = datetime.strptime(
                value, "%Y-%m-%dT%H:%M:%S.%fZ"
            )

        # Calculate date_expected_return if date_report_sent is updated
        if field_name == "date_report_sent" and approval_update_data[field_name]:
            # date_report_sent is already converted to datetime above
            date_report_sent = approval_update_data[field_name]
            date_expected_return = date_report_sent + timedelta(days=5)
            approval_update_data["date_expected_return"] = date_expected_return

        if field_name == "is_active":
            value = False if value in ["false", "False", False] else True
            approval_update_data["is_active"] = value

        with session_scope() as session:
            ir_update_data = {}
            updated_approval = InspectionRecordApprovalModel.update_approval(
                approval_id=approval_id,
                approval_update_data=approval_update_data,
                session=session,
            )
            if not updated_approval:
                raise ResourceNotFoundError("Approval not found")
            if field_name in ["date_report_sent", "date_expected_return"]:
                ir_builder = InspectionRecordDataBuilder(
                    inspection=inspection,
                    ir_status=inspection_record.ir_status_id,
                    existing_ir=inspection_record,
                )
                ir_data = ir_builder.build_action_required_by_rp(
                    hard_reset=True
                ).build()
                ir_update_data["action_required_by_rp"] = ir_data.get(
                    "action_required_by_rp"
                )
            if field_name != "is_active":
                ir_update_data["ir_progress"] = IRProgressEnum.HOLDER_PRELIMINARY_REVIEW
                # Update ir_progress to HOLDER_PRELIMINARY_REVIEW
                InspectionRecordModel.update_inspection_record(
                    inspection_record_id=inspection_record_id,
                    ir_update_data=ir_update_data,
                    session=session,
                )

        return updated_approval

    @classmethod
    def update_approval_status(
        cls, inspection_id, inspection_record_id, approval_id, approval_status_data
    ):
        """Update approval status."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.inspection_record_exist_check(inspection_record_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        latest_approval = InspectionRecordApprovalModel.get_latest_approval_by_ir(
            inspection_record_id
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
        # Set approved_date if the approval status is approved and update ir_progress
        if status_to_be_updated == IRApprovalStatusEnum.APPROVED:
            approval_status_data["approved_date"] = datetime.now(timezone.utc)
            # Store the position of the approver at the time of approval
            approved_by_id = approval_status_data.get("approved_by_id")
            if approved_by_id:
                staff_user = StaffUserModel.find_by_id(approved_by_id)
                if staff_user and staff_user.position_id:
                    approval_status_data["approved_by_position_id"] = (
                        staff_user.position_id
                    )
            ir_progress = (
                IRProgressEnum.PRELIMINARY_APPROVED
                if latest_approval.ir_status_id == IRStatusEnum.PRELIMINARY.value
                else IRProgressEnum.FINAL_APPROVED
            )
        # If not approved, the IR progress is set to the drafting status
        if status_to_be_updated == IRApprovalStatusEnum.NOT_APPROVED:
            ir_progress = (
                IRProgressEnum.PRELIMINARY_DRAFTING
                if latest_approval.ir_status_id == IRStatusEnum.PRELIMINARY.value
                else IRProgressEnum.FINALIZING_RECORD
            )
        with session_scope() as session:
            updated_approval = InspectionRecordApprovalModel.update_approval(
                approval_id=approval_id,
                approval_update_data=approval_status_data,
                session=session,
            )
            InspectionRecordModel.update_inspection_record(
                inspection_record_id=inspection_record_id,
                ir_update_data={"ir_progress": ir_progress},
                session=session,
            )

        return updated_approval
