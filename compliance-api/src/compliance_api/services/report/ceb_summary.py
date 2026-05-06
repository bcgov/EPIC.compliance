"""CEB Summary Report Generator Service."""
from datetime import datetime, time
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
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
from compliance_api.services.report.shared_queries import (
    complaints_tab_query_base,
    inspections_tab_query_base,
)
from compliance_api.services.service_utils import ServiceUtils


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
        self._reorder_pivot_column_items(
            workbook, "Compliance Finding", ["In", "Out", "Not Determined"]
        )
        self._reorder_pivot_column_items(
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

        self._populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Inspections",
            data_frame=inspections_data_frame,
            columns=inspections_columns,
            headers=inspections_headers,
        )
        self._populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Enforcement",
            data_frame=enforcements_data_frame,
            columns=enforcements_columns,
            headers=enforcements_headers,
        )
        self._populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Requirements",
            data_frame=requirements_data_frame,
            columns=requirements_columns,
            headers=requirements_headers,
        )
        self._populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Complaints",
            data_frame=complaints_data_frame,
            columns=complaints_columns,
            headers=complaints_headers,
        )

        output = BytesIO()
        workbook.save(output)

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def _populate_template_table_sheet(workbook, sheet_name, data_frame, columns, headers):
        """Populate a template worksheet table while preserving workbook pivot structure."""
        worksheet = workbook[sheet_name]
        table = next(iter(worksheet.tables.values()), None)

        if table is None:
            raise ValueError(f"Template sheet '{sheet_name}' does not contain an Excel table.")

        min_col = 1
        min_row = 1
        table_column_count = len(getattr(table, "tableColumns", []) or [])
        if table_column_count < 1:
            raise ValueError(f"Template sheet '{sheet_name}' table has no columns.")
        max_col = table_column_count

        table_headers = [
            worksheet.cell(row=min_row, column=column_number).value
            for column_number in range(min_col, max_col + 1)
        ]

        header_to_column_key = dict(zip(headers, columns))

        special_headers = {"Index", "Unique Key"}
        unknown_headers = [
            header for header in table_headers
            if header not in special_headers and header not in header_to_column_key
        ]
        if unknown_headers:
            raise ValueError(
                f"Template sheet '{sheet_name}' has unmapped headers: {unknown_headers}"
            )

        records = data_frame.reindex(columns=columns).to_dict("records")

        last_used_row = max(worksheet.max_row, min_row + 1)
        for row_number in range(min_row + 1, last_used_row + 1):
            for column_number in range(min_col, max_col + 1):
                worksheet.cell(row=row_number, column=column_number).value = None

        for row_index, record in enumerate(records, start=1):
            excel_row = min_row + row_index
            for col_offset, header in enumerate(table_headers):
                column_number = min_col + col_offset
                if header == "Index":
                    value = row_index
                elif header == "Unique Key":
                    value = record.get("enforcement_document_number")
                else:
                    column_key = header_to_column_key[header]
                    value = record.get(column_key)
                worksheet.cell(row=excel_row, column=column_number).value = value

        new_last_row = min_row + max(len(records), 1)
        table.ref = (
            f"{get_column_letter(min_col)}{min_row}:"
            f"{get_column_letter(max_col)}{new_last_row}"
        )

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

    def _get_project_details(self, row):
        """Resolve project name/type from approved and unapproved project sources."""
        # Project Logic:
        # If case_file.project_id is null it is unapproved
        # and you should be able to find it in the unapproved_projects table
        # If case_file.project_id has a valid number it should be from EPIC.Track
        if not row.project_id:
            project_name = row.unapproved_project_name
            project_type = row.unapproved_project_type
        else:
            if row.project_id in self.project_map:
                project = self.project_map[row.project_id]
            else:
                date = row.case_file_date_created.date() if row.case_file_date_created else None
                project = TrackService.get_project_by_id(row.project_id, as_of_date=date)
                self.project_map[row.project_id] = project
            project_name = project.get("name") if project else None
            project_type = project.get("type", None).get("name", None) if project else None

        return project_name, project_type

    def _format_inspections_tab_data(self, data):
        """Format unique inspections data for excel export."""
        result = []
        seen_inspections = set()

        for row in data:
            project_name, project_type = self._get_project_details(row)

            inspection_key = row.ir_number or row.case_file_number
            if inspection_key in seen_inspections:
                continue
            seen_inspections.add(inspection_key)

            item = {
                "ir_number": row.ir_number,
                "ir_progress": row.ir_progress.value if row.ir_progress else None,
                "project_name": project_name,
                "project_type": project_type,
                "ir_issuance_date": row.ir_date_issued.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
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
            project_name, project_type = self._get_project_details(row)
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
                "ir_issuance_date": row.ir_date_issued.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
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
            project_name, project_type = self._get_project_details(row)

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

            project_name, project_type = self._get_project_details(row)

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
                    row.date_received.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
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

    @staticmethod
    def _reorder_pivot_column_items(workbook, field_name, desired_order):
        """Reorder pivot field items to enforce a specific column display order."""
        # Collect all unique pivot caches from worksheets
        seen_caches = set()
        pivot_cache_pairs = []  # List of (cache, pivot) tuples

        for worksheet in workbook.worksheets:
            if not hasattr(worksheet, '_pivots'):
                continue
            for pivot in worksheet._pivots:
                cache = pivot.cache
                if cache is not None:
                    pivot_cache_pairs.append((cache, pivot, worksheet))
                    seen_caches.add(id(cache))

        # Group pivots by cache
        cache_to_pivots = {}
        for cache, pivot, ws in pivot_cache_pairs:
            cache_id = id(cache)
            if cache_id not in cache_to_pivots:
                cache_to_pivots[cache_id] = {'cache': cache, 'pivots': []}
            cache_to_pivots[cache_id]['pivots'].append(pivot)

        for cache_id, cache_data in cache_to_pivots.items():
            cache = cache_data['cache']
            pivots = cache_data['pivots']

            # Find the cache field matching field_name and record its index
            field_idx = None
            cache_field = None
            for idx, cf in enumerate(cache.cacheFields):
                if cf.name == field_name:
                    field_idx = idx
                    cache_field = cf
                    break

            if field_idx is None or cache_field is None:
                continue
            if not hasattr(cache_field, 'sharedItems') or cache_field.sharedItems is None:
                continue

            # Build a map of cache index → string value
            values_by_cache_idx = {}
            if hasattr(cache_field.sharedItems, '_fields'):
                for i, item in enumerate(cache_field.sharedItems._fields):
                    if hasattr(item, 'v'):
                        values_by_cache_idx[i] = item.v

            # Apply reordering to every pivot table that uses this cache
            for pivot in pivots:
                if field_idx >= len(pivot.pivotFields):
                    continue

                pivot_field = pivot.pivotFields[field_idx]
                if pivot_field.items is None:
                    continue

                # Separate data items (have a cache index) from subtotal/blank items
                data_items = [item for item in pivot_field.items if item.x is not None]
                other_items = [item for item in pivot_field.items if item.x is None]

                # Sort data items by position in desired_order (unknowns go last)
                def sort_key(item):
                    val = values_by_cache_idx.get(item.x, "")
                    try:
                        return desired_order.index(val)
                    except ValueError:
                        return len(desired_order)

                data_items.sort(key=sort_key)
                pivot_field.items = data_items + other_items
                pivot_field.sortType = "manual"

            # Tell Excel to rebuild the pivot layout from our reordered items on open
            cache.refreshOnLoad = True
