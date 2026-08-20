"""Review Board Service."""

from typing import List

from sqlalchemy import func, not_
from sqlalchemy.orm import aliased, joinedload

from compliance_api.models.administrative_penalty import AdministrativePenalty
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection_record import InspectionRecord, IRProgressEnum
from compliance_api.models.inspection_record_approval import InspectionRecordApproval
from compliance_api.models.order import Order
from compliance_api.models.order_approval import OrderApproval
from compliance_api.models.warning_letter import WarningLetter, WarningLetterProgressEnum
from compliance_api.models.warning_letter_approval import WarningLetterApproval


class ReviewBoardService:
    """Service layer for Review Board operations."""

    @classmethod
    def get_inspection_records_for_open_inspections(cls) -> List[InspectionRecord]:
        """Get all inspection records from OPEN inspections with approval information."""
        # Subquery to get the latest approval ID for each inspection record
        latest_approval_subq = (
            InspectionRecordApproval.query.with_entities(
                InspectionRecordApproval.inspection_record_id,
                func.max(InspectionRecordApproval.id).label("max_approval_id"),
            )
            .filter(
                InspectionRecordApproval.is_active.is_(True),
                InspectionRecordApproval.is_deleted.is_(False),
            )
            .group_by(InspectionRecordApproval.inspection_record_id)
            .subquery()
        )

        # Alias for the approval table to join with
        approval_alias = aliased(InspectionRecordApproval)

        records = (
            InspectionRecord.query.join(
                Inspection, Inspection.id == InspectionRecord.inspection_id
            )
            .outerjoin(
                latest_approval_subq,
                latest_approval_subq.c.inspection_record_id == InspectionRecord.id,
            )
            .outerjoin(
                approval_alias,
                approval_alias.id == latest_approval_subq.c.max_approval_id,
            )
            .options(
                joinedload(InspectionRecord.inspection).joinedload(Inspection.project),
                joinedload(InspectionRecord.inspection).joinedload(
                    Inspection.primary_officer
                ),
            )
            .filter(
                InspectionRecord.ir_progress != IRProgressEnum.ISSUED,
                InspectionRecord.is_active.is_(True),
                InspectionRecord.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
            )
            .add_columns(approval_alias)
            .order_by(InspectionRecord.created_date.desc())
            .all()
        )

        # Process results to attach approval data
        result_records = []
        for record_tuple in records:
            record = record_tuple[0]  # InspectionRecord object
            approval = record_tuple[1]  # InspectionRecordApproval object or None
            # pylint: disable=protected-access
            record._latest_approval = approval
            result_records.append(record)

        return result_records

    @classmethod
    def get_warning_letters_for_open_inspections(cls) -> List[WarningLetter]:
        """Get all warning letters from OPEN inspections with approval information."""
        # Subquery to get the latest approval ID for each warning letter
        latest_approval_subq = (
            WarningLetterApproval.query.with_entities(
                WarningLetterApproval.warning_letter_id,
                func.max(WarningLetterApproval.id).label("max_approval_id"),
            )
            .filter(
                WarningLetterApproval.is_active.is_(True),
                WarningLetterApproval.is_deleted.is_(False),
            )
            .group_by(WarningLetterApproval.warning_letter_id)
            .subquery()
        )

        # Alias for the approval table to join with
        approval_alias = aliased(WarningLetterApproval)

        warning_letters = (
            WarningLetter.query.join(
                Inspection, Inspection.id == WarningLetter.inspection_id
            )
            .outerjoin(
                latest_approval_subq,
                latest_approval_subq.c.warning_letter_id == WarningLetter.id,
            )
            .outerjoin(
                approval_alias,
                approval_alias.id == latest_approval_subq.c.max_approval_id,
            )
            .options(
                joinedload(WarningLetter.inspection).joinedload(Inspection.project),
                joinedload(WarningLetter.inspection).joinedload(
                    Inspection.primary_officer
                ),
            )
            .filter(
                WarningLetter.progress != WarningLetterProgressEnum.ISSUED,
                WarningLetter.is_active.is_(True),
                WarningLetter.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
            )
            .add_columns(approval_alias)
            .order_by(WarningLetter.created_date.desc())
            .all()
        )

        # Process results to attach approval data
        result_warning_letters = []
        for wl_tuple in warning_letters:
            warning_letter = wl_tuple[0]  # WarningLetter object
            approval = wl_tuple[1]  # WarningLetterApproval object or None
            # pylint: disable=protected-access
            warning_letter._latest_approval = approval
            result_warning_letters.append(warning_letter)

        return result_warning_letters

    @classmethod
    def get_orders_for_open_inspections(cls) -> List[Order]:
        """Get all orders from OPEN inspections with approval information."""
        # Subquery to get the latest approval ID for each order
        latest_approval_subq = (
            OrderApproval.query.with_entities(
                OrderApproval.order_id,
                func.max(OrderApproval.id).label("max_approval_id"),
            )
            .filter(
                OrderApproval.is_active.is_(True), OrderApproval.is_deleted.is_(False)
            )
            .group_by(OrderApproval.order_id)
            .subquery()
        )

        # Alias for the approval table to join with
        approval_alias = aliased(OrderApproval)

        orders = (
            Order.query.join(Inspection, Inspection.id == Order.inspection_id)
            .outerjoin(
                latest_approval_subq, latest_approval_subq.c.order_id == Order.id
            )
            .outerjoin(
                approval_alias,
                approval_alias.id == latest_approval_subq.c.max_approval_id,
            )
            .options(
                joinedload(Order.inspection).joinedload(Inspection.project),
                joinedload(Order.inspection).joinedload(Inspection.primary_officer),
            )
            .filter(
                Order.order_status.notin_(Order.get_closed_statuses()),
                Order.is_active.is_(True),
                Order.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
            )
            .add_columns(approval_alias)
            .order_by(Order.created_date.desc())
            .all()
        )

        # Process results to attach approval data
        result_orders = []
        for order_tuple in orders:
            order = order_tuple[0]  # Order object
            approval = order_tuple[1]  # OrderApproval object or None
            # pylint: disable=protected-access
            order._latest_approval = approval
            result_orders.append(order)

        return result_orders

    @classmethod
    def get_open_administrative_penalties(
        cls,
    ) -> List[AdministrativePenalty]:
        """Get all administrative penalties that are not closed.

        An AP is considered closed if it meets any of the following conditions:
        - AP referral status is 'AP Not Proceeding'
        - AP referral status is 'Referred to DM' AND a decision was made.
        """
        return (
            AdministrativePenalty.query.join(
                Inspection, Inspection.id == AdministrativePenalty.inspection_id
            )
            .options(
                joinedload(AdministrativePenalty.inspection).joinedload(
                    Inspection.project
                ),
                joinedload(AdministrativePenalty.inspection).joinedload(
                    Inspection.primary_officer
                ),
            )
            .filter(
                AdministrativePenalty.is_active.is_(True),
                AdministrativePenalty.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
                not_(AdministrativePenalty.get_closed_conditions()),
            )
            .order_by(AdministrativePenalty.created_date.desc())
            .all()
        )
