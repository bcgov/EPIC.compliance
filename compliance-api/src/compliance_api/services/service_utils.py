"""Some common methods which can be used across different services."""

import re

from flask import g

from compliance_api.auth import auth
from compliance_api.exceptions import PermissionDeniedError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models import Inspection as InspectionModel
from compliance_api.models import InspectionRecord as InspectionRecordModel
from compliance_api.models import InspectionRequirement as InspectionRequirementModel
from compliance_api.models import InspectionRequirementImage as InspectionRequirementImageModel
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.case_file import CaseFileOfficer as CaseFileOfficerModel
from compliance_api.models.compliance_finding import ComplianceFindingOptionEnum
from compliance_api.models.enforcement_action import EnforcementActionOption as EnforcementActionOptionModel
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection import InspectionReqSourceDetail as InspectionReqSourceDetailModel
from compliance_api.models.inspection import InspectionStatusEnum
from compliance_api.models.inspection.inspection_req_enforcement_map import \
    InspectionReqEnforcementMap as InspectionReqEnforcementMapModel
from compliance_api.models.inspection.inspection_req_image import ImageTypeEnum
from compliance_api.models.inspection.inspection_requirement import InspectionRequirementTypeEnum
from compliance_api.models.inspection_record import IRStatusEnum
from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models.order import OrderProgressEnum
from compliance_api.models.project import Project as ProjectModel
from compliance_api.models.requirement_source import RequirementSourceEnum
from compliance_api.models.unapproved_project import UnapprovedProject as UnapprovedProjectModel
from compliance_api.models.warning_letter import WarningLetter as WarningLetterModel
from compliance_api.utils.constant import UNAPPROVED_PROJECT_CODE
from compliance_api.utils.enum import PermissionEnum

from .document_service.doc_service import DocService
from .document_service.doc_service_enum import ActionOnFileEnum
from .epic_track_service.track_service import TrackService


