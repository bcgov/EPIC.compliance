"""Shared sub queries for reports."""

from compliance_api.models import db
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, AdministrativePenaltyInspectionRequirementMap)
from compliance_api.models.charge_recommendation import (
    ChargeRecommendation, ChargeRecommendationInspectionRequirementMap)
from compliance_api.models.order import Order, OrderInspectionRequirementMap, OrderReplaceStatusEnum
from compliance_api.models.restorative_justice import RestorativeJustice, RestorativeJusticeInspectionRequirementMap
from compliance_api.models.violation_ticket import ViolationTicket, ViolationTicketInspectionRequirementMap
from compliance_api.models.warning_letter import WarningLetter, WarningLetterInspectionRequirementMap


def get_requirement_order_sub_query():
    """Get requirement order sub query."""
    return (
        db.session.query(
            OrderInspectionRequirementMap.inspection_requirement_id,
            OrderInspectionRequirementMap.order_id,
        )
        .join(
            Order,
            Order.id == OrderInspectionRequirementMap.order_id,
        )
        .filter(
            OrderInspectionRequirementMap.is_active.is_(True),
            OrderInspectionRequirementMap.is_deleted.is_(False),
            Order.is_active.is_(True),
            Order.is_deleted.is_(False),
            Order.order_replace_status == OrderReplaceStatusEnum.ORIGINAL,
        )
        .subquery("requirement_order")
    )


def get_requirement_warning_letter_sub_query():
    """Get requirement warning letter sub query."""
    return (
        db.session.query(
            WarningLetterInspectionRequirementMap.inspection_requirement_id,
            WarningLetterInspectionRequirementMap.warning_letter_id,
        )
        .join(
            WarningLetter,
            WarningLetter.id == WarningLetterInspectionRequirementMap.warning_letter_id,
        )
        .filter(
            WarningLetterInspectionRequirementMap.is_active.is_(True),
            WarningLetterInspectionRequirementMap.is_deleted.is_(False),
            WarningLetter.is_active.is_(True),
            WarningLetter.is_deleted.is_(False),
        )
        .subquery("requirement_warning_letter")
    )


def get_requirement_violation_ticket_sub_query():
    """Get requirement violation ticket sub query."""
    return (
        db.session.query(
            ViolationTicketInspectionRequirementMap.inspection_requirement_id,
            ViolationTicketInspectionRequirementMap.violation_ticket_id,
        )
        .join(
            ViolationTicket,
            ViolationTicket.id
            == ViolationTicketInspectionRequirementMap.violation_ticket_id,
        )
        .filter(
            ViolationTicketInspectionRequirementMap.is_active.is_(True),
            ViolationTicketInspectionRequirementMap.is_deleted.is_(False),
            ViolationTicket.is_active.is_(True),
            ViolationTicket.is_deleted.is_(False),
        )
        .subquery("requirement_violation_ticket")
    )


def get_requirement_admin_penalty_sub_query():
    """Get requirement administrative penalty sub query."""
    return (
        db.session.query(
            AdministrativePenaltyInspectionRequirementMap.inspection_requirement_id,
            AdministrativePenaltyInspectionRequirementMap.administrative_penalty_id,
        )
        .join(
            AdministrativePenalty,
            AdministrativePenalty.id
            == AdministrativePenaltyInspectionRequirementMap.administrative_penalty_id,
        )
        .filter(
            AdministrativePenaltyInspectionRequirementMap.is_active.is_(True),
            AdministrativePenaltyInspectionRequirementMap.is_deleted.is_(False),
            AdministrativePenalty.is_active.is_(True),
            AdministrativePenalty.is_deleted.is_(False),
        )
        .subquery("requirement_admin_penalty")
    )


def get_requirement_charge_rec_sub_query():
    """Get requirement charge recommendation sub query."""
    return (
        db.session.query(
            ChargeRecommendationInspectionRequirementMap.inspection_requirement_id,
            ChargeRecommendationInspectionRequirementMap.charge_recommendation_id,
        )
        .join(
            ChargeRecommendation,
            ChargeRecommendation.id
            == ChargeRecommendationInspectionRequirementMap.charge_recommendation_id,
        )
        .filter(
            ChargeRecommendationInspectionRequirementMap.is_active.is_(True),
            ChargeRecommendationInspectionRequirementMap.is_deleted.is_(False),
            ChargeRecommendation.is_active.is_(True),
            ChargeRecommendation.is_deleted.is_(False),
        )
        .subquery("requirement_charge_rec")
    )


def get_requirement_restorative_justice_sub_query():
    """Get requirement restorative justice sub query."""
    return (
        db.session.query(
            RestorativeJusticeInspectionRequirementMap.inspection_requirement_id,
            RestorativeJusticeInspectionRequirementMap.restorative_justice_id,
        )
        .join(
            RestorativeJustice,
            RestorativeJustice.id
            == RestorativeJusticeInspectionRequirementMap.restorative_justice_id,
        )
        .filter(
            RestorativeJusticeInspectionRequirementMap.is_active.is_(True),
            RestorativeJusticeInspectionRequirementMap.is_deleted.is_(False),
            RestorativeJustice.is_active.is_(True),
            RestorativeJustice.is_deleted.is_(False),
        )
        .subquery("requirement_restorative_justice")
    )
