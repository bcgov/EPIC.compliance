"""Inspection Record Data Builder."""

from sqlalchemy.orm import joinedload

from compliance_api.exceptions import UnprocessableEntityError
from compliance_api.models.administrative_penalty import AdministrativePenalty as AdministrativePenaltyModel
from compliance_api.models.administrative_penalty import \
    AdministrativePenaltyInspectionRequirementMap as AdministrativePenaltyInspectionRequirementMapModel
from compliance_api.models.appendix import Appendix as AppendixModel
from compliance_api.models.department_detail import DepartmentDetail as DepartmentDetailModel
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.inspection import InspectionAttendanceOptionEnum
from compliance_api.models.inspection import InspectionRequirement as InspectionRequirementModel
from compliance_api.models.inspection import InspectionRequirementTypeEnum
from compliance_api.models.inspection import IRStatusOption as IRStatusOptionModel
from compliance_api.models.inspection.inspection_req_source_detail import InspectionReqSourceDetail
from compliance_api.models.inspection_record import InspectionRecord as InspectionRecordModel
from compliance_api.models.inspection_record import IRProgressEnum, IRStatusEnum
from compliance_api.models.inspection_record_approval import InspectionRecordApproval as InspectionRecordApprovalModel
from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models.order import OrderProgressEnum, OrderReplaceStatusEnum
from compliance_api.models.warning_letter import WarningLetter as WarningLetterModel
from compliance_api.models.warning_letter import \
    WarningLetterInspectionRequirementMap as WarningLetterInspectionRequirementMapModel
from compliance_api.services.inspection_record.ir_template_constant import (
    ACTION_REQUIRED_BY_RP, AREA_INSPECTED, ENFORCEMENT_SUMMARY, FINDING_STATEMENT, INSPECTION_SCOPE,
    PRELIMINARY_REVIEW_DETAILS)
from compliance_api.utils.datetime import convert_to_full_month_format
from compliance_api.utils.template_renderer import render_template_with_data

from ..service_utils import ServiceUtils


