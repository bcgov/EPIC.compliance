"""First Nation Report Generator Service."""
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from flask import current_app
from sqlalchemy import and_
from sqlalchemy.orm import aliased, selectinload

from compliance_api.models import db
from compliance_api.models.administrative_penalty import AdministrativePenalty
from compliance_api.models.case_file import CaseFile
from compliance_api.models.charge_recommendation import ChargeRecommendation
from compliance_api.models.complaint.complaint import Complaint
from compliance_api.models.complaint.complaint_option import ComplaintSource
from compliance_api.models.complaint.complaint_resolution import ComplaintResolution
from compliance_api.models.complaint.complaint_source_contact import ComplaintSourceContact
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.enforcement_action import EnforcementActionOption
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_firstnation import InspectionFirstnation
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.models.order import Order
from compliance_api.models.project import Project
from compliance_api.models.restorative_justice import RestorativeJustice
from compliance_api.models.staff_user import StaffUser
from compliance_api.models.topic import Topic
from compliance_api.models.unapproved_project import UnapprovedProject
from compliance_api.models.violation_ticket import ViolationTicket
from compliance_api.models.warning_letter import WarningLetter
from compliance_api.services.epic_track_service.track_service import TrackService
from compliance_api.services.report.shared_queries import (
    get_inspection_attendance_subquery, get_requirement_admin_penalty_sub_query, get_requirement_charge_rec_sub_query,
    get_requirement_order_sub_query, get_requirement_restorative_justice_sub_query,
    get_requirement_violation_ticket_sub_query, get_requirement_warning_letter_sub_query)
from compliance_api.services.service_utils import ServiceUtils

from .base import BaseReportGenerator


