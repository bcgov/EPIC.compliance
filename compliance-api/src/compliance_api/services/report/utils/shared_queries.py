"""Shared sub queries for reports."""
from sqlalchemy import and_, func
from sqlalchemy.orm import aliased

from compliance_api.models import db
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, AdministrativePenaltyInspectionRequirementMap)
from compliance_api.models.agency import Agency
from compliance_api.models.case_file import CaseFile
from compliance_api.models.charge_recommendation import (
    ChargeRecommendation, ChargeRecommendationInspectionRequirementMap)
from compliance_api.models.complaint.complaint import Complaint
from compliance_api.models.complaint.complaint_option import ComplaintSource
from compliance_api.models.complaint.complaint_resolution import ComplaintResolution
from compliance_api.models.complaint.complaint_source_contact import ComplaintSourceContact
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.enforcement_action import EnforcementActionOption
from compliance_api.models.inspection import Inspection
from compliance_api.models.inspection.inspection_attendance import InspectionAttendance
from compliance_api.models.inspection.inspection_firstnation import InspectionFirstnation
from compliance_api.models.inspection.inspection_option import InspectionAttendanceOption
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.models.order import Order, OrderInspectionRequirementMap, OrderReplaceStatusEnum
from compliance_api.models.project import Project
from compliance_api.models.restorative_justice import RestorativeJustice, RestorativeJusticeInspectionRequirementMap
from compliance_api.models.staff_user import StaffUser
from compliance_api.models.topic import Topic
from compliance_api.models.unapproved_project import UnapprovedProject
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


def get_inspection_attendance_subquery():
    """Get subquery for inspection attendance types as comma-separated list."""
    return (
        db.session.query(
            InspectionAttendance.inspection_id,
            func.string_agg(
                InspectionAttendanceOption.name,
                ", "
            ).label("attendance_types")
        )
        .join(
            InspectionAttendanceOption,
            InspectionAttendance.attendance_option_id == InspectionAttendanceOption.id
        )
        .filter(
            InspectionAttendance.is_active.is_(True),
            InspectionAttendance.is_deleted.is_(False)
        )
        .group_by(InspectionAttendance.inspection_id)
        .subquery()
    )


def complaints_tab_query_base():
    """Build base complaints query."""
    query = (
        db.session.query(
            Complaint.complaint_number.label("complaint_number"),
            Project.id.label("project_id"),
            UnapprovedProject.id.label("unapproved_project_id"),
            UnapprovedProject.name.label("unapproved_project_name"),
            UnapprovedProject.type.label("unapproved_project_type"),
            Topic.name.label("topic"),
            Complaint.date_received.label("date_received"),
            ComplaintSource.id.label("complaint_source_id"),
            ComplaintSource.name.label("complaint_source"),
            ComplaintSourceContact.full_name.label("complaint_source_contact_full_name"),
            ComplaintSourceContact.alliance_name.label("complaint_source_contact_alliance_name"),
            ComplaintSourceContact.description.label("complaint_source_contact_description"),
            Agency.name.label("source_agency"),
            Complaint.source_first_nation_id.label("source_first_nation_id"),
            Complaint.concern_description.label("concern_description"),
            StaffUser.first_name.label("primary_officer_first_name"),
            StaffUser.last_name.label("primary_officer_last_name"),
            Complaint.status.label("complaint_status"),
            ComplaintResolution.name.label("complaint_resolution"),
            CaseFile.case_file_number.label("case_file_number"),
            CaseFile.date_created.label("case_file_date_created")
        )
        .join(CaseFile, Complaint.case_file_id == CaseFile.id)
        .outerjoin(Topic, Complaint.topic_id == Topic.id)
        .outerjoin(Project, CaseFile.project_id == Project.id)
        .outerjoin(UnapprovedProject, CaseFile.id == UnapprovedProject.case_file_id)
        .outerjoin(StaffUser, Complaint.primary_officer_id == StaffUser.id)
        .outerjoin(ComplaintResolution, Complaint.resolution_id == ComplaintResolution.id)
        .outerjoin(Agency, Complaint.source_agency_id == Agency.id)
        .join(ComplaintSource, Complaint.source_type_id == ComplaintSource.id)
        .outerjoin(ComplaintSourceContact, and_(
            ComplaintSourceContact.complaint_id == Complaint.id,
            ComplaintSourceContact.is_active.is_(True),
            ComplaintSourceContact.is_deleted.is_(False)
        ))
    )
    return query