class InspectionRecordDataBuilder:
    """InspesctionRecordDataBuilder."""

    def __init__(
        self,
        inspection: InspectionModel,
        ir_status: int,
        existing_ir: InspectionRecordModel = None,
    ):
        """
        Initialize the builder with an inspection instance and its status.

        :param inspection: The inspection object (SQLAlchemy model instance).
        :param ir_status: The status of the inspection (PRELIMINARY or FINAL).
        :param existing_ir: The existing inspection record if present.
                This is usedful when building details from existing record)
        """
        self.inspection = inspection
        self.ir_status = ir_status
        self.requirements = []
        self.approvals = []
        self.existing_ir = existing_ir
        self.data = {
            "ir_status": IRStatusOptionModel.find_by_id(self.ir_status).name,
            "mailing_address": (
                self.existing_ir.mailing_address if self.existing_ir else None
            ),
            "record_prepared_by_id": (
                self.existing_ir.record_prepared_by_id
                if self.existing_ir
                else inspection.primary_officer_id
            ),
            "record_prepared_by_position_id": (
                self.existing_ir.record_prepared_by_position_id
                if self.existing_ir
                else inspection.primary_officer.position_id
            ),
        }
        self.data["inspection_details"] = {
            "id": self.inspection.id,
            "inspection_type": " and ".join(
                [inspection_type.type.name for inspection_type in self.inspection.types]
            ),
            "start_date": self.inspection.start_date.strftime("%Y-%m-%d"),
            "utm": self.inspection.utm,
            "project_description": self.inspection.project_description,
            "location_description": self.inspection.location_description,
            "initiation": self.inspection.initiation.name,
            "ir_number": ServiceUtils.strip_project_code(self.inspection.ir_number),
        }

        # Initialize officer_details
        self.data["officer_details"] = {}
        if self.existing_ir:
            self.data["ir_progress"] = self.existing_ir.ir_progress
        else:
            self.data["ir_progress"] = (
                IRProgressEnum.PRELIMINARY_DRAFTING
                if self.ir_status == IRStatusEnum.PRELIMINARY.value
                else IRProgressEnum.FINALIZING_RECORD
            )

    def build_approval_info(self):
        """Build the approval information for the inspection record."""
        self.approvals, inspection_record = self._get_approval()
        if len(self.approvals) > 0:
            latest_approval = self.approvals[0]
            if inspection_record.ir_progress in [
                IRProgressEnum.PRELIMINARY_APPROVED,
                IRProgressEnum.HOLDER_PRELIMINARY_REVIEW,
                IRProgressEnum.FINAL_APPROVED,
                IRProgressEnum.ISSUED,
            ]:
                if latest_approval.approved_by:
                    # Use stored position if available, otherwise fall back to current position
                    approved_by_position_name = (
                        latest_approval.approved_by_position.name
                        if latest_approval.approved_by_position
                        else latest_approval.approved_by.position.name
                    )
                    #  Use the position from existing record if the record_prepared_by_id
                    #  is same as approved_by_id
                    if (
                        self.existing_ir
                        and self.existing_ir.record_prepared_by_id
                        == latest_approval.approved_by_id
                    ):
                        approved_by_position_name = (
                            self.existing_ir.record_prepared_by_position.name
                        )
                    self.data["approval_info"] = {
                        "approved_by": latest_approval.approved_by.first_name
                        + " "
                        + latest_approval.approved_by.last_name,
                        "approved_by_position": approved_by_position_name,
                    }
        return self

    def build_officer_details(self):
        """Build the officer details for the inspection record."""
        record_prepared_by = (
            self.existing_ir.record_prepared_by
            if self.existing_ir
            else self.inspection.primary_officer
        )
        record_prepared_by_position = (
            self.existing_ir.record_prepared_by_position
            if self.existing_ir
            else self.inspection.primary_officer.position
        )
        self.data["officer_details"] = {
            "primary_officer": {
                "name": f"{self.inspection.primary_officer.first_name} {self.inspection.primary_officer.last_name}",
                "position": self.inspection.primary_officer.position.name,
            },
            "record_prepared_by": {
                "name": f"{record_prepared_by.first_name} "
                f"{record_prepared_by.last_name}",
                "position": record_prepared_by_position.name,
            },
        }

        # Build the attendance information
        self._build_officer_attendance()

        return self

    def _build_officer_attendance(self):
        """Build the attendance information for the inspection record."""
        from compliance_api.services.inspection import InspectionService

        # Get all attendance options for this inspection
        attendance_options = InspectionService.get_attendance_options(
            self.inspection.id
        )

        # Initialize an empty list to store attendance information
        attendance_list = []
        # Initialize inspecting officers list with primary officer
        inspecting_officers = []
        # Process each attendance option
        for option in attendance_options:
            # Skip officer attendance as per requirement
            if (
                option.attendance_option_id
                == InspectionAttendanceOptionEnum.ATTENDING_OFFICERS.value
            ):
                for officer in option.data:
                    inspecting_officers.append(
                        {
                            "id": officer.get("id"),
                            "name": f"{officer.get('name')}",
                            "position": officer.get("position").get("name"),
                        }
                    )
                #  Iterate over the inspecting officers to fix their position name
                for officer in inspecting_officers:
                    if (
                        self.existing_ir
                        and self.existing_ir.record_prepared_by_id == officer.get("id")
                    ):
                        officer["position"] = (
                            self.existing_ir.record_prepared_by_position.name
                        )
                continue
            # Handle different types of attendance data
            if option.data:
                if isinstance(option.data, list):
                    # For agencies, first nations, etc.
                    for item in option.data:
                        if isinstance(item, dict) and "name" in item:
                            attendance_list.append(item["name"])
                elif isinstance(option.data, str):
                    # For other attendance
                    for item in option.data.splitlines():
                        if item.strip():
                            attendance_list.append(item.strip())
            else:
                # If no data, use the attendance option name
                if (
                    option.attendance_option_id
                    == InspectionAttendanceOptionEnum.CERTIFICATE_HOLDER_OR_REGULATED_PARTY_REPRESENTATIVE.value
                ):
                    if not self.data.get("project_details"):
                        self.build_project_details()
                    attendance_list.append(self.data["project_details"]["proponent"])
                else:
                    attendance_list.append(option.attendance_option.name)

        # Add the attendance information to the officer_details dictionary
        self.data["officer_details"]["in_attendance"] = attendance_list
        self.data["officer_details"]["inspecting_officers"] = inspecting_officers

        return self

    def build_appendices(self):
        """Build the appendices for the inspection record."""
        # Get all active non-deleted appendices for this inspection
        appendices = AppendixModel.get_by_inspection_id(self.inspection.id)

        # Add the appendices to the data dictionary
        self.data["appendices"] = appendices

        return self

    def build_department_details(self):
        """Build the department details for the inspection record."""
        # Get the department details
        department_details = DepartmentDetailModel.query.filter_by(
            is_active=True, is_deleted=False
        ).first()

        # Add the department details to the data dictionary
        if department_details:
            self.data["department_details"] = {
                "logo_url": department_details.logo_url,
                "email": department_details.email,
                "address_line1": department_details.address_line1,
                "address_line2": department_details.address_line2,
                "phone": department_details.phone,
                "website": department_details.website,
            }

        return self

    def build_project_details(self):
        """Populate project specific details."""
        if self.data.get("project_details"):
            return self

        project_id = self.inspection.case_file.project_id
        self.data["project_details"] = ServiceUtils.get_project_details(
            project_id, self.inspection.case_file.id, self.inspection.project_status_id
        )
        return self

    def build_inspection_scope(self):
        """Populate the inspection scope data."""
        #  if there is an existing ir and we are building the same ir, then the inspection scope should not be built
        if (
            self.existing_ir is not None
            and self.existing_ir.ir_status.id == self.ir_status
        ):
            self.data["inspection_scope"] = self.existing_ir.inspection_scope
            return self
        debreif_date = self.inspection.debrief_date
        area_inspected = self.inspection.area_inspected
        inspection_scope_data = {
            "debrief_date": (
                convert_to_full_month_format(debreif_date) if debreif_date else None
            ),  # handling of the null case
            "requirements": [],
            "area_inspected": area_inspected if area_inspected else AREA_INSPECTED,
        }
        requirements = InspectionRequirementModel.get_by_inspection_id(
            self.inspection.id
        )
        #  set the requirements to the builder for later use
        self.requirements = requirements
        requirement_lines = []
        if len(requirements) > 0:
            for requirement in requirements:
                #  Some requirements may not have any source details
                if requirement.requirement_source_details:
                    #  Identify the first requirement source detail
                    first_rq_detail = requirement.requirement_source_details[0]
                    number = ServiceUtils.get_requirement_source_number_field(
                        first_rq_detail
                    )

                    requirement_lines.append(
                        f"{number} of {first_rq_detail.requirement_source.name} with respect to {requirement.summary}"
                    )

        inspection_scope_data["requirements"] = requirement_lines
        self.data["inspection_scope"] = render_template_with_data(
            "INSPECTION_SCOPE", INSPECTION_SCOPE, data=inspection_scope_data
        )
        return self

    def build_preliminary_review_details(self):
        """Build the preliminary review details."""
        #  if there is an existing ir and we are building the same ir, then
        # the preliminary review details should not be built
        if (
            self.existing_ir is not None
            and self.existing_ir.ir_status.id == self.ir_status
        ):
            self.data["preliminary_review_details"] = (
                self.existing_ir.preliminary_review_details
            )
            return self
        preliminary_review_details = {}
        #  No preliminary_review_details for ir when it is PRELIMINARY
        if self.ir_status == IRStatusEnum.PRELIMINARY.value:
            preliminary_review_details = None
        elif self.ir_status == IRStatusEnum.FINAL.value:
            self.approvals, _ = self._get_approval()
            # Build comma separated dates from the approval requests
            if self.approvals:
                data = {
                    "date_report_sent": ", ".join(
                        convert_to_full_month_format(approval.date_report_sent)
                        for approval in self.approvals
                        if approval.date_report_sent is not None
                    ),
                    "date_response": ", ".join(
                        convert_to_full_month_format(approval.date_response)
                        for approval in self.approvals
                        if approval.date_response is not None
                    ),
                }
                # Bulid the project details if not yet build to get the proponent label
                if not self.data.get("project_details"):
                    self.build_project_details()
                data["proponent_label"] = self.data["project_details"][
                    "proponent_label"
                ]
                data["primary_last_name"] = self.inspection.primary_officer.last_name
                preliminary_review_details = render_template_with_data(
                    "PRELIMINARY_REVIEW_DETAILS", PRELIMINARY_REVIEW_DETAILS, data
                )
                self.data["preliminary_review_details"] = preliminary_review_details
        return self

    def build_version_date_info(self):
        """Build the version date info for the inspection record."""
        self.approvals, inspection_record = self._get_approval()
        preliminary_dates = []
        if self.approvals:
            for approval in self.approvals:
                if approval.date_report_sent is not None:
                    preliminary_dates.append(
                        approval.date_report_sent.strftime("%Y-%m-%d")
                    )
            self.data["version_date_info"] = {
                "preliminary_dates": preliminary_dates,
                "final_date": (
                    inspection_record.date_issued.strftime("%Y-%m-%d")
                    if inspection_record.date_issued
                    else (
                        inspection_record.intended_issuance_date.strftime("%Y-%m-%d")
                        if inspection_record.intended_issuance_date
                        else None
                    )
                ),
            }
        return self

    def build_finding_statement(self):
        """Build the finding statement for the inspection record."""
        #  if there is an existing ir and we are building the same ir, then the finding statement should not be built
        if (
            self.existing_ir is not None
            and self.existing_ir.ir_status.id == self.ir_status
        ):
            self.data["finding_statement"] = self.existing_ir.finding_statement
            return self
        self.data["finding_statement"] = render_template_with_data(
            "FINDING_STATEMENT", FINDING_STATEMENT, data={}
        )
        return self

    def build_enforcement_summary(self):
        """Build the enforcement summary for the inspection record."""
        #  if there is an existing ir and we are building the same ir, then the enforcement summary should not be built
        if (
            self.existing_ir is not None
            and self.existing_ir.ir_status.id == self.ir_status
        ):
            self.data["enforcement_summary"] = self.existing_ir.enforcement_summary
            return self
        enforcement_summary_lines = []
        #  Only Issued Orders are required to be shown in the enforcement summary at Preliminary level
        if self.ir_status == IRStatusEnum.PRELIMINARY.value:
            enforcement_summary_lines = (
                self._generate_enforcement_summary_lines_for_special_actions(
                    EnforcementActionOptionEnum.ORDER, IRStatusEnum.PRELIMINARY.value
                )
            )
            #  Order needs to be checked and returned from here
        elif self.ir_status == IRStatusEnum.FINAL.value:
            if not self.requirements:
                self.requirements = (
                    InspectionRequirementModel.query
                    .filter_by(inspection_id=self.inspection.id, is_deleted=False, is_active=True)
                    .options(
                        joinedload(InspectionRequirementModel.enforcement_actions),
                        joinedload(InspectionRequirementModel.requirement_source_details)
                        .joinedload(InspectionReqSourceDetail.requirement_source),
                        joinedload(InspectionRequirementModel.agency)
                    )
                    .all()
                )
            if not self.data.get("project_details"):
                self.build_project_details()
            grouped_enforcementactions = self._get_requirements_by_enforcement_action(
                self.requirements
            )
            #  Actions that can be applied to individual requirements
            valid_actions_for_individual_requirements = {
                EnforcementActionOptionEnum.NOTICE_OF_NON_COMPLIANCE,
                EnforcementActionOptionEnum.REFERRAL_TO_ANOTHER_AGENCY,
            }
            #  Actions that are mapped to multiple requirements
            special_actions = {
                EnforcementActionOptionEnum.WARNING_LETTER,
                EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION,
                EnforcementActionOptionEnum.ORDER,
            }
            for action_id, requirements in grouped_enforcementactions.items():
                for requirement in requirements:
                    if (
                        EnforcementActionOptionEnum(action_id)
                        in valid_actions_for_individual_requirements
                    ):
                        summary_line = self._generate_enforcement_summary_lines(
                            EnforcementActionOptionEnum(action_id), requirement
                        )
                        if summary_line:
                            enforcement_summary_lines.append(summary_line)
                #  _generate_enforcement_summary_lines_for_special_actions is only called for special actions
                #  it handles multiple requirements at once for a single action
                if EnforcementActionOptionEnum(action_id) in special_actions:
                    summary_lines = (
                        self._generate_enforcement_summary_lines_for_special_actions(
                            EnforcementActionOptionEnum(action_id),
                            self.ir_status,
                        )
                    )
                    if summary_lines:
                        enforcement_summary_lines.extend(summary_lines)
            # Add a line for Regulatory Considerations in the requirements
            if any(
                req.req_type == InspectionRequirementTypeEnum.REG
                for req in self.requirements
            ):
                enforcement_summary_lines.append(
                    """<p class="editor-paragraph" dir="ltr">See Regulatory Considerations
                    Section for additional information.</p>"""
                )
        if len(enforcement_summary_lines) > 0:
            if not self.data.get("project_details"):
                self.build_project_details()
            enforcement_summary_lines.append(
                render_template_with_data(
                    "ENFORCEMENT_SUMMARY.DEFAULT",
                    ENFORCEMENT_SUMMARY.get("DEFAULT"),
                    {
                        "project_name": self.data["project_details"].get("name"),
                        "act": "Environmental Assessment Act",
                        "act_year": "2018",
                    },
                )
            )
            self.data["enforcement_summary"] = (
                '<p class="editor-paragraph" dir="ltr">'
                + '<p class="editor-paragraph"><br></p>'.join(enforcement_summary_lines)
                + "</p>"
            )
        return self

    def build_action_required_by_rp(self, hard_reset=False):
        """Build the action required by proponent."""
        """
        Parameters
        ----------
        hard_reset : bool
            If True, the action_required_by_rp will be reset.
        """
        #  if there is an existing ir and we are building the same ir,
        # then the action_required_by_rp should not be built
        if (
            self.existing_ir is not None
            and self.existing_ir.ir_status.id == self.ir_status
            and not hard_reset
        ):
            self.data["action_required_by_rp"] = self.existing_ir.action_required_by_rp
            return self
        if self.ir_status == IRStatusEnum.FINAL.value:
            self.data["action_required_by_rp"] = None
            return self
        # Check if officer_details are populated
        if not self.data["officer_details"].get("primary_officer"):
            self.build_officer_details()
        data = {
            "primary_officer": self.data["officer_details"]
            .get("primary_officer")
            .get("name")
        }
        if self.existing_ir:
            latest_approval = InspectionRecordApprovalModel.get_latest_approval_by_ir(
                self.existing_ir.id
            )
            if latest_approval:
                date_expected_return = convert_to_full_month_format(latest_approval.date_expected_return)
                data["date_expected_return"] = date_expected_return
        action_required_by_rp = render_template_with_data(
            "ACTION_REQUIRED_BY_RP",
            ACTION_REQUIRED_BY_RP,
            data,
        )
        self.data["action_required_by_rp"] = action_required_by_rp
        return self

    def build_requirement_details(self):
        """Build the requirement details for the inspection record."""
        result = []
        if not self.requirements:
            self.requirements = InspectionRequirementModel.get_by_inspection_id(
                self.inspection.id
            )
        result = ServiceUtils.get_formatted_requirement_details(
            self.requirements, self.ir_status, photo_required=True
        )
        self.data["requirement_details"] = result
        return self

    def build_regulatory_considerations(self):
        """Build the regulatory considerations for the inspection record."""
        if not self.requirements:
            self.requirements = InspectionRequirementModel.get_by_inspection_id(
                self.inspection.id
            )
        # There will be only one regulatory consideration possible for an inspection
        regulatory_consideration = next(
            (
                req
                for req in self.requirements
                if req.req_type == InspectionRequirementTypeEnum.REG
            ),
            None,
        )
        if regulatory_consideration:
            photos = []
            figures = []
            photos, figures = ServiceUtils.get_photos_and_figures(
                regulatory_consideration.id
            )
            self.data["regulatory_consideration"] = {
                "findings": regulatory_consideration.findings,
                "photos": photos,
                "figures": figures,
            }
        return self

    def build(self):
        """Return the final object."""
        return self.data

    def _generate_enforcement_summary_lines_for_special_actions(
        self, action, ir_status_id
    ):
        """Generate enforcement summary lines for special actions."""
        from compliance_api.models.inspection import InspectionRequirement as InspectionRequirementModel

        object_map = {
            EnforcementActionOptionEnum.ORDER: {
                "template": "ENFORCEMENT_SUMMARY.ORDER",
                "template_data": ENFORCEMENT_SUMMARY.get("ORDER"),
                "map_model": OrderInspectionRequirementMapModel,
                "foreign_key": "order_id",
            },
            EnforcementActionOptionEnum.WARNING_LETTER: {
                "template": "ENFORCEMENT_SUMMARY.WARNING_LETTER",
                "template_data": ENFORCEMENT_SUMMARY.get("WARNING_LETTER"),
                "map_model": WarningLetterInspectionRequirementMapModel,
                "foreign_key": "warning_letter_id",
            },
            EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION: {
                "template": "ENFORCEMENT_SUMMARY.ADMINISTRATIVE_PENALTY",
                "template_data": ENFORCEMENT_SUMMARY.get("ADMINISTRATIVE_PENALTY"),
                "map_model": AdministrativePenaltyInspectionRequirementMapModel,
                "foreign_key": "administrative_penalty_id",
            },
        }

        results = []

        # Get items based on action type
        if action == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION:
            items = AdministrativePenaltyModel.get_by_inspection_id(self.inspection.id)
        elif action == EnforcementActionOptionEnum.WARNING_LETTER:
            items = WarningLetterModel.get_by_inspection_id(self.inspection.id)
        elif action == EnforcementActionOptionEnum.ORDER:
            items = OrderModel.get_by_inspection_id(self.inspection.id)
            if items:
                items = [
                    item for item in items
                    if item.order_replace_status == OrderReplaceStatusEnum.ORIGINAL
                ]
            if ir_status_id == IRStatusEnum.PRELIMINARY.value:
                items = [
                    item for item in items
                    if item.order_progress == OrderProgressEnum.ISSUED
                ]

        if not items:
            return []

        if not self.data.get("project_details"):
            self.build_project_details()

        # Batch fetch all requirement maps at once
        item_ids = [item.id for item in items]
        map_model = object_map[action]["map_model"]
        foreign_key = object_map[action]["foreign_key"]

        # Query with prefetching
        all_requirement_maps = (
            map_model.query
            .filter(
                getattr(map_model, foreign_key).in_(item_ids),
                map_model.is_deleted.is_(False),
                map_model.is_active.is_(True),
            )
            .options(
                joinedload(map_model.inspection_requirement)
                .joinedload(InspectionRequirementModel.requirement_source_details)
                .joinedload(InspectionReqSourceDetail.requirement_source),
                joinedload(map_model.inspection_requirement)
                .joinedload(InspectionRequirementModel.agency)
            )
            .all()
        )

        # Group maps by item ID for lookup
        maps_by_item_id = {}
        for req_map in all_requirement_maps:
            item_id = getattr(req_map, foreign_key)
            if item_id not in maps_by_item_id:
                maps_by_item_id[item_id] = []
            maps_by_item_id[item_id].append(req_map)

        # Process without additional queries
        for item in items:
            requirement_maps = maps_by_item_id.get(item.id, [])
            if not requirement_maps:
                continue

            requirements = [req_map.inspection_requirement for req_map in requirement_maps]

            grouped_requirements = {}
            sort_order_line = []

            for requirement in requirements:
                if len(requirement.requirement_source_details) == 0:
                    raise UnprocessableEntityError(
                        f"Requirement {requirement.sort_order} doesn't have any requirement source details"
                    )
                data_to_be_rendered = self._get_basic_data_for_enforcement_summary(
                    requirement
                )
                req_source_name = data_to_be_rendered["req_source_name"]
                number = data_to_be_rendered["number"]
                req_sort_order = data_to_be_rendered["req_sort_order"]

                if req_source_name not in grouped_requirements:
                    grouped_requirements[req_source_name] = []
                grouped_requirements[req_source_name].append({"number": number})
                sort_order_line.append(f"Requirement {req_sort_order}")

            condition_lines = []
            for source_name, reqs in grouped_requirements.items():
                valid_numbers = [
                    req["number"] for req in reqs if req["number"] is not None
                ]
                if valid_numbers:
                    numbers = ", ".join(valid_numbers)
                    condition_lines.append(f" {numbers} of {source_name}")
            data_to_be_rendered["condition_lines"] = condition_lines
            data_to_be_rendered["sort_order_line"] = ", ".join(sort_order_line)

            if action == EnforcementActionOptionEnum.ORDER:
                data_to_be_rendered["order_no"] = ServiceUtils.strip_project_code(
                    item.order_number
                )
                data_to_be_rendered["section_no"] = item.section.name
                data_to_be_rendered["act_year"] = item.section.act
            elif action == EnforcementActionOptionEnum.WARNING_LETTER:
                data_to_be_rendered["warning_letter_no"] = (
                    ServiceUtils.strip_project_code(item.warning_letter_number)
                )

            results.append(
                render_template_with_data(
                    object_map[action]["template"],
                    object_map[action]["template_data"],
                    data_to_be_rendered,
                )
            )

        return results

    def _get_basic_data_for_enforcement_summary(self, requirement):
        """Get the basic data for enforcement summary."""
        first_req_detail = requirement.requirement_source_details[0]
        number = ServiceUtils.get_requirement_source_number_field(first_req_detail)
        req_source_name = first_req_detail.requirement_source.name
        #  Build the project details if not already built
        if self.data.get("project_details", None) is None:
            self.build_project_details()
        regulated_party = self.data["project_details"].get("proponent")
        eac = self.data["project_details"].get("eac_certificate")
        data_to_be_rendered = {
            "regulated_party": regulated_party,
            "number": number,
            "req_source_name": req_source_name,
            "eac": eac,
            "req_sort_order": requirement.sort_order,
            "act": "Environmental Assessment Act",
            "act_year": "2018",
        }
        return data_to_be_rendered

    def _get_approval(self):
        """Get the latest approval for the inspection record and the inspection record."""
        inspection_record = self.existing_ir
        if inspection_record is None:
            inspection_record = InspectionRecordModel.get_by_inspection_id(
                self.inspection.id
            )
        if inspection_record:
            approvals = (
                self.approvals
                or InspectionRecordApprovalModel.get_approvals_by_ir(
                    inspection_record.id
                )
            )
            return approvals, inspection_record
        return [], None

    def _generate_enforcement_summary_lines(
        self,
        action: EnforcementActionOptionEnum,
        requirement: InspectionRequirementModel,
    ):
        """Create the enforcement summary lines."""
        if action == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION:
            return render_template_with_data(
                "ENFORCEMENT_SUMMARY.ADMINISTRATIVE_PENALTY",
                ENFORCEMENT_SUMMARY.get("ADMINISTRATIVE_PENALTY"),
                {"req_sort_order": requirement.sort_order},
            )
        if requirement.requirement_source_details:
            data_to_be_rendered = self._get_basic_data_for_enforcement_summary(
                requirement
            )
            if action == EnforcementActionOptionEnum.NOTICE_OF_NON_COMPLIANCE:
                return render_template_with_data(
                    "ENFORCEMENT_SUMMARY.NOTICE_OF_NON_COMPLIANCE",
                    ENFORCEMENT_SUMMARY.get("NOTICE_OF_NON_COMPLIANCE"),
                    data_to_be_rendered,
                )
            if action == EnforcementActionOptionEnum.REFERRAL_TO_ANOTHER_AGENCY:
                data_to_be_rendered["agency_name"] = requirement.agency.name
                return render_template_with_data(
                    "ENFORCEMENT_SUMMARY.AGENCY",
                    ENFORCEMENT_SUMMARY.get("AGENCY"),
                    data_to_be_rendered,
                )
        return None

    def _get_requirements_by_enforcement_action(self, requirements):
        """Group requirements by enforcement action ID."""
        grouped_requirements = {}

        for requirement in requirements:
            # Get enforcement actions for this requirement
            enforcement_actions = requirement.sorted_enforcement_actions

            if enforcement_actions:
                for enforcement_action in enforcement_actions:
                    enforcement_id = enforcement_action.enforcement_action_id
                    if enforcement_id not in grouped_requirements:
                        grouped_requirements[enforcement_id] = []
                    grouped_requirements[enforcement_id].append(requirement)

        return dict(sorted(grouped_requirements.items()))