class FirstNationReportGenerator(BaseReportGenerator):
    """First Nation Report Generator Service."""

    def __init__(self, report_data):
        """Initialize the First Nation Report Generator with the provided report data."""
        super().__init__(report_data)

        self.first_nation_id = report_data.get("first_nation_id")
        self._project_cache = {}  # key: (project_id, date_str), value: project dict

        current_app.logger.info(
            f"First Nation Report Generator initialized with first_nation_id: {self.first_nation_id}."
        )

    def generate(self):
        """First Nation Report Generation Logic."""
        first_nations = TrackService.get_first_nations()
        first_nations_name = next(
            (fn.get("name") for fn in first_nations if fn.get("id") == self.first_nation_id),
            "Unknown First Nation"
        )

        # Inspections Tab
        data = self._build_inspections_tab_query().all()
        data = self._format_inspections_tab_data(data, first_nations)
        inspections_data_frame = pd.json_normalize(data)
        inspections_headers, inspections_columns = self._get_inspections_tab_columns_and_headers()

        # Complaints Tab
        data = self._build_complaints_tab_query().all()
        data = self._format_complaints_tab_data(data, first_nations_name)
        complaints_data_frame = pd.json_normalize(data)
        complaints_headers, complaints_columns = self._get_complaints_tab_columns_and_headers()

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

            # If there is no data, create an empty dataframe with columns so that
            # the excel file will still have the correct headers and structure
            if inspections_data_frame.empty:
                inspections_data_frame = pd.DataFrame(columns=inspections_columns)
            if complaints_data_frame.empty:
                complaints_data_frame = pd.DataFrame(columns=complaints_columns)

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
                StaffUser,
                Inspection.inspection_status.label("inspection_status"),
                CaseFile.case_file_number.label("case_file_number"),
                CaseFile.date_created.label("case_file_date_created"),
            )
            .join(Inspection, InspectionRequirement.inspection_id == Inspection.id)
            .join(Topic, InspectionRequirement.topic_id == Topic.id)
            .join(attendance_subquery, attendance_subquery.c.inspection_id == Inspection.id)
            .join(InspectionFirstnation, and_(
                InspectionFirstnation.is_deleted.is_(False),
                InspectionFirstnation.inspection_id == Inspection.id,
                InspectionFirstnation.firstnation_id == self.first_nation_id
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
            .filter(
                InspectionRequirement.is_active.is_(True),
                InspectionRequirement.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
                InspectionRecord.is_active.is_(True),
                InspectionRecord.is_deleted.is_(False),
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
                Complaint.source_first_nation_id.label("source_first_nation_id"),
                Complaint.concern_description.label("concern_description"),
                StaffUser,
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
            .outerjoin(ComplaintSourceContact, and_(
                ComplaintSourceContact.complaint_id == Complaint.id,
                ComplaintSourceContact.is_active.is_(True),
                ComplaintSourceContact.is_deleted.is_(False)
            ))
            .join(ComplaintSource, Complaint.source_type_id == ComplaintSource.id)
            .filter(
                Complaint.is_active.is_(True),
                Complaint.is_deleted.is_(False),
                Complaint.source_first_nation_id == self.first_nation_id,
                CaseFile.is_active.is_(True),
                CaseFile.is_deleted.is_(False),
            )
            .order_by(Complaint.id)
            .distinct(Complaint.id)
        )
        return query

    def _format_inspections_tab_data(self, data, first_nations):
        """Format data for excel export."""
        result = []
        first_nation = next((fn for fn in first_nations if fn.get('id') == self.first_nation_id), None)
        first_nation_name = first_nation.get("name") if first_nation else ""

        for row in data:
            inspection_requirement = row.InspectionRequirement
            raw_enforcement_status = ServiceUtils.get_enforcement_status_by_type(row)
            primary_officer = row.StaffUser
            req_source_details = inspection_requirement.requirement_source_details

            # Project Logic:
            # If case_file.project_id is null it is unapproved
            # and in the unapproved_projects table
            # If case_file.project_id has a valid number it should be from EPIC.Track

            if not row.project_id:
                project_name = row.unapproved_project_name
                project_type = row.unapproved_project_type
            else:
                project = self._get_project_cached(row.project_id, as_of_date=row.case_file_date_created)
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
                "first_nation": first_nation_name,
                "ir_progress": row.ir_progress.value if row.ir_progress else None,
                "project_name": project_name,
                "project_type": project_type,
                "start_date": row.start_date.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
                if row.start_date else None,
                "end_date": row.end_date.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
                if row.end_date and row.start_date != row.end_date else None,
                "topic_name": row.topic_name,
                "summary": row.summary,
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
                "case_file_number": row.case_file_number,
            }
            result.append(item)
        return result

    def _format_complaints_tab_data(self, data, first_nations_name):
        """Format complaints data for excel export."""
        result = []
        for row in data:
            primary_officer = row.StaffUser

            # Project Logic:
            # If case_file.project_id is null it is unapproved
            # and in the unapproved_projects table
            # If case_file.project_id has a valid number it should be from EPIC.Track

            if not row.project_id:
                project_name = row.unapproved_project_name
                project_type = row.unapproved_project_type
            else:
                project = self._get_project_cached(row.project_id, as_of_date=row.case_file_date_created)
                project_name = project.get("name") if project else None
                project_type = project.get("type", None).get("name", None) if project else None

            item = {
                "complaint_number": row.complaint_number,
                "project_name": project_name,
                "project_type": project_type,
                "topic": row.topic,
                "date_received": row.date_received.astimezone(ZoneInfo("America/Los_Angeles"))
                .strftime("%Y-%m-%d") if row.date_received else None,
                "concern_description": row.concern_description,
                "primary_officer": f"{primary_officer.first_name} {primary_officer.last_name}"
                if primary_officer else None,
                "complaint_status": row.complaint_status.value if row.complaint_status else None,
                "complaint_resolution": row.complaint_resolution,
                "case_file_number": row.case_file_number,
            }
            result.append(item)
        return result

    @staticmethod
    def _get_inspections_tab_columns_and_headers():
        """Get inspection existing columns and their headers for Excel export."""
        headers = [
            "IR Number",
            "First Nation/First Nation Alliance",
            "IR Progress",
            "Project",
            "Project Type",
            "Inspection Start Date",
            "Inspection End Date",
            "Topic",
            "Summary",
            "Compliance Finding",
            "Enforcement Action",
            "Enforcement Status",
            "Enforcement Document",
            "Condition Number",
            "Requirement Source",
            "IR Issuance Date",
            "Primary",
            "Inspection Status",
            "Case File Number"
        ]

        columns = [
            "ir_number",
            "first_nation",
            "ir_progress",
            "project_name",
            "project_type",
            "start_date",
            "end_date",
            "topic_name",
            "summary",
            "compliance_finding",
            "enforcement_action",
            "enforcement_status",
            "enforcement_document_number",
            "condition_number",
            "requirement_source",
            "ir_issuance_date",
            "primary_officer",
            "inspection_status",
            "case_file_number",
        ]

        return headers, columns

    @staticmethod
    def _get_complaints_tab_columns_and_headers():
        """Get complaints existing columns and their headers for Excel export."""
        headers = [
            "Complaint Number",
            "Project",
            "Project Type",
            "Topic",
            "Concern Description",
            "Date Received",
            "Primary",
            "Status",
            "Complaint Resolution",
            "Case File Number",
        ]

        columns = [
            "complaint_number",
            "project_name",
            "project_type",
            "topic",
            "concern_description",
            "date_received",
            "primary_officer",
            "complaint_status",
            "complaint_resolution",
            "case_file_number",
        ]

        return headers, columns

    def _get_project_cached(self, project_id, as_of_date):
        if not project_id:
            return None
        date_str = as_of_date.strftime("%Y-%m-%d") if as_of_date else None
        cache_key = (project_id, date_str)
        if cache_key not in self._project_cache:
            self._project_cache[cache_key] = TrackService.get_project_by_id(project_id, as_of_date=as_of_date)
        return self._project_cache[cache_key]
