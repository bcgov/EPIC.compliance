"""CEB Summary Report Generator Service."""
from datetime import datetime, time
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from flask import current_app
from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from compliance_api.models import db
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, AdministrativePenaltyInspectionRequirementMap)
from compliance_api.models.agency import Agency
from compliance_api.models.case_file import CaseFile
from compliance_api.models.charge_recommendation import (
    ChargeRecommendation, ChargeRecommendationInspectionRequirementMap)
from compliance_api.models.complaint.complaint import Complaint
from compliance_api.models.complaint.complaint_option import ComplaintSource, ComplaintSourceEnum
from compliance_api.models.complaint.complaint_resolution import ComplaintResolution
from compliance_api.models.complaint.complaint_source_contact import ComplaintSourceContact
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.enforcement_action import EnforcementActionOption
from compliance_api.models.inspection.inspection import Inspection
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
from compliance_api.services.epic_track_service.track_service import TrackService
from compliance_api.services.service_utils import ServiceUtils

from .base import BaseReportGenerator


class CEBSummaryReportGenerator(BaseReportGenerator):
    """CEB Summary Report Generator Service."""

    def __init__(self, report_data):
        """Initialize the CEB Summary Report Generator with the provided report data."""
        super().__init__(report_data)

        start_date_raw = report_data.get("start_date")
        end_date_raw = report_data.get("end_date")

        self.start_date = (
            datetime.combine(
                start_date_raw, time.min
            ) if start_date_raw else None
        )
        self.end_date = (
            datetime.combine(
                end_date_raw, time.max
            ) if end_date_raw else None
        )
        current_app.logger.info(
            f"CEB Summary Report Generator initialized with start_date: {self.start_date}, end_date: {self.end_date}"
        )

    def generate(self):
        """CEB Summary Report Generation Logic."""
        projects = TrackService.get_projects()
        first_nations = TrackService.get_first_nations()

        # Inspections Tab
        data = self._build_inspections_tab_query().all()
        data = self._format_inspections_tab_data(data, projects)
        inspections_data_frame = pd.json_normalize(data)
        inspections_columns, inspections_headers = self._get_inspections_tab_columns_and_headers(inspections_data_frame)

        # Complaints Tab
        data = self._build_complaints_tab_query().all()
        data = self._format_complaints_tab_data(data, projects, first_nations)
        complaints_data_frame = pd.json_normalize(data)
        complaints_columns, complaints_headers = self._get_complaints_tab_columns_and_headers(complaints_data_frame)

        output = self._to_excel(
            inspections_data_frame,
            inspections_columns,
            inspections_headers,
            complaints_data_frame,
            complaints_columns,
            complaints_headers)
        return output

    def _to_excel(
                self,
                inspections_data_frame,
                inspections_columns,
                inspections_headers,
                complaints_data_frame,
                complaints_columns,
                complaints_headers
    ):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Inspections Tab
            inspections_data_frame.to_excel(
                writer,
                sheet_name="Inspections",
                columns=inspections_columns,
                header=inspections_headers,
                index=False,
            )
            worksheet = writer.sheets["Inspections"]
            # Making the columns wider
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))

                adjusted_width = min(max_length, 30)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Complaints Tab
            complaints_data_frame.to_excel(
                writer,
                sheet_name="Complaints",
                columns=complaints_columns,
                header=complaints_headers,
                index=False,
            )
            complaints_worksheet = writer.sheets["Complaints"]
            # Making the columns wider
            for column in complaints_worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))

                adjusted_width = min(max_length, 30)
                complaints_worksheet.column_dimensions[column_letter].width = adjusted_width
        output.seek(0)
        return output.getvalue()

    def _build_inspections_tab_query(self):
        """Build base query for CEB Summary Report."""

        requirement_order_subquery = self._get_requirement_order_sub_query()
        requirement_warning_letter_subquery = self._get_requirement_warning_letter_sub_query()
        requirement_violation_ticket_subquery = self._get_requirement_violation_ticket_sub_query()
        requirement_admin_penalty_subquery = self._get_requirement_admin_penalty_sub_query()
        requirement_charge_rec_subquery = self._get_requirement_charge_rec_sub_query()
        requirement_restorative_justice_subquery = self._get_requirement_restorative_justice_sub_query()

        query = (
            db.session.query(
                InspectionRequirement,
                InspectionRequirement.summary.label("summary"),
                Inspection.ir_number.label("ir_number"),
                Topic.name.label("topic_name"),
                InspectionRecord.ir_progress.label("ir_progress"),
                Project.id.label("project_id"),
                UnapprovedProject.id.label("unapproved_project_id"),
                UnapprovedProject.name.label("unapproved_project_name"),
                UnapprovedProject.type.label("unapproved_project_type"),
                ComplianceFindingOption.name.label("compliance_finding"),
                InspectionReqEnforcementMap.enforcement_action_id.label("enforcement_action_id"),
                EnforcementActionOption.name.label("enforcement_action"),
                # Enforcement statuses
                Order.order_status.label("order_status"),
                WarningLetter.status.label("warning_letter_status"),
                ViolationTicket.status.label("violation_ticket_status"),
                AdministrativePenalty.referral_status.label("admin_penalty_status"),
                ChargeRecommendation.status.label("charge_rec_status"),
                RestorativeJustice.status.label("restorative_justice_status"),
                # Enforcement numbers
                Order.order_number.label("order_number"),
                WarningLetter.warning_letter_number.label("warning_letter_number"),
                ViolationTicket.ticket_number.label("violation_ticket_number"),
                AdministrativePenalty.administrative_penalty_number.label("admin_penalty_number"),
                ChargeRecommendation.charge_recommendation_number.label("charge_rec_number"),
                RestorativeJustice.restorative_justice_number.label("restorative_justice_number"),
                InspectionRecord.date_issued.label("ir_date_issued"),
                StaffUser,
                Inspection.inspection_status.label("inspection_status"),
            )
            .join(Inspection, InspectionRequirement.inspection_id == Inspection.id)
            .join(Topic, InspectionRequirement.topic_id == Topic.id)
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
                Order,
                Order.id == requirement_order_subquery.c.order_id
            )
            .outerjoin(
                requirement_warning_letter_subquery,
                requirement_warning_letter_subquery.c.inspection_requirement_id == InspectionRequirement.id
            )
            .outerjoin(
                WarningLetter,
                WarningLetter.id == requirement_warning_letter_subquery.c.warning_letter_id
            )
            .outerjoin(
                requirement_violation_ticket_subquery,
                requirement_violation_ticket_subquery.c.inspection_requirement_id == InspectionRequirement.id
            )
            .outerjoin(
                ViolationTicket,
                ViolationTicket.id == requirement_violation_ticket_subquery.c.violation_ticket_id
            )
            .outerjoin(
                requirement_admin_penalty_subquery,
                requirement_admin_penalty_subquery.c.inspection_requirement_id == InspectionRequirement.id
            )
            .outerjoin(
                AdministrativePenalty,
                AdministrativePenalty.id == requirement_admin_penalty_subquery.c.administrative_penalty_id
            )
            .outerjoin(
                requirement_charge_rec_subquery,
                requirement_charge_rec_subquery.c.inspection_requirement_id == InspectionRequirement.id
            )
            .outerjoin(
                ChargeRecommendation,
                ChargeRecommendation.id == requirement_charge_rec_subquery.c.charge_recommendation_id
            )
            .outerjoin(
                requirement_restorative_justice_subquery,
                requirement_restorative_justice_subquery.c.inspection_requirement_id == InspectionRequirement.id
            )
            .outerjoin(
                RestorativeJustice,
                RestorativeJustice.id == requirement_restorative_justice_subquery.c.restorative_justice_id
            )
            .filter(
                InspectionRequirement.is_active.is_(True),
                InspectionRequirement.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
                InspectionRecord.is_active.is_(True),
                InspectionRecord.is_deleted.is_(False),
                Inspection.start_date >= self.start_date if self.start_date else True,
                Inspection.start_date <= self.end_date if self.end_date else True,
            )
            .order_by(InspectionRequirement.id, EnforcementActionOption.id)
            .options(
                selectinload(InspectionRequirement.requirement_source_details)
            )
        )
        return query

    def _build_complaints_tab_query(self):
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
                ComplaintSourceContact,
                Agency.name.label("source_agency"),
                Complaint.source_first_nation_id.label("source_first_nation_id"),
                StaffUser,
                Complaint.status.label("complaint_status"),
                ComplaintResolution.name.label("complaint_resolution"),
                CaseFile.case_file_number.label("case_file_number"),
            )
            .join(CaseFile, Complaint.case_file_id == CaseFile.id)
            .outerjoin(Topic, Complaint.topic_id == Topic.id)
            .outerjoin(Project, CaseFile.project_id == Project.id)
            .outerjoin(UnapprovedProject, CaseFile.id == UnapprovedProject.case_file_id)
            .outerjoin(StaffUser, Complaint.primary_officer_id == StaffUser.id)
            .outerjoin(ComplaintResolution, Complaint.resolution_id == ComplaintResolution.id)
            .outerjoin(ComplaintSourceContact, ComplaintSourceContact.complaint_id == Complaint.id)
            .outerjoin(Agency, Complaint.source_agency_id == Agency.id)
            .join(ComplaintSource, Complaint.source_type_id == ComplaintSource.id)
            .filter(
                Complaint.is_active.is_(True),
                Complaint.is_deleted.is_(False),
                CaseFile.is_active.is_(True),
                CaseFile.is_deleted.is_(False),
                Complaint.date_received >= self.start_date if self.start_date else True,
                Complaint.date_received <= self.end_date if self.end_date else True,
            )
            .distinct(Complaint.id)
        )
        return query

    @staticmethod
    def _get_requirement_order_sub_query():
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

    @staticmethod
    def _get_requirement_warning_letter_sub_query():
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

    @staticmethod
    def _get_requirement_violation_ticket_sub_query():
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

    @staticmethod
    def _get_requirement_admin_penalty_sub_query():
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

    @staticmethod
    def _get_requirement_charge_rec_sub_query():
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

    @staticmethod
    def _get_requirement_restorative_justice_sub_query():
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

    @staticmethod
    def _format_inspections_tab_data(data, projects):
        """Format data for excel export."""
        result = []
        for row in data:
            inspection_requirement = row.InspectionRequirement
            raw_enforcement_status = ServiceUtils.get_enforcement_status_by_type(row)
            primary_officer = row.StaffUser
            req_source_details = inspection_requirement.requirement_source_details

            # Project Logic:
            # If case_file.project_id is null it is unapproved
            # and you should be able to find it in the unapproved_projects table
            # If case_file.project_id has a valid number it should be from EPIC.Track

            if not row.project_id:
                project_name = row.unapproved_project_name
                project_type = row.unapproved_project_type
            else:
                project = next((p for p in projects if p.get('id') == row.project_id), None)
                project_name = project.get("name") if project else None
                project_type = project.get("type", None).get("name", None) if project else None

            condition_num_string = ""
            source_string = ""
            for req_source in req_source_details:
                number_field = ServiceUtils.get_requirement_grid_source_number_field(req_source)
                name_field = ServiceUtils.get_requirement_grid_source_name_field(req_source)
                condition_num_string += f", {number_field}" if condition_num_string else number_field or ""
                source_string += f", {name_field}" if source_string else name_field

            item = {
                "ir_number": row.ir_number,
                "topic_name": row.topic_name,
                "summary": row.summary,
                "ir_progress": row.ir_progress.value if row.ir_progress else None,
                "project_name": project_name,
                "project_type": project_type,
                "compliance_finding": row.compliance_finding,
                "enforcement_action": row.enforcement_action,
                "enforcement_status": raw_enforcement_status.value if raw_enforcement_status else None,
                "enforcement_document_number": ServiceUtils.get_enforcement_number_by_type(row),
                "condition_number": condition_num_string,
                "requirement_source": source_string,
                "ir_issuance_date": row.ir_date_issued.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
                if row.ir_date_issued else None,
                "primary_officer": f"{primary_officer.first_name} {primary_officer.last_name}"
                if primary_officer else None,
                "inspection_status": row.inspection_status.value if row.inspection_status else None,
            }
            result.append(item)
        return result

    @staticmethod
    def _format_complaints_tab_data(data, projects, first_nations):
        """Format complaints data for excel export."""
        result = []
        for row in data:
            primary_officer = row.StaffUser

            # Project Logic:
            # If case_file.project_id is null it is unapproved
            # and you should be able to find it in the unapproved_projects table
            # If case_file.project_id has a valid number it should be from EPIC.Track

            if not row.project_id:
                project_name = row.unapproved_project_name
                project_type = row.unapproved_project_type
            else:
                project = next((p for p in projects if p.get('id') == row.project_id), None)
                project_name = project.get("name") if project else None
                project_type = project.get("type", None).get("name", None) if project else None

            # Complaint Source Details Logic
            # If Complaint Source = Public, pull field “Full Name”
            # If Complaint Source = First Nation, pull field “First Nation”
            # If Complaint Source = First Nations Alliance, pull field “Alliance Name”
            # If Complaint Source = Agency, pull field “Agency”
            # If Complaint Source = Other, pull field “Description”

            complaint_source_contact = row.ComplaintSourceContact
            complaint_source_details = ""

            if row.complaint_source == ComplaintSourceEnum.PUBLIC.value:
                complaint_source_details = complaint_source_contact.full_name if complaint_source_contact else ""
            elif row.complaint_source == ComplaintSourceEnum.FIRST_NATION.value:
                first_nation = next((fn for fn in first_nations if fn.get('id') == row.source_first_nation_id), None)
                complaint_source_details = first_nation.get("name") if first_nation else ""
            elif row.complaint_source == ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE.value:
                complaint_source_details = complaint_source_contact.alliance_name if complaint_source_contact else ""
            elif row.complaint_source == ComplaintSourceEnum.AGENCY.value:
                complaint_source_details = row.source_agency if row.source_agency else ""
            elif row.complaint_source == ComplaintSourceEnum.OTHER.value:
                complaint_source_details = complaint_source_contact.description if complaint_source_contact else ""

            item = {
                "complaint_number": row.complaint_number,
                "project_name": project_name,
                "project_type": project_type,
                "topic": row.topic,
                "date_received": row.date_received.astimezone(ZoneInfo("America/Los_Angeles"))
                .strftime("%Y-%m-%d") if row.date_received else None,
                "complaint_source": row.complaint_source,
                "complaint_source_details": complaint_source_details,
                "primary_officer": f"{primary_officer.first_name} {primary_officer.last_name}"
                if primary_officer else None,
                "complaint_status": row.complaint_status.value if row.complaint_status else None,
                "complaint_resolution": row.complaint_resolution,
                "case_file_number": row.case_file_number,
            }
            result.append(item)
        return result

    @staticmethod
    def _get_inspections_tab_columns_and_headers(data_frame):
        """Get existing columns and their headers for Excel export."""
        column_mapping = {
            "ir_number": "IR Number",
            "topic_name": "Topic",
            "summary": "Summary",
            "ir_progress": "IR Progress",
            "project_name": "Project Name",
            "project_type": "Project Type",
            "compliance_finding": "Compliance Finding",
            "enforcement_action": "Enforcement Action",
            "enforcement_status": "Enforcement Status",
            "enforcement_document_number": "Enforcement Document Number",
            "condition_number": "Condition Number",
            "requirement_source": "Requirement Source",
            "ir_issuance_date": "IR Issuance Date",
            "primary_officer": "Primary Officer",
            "inspection_status": "Inspection Status",
        }

        existing_columns = [col for col in column_mapping.keys() if col in data_frame.columns]
        headers = [column_mapping[col] for col in existing_columns]

        return existing_columns, headers

    @staticmethod
    def _get_complaints_tab_columns_and_headers(data_frame):
        """Get existing columns and their headers for Excel export."""
        column_mapping = {
            "complaint_number": "Complaint Number",
            "project_name": "Project Name",
            "project_type": "Project Type",
            "topic": "Topic",
            "date_received": "Date Received",
            "complaint_source": "Complaint Source",
            "complaint_source_details": "Complaint Source Details",
            "primary_officer": "Primary Officer",
            "complaint_status": "Complaint Status",
            "complaint_resolution": "Complaint Resolution",
            "case_file_number": "Case File Number",
        }

        existing_columns = [col for col in column_mapping.keys() if col in data_frame.columns]
        headers = [column_mapping[col] for col in existing_columns]

        return existing_columns, headers
