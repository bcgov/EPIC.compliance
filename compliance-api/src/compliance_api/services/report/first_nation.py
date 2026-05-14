"""First Nation Report Generator Service."""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from openpyxl import load_workbook
from flask import current_app
from sqlalchemy.orm import selectinload

from compliance_api.models.case_file import CaseFile
from compliance_api.models.complaint.complaint import Complaint
from compliance_api.models.complaint.complaint_option import ComplaintSourceEnum
from compliance_api.models.enforcement_action import EnforcementActionOption
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection.inspection_firstnation import InspectionFirstnation
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.services.epic_track_service.track_service import TrackService
from compliance_api.services.report.utils.shared_queries import (
    complaints_tab_query_base,
    inspections_tab_query_base,
)
from compliance_api.services.report.utils.utils import (
    compact_pivot_tables,
    get_project_details,
    populate_template_table_sheet,
)

from .base import BaseReportGenerator


class FirstNationReportGenerator(BaseReportGenerator):
    """First Nation Report Generator Service."""

    def __init__(self, report_data):
        """Initialize the First Nation Report Generator with the provided report data."""
        super().__init__(report_data)

        self.first_nation_id = report_data.get("first_nation_id")
        self.project_map = {}
        self.template_path = Path(__file__).with_name("first_nation_template.xlsx")

        current_app.logger.info(
            f"First Nation Report Generator initialized with first_nation_id: {self.first_nation_id}."
        )

    def get_filename(self):
        """Return the filename (without extension) for the First Nation report."""
        today = datetime.now()
        start = self.effective_start_date or today
        end = today
        return f"FirstNationReport_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}"

    def generate(self):
        """First Nation Report Generation Logic."""
        first_nations = TrackService.get_first_nations()
        first_nations_name = next(
            (fn.get("name") for fn in first_nations if fn.get("id") == self.first_nation_id),
            "Unknown First Nation"
        )

        inspection_data = self._build_inspections_tab_query().all()

        # Compute effective date range for filename
        today = datetime.now()
        issued_dates = [row.ir_date_issued for row in inspection_data if row.ir_date_issued]
        self.effective_start_date = min(issued_dates).replace(tzinfo=None) if issued_dates else today

        # Inspections Tab
        inspection_data = self._format_inspections_tab_data(inspection_data, first_nations)
        inspections_data_frame = pd.json_normalize(inspection_data)
        inspections_headers, inspections_columns = self._get_inspections_tab_columns_and_headers()

        # Complaints Tab
        complaints_data = self._build_complaints_tab_query().all()
        complaints_data = self._format_complaints_tab_data(complaints_data, first_nations_name)
        complaints_data_frame = pd.json_normalize(complaints_data)
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
        if not self.template_path.exists():
            raise FileNotFoundError(f"First Nation template not found at {self.template_path}")
        workbook = load_workbook(self.template_path)

        if inspections_data_frame.empty:
            inspections_data_frame = pd.DataFrame(columns=inspections_columns)
        if complaints_data_frame.empty:
            complaints_data_frame = pd.DataFrame(columns=complaints_columns)

        populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Inspections",
            data_frame=inspections_data_frame,
            columns=inspections_columns,
            headers=inspections_headers,
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
        """Build base query for First Nation Report."""
        query = inspections_tab_query_base()  # Base query with necessary joins
        query = query.filter(
                InspectionRequirement.is_active.is_(True),
                InspectionRequirement.is_deleted.is_(False),
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
                InspectionRecord.is_active.is_(True),
                InspectionRecord.is_deleted.is_(False),
                InspectionFirstnation.firstnation_id == self.first_nation_id
        ).order_by(
            InspectionRequirement.id,
            EnforcementActionOption.id
        ).options(
            selectinload(InspectionRequirement.requirement_source_details)
        )

        return query

    def _build_complaints_tab_query(self):
        query = complaints_tab_query_base()
        query = query.filter(
                Complaint.is_active.is_(True),
                Complaint.is_deleted.is_(False),
                Complaint.source_first_nation_id == self.first_nation_id,
                CaseFile.is_active.is_(True),
                CaseFile.is_deleted.is_(False),
        ).order_by(Complaint.id).distinct(Complaint.id)

        return query

    def _format_inspections_tab_data(self, data, first_nations):
        """Format unique inspections data for excel export."""
        result = []
        seen_inspections = set()
        first_nation = next((fn for fn in first_nations if fn.get('id') == self.first_nation_id), None)
        first_nation_name = first_nation.get("name") if first_nation else ""

        for row in data:
            project_name, project_type = get_project_details(self.project_map, row)
            inspection_key = row.ir_number or row.case_file_number
            if inspection_key in seen_inspections:
                continue
            seen_inspections.add(inspection_key)

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
                "ir_issuance_date": row.ir_date_issued.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
                if row.ir_date_issued else None,
                "inspection_status": row.inspection_status.value if row.inspection_status else None,
                "case_file_number": row.case_file_number,
            }
            result.append(item)

        return result

    def _format_complaints_tab_data(self, data, first_nations_name):
        """Format complaints data for excel export."""
        result = []
        seen_complaints = set()

        for row in data:
            complaint_key = row.complaint_number
            if complaint_key in seen_complaints:
                continue
            seen_complaints.add(complaint_key)

            project_name, project_type = get_project_details(self.project_map, row)

            # Get complaint source details based on source type
            complaint_source_details = ""
            if row.complaint_source == ComplaintSourceEnum.FIRST_NATION.value:
                complaint_source_details = first_nations_name
            elif row.complaint_source == ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE.value:
                complaint_source_details = row.complaint_source_contact_alliance_name or ""

            item = {
                "complaint_number": row.complaint_number,
                "project_name": project_name,
                "project_type": project_type,
                "topic": row.topic,
                "date_received": row.date_received.astimezone(ZoneInfo("America/Los_Angeles"))
                .strftime("%Y-%m-%d") if row.date_received else None,
                "complaint_source": row.complaint_source,
                "complaint_source_details": complaint_source_details,
                "concern_description": row.concern_description,
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
            "IR Issuance Date",
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
            "ir_issuance_date",
            "inspection_status",
            "case_file_number",
        ]

        return headers, columns

    @staticmethod
    def _get_complaints_tab_columns_and_headers():
        """Get complaints existing columns and their headers for Excel export."""
        headers = [
            "Complaint Number",
            "Complaint Source",
            "Complaint Source Details",
            "Project Name",
            "Project Type",
            "Topic",
            "Concern Description",
            "Date Received",
            "Primary Officer",
            "Complaint Status",
            "Complaint Resolution",
            "Case File Number",
        ]

        columns = [
            "complaint_number",
            "complaint_source",
            "complaint_source_details",
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
