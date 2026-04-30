"""CEB Summary Report Generator Service."""
from datetime import datetime, time
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from flask import current_app
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from compliance_api.models import db
from compliance_api.models.administrative_penalty import AdministrativePenalty
from compliance_api.models.case_file import CaseFile
from compliance_api.models.charge_recommendation import ChargeRecommendation
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.enforcement_action import EnforcementActionOption
from compliance_api.models.inspection.inspection import Inspection
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
    get_requirement_admin_penalty_sub_query, get_requirement_charge_rec_sub_query, get_requirement_order_sub_query,
    get_requirement_restorative_justice_sub_query, get_requirement_violation_ticket_sub_query,
    get_requirement_warning_letter_sub_query)
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
        data = self._build_inspections_tab_query().all()

        # Compute effective date range for filename
        today = datetime.now()
        if self.start_date:
            self.effective_start_date = self.start_date
        else:
            issued_dates = [row.ir_date_issued for row in data if row.ir_date_issued]
            self.effective_start_date = min(issued_dates).replace(tzinfo=None) if issued_dates else today
        self.effective_end_date = self.end_date if self.end_date else today

        # Inspections Tab
        inspections_data = self._format_inspections_tab_data(data)
        inspections_data_frame = pd.json_normalize(inspections_data)
        inspections_headers, inspections_columns = self._get_inspections_tab_columns_and_headers()

        # Enforcements Tab
        enforcements_data = self._format_enforcements_tab_data(data)
        enforcements_data_frame = pd.json_normalize(enforcements_data)
        enforcements_headers, enforcements_columns = self._get_enforcements_tab_columns_and_headers()

        # Requirements Tab
        requirements_data = self._format_requirements_tab_data(data)
        requirements_data_frame = pd.json_normalize(requirements_data)
        requirements_headers, requirements_columns = self._get_requirements_tab_columns_and_headers()

        output = self._to_excel(
            inspections_data_frame,
            inspections_columns,
            inspections_headers,
            enforcements_data_frame,
            enforcements_columns,
            enforcements_headers,
            requirements_data_frame,
            requirements_columns,
            requirements_headers)
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
                requirements_headers
    ):
        if not self.template_path.exists():
            raise FileNotFoundError(f"CEB template not found at {self.template_path}")
        workbook = load_workbook(self.template_path)

        if inspections_data_frame.empty:
            inspections_data_frame = pd.DataFrame(columns=inspections_columns)
        if enforcements_data_frame.empty:
            enforcements_data_frame = pd.DataFrame(columns=enforcements_columns)
        if requirements_data_frame.empty:
            requirements_data_frame = pd.DataFrame(columns=requirements_columns)

        self._populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Inspections",
            data_frame=inspections_data_frame,
            columns=inspections_columns,
            headers=inspections_headers,
        )
        self._populate_template_table_sheet(
            workbook=workbook,
            sheet_name="Enforcements",
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
        requirement_order_subquery = get_requirement_order_sub_query()
        requirement_warning_letter_subquery = get_requirement_warning_letter_sub_query()
        requirement_violation_ticket_subquery = get_requirement_violation_ticket_sub_query()
        requirement_admin_penalty_subquery = get_requirement_admin_penalty_sub_query()
        requirement_charge_rec_subquery = get_requirement_charge_rec_sub_query()
        requirement_restorative_justice_subquery = get_requirement_restorative_justice_sub_query()

        query = (
            db.session.query(
                InspectionRequirement,
                Inspection.ir_number.label("ir_number"),
                InspectionRequirement.summary.label("summary"),
                Topic.name.label("topic_name"),
                InspectionRecord.ir_progress.label("ir_progress"),
                Project.id.label("project_id"),
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
                StaffUser.first_name.label("primary_officer_first_name"),
                StaffUser.last_name.label("primary_officer_last_name"),
                Inspection.inspection_status.label("inspection_status"),
                CaseFile.case_file_number.label("case_file_number"),
                CaseFile.date_created.label("case_file_date_created"),
            )
            .join(Inspection, InspectionRequirement.inspection_id == Inspection.id)
            .join(CaseFile, Inspection.case_file_id == CaseFile.id)
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
