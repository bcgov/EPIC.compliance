"""CEB Summary Report Generator Service."""
from datetime import datetime, time
from io import BytesIO
from pathlib import Path

import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from sqlalchemy.orm import selectinload

from compliance_api.models.case_file import CaseFile
from compliance_api.models.complaint import Complaint
from compliance_api.models.complaint.complaint_option import ComplaintSourceEnum
from compliance_api.models.enforcement_action import EnforcementActionOption
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.services.epic_track_service.track_service import TrackService
from compliance_api.services.report.base import BaseReportGenerator
from compliance_api.services.report.utils.shared_queries import (
    complaints_tab_query_base,
    inspections_tab_query_base,
)
from compliance_api.services.report.utils.utils import (
    compact_pivot_tables,
    get_project_details,
    populate_template_table_sheet,
    reorder_pivot_column_items,
    sort_dataframe_for_pivot_order,
)
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.utils.datetime import BC_TIMEZONE


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
        self.project_map = {}
        self.template_path = Path(__file__).with_name("ceb_template.xlsx")

    def get_filename(self):
        """Return the filename (without extension) for the CEB Summary report."""
        today = datetime.now()
        start = self.effective_start_date or today
        end = self.effective_end_date or today
        return f"CEBSummaryReport_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}"

    def generate(self):
        """CEB Summary Report Generation Logic."""
        # Shared source data for all tabs
        inspection_data = self._build_inspections_tab_query().all()
        complaint_data = self._build_complaints_tab_query().all()

        # Compute effective date range for filename
        today = datetime.now()
        if self.start_date:
            self.effective_start_date = self.start_date
        else:
            issued_dates = [row.ir_date_issued for row in inspection_data if row.ir_date_issued]
            self.effective_start_date = min(issued_dates).replace(tzinfo=None) if issued_dates else today
        self.effective_end_date = self.end_date if self.end_date else today

        # Inspections Tab
        inspections_data = self._format_inspections_tab_data(inspection_data)
        inspections_data_frame = pd.json_normalize(inspections_data)
        inspections_headers, inspections_columns = self._get_inspections_tab_columns_and_headers()

        # Enforcement Tab
        enforcements_data = self._format_enforcements_tab_data(inspection_data)
        enforcements_data_frame = pd.json_normalize(enforcements_data)
        enforcements_headers, enforcements_columns = self._get_enforcements_tab_columns_and_headers()

        # Requirements Tab
        requirements_data = self._format_requirements_tab_data(inspection_data)
        requirements_data_frame = pd.json_normalize(requirements_data)
        requirements_headers, requirements_columns = self._get_requirements_tab_columns_and_headers()

        # Complaints Tab
        complaints_data = self._format_complaints_tab_data(complaint_data)
        complaints_data_frame = pd.json_normalize(complaints_data)
        complaints_headers, complaints_columns = self._get_complaints_tab_columns_and_headers()

        output = self._to_excel(
            inspections_data_frame,
            inspections_columns,
            inspections_headers,
            enforcements_data_frame,
            enforcements_columns,
            enforcements_headers,
            requirements_data_frame,
            requirements_columns,
            requirements_headers,
            complaints_data_frame,
            complaints_columns,
            complaints_headers)
        return output

    def _to_excel(
                self,
                inspections_data_frame,
                inspections_columns,
                inspections_headers,
                enforcements_data_frame,
                enforcements_columns,
                enforcements_headers,
                requirements_data_frame,
                requirements_columns,
                requirements_headers,
                complaints_data_frame,
                complaints_columns,
                complaints_headers
    ):
        if not self.template_path.exists():
            raise FileNotFoundError(f"CEB template not found at {self.template_path}")
        workbook = load_workbook(self.template_path)
        reorder_pivot_column_items(
            workbook, "Compliance Finding", ["In", "Out", "Not Determined"]
        )
        reorder_pivot_column_items(
            workbook, "Enforcement Status", ["Issued", "Rescinded", "Closed"]
        )

        if inspections_data_frame.empty:
            inspections_data_frame = pd.DataFrame(columns=inspections_columns)
        if enforcements_data_frame.empty:
            enforcements_data_frame = pd.DataFrame(columns=enforcements_columns)
        if requirements_data_frame.empty:
            requirements_data_frame = pd.DataFrame(columns=requirements_columns)
        if complaints_data_frame.empty:
            complaints_data_frame = pd.DataFrame(columns=complaints_columns)

        # Sort dataframes to control pivot column order in Excel
        # Excel builds pivot cache from first-occurrence order in source data
        pivot_column_orders = {
            "compliance_finding": ["In", "Out", "Not Determined"],
            "enforcement_status": ["Issued", "Rescinded", "Closed"],
        }
        enforcements_data_frame = sort_dataframe_for_pivot_order(
            enforcements_data_frame, pivot_column_orders
        )
        requirements_data_frame = sort_dataframe_for_pivot_order(
            requirements_data_frame, pivot_column_orders
        )

        populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Inspections",
            data_frame=inspections_data_frame,
            columns=inspections_columns,
            headers=inspections_headers,
        )
        populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Enforcement",
            data_frame=enforcements_data_frame,
            columns=enforcements_columns,
            headers=enforcements_headers,
        )
        populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Requirements",
            data_frame=requirements_data_frame,
            columns=requirements_columns,
            headers=requirements_headers,
        )
        populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Complaints",
            data_frame=complaints_data_frame,
            columns=complaints_columns,
            headers=complaints_headers,
        )
        compact_pivot_tables(workbook, gap_columns=1)

        output = BytesIO()
        workbook.save(output)

        output.seek(0)
        return output.getvalue()

    def _build_inspections_tab_query(self):
        """Build base query for CEB Summary Report."""
        query = inspections_tab_query_base()  # Base query with necessary joins and filters
        query = query.filter(
            InspectionRequirement.is_active.is_(True),
            InspectionRequirement.is_deleted.is_(False),
            Inspection.is_active.is_(True),
            Inspection.is_deleted.is_(False),
            InspectionRecord.is_active.is_(True),
            InspectionRecord.is_deleted.is_(False),
            Inspection.start_date >= self.start_date if self.start_date else True,
            Inspection.start_date <= self.end_date if self.end_date else True,
        ).order_by(
            InspectionRequirement.id,
            EnforcementActionOption.id
        ).options(
            selectinload(InspectionRequirement.requirement_source_details)
        )

        return query

    def _build_complaints_tab_query(self):
        query = complaints_tab_query_base()  # Base query with necessary joins and filters
        query = query.filter(
            Complaint.is_active.is_(True),
            Complaint.is_deleted.is_(False),
            CaseFile.is_active.is_(True),
            CaseFile.is_deleted.is_(False),
        ).order_by(Complaint.id)

        return query

    def _format_inspections_tab_data(self, data):
        """Format unique inspections data for excel export."""
        result = []
        seen_inspections = set()

        for row in data:
            project_name, project_type = get_project_details(self.project_map, row)

            inspection_key = row.ir_number or row.case_file_number
            if inspection_key in seen_inspections:
                continue
            seen_inspections.add(inspection_key)

            item = {
                "ir_number": row.ir_number,
                "ir_progress": row.ir_progress.value if row.ir_progress else None,
                "project_name": project_name,
                "project_type": project_type,
                "ir_issuance_date": row.ir_date_issued.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                if row.ir_date_issued else None,
                "primary_officer": self._format_primary_officer_name(row),
                "inspection_status": row.inspection_status.value if row.inspection_status else None,
                "case_file_number": row.case_file_number,
            }
            result.append(item)

        return result

    def _format_enforcements_tab_data(self, data):
        """Format unique enforcements data for excel export."""
        result = []
        seen_document_keys = set()

        for row in data:
            project_name, project_type = get_project_details(self.project_map, row)
            enforcement_document_number = ServiceUtils.get_enforcement_number_by_type(row)
            raw_enforcement_status = ServiceUtils.get_enforcement_status_by_type(row)
            # Keep unique document numbers by enforcement action.
            # If document number is blank, count the selected enforcement action entry.
            if enforcement_document_number:
                key = (row.enforcement_action_id, enforcement_document_number)
            else:
                key = (row.InspectionRequirement.id, row.enforcement_action_id, "")

            if key in seen_document_keys:
                continue
            seen_document_keys.add(key)

            item = {
                "ir_number": row.ir_number,
                "ir_progress": row.ir_progress.value if row.ir_progress else None,
                "project_name": project_name,
                "project_type": project_type,
                "compliance_finding": row.compliance_finding,
                "enforcement_action": row.enforcement_action,
                "enforcement_document_number": enforcement_document_number,
                "enforcement_status": raw_enforcement_status.value if raw_enforcement_status else None,
                "ir_issuance_date": row.ir_date_issued.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                if row.ir_date_issued else None,
                "primary_officer": self._format_primary_officer_name(row),
                "inspection_status": row.inspection_status.value if row.inspection_status else None,
                "case_file_number": row.case_file_number,
            }
            result.append(item)

        return result

    def _format_requirements_tab_data(self, data):
        """Format requirements data for excel export."""
        result = []

        for row in data:
            inspection_requirement = row.InspectionRequirement
            raw_enforcement_status = ServiceUtils.get_enforcement_status_by_type(row)
            req_source_details = inspection_requirement.requirement_source_details
            project_name, project_type = get_project_details(self.project_map, row)

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
                "ir_issuance_date": row.ir_date_issued.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                if row.ir_date_issued else None,
                "primary_officer": self._format_primary_officer_name(row),
                "inspection_status": row.inspection_status.value if row.inspection_status else None,
                "case_file_number": row.case_file_number,
            }
            result.append(item)

        return result

    def _format_complaints_tab_data(self, data):
        """Format complaints data for excel export."""
        result = []
        seen_complaints = set()
        first_nations = TrackService.get_first_nations()

        for row in data:
            complaint_key = row.complaint_number
            if complaint_key in seen_complaints:
                continue
            seen_complaints.add(complaint_key)

            project_name, project_type = get_project_details(self.project_map, row)

            # Get complaint source details based on source type
            complaint_source_details = ""

            if row.complaint_source == ComplaintSourceEnum.PUBLIC.value:
                complaint_source_details = row.complaint_source_contact_full_name or ""
            elif row.complaint_source == ComplaintSourceEnum.FIRST_NATION.value:
                first_nation = next((fn for fn in first_nations if fn.get('id') == row.source_first_nation_id), None)
                complaint_source_details = first_nation.get("name") if first_nation else ""
            elif row.complaint_source == ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE.value:
                complaint_source_details = row.complaint_source_contact_alliance_name or ""
            elif row.complaint_source == ComplaintSourceEnum.AGENCY.value:
                complaint_source_details = row.source_agency or ""
            elif row.complaint_source == ComplaintSourceEnum.OTHER.value:
                complaint_source_details = row.complaint_source_contact_description or ""

            item = {
                "complaint_number": row.complaint_number,
                "project_name": project_name,
                "project_type": project_type,
                "topic": row.topic,
                "date_received":
                    row.date_received.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                    if row.date_received else None,
                "complaint_source": row.complaint_source,
                "complaint_source_details": complaint_source_details,
                "primary_officer": self._format_primary_officer_name(row),
                "complaint_status": row.complaint_status.value if row.complaint_status else None,
                "complaint_resolution": row.complaint_resolution,
                "case_file_number": row.case_file_number,
            }
            result.append(item)

        return result

    @staticmethod
    def _format_primary_officer_name(row):
        """Get formatted officer name from query labels."""
        if not row.primary_officer_first_name and not row.primary_officer_last_name:
            return None
        return f"{row.primary_officer_first_name or ''} {row.primary_officer_last_name or ''}".strip()

    @staticmethod
    def _get_inspections_tab_columns_and_headers():
        """Get existing columns and their headers for Excel export."""
        headers = [
            "IR Number",
            "IR Progress",
            "Project Name",
            "Project Type",
            "IR Issuance Date",
            "Primary Officer",
            "Inspection Status",
            "Case File Number",
        ]

        columns = [
            "ir_number",
            "ir_progress",
            "project_name",
            "project_type",
            "ir_issuance_date",
            "primary_officer",
            "inspection_status",
            "case_file_number",
        ]

        return headers, columns

    @staticmethod
    def _get_enforcements_tab_columns_and_headers():
        """Get enforcements columns and headers for Excel export."""
        headers = [
            "IR Number",
            "IR Progress",
            "Project Name",
            "Project Type",
            "Compliance Finding",
            "Enforcement Action",
            "Enforcement Document Number",
            "Enforcement Status",
            "IR Issuance Date",
            "Primary Officer",
            "Inspection Status",
            "Case File Number",
        ]

        columns = [
            "ir_number",
            "ir_progress",
            "project_name",
            "project_type",
            "compliance_finding",
            "enforcement_action",
            "enforcement_document_number",
            "enforcement_status",
            "ir_issuance_date",
            "primary_officer",
            "inspection_status",
            "case_file_number",
        ]

        return headers, columns

    @staticmethod
    def _get_requirements_tab_columns_and_headers():
        """Get requirements columns and headers for Excel export."""
        headers = [
            "IR Number",
            "Topic",
            "Summary",
            "IR Progress",
            "Project Name",
            "Project Type",
            "Compliance Finding",
            "Enforcement Action",
            "Enforcement Status",
            "Enforcement Document Number",
            "Condition Number",
            "Requirement Source",
            "IR Issuance Date",
            "Primary Officer",
            "Inspection Status",
            "Case File Number",
        ]

        columns = [
            "ir_number",
            "topic_name",
            "summary",
            "ir_progress",
            "project_name",
            "project_type",
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
        """Get complaints columns and headers for Excel export."""
        headers = [
            "Complaint Number",
            "Project Name",
            "Project Type",
            "Topic",
            "Date Received",
            "Complaint Source",
            "Complaint Source Details",
            "Primary Officer",
            "Complaint Status",
            "Complaint Resolution",
            "Case File Number",
        ]

        columns = [
            "complaint_number",
            "project_name",
            "project_type",
            "topic",
            "date_received",
            "complaint_source",
            "complaint_source_details",
            "primary_officer",
            "complaint_status",
            "complaint_resolution",
            "case_file_number",
        ]

        return headers, columns
