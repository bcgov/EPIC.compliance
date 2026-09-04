"""Project Compliance History Report Generator Service."""
from datetime import datetime, time
from io import BytesIO

import pandas as pd

from flask import current_app
from sqlalchemy import and_, func
from sqlalchemy.orm import aliased, selectinload

from compliance_api.models import db
from compliance_api.models.administrative_penalty import AdministrativePenalty, DecisionEnum
from compliance_api.models.charge_recommendation import ChargeRecommendation
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.enforcement_action import EnforcementActionOption, EnforcementActionOptionEnum
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_option import InspectionInitiationOption, InspectionTypeOption
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection.inspection_type import InspectionType
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.models.order import Order
from compliance_api.models.project import Project
from compliance_api.models.restorative_justice import RestorativeJustice
from compliance_api.models.staff_user import StaffUser
from compliance_api.models.topic import Topic
from compliance_api.models.violation_ticket import ViolationTicket
from compliance_api.models.warning_letter import WarningLetter
from compliance_api.services.report.utils.shared_queries import (
    get_requirement_admin_penalty_sub_query, get_requirement_charge_rec_sub_query, get_requirement_order_sub_query,
    get_requirement_restorative_justice_sub_query, get_requirement_violation_ticket_sub_query,
    get_requirement_warning_letter_sub_query)
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.utils.datetime import BC_TIMEZONE

from .base import BaseReportGenerator