class ServiceUtils:  # pylint: disable=too-many-public-methods
    """ServiceUtils class."""

    @staticmethod
    def access_check_update_for_inspection(inspection: dict):
        """Access check for update an inspection."""
        auth_user_guid = g.token_info["preferred_username"]
        if (
            not auth.has_permission([PermissionEnum.SUPERUSER])
            and not inspection.primary_officer.auth_user_guid == auth_user_guid
        ):
            raise PermissionDeniedError(
                "Only the Superuser or the Primary officer on this inspection can perform this operation."
            )

    @staticmethod
    def access_check_for_super_user():
        """Access check for super user."""
        if not auth.has_permission([PermissionEnum.SUPERUSER]):
            raise PermissionDeniedError(
                "Only the Superuser can perform this operation."
            )

    @staticmethod
    def inspection_exist_check(inspection_id: int):
        """Check if the inspection exist or not."""
        inspection = InspectionModel.find_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError("Inspection not found")
        return inspection

    @staticmethod
    def inspection_record_exist_check(inspection_record_id: int):
        """Check if the inspection record exist or not."""
        inspection_record = InspectionRecordModel.find_by_id(inspection_record_id)
        if not inspection_record:
            raise ResourceNotFoundError("Inspection record not found")
        return inspection_record

    @staticmethod
    def get_project_details(project_id: int, case_file_id: int, project_status_id=None):
        """
        Get project details.

        :param project_id: The project id.
        :param case_file_id: The case file id.
        :param project_status_id: The project status id.
        """
        eac_certicate = proponent = name = None
        if not project_id:
            project = UnapprovedProjectModel.get_by_case_file_id(case_file_id)
            if project:
                eac_certicate = project.authorization or "N/A"
                proponent = project.regulated_party
                name = project.name
        else:
            case_file = CaseFileModel.find_by_id(case_file_id)
            date_time = case_file.date_created
            date = date_time.date() if date_time else None
            project = TrackService.get_project_by_id(project_id, as_of_date=date)
            if project:
                eac_certicate = project.get("ea_certificate") or "N/A"
                proponent = project.get("proponent").get("name")
                name = project.get("name")
        project_status_name = None
        if project_status_id:
            project_statuses = TrackService.get_project_statuses()
            project_status = next(
                (
                    status
                    for status in project_statuses
                    if status.get("id") == project_status_id
                ),
                None,
            )
            if project_status:
                project_status_name = project_status.get("name")
        return {
            "eac_certificate": eac_certicate,
            "proponent": proponent,
            "name": name,
            "project_state": project_status_name,
            "certificate_label": (
                "Exemption Order #"
                if re.match(r"^X\d{1,3}-\d{1,3}$", eac_certicate)
                else "EA Certificate #"
            ),
            "proponent_label": (
                "Certificate Holder"
                if ServiceUtils.is_valid_certificate(eac_certicate)
                else "Regulated Party"
            ),
            "has_certificate": ServiceUtils.is_valid_certificate(eac_certicate),
        }

    @staticmethod
    def is_valid_certificate(eac_certificate: str) -> bool:
        """Check if the given certificate is valid according to the expected format and rules."""
        if not isinstance(eac_certificate, str):
            return False
        # Normalize input to uppercase for consistent checking
        cert = eac_certificate.upper()
        # Match the general format: 1–4 uppercase letters + 2 digits + '-' + 2 digits
        match = re.match(r"^([A-Z]{1,4})\d{2}-\d{2}$", cert)
        if not match:
            return False
        prefix = match.group(1)
        # Reject if the prefix is exactly 'X' (indicates exemption number)
        if prefix == "X":
            return False
        return True

    @staticmethod
    def get_formatted_requirement_details(
        requirements: [InspectionRequirementModel],
        ir_status: int = None,
        photo_required: bool = False,
    ):
        """
        Get requirement details.

        :param requirements: The requirements.
        :param photo_required: Whether to include photos.
        """
        result = []
        for requirement in requirements:
            #  Skip regulatory considerations
            if requirement.req_type == InspectionRequirementTypeEnum.REG:
                continue

            req = ServiceUtils._build_base_requirement_dict(requirement, ir_status)

            if requirement.requirement_source_details:
                ServiceUtils._process_requirement_source_details(
                    req, requirement.requirement_source_details
                )

            if photo_required:
                ServiceUtils._add_photos_and_figures(req, requirement.id)

            result.append(req)
        return result

    @staticmethod
    def _build_base_requirement_dict(requirement, ir_status):
        """Build the base requirement dictionary."""
        return {
            "requirement_id": requirement.id,
            "requirement_findings": requirement.findings,
            "requirement_summary": requirement.summary,
            "sort_order": requirement.sort_order,
            "compliance_finding": (
                requirement.compliance_finding.name
                if requirement.compliance_finding
                else None
            ),
            "enforcement_action": ServiceUtils.get_enforcement_action(
                requirement, ir_status
            ),
            "requirement_source_details": [],
            "requirement_photos": [],
            "requirement_figures": [],
        }

    @staticmethod
    def _process_requirement_source_details(req, source_details):
        """Process requirement source details and add to req dict."""
        for detail in source_details:
            requirement_source_number = (
                ServiceUtils.get_requirement_source_number_field(detail)
            )
            source_detail_dict = {
                "requirement_source_id": detail.requirement_source.id,
                "requirement_source_name": detail.requirement_source.name,
                "title": detail.title,
                "requirement_title": ServiceUtils.get_requirement_title(
                    detail, requirement_source_number
                ),
                "appendix_no": (
                    detail.appendix.appendix_no if detail.appendix else None
                ),
                "requirement_source_number": requirement_source_number,
                "requirement_source_description": detail.description,
                "requirement_documents": [],
                "requirement_source_images": [],
            }
            req["requirement_source_details"].append(source_detail_dict)

            if detail.documents:
                ServiceUtils._process_documents(source_detail_dict, detail.documents)

            if detail.images:
                ServiceUtils._process_requirement_source_images(
                    source_detail_dict, detail.images
                )

    @staticmethod
    def _process_documents(source_detail_dict, documents):
        """Process and group documents by title."""
        grouped_docs = {}
        for doc in documents:
            title = doc.document_title
            if title not in grouped_docs:
                grouped_docs[title] = {"documents": [], "document_title": title}

            # Process document images
            doc_images = []
            if doc.images:
                ServiceUtils._process_document_images(doc_images, doc.images)

            grouped_docs[title]["documents"].append(
                {
                    "appendix_no": (doc.appendix.appendix_no if doc.appendix else None),
                    "section_number": doc.section_number,
                    "section_title": doc.section_title,
                    "description": doc.description,
                    "document_images": doc_images,
                }
            )

        # Add grouped documents to requirement_documents
        for grouped_doc in grouped_docs.values():
            source_detail_dict["requirement_documents"].append(grouped_doc)

    @staticmethod
    def _process_requirement_source_images(source_detail_dict, images):
        """Process requirement source images and get presigned URLs."""
        for image in images:
            image_response = DocService.get_presigned_url(
                {
                    "relative_url": image.relative_url,
                    "action": ActionOnFileEnum.GET.value,
                }
            )
            source_detail_dict["requirement_source_images"].append(
                {
                    "original_file_name": image.original_file_name,
                    "image_url": image_response.get("presigned_url"),
                }
            )

    @staticmethod
    def _process_document_images(doc_images_list, images):
        """Process document images and get presigned URLs."""
        for image in images:
            image_response = DocService.get_presigned_url(
                {
                    "relative_url": image.relative_url,
                    "action": ActionOnFileEnum.GET.value,
                }
            )
            doc_images_list.append(
                {
                    "original_file_name": image.original_file_name,
                    "image_url": image_response.get("presigned_url"),
                }
            )

    @staticmethod
    def _add_photos_and_figures(req, requirement_id):
        """Add photos and figures to requirement dict."""
        photos, figures = ServiceUtils.get_photos_and_figures(requirement_id)
        req["requirement_photos"] = photos
        req["requirement_figures"] = figures

    @staticmethod
    def get_requirement_title(
        detail: InspectionReqSourceDetailModel, requirement_source_number: str
    ):
        """Get the requirement title in a particular format based on the requirement source."""
        #  Extracting the common element for the final output
        requirement_title = f"{requirement_source_number} of {detail.source_title}"
        if requirement_source_number is None:
            requirement_title = detail.source_title

        #  format: Section [Section #] of [Source Title]
        #  format: Condition [Condition #] of [Source Title]
        if detail.requirement_source_id in [
            RequirementSourceEnum.ACT_2002.value,
            RequirementSourceEnum.ACT_2018.value,
            RequirementSourceEnum.EAC_CERTIFICATE.value,
            RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION.value,
            RequirementSourceEnum.SCHEDULE_B.value,
            RequirementSourceEnum.OTHER.value,
            RequirementSourceEnum.EXEMPTION_ORDER.value,
        ]:
            pass
        #  format: Order [Order #]
        elif detail.requirement_source_id == RequirementSourceEnum.ORDER.value:
            requirement_title = detail.source_title
        #  format: Condition [Condition #] of [Source Title][Amendment #]
        elif detail.requirement_source_id == RequirementSourceEnum.EAC_AMENDMENT.value:
            requirement_title += f" {detail.amendment_number}"
        #  format: Section [Section #] of [Source Title][Compliance #]
        # ToDo: compliance number
        elif (
            detail.requirement_source_id
            == RequirementSourceEnum.COMPLIANCE_AGREEMENT.value
        ):
            requirement_title += f" {detail.compliance_number}"
        #  format: [Source Title],[Regulation #]
        elif detail.requirement_source_id == RequirementSourceEnum.REGULATION.value:
            requirement_title += f", {detail.regulation_number}"
        else:
            requirement_title = ""

        return requirement_title

    @staticmethod
    def get_photos_and_figures(requirement_id: int):
        """Get photos and figures for a requirement."""
        photo_list = []
        figure_list = []
        photos = InspectionRequirementImageModel.find_all_images(
            requirement_id, ImageTypeEnum.PHOTO
        )
        figures = InspectionRequirementImageModel.find_all_images(
            requirement_id, ImageTypeEnum.FIGURE
        )
        for photo in photos:
            photo_response = DocService.get_presigned_url(
                {
                    "relative_url": photo.relative_url,
                    "action": ActionOnFileEnum.GET.value,
                }
            )
            photo_list.append(
                {
                    "photo_caption": photo.caption,
                    "photo_number": photo.sort_order,
                    "photo_url": photo_response.get("presigned_url"),
                }
            )
        for figure in figures:
            figure_response = DocService.get_presigned_url(
                {
                    "relative_url": figure.relative_url,
                    "action": ActionOnFileEnum.GET.value,
                }
            )
            figure_list.append(
                {
                    "figure_caption": figure.caption,
                    "figure_number": figure.sort_order,
                    "figure_url": figure_response.get("presigned_url"),
                }
            )
        return photo_list, figure_list

    @staticmethod
    def get_enforcement_action(
        requirement: InspectionRequirementModel, ir_status: int = None
    ):
        """Get the enforcement action based on the compliance finding and ir status."""
        enforcement_actions = [
            action.enforcement_action for action in requirement.enforcement_actions
        ]
        result = None
        if not ir_status:
            return result
        if ir_status == IRStatusEnum.PRELIMINARY.value:
            if (
                requirement.compliance_finding_id
                == ComplianceFindingOptionEnum.IN.value
            ):
                result = "Not Applicable"
            else:
                if EnforcementActionOptionEnum.ORDER.value in [
                    action.id for action in enforcement_actions
                ]:
                    order_map = (
                        OrderInspectionRequirementMapModel.get_by_requirement_id(
                            requirement.id
                        )
                    )
                    if (
                        order_map
                        and order_map.order.order_progress == OrderProgressEnum.ISSUED
                    ):
                        result = "Order"
                    else:
                        result = "Not Determined"
                else:
                    result = "Not Determined"
        if ir_status == IRStatusEnum.FINAL.value:
            if (
                requirement.compliance_finding_id
                == ComplianceFindingOptionEnum.IN.value
            ):
                return enforcement_actions[0].name
            if any(
                action.id
                in [
                    EnforcementActionOptionEnum.ORDER.value,
                    EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
                    EnforcementActionOptionEnum.WARNING_LETTER.value,
                ]
                for action in enforcement_actions
            ):
                result = (
                    ", ".join([action.name for action in enforcement_actions])
                    + " - Refer to Enforcement Summary"
                )
            if any(
                action.id
                == EnforcementActionOptionEnum.REFERRAL_TO_ANOTHER_AGENCY.value
                for action in enforcement_actions
            ):
                result = (
                    " - ".join([action.name for action in enforcement_actions])
                    + " - "
                    + requirement.agency.name
                )
            if not result:
                result = "".join([action.name for action in enforcement_actions])
        return result

    @staticmethod
    def get_requirement_source_number_field(detail_obj: InspectionReqSourceDetailModel):
        """Identify the number field based on the requirement source id."""
        requirement_source = RequirementSourceEnum(detail_obj.requirement_source_id)
        section_sources = {
            RequirementSourceEnum.ACT_2002,
            RequirementSourceEnum.ACT_2018,
            RequirementSourceEnum.COMPLIANCE_AGREEMENT,
            RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION,
            RequirementSourceEnum.REGULATION,
            RequirementSourceEnum.OTHER,
        }
        condition_sources = {
            RequirementSourceEnum.EAC_AMENDMENT,
            RequirementSourceEnum.EAC_CERTIFICATE,
            RequirementSourceEnum.SCHEDULE_B,
        }
        if requirement_source in section_sources:
            return (
                f"Section {getattr(detail_obj, 'section_number')}"
                if getattr(detail_obj, "section_number")
                else None
            )
        if requirement_source in condition_sources:
            return (
                f"Condition {getattr(detail_obj, 'condition_number')}"
                if getattr(detail_obj, "condition_number")
                else None
            )
        if requirement_source == RequirementSourceEnum.ORDER:
            return (
                f"Order {getattr(detail_obj.order, 'order_number')}"
                if getattr(detail_obj.order, "order_number")
                else None
            )
        if requirement_source == RequirementSourceEnum.EXEMPTION_ORDER:
            return (
                f"Clause {getattr(detail_obj, 'clause_number')}"
                if getattr(detail_obj, "clause_number")
                else None
            )
        return None

    @staticmethod
    def get_requirement_grid_source_number_field(
        detail_obj: InspectionReqSourceDetailModel
    ):  # pylint: disable=too-many-return-statements
        """Identify the number field based on the requirement source id for the requirements grid."""
        requirement_source = RequirementSourceEnum(detail_obj.requirement_source_id)
        section_sources = {
            RequirementSourceEnum.ACT_2018,
            RequirementSourceEnum.ACT_2002,
            RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION,
            RequirementSourceEnum.COMPLIANCE_AGREEMENT,
        }
        condition_sources = {
            RequirementSourceEnum.EAC_CERTIFICATE,
            RequirementSourceEnum.SCHEDULE_B,
        }
        amendment_sources = {
            RequirementSourceEnum.EAC_AMENDMENT,
        }
        order_sources = {
            RequirementSourceEnum.ORDER,
        }
        regulation_sources = {
            RequirementSourceEnum.REGULATION,
        }
        exemption_sources = {
            RequirementSourceEnum.EXEMPTION_ORDER,
        }
        if requirement_source in section_sources:
            return getattr(detail_obj, "section_number", "")
        if requirement_source in condition_sources:
            return getattr(detail_obj, "condition_number", "")
        if requirement_source in amendment_sources:
            return getattr(detail_obj, "amendment_number", "")
        if requirement_source in order_sources:
            return getattr(detail_obj.order, "order_number", "")
        if requirement_source in regulation_sources:
            return getattr(detail_obj, "regulation_number", "")
        if requirement_source in exemption_sources:
            return getattr(detail_obj, "clause_number", "")
        return getattr(detail_obj, "section_number", "")

    @staticmethod
    def get_requirement_grid_source_name_field(detail_obj: InspectionReqSourceDetailModel):
        """Get the requirement source name."""
        if detail_obj.requirement_source_id == RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION.value:
            return "Schedule A"
        if detail_obj.requirement_source_id == RequirementSourceEnum.SCHEDULE_B.value:
            return "Schedule B"
        return detail_obj.requirement_source.name

    @staticmethod
    def check_requirement_for_enforcement_action(
        requirement_ids: list[int], enforcement_action_id: int
    ) -> None:
        """Check if all requirements have a given enforcement action.

        Args:
            requirement_ids (List[int]): List of requirement IDs to check
            enforcement_action_id (int): Enforcement action ID to check

        Raises:
            UnprocessableEntityError: If any requirement doesn't have the given enforcement action
        """
        if not requirement_ids:
            return

        valid_mappings = (
            InspectionReqEnforcementMapModel.query.filter(
                InspectionReqEnforcementMapModel.requirement_id.in_(requirement_ids),
                InspectionReqEnforcementMapModel.enforcement_action_id
                == enforcement_action_id,
            )
            .with_entities(InspectionReqEnforcementMapModel.requirement_id)
            .distinct()
            .all()
        )

        # Extract requirement IDs that have the enforcement action
        valid_req_ids = {mapping.requirement_id for mapping in valid_mappings}

        # Find requirements that don't have the enforcement action
        invalid_reqs = [
            req_id for req_id in requirement_ids if req_id not in valid_req_ids
        ]

        if invalid_reqs:
            enforcement_action = EnforcementActionOptionModel.find_by_id(
                enforcement_action_id
            )
            action_name = (
                enforcement_action.name.lower()
                if enforcement_action
                else "specified enforcement action"
            )

            raise UnprocessableEntityError(
                f"Requirements {', '.join(map(str, invalid_reqs))} do not have enforcement action as {action_name}"
            )

    @staticmethod
    def get_project_by_case_file_id(case_file_id: int):
        """Get project by case file id."""
        result = {"project": None, "unapproved_project": None}
        case_file = CaseFileModel.find_by_id(case_file_id)
        if case_file.project_id:
            result["project"] = ProjectModel.find_by_id(case_file.project_id)
        else:
            result["unapproved_project"] = UnapprovedProjectModel.get_by_case_file_id(
                case_file_id
            )
        return result

    @staticmethod
    def order_exist_check(order_id):
        """Check if order exists."""
        order = OrderModel.find_by_id(order_id)
        if not order:
            raise ResourceNotFoundError(f"Order with ID {order_id} not found")
        return order

    @staticmethod
    def warning_letter_exist_check(warning_letter_id):
        """Check if warning letter exists."""
        warning_letter = WarningLetterModel.find_by_id(warning_letter_id)
        if not warning_letter:
            raise ResourceNotFoundError(
                f"Warning letter with ID {warning_letter_id} not found"
            )
        return warning_letter

    @staticmethod
    def officer_check(officer_id, inspection: InspectionModel):
        """Check to see if the officer belong to the list of possible officers."""
        # This check is mainly for order and warning letters
        if not officer_id:
            return
        possible_officers = [inspection.primary_officer_id]
        case_file_officers = CaseFileOfficerModel.get_all_by_case_file_id(
            inspection.case_file_id
        )
        possible_officers.extend([officer.officer_id for officer in case_file_officers])
        possible_officers.extend([inspection.case_file.primary_officer_id])
        if officer_id not in possible_officers:
            raise UnprocessableEntityError(
                "Given officer doesn't belong to the list of possible officers"
            )

    @staticmethod
    def inspection_status_check(inspection: InspectionModel):
        """Check the inspection status."""
        invalid_statuses = {InspectionStatusEnum.CANCELED, InspectionStatusEnum.CLOSED}
        if inspection.inspection_status in invalid_statuses:
            raise UnprocessableEntityError(
                f"You cannot make changes to  {inspection.inspection_status.name} inspection"
            )
        return inspection

    @staticmethod
    def strip_project_code(auto_generated_number):
        """Remove the first part of a project code (e.g., 'PRGTRA_20250001_OR001' -> '20250001_OR001')."""
        if "_" in auto_generated_number:
            return auto_generated_number[
                auto_generated_number.index("_") + 1:
            ]  # Return from the first underscore onwards
        return auto_generated_number  # Return original if no underscore found

    @staticmethod
    def get_project_abbreviation(project_id: int) -> str:
        """Return the project abbreviation."""
        if project_id:
            project = TrackService.get_project_by_id(project_id)
            return project.get("abbreviation")
        return UNAPPROVED_PROJECT_CODE

    @staticmethod
    def get_enforcement_status_by_type(result):  # pylint: disable=too-many-return-statements
        """Get the correct enforcement status based on the enforcement action type."""
        enforcement_action_id = result.enforcement_action_id

        # Map enforcement action ID to the corresponding status field
        if enforcement_action_id == EnforcementActionOptionEnum.ORDER.value:
            return result.order_status
        if enforcement_action_id == EnforcementActionOptionEnum.WARNING_LETTER.value:
            return result.warning_letter_status
        if enforcement_action_id == EnforcementActionOptionEnum.VIOLATION_TICKET.value:
            return result.violation_ticket_status
        if (
            enforcement_action_id
            == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value
        ):
            return result.admin_penalty_status
        if (
            enforcement_action_id == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value
        ):
            return result.charge_rec_status
        if enforcement_action_id == EnforcementActionOptionEnum.RESTORATIVE_JUSTICE.value:
            return result.restorative_justice_status
        return None

    @staticmethod
    def convert_enum_to_object(enum_value):
        """Convert enum value to proper object format for API response."""
        if not enum_value:
            return None

        # If it's already an enum object, convert it to the expected format
        if hasattr(enum_value, "name") and hasattr(enum_value, "value"):
            return {
                "id": enum_value.name,
                "name": enum_value.value,
            }

        # If it's just a string, return it as is (shouldn't happen with our current logic)
        return {
            "id": str(enum_value),
            "name": str(enum_value),
        }

    @staticmethod
    def get_enforcement_number_by_type(result):
        """Get the correct enforcement number based on the enforcement action type."""
        enforcement_action_id = result.enforcement_action_id

        # Map enforcement action ID to the corresponding number field attribute
        enforcement_number_map = {
            EnforcementActionOptionEnum.ORDER.value: "order_number",
            EnforcementActionOptionEnum.WARNING_LETTER.value: "warning_letter_number",
            EnforcementActionOptionEnum.VIOLATION_TICKET.value: "violation_ticket_number",
            EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value: "admin_penalty_number",
            EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value: "charge_rec_number",
            EnforcementActionOptionEnum.RESTORATIVE_JUSTICE.value: "restorative_justice_number",
        }

        field_name = enforcement_number_map.get(enforcement_action_id)
        if field_name:
            return getattr(result, field_name, "") or ""
        return ""
