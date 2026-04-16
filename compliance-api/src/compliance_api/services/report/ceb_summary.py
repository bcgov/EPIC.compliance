"""CEB Summary Report Generator Service."""
from datetime import datetime, time
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from flask import current_app
from openpyxl.styles import Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table
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

    def generate(self):
        """CEB Summary Report Generation Logic."""
        # Shared source data for all tabs
        data = self._build_inspections_tab_query().all()

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

        # Insights Tabs
        # Number of Inspections by IR Progress (all inspections)
        insights_data = self._format_insights_tab_data(inspections_data)
        insights_data_frame = pd.json_normalize(insights_data)
        insights_headers, insights_columns = self._get_insights_tab_columns_and_headers()
        # Inspection Requirement distribution by Project \ Type
        insights_distribution_data = self._format_requirement_distribution_insights_data(data)
        insights_distribution_data_frame = pd.json_normalize(insights_distribution_data)
        insights_distribution_headers, insights_distribution_columns = (
            self._get_insights_distribution_columns_and_headers()
        )
        # Enforcement distribution by Project
        insights_enforcement_distribution_data, enforcement_status_columns = (
            self._format_enforcement_distribution_insights_data(enforcements_data)
        )
        insights_enforcement_distribution_data_frame = pd.json_normalize(insights_enforcement_distribution_data)
        insights_enforcement_distribution_headers, insights_enforcement_distribution_columns = (
            self._get_insights_enforcement_distribution_columns_and_headers(enforcement_status_columns)
        )

        output = self._to_excel(
            inspections_data_frame,
            inspections_columns,
            inspections_headers,
            insights_data_frame,
            insights_columns,
            insights_headers,
            insights_distribution_data,
            insights_distribution_data_frame,
            insights_distribution_columns,
            insights_distribution_headers,
            insights_enforcement_distribution_data,
            insights_enforcement_distribution_data_frame,
            insights_enforcement_distribution_columns,
            insights_enforcement_distribution_headers,
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
                insights_data_frame,
                insights_columns,
                insights_headers,
                insights_distribution_data,
                insights_distribution_data_frame,
                insights_distribution_columns,
                insights_distribution_headers,
                insights_enforcement_distribution_data,
                insights_enforcement_distribution_data_frame,
                insights_enforcement_distribution_columns,
                insights_enforcement_distribution_headers,
                enforcements_data_frame,
                enforcements_columns,
                enforcements_headers,
                requirements_data_frame,
                requirements_columns,
                requirements_headers
    ):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:

            # If there is no data, create an empty dataframe with columns so that
            # the excel file will still have the correct headers and structure
            if inspections_data_frame.empty:
                inspections_data_frame = pd.DataFrame(columns=inspections_columns)
            if insights_data_frame.empty:
                insights_data_frame = pd.DataFrame(columns=insights_columns)
            if insights_distribution_data_frame.empty:
                insights_distribution_data_frame = pd.DataFrame(columns=insights_distribution_columns)
            if insights_enforcement_distribution_data_frame.empty:
                insights_enforcement_distribution_data_frame = pd.DataFrame(
                    columns=insights_enforcement_distribution_columns
                )
            if enforcements_data_frame.empty:
                enforcements_data_frame = pd.DataFrame(columns=enforcements_columns)
            if requirements_data_frame.empty:
                requirements_data_frame = pd.DataFrame(columns=requirements_columns)

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
            self._auto_size_table_columns(
                worksheet,
                start_col=0,
                num_cols=len(inspections_columns),
                max_row=len(inspections_data_frame.index) + 1,
            )

            # Enforcements Tab
            enforcements_data_frame.to_excel(
                writer,
                sheet_name="Enforcements",
                columns=enforcements_columns,
                header=enforcements_headers,
                index=False,
            )
            enforcements_worksheet = writer.sheets["Enforcements"]
            # Making the columns wider
            self._auto_size_table_columns(
                enforcements_worksheet,
                start_col=0,
                num_cols=len(enforcements_columns),
                max_row=len(enforcements_data_frame.index) + 1,
            )

            # Requirements Tab
            requirements_data_frame.to_excel(
                writer,
                sheet_name="Requirements",
                columns=requirements_columns,
                header=requirements_headers,
                index=False,
            )
            requirements_worksheet = writer.sheets["Requirements"]
            # Making the columns wider
            self._auto_size_table_columns(
                requirements_worksheet,
                start_col=0,
                num_cols=len(requirements_columns),
                max_row=len(requirements_data_frame.index) + 1,
            )

            # Insights Tab (all three insight tables side-by-side)
            insights_sheet_name = "Insights"
            table_gap_columns = 1
            insights_start_row = 0

            inspections_start_col = 0
            requirements_start_col = inspections_start_col + len(insights_columns) + table_gap_columns
            enforcements_start_col = (
                requirements_start_col + len(insights_distribution_columns) + table_gap_columns
            )

            insights_data_frame.to_excel(
                writer,
                sheet_name=insights_sheet_name,
                columns=insights_columns,
                header=insights_headers,
                index=False,
                startrow=insights_start_row,
                startcol=inspections_start_col,
            )

            insights_distribution_data_frame.to_excel(
                writer,
                sheet_name=insights_sheet_name,
                columns=insights_distribution_columns,
                header=insights_distribution_headers,
                index=False,
                startrow=insights_start_row,
                startcol=requirements_start_col,
            )

            insights_enforcement_distribution_data_frame.to_excel(
                writer,
                sheet_name=insights_sheet_name,
                columns=insights_enforcement_distribution_columns,
                header=insights_enforcement_distribution_headers,
                index=False,
                startrow=insights_start_row,
                startcol=enforcements_start_col,
            )

            insights_worksheet = writer.sheets[insights_sheet_name]

            # Make columns wider for all three tables in the Insights sheet, with some extra padding for readability
            self._auto_size_table_columns(
                insights_worksheet,
                start_col=inspections_start_col,
                num_cols=len(insights_columns),
                max_row=insights_start_row + len(insights_data_frame.index) + 1,
            )
            self._auto_size_table_columns(
                insights_worksheet,
                start_col=requirements_start_col,
                num_cols=len(insights_distribution_columns),
                max_row=insights_start_row + len(insights_distribution_data_frame.index) + 1,
            )
            self._auto_size_table_columns(
                insights_worksheet,
                start_col=enforcements_start_col,
                num_cols=len(insights_enforcement_distribution_columns),
                max_row=insights_start_row + len(insights_enforcement_distribution_data_frame.index) + 1,
            )

            # Apply grid styling per table.
            insights_header_row = insights_start_row + 1
            self._style_table_region_as_grid(
                insights_worksheet,
                start_row=insights_header_row,
                start_col=inspections_start_col + 1,
                row_count=len(insights_data_frame.index) + 1,
                col_count=len(insights_columns),
                total_row=insights_start_row + len(insights_data_frame.index) + 1,
            )
            self._style_table_region_as_grid(
                insights_worksheet,
                start_row=insights_header_row,
                start_col=requirements_start_col + 1,
                row_count=len(insights_distribution_data_frame.index) + 1,
                col_count=len(insights_distribution_columns),
            )
            self._style_table_region_as_grid(
                insights_worksheet,
                start_row=insights_header_row,
                start_col=enforcements_start_col + 1,
                row_count=len(insights_enforcement_distribution_data_frame.index) + 1,
                col_count=len(insights_enforcement_distribution_columns),
            )

            # Add per-table filters in the combined Insights sheet.
            self._add_filter_table(
                insights_worksheet,
                start_row=insights_header_row,
                start_col=inspections_start_col + 1,
                row_count=len(insights_data_frame.index) + 1,
                col_count=1,
                table_name="InsightsInspectionsTbl",
            )
            self._add_filter_table(
                insights_worksheet,
                start_row=insights_header_row,
                start_col=requirements_start_col + 1,
                row_count=len(insights_distribution_data_frame.index) + 1,
                col_count=2,
                table_name="InsightsRequirementsTbl",
            )
            self._add_filter_table(
                insights_worksheet,
                start_row=insights_header_row,
                start_col=enforcements_start_col + 1,
                row_count=len(insights_enforcement_distribution_data_frame.index) + 1,
                col_count=2,
                table_name="InsightsEnforcementsTbl",
            )

            # Apply outline/grouping and total row emphasis per table region.
            self._apply_insights_distribution_outline(
                insights_worksheet,
                start_row=insights_start_row + 2,
                insights_distribution_data=insights_distribution_data,
                start_col=requirements_start_col + 1,
                end_col=requirements_start_col + len(insights_distribution_columns),
            )
            self._apply_enforcement_distribution_outline(
                insights_worksheet,
                start_row=insights_start_row + 2,
                insights_enforcement_distribution_data=insights_enforcement_distribution_data,
                start_col=enforcements_start_col + 1,
                end_col=enforcements_start_col + len(insights_enforcement_distribution_columns),
            )
        output.seek(0)
        return output.getvalue()

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

    @staticmethod
    def _format_insights_tab_data(inspections_data):
        """Format insights data for excel export."""
        progress_counts = {}

        for item in inspections_data:
            progress = item.get("ir_progress") or "Unknown"
            progress_counts[progress] = progress_counts.get(progress, 0) + 1

        result = []
        for progress, count in sorted(progress_counts.items()):
            result.append(
                {
                    "ir_progress": progress,
                    "number_of_inspections": count,
                }
            )

        result.append(
            {
                "ir_progress": "Total",
                "number_of_inspections": len(inspections_data),
            }
        )

        return result

    def _format_requirement_distribution_insights_data(self, data):
        """Format requirement distribution insights by project type/project."""
        result = []
        distribution_by_type = {}
        seen_requirement_ids = set()

        for row in data:
            requirement_id = row.InspectionRequirement.id
            if requirement_id in seen_requirement_ids:
                continue
            seen_requirement_ids.add(requirement_id)

            project_name, project_type = self._get_project_details(row)
            project_type = project_type or "Unknown"
            project_name = project_name or "Unknown"

            if project_type not in distribution_by_type:
                distribution_by_type[project_type] = {
                    "projects": {},
                    "totals": {
                        "in_count": 0,
                        "out_count": 0,
                        "not_determined_count": 0,
                        "total": 0,
                    },
                }

            projects = distribution_by_type[project_type]["projects"]
            if project_name not in projects:
                projects[project_name] = {
                    "in_count": 0,
                    "out_count": 0,
                    "not_determined_count": 0,
                    "total": 0,
                }

            compliance_finding = (row.compliance_finding or "").strip().lower()

            if compliance_finding == "in":
                projects[project_name]["in_count"] += 1
                distribution_by_type[project_type]["totals"]["in_count"] += 1
            elif compliance_finding == "out":
                projects[project_name]["out_count"] += 1
                distribution_by_type[project_type]["totals"]["out_count"] += 1
            else:
                projects[project_name]["not_determined_count"] += 1
                distribution_by_type[project_type]["totals"]["not_determined_count"] += 1

            projects[project_name]["total"] += 1
            distribution_by_type[project_type]["totals"]["total"] += 1

        for project_type in sorted(distribution_by_type.keys()):
            totals = distribution_by_type[project_type]["totals"]
            result.append(
                {
                    "project_type": project_type,
                    "project_name": "Total",
                    "in_count": totals["in_count"],
                    "out_count": totals["out_count"],
                    "not_determined_count": totals["not_determined_count"],
                    "total": totals["total"],
                    "row_type": "project_type_total",
                }
            )

            projects = distribution_by_type[project_type]["projects"]
            for project_name in sorted(projects.keys()):
                project_counts = projects[project_name]
                result.append(
                    {
                        "project_type": project_type,
                        "project_name": f"{project_name}",
                        "in_count": project_counts["in_count"],
                        "out_count": project_counts["out_count"],
                        "not_determined_count": project_counts["not_determined_count"],
                        "total": project_counts["total"],
                        "row_type": "project",
                    }
                )

        return result

    @staticmethod
    def _format_enforcement_distribution_insights_data(enforcements_data):
        """Format enforcement distribution insights by project/action with status columns."""
        distribution_by_project = {}
        all_statuses = set()

        for row in enforcements_data:
            project_name = row.get("project_name") or "Unknown"
            enforcement_action = row.get("enforcement_action") or "(empty)"
            enforcement_status = row.get("enforcement_status") or "(empty)"
            all_statuses.add(enforcement_status)

            if project_name not in distribution_by_project:
                distribution_by_project[project_name] = {"actions": {}}

            actions = distribution_by_project[project_name]["actions"]
            if enforcement_action not in actions:
                actions[enforcement_action] = {
                    "statuses": {},
                }

            statuses = actions[enforcement_action]["statuses"]
            statuses[enforcement_status] = statuses.get(enforcement_status, 0) + 1

        status_columns = sorted(all_statuses)

        def _build_status_count_row(statuses):
            row = {status: statuses.get(status, 0) for status in status_columns}
            row["total"] = sum(statuses.values())
            return row

        result = []
        for project_name in sorted(distribution_by_project.keys()):
            project_data = distribution_by_project[project_name]

            project_statuses = {}
            for action_data in project_data["actions"].values():
                for status, count in action_data["statuses"].items():
                    project_statuses[status] = project_statuses.get(status, 0) + count

            project_row = {
                "project_name": project_name,
                "enforcement_action": "Total",
                "row_type": "project_total",
            }
            project_row.update(_build_status_count_row(project_statuses))
            result.append(
                project_row
            )

            for enforcement_action in sorted(project_data["actions"].keys()):
                action_data = project_data["actions"][enforcement_action]

                action_row = {
                    "project_name": project_name,
                    "enforcement_action": f"{enforcement_action}",
                    "row_type": "action_total",
                }
                action_row.update(_build_status_count_row(action_data["statuses"]))
                result.append(
                    action_row
                )

        return result, status_columns

    @staticmethod
    def _apply_insights_distribution_outline(
        worksheet,
        start_row,
        insights_distribution_data,
        start_col=1,
        end_col=None,
    ):
        """Apply row hierarchy formatting for project rows under each project type total row."""
        worksheet.sheet_properties.outlinePr.summaryBelow = False
        border_side = Side(style="thin", color="000000")
        total_row_border = Border(
            left=border_side,
            right=border_side,
            top=border_side,
            bottom=border_side,
        )
        if end_col is None:
            end_col = worksheet.max_column

        for index, item in enumerate(insights_distribution_data):
            row_number = start_row + index
            row_type = item.get("row_type")

            if row_type == "project":
                worksheet.row_dimensions[row_number].outlineLevel = 1
                worksheet.row_dimensions[row_number].hidden = False
            elif row_type == "project_type_total":
                for col_number in range(start_col, end_col + 1):
                    cell = worksheet.cell(row=row_number, column=col_number)
                    cell.font = Font(bold=True)
                    cell.border = total_row_border

    @staticmethod
    def _apply_enforcement_distribution_outline(
        worksheet,
        start_row,
        insights_enforcement_distribution_data,
        start_col=1,
        end_col=None,
    ):
        """Apply row hierarchy formatting for enforcement rows under each project row."""
        worksheet.sheet_properties.outlinePr.summaryBelow = False
        border_side = Side(style="thin", color="000000")
        total_row_border = Border(
            left=border_side,
            right=border_side,
            top=border_side,
            bottom=border_side,
        )
        if end_col is None:
            end_col = worksheet.max_column

        for index, item in enumerate(insights_enforcement_distribution_data):
            row_number = start_row + index
            row_type = item.get("row_type")

            if row_type == "project_total":
                for col_number in range(start_col, end_col + 1):
                    cell = worksheet.cell(row=row_number, column=col_number)
                    cell.font = Font(bold=True)
                    cell.border = total_row_border
            elif row_type == "action_total":
                worksheet.row_dimensions[row_number].outlineLevel = 1
                worksheet.row_dimensions[row_number].hidden = False

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
    def _auto_size_table_columns(worksheet, start_col, num_cols, max_row, max_width=30, min_width=10):
        """Auto-size only a specific table region's columns."""
        if num_cols < 1 or max_row < 1:
            return

        for col_offset in range(num_cols):
            col_number = start_col + col_offset + 1
            max_length = 0
            for row_number in range(1, max_row + 1):
                value = worksheet.cell(row=row_number, column=col_number).value
                if value is not None:
                    max_length = max(max_length, len(str(value)))
            worksheet.column_dimensions[get_column_letter(col_number)].width = min(
                max(max_length, min_width), max_width
            )

    @staticmethod
    def _style_table_region_as_grid(
        worksheet,
        start_row,
        start_col,
        row_count,
        col_count,
        total_row=None,
    ):
        """Apply grid styling to a bounded table region."""
        if row_count < 1 or col_count < 1:
            return

        border_side = Side(style="thin", color="000000")
        vertical_border = Border(left=border_side, right=border_side)
        full_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
        header_fill = PatternFill(fill_type="solid", fgColor="F2F2F2")
        header_font = Font(bold=True)
        total_font = Font(bold=True)

        end_row = start_row + row_count - 1
        end_col = start_col + col_count - 1

        for row_number in range(start_row, end_row + 1):
            for col_number in range(start_col, end_col + 1):
                worksheet.cell(row=row_number, column=col_number).border = vertical_border

        for col_number in range(start_col, end_col + 1):
            cell = worksheet.cell(row=start_row, column=col_number)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = full_border

        if total_row and total_row > start_row:
            for col_number in range(start_col, end_col + 1):
                cell = worksheet.cell(row=total_row, column=col_number)
                cell.font = total_font
                cell.border = full_border

    @staticmethod
    def _add_filter_table(worksheet, start_row, start_col, row_count, col_count, table_name):
        """Add an Excel table to enable filter dropdowns for a specific table region."""
        if row_count < 1 or col_count < 1:
            return

        end_row = start_row + row_count - 1
        end_col = start_col + col_count - 1
        table_ref = f"{get_column_letter(start_col)}{start_row}:{get_column_letter(end_col)}{end_row}"
        worksheet.add_table(Table(displayName=table_name, ref=table_ref))

    @staticmethod
    def _get_inspections_tab_columns_and_headers():
        """Get existing columns and their headers for Excel export."""
        headers = [
            "IR Number",
            "IR Progress",
            "Project Name",
            "Project Type",
            "IR Issuance Date",
            "Primary",
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
            "Enforcement Doc #",
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
    def _get_insights_tab_columns_and_headers():
        """Get insights columns and headers for Excel export."""
        headers = [
            "IR Progress",
            "Number of Inspections",
        ]

        columns = [
            "ir_progress",
            "number_of_inspections",
        ]

        return headers, columns

    @staticmethod
    def _get_insights_distribution_columns_and_headers():
        """Get insights distribution columns and headers for Excel export."""
        headers = [
            "Project Type",
            "Project Name",
            "In",
            "Out",
            "Not Determined",
            "Total",
        ]

        columns = [
            "project_type",
            "project_name",
            "in_count",
            "out_count",
            "not_determined_count",
            "total",
        ]

        return headers, columns

    @staticmethod
    def _get_insights_enforcement_distribution_columns_and_headers(status_columns):
        """Get enforcement distribution insights columns and headers for Excel export."""
        headers = [
            "Project",
            "Enforcement Action",
        ] + status_columns + [
            "Total",
        ]

        columns = [
            "project_name",
            "enforcement_action",
        ] + status_columns + [
            "total",
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