class ProjectComplianceReportGenerator(BaseReportGenerator):
    """Project Compliance Report Generator Service."""

    def __init__(self, report_data):
        """Initialize the Project Compliance Report Generator with the provided report data."""
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
        self.project_id = report_data.get("project_id")

        current_app.logger.info(
            f"Project Compliance History Report Generator initialized with start_date: {self.start_date}, \
                end_date: {self.end_date}, project_id: {self.project_id}."
        )

        if self.project_id is None:
            raise ValueError("Project ID must be provided for Project Compliance History Report.")

    def generate(self):
        """Project Compliance Report Generation Logic."""
        # Inspections Requirements Tab
        data = self._build_inspection_requirements_query(self.project_id).all()
        data = self._format_inspection_requirements_data(data)
        inspections_data_frame = pd.json_normalize(data)
        inspections_headers, inspections_columns = self._get_inspection_requirements_tab_columns_and_headers()
        output = self._to_excel(
            inspections_data_frame,
            inspections_columns,
            inspections_headers
        )
        return output

    def _to_excel(
                self,
                inspections_data_frame,
                inspections_columns,
                inspections_headers
    ):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:

            # If there is no data, create an empty dataframe with columns so that
            # the excel file will still have the correct headers and structure
            if inspections_data_frame.empty:
                inspections_data_frame = pd.DataFrame(columns=inspections_columns)

            # Inspection Requirements
            inspections_data_frame.to_excel(
                writer,
                sheet_name="Inspection Requirements",
                columns=inspections_columns,
                header=inspections_headers,
                index=False,
            )
            worksheet = writer.sheets["Inspection Requirements"]
            # Making the columns wider
            for col_idx, column in enumerate(worksheet.columns, start=1):
                column_letter = column[0].column_letter

                # Header length (from inspections_headers)
                header_text = inspections_headers[col_idx - 1]
                max_length = len(str(header_text))

                # Data cell lengths
                for cell in column[1:]:
                    if cell.value is not None:
                        max_length = max(max_length, len(str(cell.value)))

                worksheet.column_dimensions[column_letter].width = min(max_length, 50)

        output.seek(0)
        return output.getvalue()

    def _build_inspection_requirements_query(self, project_id: int):
        """Build base query for Project Compliance History Report."""
        # Alias all enforcement types to join on ALL linked enforcement actions.
        order_alias = aliased(Order)
        warning_letter_alias = aliased(WarningLetter)
        violation_ticket_alias = aliased(ViolationTicket)
        admin_penalty_alias = aliased(AdministrativePenalty)
        restorative_justice_alias = aliased(RestorativeJustice)
        charge_rec_alias = aliased(ChargeRecommendation)

        requirement_order_subquery = get_requirement_order_sub_query()
        requirement_warning_letter_subquery = get_requirement_warning_letter_sub_query()
        requirement_violation_ticket_subquery = get_requirement_violation_ticket_sub_query()
        requirement_admin_penalty_subquery = get_requirement_admin_penalty_sub_query()
        requirement_charge_rec_subquery = get_requirement_charge_rec_sub_query()
        requirement_restorative_justice_subquery = get_requirement_restorative_justice_sub_query()
        inspection_type_subquery = _get_inspection_type_subquery()

        query = (
            db.session.query(
                InspectionRequirement,
                InspectionRequirement.summary.label("summary"),
                Inspection.ir_number.label("ir_number"),
                Topic.name.label("topic_name"),
                Inspection.start_date.label("start_date"),
                Inspection.end_date.label("end_date"),
                inspection_type_subquery.c.inspection_types.label("inspection_type"),
                InspectionInitiationOption.name.label("initiation_name"),
                InspectionRecord.ir_progress.label("ir_progress"),
                Project.id.label("project_id"),
                ComplianceFindingOption.name.label("compliance_finding"),
                InspectionReqEnforcementMap.enforcement_action_id.label("enforcement_action_id"),
                EnforcementActionOption.name.label("enforcement_action"),
                # Enforcement statuses
                order_alias.order_status.label("order_status"),
                warning_letter_alias.status.label("warning_letter_status"),
                violation_ticket_alias.status.label("violation_ticket_status"),
                admin_penalty_alias.referral_status.label("admin_penalty_status"),
                charge_rec_alias.status.label("charge_rec_status"),
                restorative_justice_alias.status.label("restorative_justice_status"),
                # Enforcement document numbers
                order_alias.order_number.label("order_number"),
                warning_letter_alias.warning_letter_number.label("warning_letter_number"),
                violation_ticket_alias.ticket_number.label("violation_ticket_number"),
                admin_penalty_alias.administrative_penalty_number.label("admin_penalty_number"),
                charge_rec_alias.charge_recommendation_number.label("charge_rec_number"),
                restorative_justice_alias.restorative_justice_number.label("restorative_justice_number"),
                admin_penalty_alias.decision.label("ap_dm_decision"),
                admin_penalty_alias.penalty_amount.label("ap_penalty_amount"),
                InspectionRecord.date_issued.label("ir_date_issued"),
                StaffUser,
                Inspection.inspection_status.label("inspection_status"),
            )
            .join(Inspection, and_(
                InspectionRequirement.inspection_id == Inspection.id,
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False)
            ))
            .outerjoin(
                inspection_type_subquery,
                inspection_type_subquery.c.inspection_id == Inspection.id
            )
            .outerjoin(InspectionInitiationOption, Inspection.initiation_id == InspectionInitiationOption.id)
            .outerjoin(Topic, InspectionRequirement.topic_id == Topic.id)
            .outerjoin(Project, Inspection.project_id == Project.id)
            .outerjoin(
                ComplianceFindingOption,
                InspectionRequirement.compliance_finding_id == ComplianceFindingOption.id
            )
            .outerjoin(InspectionReqEnforcementMap, and_(
                InspectionReqEnforcementMap.requirement_id == InspectionRequirement.id,
                InspectionReqEnforcementMap.is_active.is_(True),
                InspectionReqEnforcementMap.is_deleted.is_(False)
            ))
            .join(InspectionRecord, and_(
                InspectionRecord.inspection_id == Inspection.id,
                InspectionRecord.is_active.is_(True),
                InspectionRecord.is_deleted.is_(False)
            ))
            .outerjoin(
                EnforcementActionOption,
                InspectionReqEnforcementMap.enforcement_action_id == EnforcementActionOption.id
            )
            .outerjoin(StaffUser, Inspection.primary_officer_id == StaffUser.id)
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
                admin_penalty_alias,
                admin_penalty_alias.id == requirement_admin_penalty_subquery.c.administrative_penalty_id
            )
            .outerjoin(
                requirement_charge_rec_subquery,
                requirement_charge_rec_subquery.c.inspection_requirement_id == InspectionRequirement.id
            )
            .outerjoin(
                charge_rec_alias,
                charge_rec_alias.id == requirement_charge_rec_subquery.c.charge_recommendation_id
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
                Inspection.project_id == project_id,
                Inspection.start_date >= self.start_date if self.start_date else True,
                Inspection.start_date <= self.end_date if self.end_date else True,
            )
            .order_by(Inspection.ir_number, EnforcementActionOption.id)
            .options(
                selectinload(InspectionRequirement.requirement_source_details)
            )
        )
        return query

    @staticmethod
    def _format_inspection_requirements_data(data):
        """Format data for excel export."""
        result = []
        for row in data:
            inspection_requirement = row.InspectionRequirement
            raw_enforcement_status = ServiceUtils.get_enforcement_status_by_type(row)
            primary_officer = row.StaffUser
            req_source_details = inspection_requirement.requirement_source_details
            is_ap_penalty = row.enforcement_action_id \
                and row.enforcement_action_id == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value

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
                "start_date": row.start_date.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                if row.start_date else None,
                "end_date": row.end_date.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                if row.end_date and row.start_date != row.end_date else None,
                "initiation": row.initiation_name if row.initiation_name else row.initiation,
                "ir_progress": row.ir_progress.value if row.ir_progress else None,
                "inspection_type": row.inspection_type,
                "compliance_finding": row.compliance_finding,
                "enforcement_action": row.enforcement_action,
                "enforcement_status": raw_enforcement_status.value if raw_enforcement_status else None,
                "ap_dm_decision": row.ap_dm_decision.value if is_ap_penalty and row.ap_dm_decision else None,
                "ap_penalty_amount": row.ap_penalty_amount
                if is_ap_penalty and row.ap_dm_decision == DecisionEnum.AP_ISSUED else None,
                "enforcement_document_number": ServiceUtils.get_enforcement_number_by_type(row),
                "condition_number": condition_num_string,
                "requirement_source": source_string,
                "ir_issuance_date": row.ir_date_issued.astimezone(BC_TIMEZONE).strftime("%Y-%m-%d")
                if row.ir_date_issued else None,
                "primary_officer": f"{primary_officer.first_name} {primary_officer.last_name}"
                if primary_officer else None,
                "inspection_status": row.inspection_status.value if row.inspection_status else None,
            }
            result.append(item)
        return result

    @staticmethod
    def _get_inspection_requirements_tab_columns_and_headers():
        """Get existing columns and their headers for Excel export."""
        headers = [
            "IR Number",
            "Topic",
            "Summary",
            "Inspection Start Date",
            "Inspection End Date",
            "Initiation",
            "IR Progress",
            "Inspection Type",
            "Compliance Finding",
            "Enforcement Action",
            "Enforcement Status",
            "DM Decision",
            "AP Value",
            "Enforcement Document",
            "Condition Number",
            "Requirement Source",
            "IR Issuance Date",
            "Primary Officer",
            "Inspection Status",
        ]

        columns = [
            "ir_number",
            "topic_name",
            "summary",
            "start_date",
            "end_date",
            "initiation",
            "ir_progress",
            "inspection_type",
            "compliance_finding",
            "enforcement_action",
            "enforcement_status",
            "ap_dm_decision",
            "ap_penalty_amount",
            "enforcement_document_number",
            "condition_number",
            "requirement_source",
            "ir_issuance_date",
            "primary_officer",
            "inspection_status",
        ]

        return headers, columns


def _get_inspection_type_subquery():
    """Get subquery for inspection types as comma-separated list."""
    return (
        db.session.query(
            InspectionType.inspection_id,
            func.string_agg(
                InspectionTypeOption.name,
                ", "
            ).label("inspection_types")
        )
        .join(
            InspectionTypeOption,
            InspectionType.type_id == InspectionTypeOption.id
        )
        .group_by(InspectionType.inspection_id)
        .subquery()
    )
