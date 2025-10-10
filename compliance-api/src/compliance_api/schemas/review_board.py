"""Schema for Review Board responses."""

from marshmallow import Schema, fields

from compliance_api.models.staff_user import StaffUser
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT, UNAPPROVED_PROJECT_NAME


class ReviewBoardInspectionRecordSchema(Schema):  # pylint: disable=no-self-use
    """Schema for Review Board Inspection Record response."""

    # IR Number
    ir_number = fields.Str(dump_only=True, attribute="inspection.ir_number")

    # Project title from inspection
    project_title = fields.Method("get_project_title", dump_only=True)

    # Inspection start date
    inspection_start_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        dump_only=True,
        attribute="inspection.start_date",
        allow_none=True,
    )

    # Primary officer from inspection
    primary_officer = fields.Method("get_primary_officer", dump_only=True)

    # Approval fields - if under review
    send_for_review_date = fields.Method("get_send_for_review_date", dump_only=True)
    deputy_director = fields.Method("get_deputy_director", dump_only=True)
    approved_date = fields.Method("get_approved_date", dump_only=True)

    # Approval fields from inspection record approval
    date_report_sent = fields.Method("get_date_report_sent", dump_only=True)
    expected_return_date = fields.Method("get_expected_return_date", dump_only=True)
    date_response = fields.Method("get_date_response", dump_only=True)

    # Intended issuance date from inspection record
    intended_issuance_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT, dump_only=True
    )

    # IR Status, Progress and Approval Status
    ir_status = fields.Method("get_ir_status", dump_only=True)
    ir_progress = fields.Method("get_ir_progress", dump_only=True)
    approval_status = fields.Method("get_approval_status", dump_only=True)

    def get_project_title(self, obj):  # pylint: disable=no-self-use
        """Get project title from inspection."""
        if obj.inspection and obj.inspection.project:
            return obj.inspection.project.name
        return UNAPPROVED_PROJECT_NAME

    def get_primary_officer(self, obj):  # pylint: disable=no-self-use
        """Get primary officer from inspection."""
        if obj.inspection and obj.inspection.primary_officer:
            officer = obj.inspection.primary_officer
            return {
                "id": officer.id,
                "first_name": officer.first_name,
                "last_name": officer.last_name,
                "name": f"{officer.first_name} {officer.last_name}",
            }
        return None

    def get_send_for_review_date(self, obj):  # pylint: disable=no-self-use
        """Get send for review date from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.created_date:
            return latest_approval.created_date.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_deputy_director(self, obj):  # pylint: disable=no-self-use
        """Get deputy director name from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.approved_by:
            officer = latest_approval.approved_by
            return {
                "id": officer.id,
                "first_name": officer.first_name,
                "last_name": officer.last_name,
                "name": f"{officer.first_name} {officer.last_name}",
            }
        return None

    def get_approved_date(self, obj):  # pylint: disable=no-self-use
        """Get approved date from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.approved_date:
            return latest_approval.approved_date.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_date_report_sent(self, obj):  # pylint: disable=no-self-use
        """Get date report sent from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.date_report_sent:
            return latest_approval.date_report_sent.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_expected_return_date(self, obj):  # pylint: disable=no-self-use
        """Get expected return date from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.date_expected_return:
            return latest_approval.date_expected_return.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_date_response(self, obj):  # pylint: disable=no-self-use
        """Get date response from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.date_response:
            return latest_approval.date_response.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_ir_status(self, obj):  # pylint: disable=no-self-use
        """Get IR status from inspection record."""
        if hasattr(obj, "ir_status") and obj.ir_status:
            return {"id": obj.ir_status.id, "name": obj.ir_status.name}
        return None

    def get_ir_progress(self, obj):  # pylint: disable=no-self-use
        """Get IR progress from inspection record."""
        if hasattr(obj, "ir_progress") and obj.ir_progress:
            return {"id": obj.ir_progress.name, "name": obj.ir_progress.value}
        return None

    def get_approval_status(self, obj):  # pylint: disable=no-self-use
        """Get approval status from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if (
            latest_approval
            and hasattr(latest_approval, "approval_status")
            and latest_approval.approval_status
        ):
            return {
                "id": latest_approval.approval_status.name,
                "name": latest_approval.approval_status.value,
            }
        return None

    def _get_latest_approval(self, obj):  # pylint: disable=no-self-use
        """Get the latest approval data that was pre-fetched by the service layer."""
        return getattr(obj, "_latest_approval", None)


class ReviewBoardWarningLetterSchema(Schema):  # pylint: disable=no-self-use
    """Schema for warning letter review board response."""

    # IR Number
    ir_number = fields.Str(dump_only=True, attribute="inspection.ir_number")

    # Warning Letter Number
    warning_letter_number = fields.Str(dump_only=True)

    project_title = fields.Method("get_project_title")
    inspection_start_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        dump_only=True,
        attribute="inspection.start_date",
        allow_none=True,
    )
    primary_officer = fields.Method("get_primary_officer")
    issuing_officer = fields.Method("get_issuing_officer")
    approved_date = fields.Method("get_approved_date")
    review_requested_date = fields.Method("get_review_requested_date")
    approved_by = fields.Method("get_approved_by")
    deputy_director = fields.Method("get_deputy_director")
    intended_issuance_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT, dump_only=True
    )

    # Warning Letter Status, Progress and Approval Status
    warning_letter_status = fields.Method("get_warning_letter_status", dump_only=True)
    warning_letter_progress = fields.Method(
        "get_warning_letter_progress", dump_only=True
    )
    approval_status = fields.Method("get_approval_status", dump_only=True)

    def get_project_title(self, obj):  # pylint: disable=no-self-use
        """Get project title from inspection."""
        return (
            obj.inspection.project.name
            if obj.inspection and obj.inspection.project
            else UNAPPROVED_PROJECT_NAME
        )

    def get_issuing_officer(self, obj):  # pylint: disable=no-self-use
        """Get issuing officer information."""
        if obj.issuing_officer:
            officer = obj.issuing_officer
            return {
                "id": officer.id,
                "first_name": officer.first_name,
                "last_name": officer.last_name,
                "name": f"{officer.first_name} {officer.last_name}",
            }
        return None

    def get_primary_officer(self, obj):  # pylint: disable=no-self-use
        """Get primary officer from pre-fetched data."""
        if obj.inspection and obj.inspection.primary_officer:
            officer = obj.inspection.primary_officer
            return {
                "id": officer.id,
                "first_name": officer.first_name,
                "last_name": officer.last_name,
                "name": f"{officer.first_name} {officer.last_name}",
            }
        return None

    def _get_latest_approval(self, obj):  # pylint: disable=no-self-use
        """Get the latest approval data that was pre-fetched by the service layer."""
        return getattr(obj, "_latest_approval", None)

    def get_approved_date(self, obj):  # pylint: disable=no-self-use
        """Get approved date from latest approval."""
        approval = self._get_latest_approval(obj)
        if approval and approval.approved_date:
            return approval.approved_date.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_review_requested_date(self, obj):  # pylint: disable=no-self-use
        """Get review requested date from latest approval."""
        approval = self._get_latest_approval(obj)
        if approval and approval.created_date:
            return approval.created_date.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_approved_by(self, obj):  # pylint: disable=no-self-use
        """Get approved by staff user name from latest approval."""
        approval = self._get_latest_approval(obj)
        if approval and approval.approved_by_id:
            # Need to fetch the staff user for the name
            staff_user = StaffUser.query.get(approval.approved_by_id)
            if staff_user:
                return f"{staff_user.first_name} {staff_user.last_name}"
        return None

    def get_deputy_director(self, obj):  # pylint: disable=no-self-use
        """Get deputy director name from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.approved_by_id:
            # Need to fetch the staff user for the name
            staff_user = StaffUser.query.get(latest_approval.approved_by_id)
            if staff_user:
                return {
                    "id": staff_user.id,
                    "first_name": staff_user.first_name,
                    "last_name": staff_user.last_name,
                    "name": f"{staff_user.first_name} {staff_user.last_name}",
                }
        return None

    def get_warning_letter_status(self, obj):  # pylint: disable=no-self-use
        """Get warning letter status."""
        if hasattr(obj, "warning_letter_status") and obj.warning_letter_status:
            return {
                "id": obj.warning_letter_status.name,
                "name": obj.warning_letter_status.value,
            }
        return None

    def get_warning_letter_progress(self, obj):  # pylint: disable=no-self-use
        """Get warning letter progress."""
        if hasattr(obj, "warning_letter_progress") and obj.warning_letter_progress:
            return {
                "id": obj.warning_letter_progress.name,
                "name": obj.warning_letter_progress.value,
            }
        return None

    def get_approval_status(self, obj):  # pylint: disable=no-self-use
        """Get approval status from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if (
            latest_approval
            and hasattr(latest_approval, "approval_status")
            and latest_approval.approval_status
        ):
            return {
                "id": latest_approval.approval_status.name,
                "name": latest_approval.approval_status.value,
            }
        return None


class ReviewBoardOrderSchema(Schema):  # pylint: disable=no-self-use
    """Schema for Review Board Order response."""

    # IR Number
    ir_number = fields.Str(dump_only=True, attribute="inspection.ir_number")

    # Order number
    order_number = fields.Str(dump_only=True)

    # Project title from inspection
    project_title = fields.Method("get_project_title", dump_only=True)

    # Inspection start date
    inspection_start_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        dump_only=True,
        attribute="inspection.start_date",
        allow_none=True,
    )

    # Primary officer from inspection
    primary_officer = fields.Method("get_primary_officer", dump_only=True)
    issuing_officer = fields.Method("get_issuing_officer", dump_only=True)
    # Approval fields
    send_for_review_date = fields.Method("get_send_for_review_date", dump_only=True)
    deputy_director = fields.Method("get_deputy_director", dump_only=True)
    approved_date = fields.Method("get_approved_date", dump_only=True)

    # Order specific fields
    order_status = fields.Method("get_order_status", dump_only=True)
    order_progress = fields.Method("get_order_progress", dump_only=True)
    approval_status = fields.Method("get_approval_status", dump_only=True)
    intended_issuance_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT, dump_only=True
    )

    def get_project_title(self, obj):  # pylint: disable=no-self-use
        """Get project title from inspection."""
        if obj.inspection and obj.inspection.project:
            return obj.inspection.project.name
        return UNAPPROVED_PROJECT_NAME

    def get_issuing_officer(self, obj):  # pylint: disable=no-self-use
        """Get issuing officer from pre-fetched data."""
        if obj.issuing_officer:
            return {
                "id": obj.issuing_officer.id,
                "first_name": obj.issuing_officer.first_name,
                "last_name": obj.issuing_officer.last_name,
                "name": f"{obj.issuing_officer.first_name} {obj.issuing_officer.last_name}",
            }
        return None

    def get_primary_officer(self, obj):  # pylint: disable=no-self-use
        """Get primary officer from pre-fetched data."""
        if obj.inspection and obj.inspection.primary_officer:
            officer = obj.inspection.primary_officer
            return {
                "id": officer.id,
                "first_name": officer.first_name,
                "last_name": officer.last_name,
                "name": f"{officer.first_name} {officer.last_name}",
            }
        return None

    def get_send_for_review_date(self, obj):  # pylint: disable=no-self-use
        """Get send for review date from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.created_date:
            return latest_approval.created_date.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_deputy_director(self, obj):  # pylint: disable=no-self-use
        """Get deputy director name from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.approved_by_id:
            # Need to fetch the staff user for the name
            staff_user = StaffUser.query.get(latest_approval.approved_by_id)
            if staff_user:
                return {
                    "id": staff_user.id,
                    "first_name": staff_user.first_name,
                    "last_name": staff_user.last_name,
                    "name": f"{staff_user.first_name} {staff_user.last_name}",
                }
        return None

    def get_approved_date(self, obj):  # pylint: disable=no-self-use
        """Get approved date from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if latest_approval and latest_approval.approved_date:
            return latest_approval.approved_date.strftime(INPUT_DATE_TIME_FORMAT)
        return None

    def get_order_status(self, obj):  # pylint: disable=no-self-use
        """Get order status."""
        if obj.order_status:
            return {"id": obj.order_status.name, "name": obj.order_status.value}
        return None

    def get_order_progress(self, obj):  # pylint: disable=no-self-use
        """Get order progress."""
        if obj.order_progress:
            return {"id": obj.order_progress.name, "name": obj.order_progress.value}
        return None

    def get_approval_status(self, obj):  # pylint: disable=no-self-use
        """Get approval status from latest approval."""
        latest_approval = self._get_latest_approval(obj)
        if (
            latest_approval
            and hasattr(latest_approval, "approval_status")
            and latest_approval.approval_status
        ):
            return {
                "id": latest_approval.approval_status.name,
                "name": latest_approval.approval_status.value,
            }
        return None

    def _get_latest_approval(self, obj):  # pylint: disable=no-self-use
        """Get the latest approval data that was pre-fetched by the service layer."""
        return getattr(obj, "_latest_approval", None)