def inspections_tab_query_base():
    """Build base query for First Nation Report."""
    # Create aliases for enforcement document models
    order_alias = aliased(Order)
    warning_letter_alias = aliased(WarningLetter)
    violation_ticket_alias = aliased(ViolationTicket)
    administrative_penalty_alias = aliased(AdministrativePenalty)
    charge_recommendation_alias = aliased(ChargeRecommendation)
    restorative_justice_alias = aliased(RestorativeJustice)

    requirement_order_subquery = get_requirement_order_sub_query()
    requirement_warning_letter_subquery = get_requirement_warning_letter_sub_query()
    requirement_violation_ticket_subquery = get_requirement_violation_ticket_sub_query()
    requirement_admin_penalty_subquery = get_requirement_admin_penalty_sub_query()
    requirement_charge_rec_subquery = get_requirement_charge_rec_sub_query()
    requirement_restorative_justice_subquery = get_requirement_restorative_justice_sub_query()
    attendance_subquery = get_inspection_attendance_subquery()

    query = (
        db.session.query(
            InspectionRequirement,
            InspectionRequirement.summary.label("summary"),
            Inspection.ir_number.label("ir_number"),
            attendance_subquery.c.attendance_types.label("inspection_attendance"),
            InspectionFirstnation.firstnation_id.label("first_nation_id"),
            Topic.name.label("topic_name"),
            InspectionRecord.ir_progress.label("ir_progress"),
            Inspection.start_date.label("start_date"),
            Inspection.end_date.label("end_date"),
            Project.id.label("project_id"),
            UnapprovedProject.id.label("unapproved_project_id"),
            UnapprovedProject.name.label("unapproved_project_name"),
            UnapprovedProject.type.label("unapproved_project_type"),
            ComplianceFindingOption.name.label("compliance_finding"),
            InspectionReqEnforcementMap.enforcement_action_id.label("enforcement_action_id"),
            EnforcementActionOption.name.label("enforcement_action"),
            # Enforcement statuses
            order_alias.order_status.label("order_status"),
            warning_letter_alias.status.label("warning_letter_status"),
            violation_ticket_alias.status.label("violation_ticket_status"),
            administrative_penalty_alias.referral_status.label("admin_penalty_status"),
            charge_recommendation_alias.status.label("charge_rec_status"),
            restorative_justice_alias.status.label("restorative_justice_status"),
            # Enforcement document numbers
            order_alias.order_number.label("order_number"),
            warning_letter_alias.warning_letter_number.label("warning_letter_number"),
            violation_ticket_alias.ticket_number.label("violation_ticket_number"),
            administrative_penalty_alias.administrative_penalty_number.label("admin_penalty_number"),
            charge_recommendation_alias.charge_recommendation_number.label("charge_rec_number"),
            restorative_justice_alias.restorative_justice_number.label("restorative_justice_number"),
            InspectionRecord.date_issued.label("ir_date_issued"),
            StaffUser.first_name.label("primary_officer_first_name"),
            StaffUser.last_name.label("primary_officer_last_name"),
            Inspection.inspection_status.label("inspection_status"),
            CaseFile.case_file_number.label("case_file_number"),
            CaseFile.date_created.label("case_file_date_created"),
        )
        .join(Inspection, InspectionRequirement.inspection_id == Inspection.id)
        .join(Topic, InspectionRequirement.topic_id == Topic.id)
        .join(attendance_subquery, attendance_subquery.c.inspection_id == Inspection.id)
        .outerjoin(InspectionFirstnation, and_(
            InspectionFirstnation.is_deleted.is_(False),
            InspectionFirstnation.inspection_id == Inspection.id,
        ))
        .join(CaseFile, Inspection.case_file_id == CaseFile.id)
        .outerjoin(Project, Inspection.project_id == Project.id)
        .outerjoin(UnapprovedProject, Inspection.case_file_id == UnapprovedProject.case_file_id)
        .join(ComplianceFindingOption, InspectionRequirement.compliance_finding_id == ComplianceFindingOption.id)
        .join(InspectionReqEnforcementMap, and_(
            InspectionReqEnforcementMap.requirement_id == InspectionRequirement.id,
            InspectionReqEnforcementMap.is_active.is_(True),
            InspectionReqEnforcementMap.is_deleted.is_(False)
        ))
        .join(InspectionRecord, InspectionRecord.inspection_id == Inspection.id)
        .join(
            EnforcementActionOption,
            InspectionReqEnforcementMap.enforcement_action_id == EnforcementActionOption.id
        )
        .join(StaffUser, Inspection.primary_officer_id == StaffUser.id)
        .outerjoin(
            requirement_order_subquery,
            requirement_order_subquery.c.inspection_requirement_id == InspectionRequirement.id
        )
        .outerjoin(
            order_alias,
            order_alias.id == requirement_order_subquery.c.order_id
        )
        .outerjoin(
            requirement_warning_letter_subquery,
            requirement_warning_letter_subquery.c.inspection_requirement_id == InspectionRequirement.id
        )
        .outerjoin(
            warning_letter_alias,
            warning_letter_alias.id == requirement_warning_letter_subquery.c.warning_letter_id
        )
        .outerjoin(
            requirement_violation_ticket_subquery,
            requirement_violation_ticket_subquery.c.inspection_requirement_id == InspectionRequirement.id
        )
        .outerjoin(
            violation_ticket_alias,
            violation_ticket_alias.id == requirement_violation_ticket_subquery.c.violation_ticket_id
        )
        .outerjoin(
            requirement_admin_penalty_subquery,
            requirement_admin_penalty_subquery.c.inspection_requirement_id == InspectionRequirement.id
        )
        .outerjoin(
            administrative_penalty_alias,
            administrative_penalty_alias.id == requirement_admin_penalty_subquery.c.administrative_penalty_id
        )
        .outerjoin(
            requirement_charge_rec_subquery,
            requirement_charge_rec_subquery.c.inspection_requirement_id == InspectionRequirement.id
        )
        .outerjoin(
            charge_recommendation_alias,
            charge_recommendation_alias.id == requirement_charge_rec_subquery.c.charge_recommendation_id
        )
        .outerjoin(
            requirement_restorative_justice_subquery,
            requirement_restorative_justice_subquery.c.inspection_requirement_id == InspectionRequirement.id
        )
        .outerjoin(
            restorative_justice_alias,
            restorative_justice_alias.id == requirement_restorative_justice_subquery.c.restorative_justice_id
        )
    )

    return query