class ReviewBoardAdministrativePenaltySchema(Schema):  # pylint: disable=no-self-use
    """Schema for Review Board Administrative Penalty response."""

    # IR Number
    ir_number = fields.Str(dump_only=True, attribute="inspection.ir_number")

    # Administrative penalty number
    administrative_penalty_number = fields.Str(dump_only=True)

    # Project title from inspection
    project_title = fields.Method("get_project_title", dump_only=True)

    # Inspection start date
    inspection_start_date = fields.DateTime(
        format=INPUT_DATE_TIME_FORMAT,
        dump_only=True,
        attribute="inspection.start_date",
        allow_none=True,
    )

    # Primary officer from inspection
    primary_officer = fields.Method("get_primary_officer", dump_only=True)

    # Administrative penalty specific fields
    referral_status = fields.Method("get_referral_status", dump_only=True)
    date_referred = fields.DateTime(format=INPUT_DATE_TIME_FORMAT, dump_only=True)
    decision_date = fields.DateTime(format=INPUT_DATE_TIME_FORMAT, dump_only=True)
    decision = fields.Method("get_decision", dump_only=True)
    penalty_amount = fields.Decimal(dump_only=True, as_string=True)

    def get_project_title(self, obj):  # pylint: disable=no-self-use
        """Get project title from inspection."""
        if obj.inspection and obj.inspection.project:
            return obj.inspection.project.name
        return UNAPPROVED_PROJECT_NAME

    def get_primary_officer(self, obj):  # pylint: disable=no-self-use
        """Get primary officer from pre-fetched data."""
        officer = getattr(obj, "_primary_officer", None)
        if officer:
            return {
                "id": officer.id,
                "first_name": officer.first_name,
                "last_name": officer.last_name,
                "name": f"{officer.first_name} {officer.last_name}",
            }
        return None

    def get_referral_status(self, obj):  # pylint: disable=no-self-use
        """Get referral status."""
        if obj.referral_status:
            return {"id": obj.referral_status.name, "name": obj.referral_status.value}
        return None

    def get_decision(self, obj):  # pylint: disable=no-self-use
        """Get decision."""
        if obj.decision:
            return {"id": obj.decision.name, "name": obj.decision.value}
        return None
