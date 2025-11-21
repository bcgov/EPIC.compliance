"""Service for inspection requirement operations."""

# pylint: disable=too-many-lines

from datetime import datetime
from io import BytesIO
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import String, and_, case, cast, func, nullslast, or_
from sqlalchemy.orm import aliased, selectinload

from compliance_api.exceptions import BadRequestError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models import Appendix as AppendixModel
from compliance_api.models import EnforcementActionOption as EnforcementActionOptionModel
from compliance_api.models import EnforcementActionOptionEnum, ImageTypeEnum
from compliance_api.models import Inspection as InspectionModel
from compliance_api.models import InspectionReqDetailDocument as InspectionReqDetailDocumentModel
from compliance_api.models import InspectionReqEnforcementMap as InspectionReqEnforcementMapModel
from compliance_api.models import InspectionReqSourceDetail as InspectionReqSourceDetailModel
from compliance_api.models import InspectionRequirement as InspectionRequirementModel
from compliance_api.models import InspectionRequirementImage as InspectionRequirementImageModel
from compliance_api.models import InspectionStatusEnum
from compliance_api.models import WarningLetter as WarningLetterModel
from compliance_api.models import WarningLetterProgressEnum
from compliance_api.models.administrative_penalty import AdministrativePenalty as AdministrativePenaltyModel
from compliance_api.models.administrative_penalty import \
    AdministrativePenaltyInspectionRequirementMap as AdministrativePenaltyInspectionRequirementMapModel
from compliance_api.models.administrative_penalty import ReferralStatusEnum
from compliance_api.models.charge_recommendation import ChargeRecommendation as ChargeRecommendationModel
from compliance_api.models.charge_recommendation import \
    ChargeRecommendationInspectionRequirementMap as ChargeRecommendationInspectionRequirementMapModel
from compliance_api.models.charge_recommendation import ChargeRecommendationStatusEnum
from compliance_api.models.compliance_finding import ComplianceFindingOption as ComplianceFindingOptionModel
from compliance_api.models.db import db, session_scope
from compliance_api.models.inspection.inspection_req_detail_doc_image import \
    InspectionRequirementDetailDocImage as InspectionReqDetailDocImageModel
from compliance_api.models.inspection.inspection_req_detail_image import \
    InspectionRequirementDetailImage as InspectionReqDetailImageModel
from compliance_api.models.inspection_record import InspectionRecord as InspectionRecordModel
from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models.order import OrderProgressEnum, OrderReplaceStatusEnum, OrderStatusEnum
from compliance_api.models.requirement_source import RequirementSource as RequirementSourceOptionModel
from compliance_api.models.restorative_justice import RestorativeJustice as RestorativeJusticeModel
from compliance_api.models.restorative_justice import \
    RestorativeJusticeInspectionRequirementMap as RestorativeJusticeInspectionRequirementMapModel
from compliance_api.models.restorative_justice import RestorativeJusticeStatusEnum
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.models.topic import Topic as TopicModel
from compliance_api.models.violation_ticket import ViolationTicket as ViolationTicketModel
from compliance_api.models.violation_ticket import \
    ViolationTicketInspectionRequirementMap as ViolationTicketInspectionRequirementMapModel
from compliance_api.models.violation_ticket import ViolationTicketStatusEnum
from compliance_api.models.warning_letter import \
    WarningLetterInspectionRequirementMap as WarningLetterInspectionRequirementMapModel
from compliance_api.models.warning_letter import WarningLetterStatusEnum
from compliance_api.schemas.inspection_requirement_grid import InspectionRequirementGridItemSchema
from compliance_api.services.document_service.doc_service import DocService
from compliance_api.services.document_service.doc_service_enum import ActionOnFileEnum
from compliance_api.utils.sql_alchemy_utils import null_if_empty

from .service_utils import ServiceUtils


class InspectionRequirementService:
    """Service for inspection requirement operations."""

    @classmethod
    def get_all_inspection_requirements(cls, args):
        """Get all inspection requirements with filtering and pagination."""
        paginated_query, total_count = _build_inspection_requirements_query(
            args, enable_pagination=True
        )
        query_results = paginated_query.all()

        # Process results
        processed_requirements = _process_inspection_requirement_query_results(
            query_results
        )
        # Create final formatted response
        requirement_details = _make_requirement_detail_object(processed_requirements)
        return requirement_details, total_count

    @classmethod
    def generate_inspection_requirements_excel(cls, args):
        """Generate inspection requirements excel."""
        # Get and process query results
        paginated_query = _build_inspection_requirements_query(
            args, enable_pagination=False
        )
        query_results = paginated_query.all()
        processed_requirements = _process_inspection_requirement_query_results(
            query_results
        )

        # Convert to DataFrame
        requirement_details = _make_requirement_detail_object(processed_requirements)
        requirements_data = InspectionRequirementGridItemSchema(many=True).dump(
            requirement_details
        )
        data_frame = pd.json_normalize(requirements_data)

        # Create Excel file
        return _create_excel_from_dataframe(data_frame)

    @classmethod
    def get_all(cls, inspection_id):
        """Get all requirements by inspection id."""
        ServiceUtils.inspection_exist_check(inspection_id)
        return InspectionRequirementModel.get_by_inspection_id(inspection_id)

    @classmethod
    def get_by_id(cls, inspection_id, requirement_id):
        """Get inspection requirement by id."""
        ServiceUtils.inspection_exist_check(inspection_id)
        return InspectionRequirementModel.find_by_id(requirement_id)

    @classmethod
    def create(cls, inspection_id, requirement_data):
        """Create inspection requirement."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.inspection_status_check(inspection)
        ServiceUtils.access_check_update_for_inspection(inspection)
        requirements = InspectionRequirementModel.get_by_inspection_id(inspection_id)
        requirement_obj = _create_requirement_obj(inspection_id, requirement_data)
        requirement_obj["sort_order"] = len(requirements) + 1
        with session_scope() as session:
            created_requirement = InspectionRequirementModel.create_requirement(
                requirement_obj, session
            )
            _create_update_source_details_nd_docs(
                inspection, created_requirement.id, requirement_data, session
            )
            cls.insert_or_update_enforcements(
                created_requirement.id,
                requirement_data.get("enforcement_action_ids", []),
                session,
            )
            #  inserting photos
            created_photos = _insert_or_update_images(
                requirement_id=created_requirement.id,
                images=requirement_data.get("photos", []),
                image_type=ImageTypeEnum.PHOTO,
                session=session,
            )
            created_figures = _insert_or_update_images(
                requirement_id=created_requirement.id,
                images=requirement_data.get("figures", []),
                image_type=ImageTypeEnum.FIGURE,
                session=session,
            )
            _update_the_findigs_by_images(
                photos=created_photos,
                figures=created_figures,
                requirement=created_requirement,
                session=session,
            )
        return created_requirement

    @classmethod
    def update(cls, inspection_id, requirement_id, requirement_data):
        """Update inspection requirement."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.inspection_status_check(inspection)
        _requirement_check(requirement_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        requirement_obj = _create_requirement_obj(inspection_id, requirement_data)
        with session_scope() as session:
            _check_enforcement_action_existennce(
                requirement_data.get("enforcement_action_ids", []),
                requirement_id,
                inspection_id,
                session,
            )
            updated_requirement = InspectionRequirementModel.update_requirement(
                requirement_id, requirement_obj, session
            )
            _handle_deletion_req_detail_nd_doc(
                requirement_id, requirement_data, session
            )
            _create_update_source_details_nd_docs(
                inspection, requirement_id, requirement_data, session
            )
            cls.insert_or_update_enforcements(
                requirement_id,
                requirement_data.get("enforcement_action_ids", []),
                session,
            )
            created_photos = _insert_or_update_images(
                requirement_id=requirement_id,
                images=requirement_data.get("photos", []),
                image_type=ImageTypeEnum.PHOTO,
                session=session,
            )
            created_figures = _insert_or_update_images(
                requirement_id=requirement_id,
                images=requirement_data.get("figures", []),
                image_type=ImageTypeEnum.FIGURE,
                session=session,
            )
            _update_the_findigs_by_images(
                photos=created_photos,
                figures=created_figures,
                requirement=updated_requirement,
                session=session,
            )
        return updated_requirement

    @classmethod
    def delete(cls, inspection_id, requirement_id):
        """Delete the requirement."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.inspection_status_check(inspection)
        requirement = _requirement_check(requirement_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        _check_orders_and_warning_letters(requirement)
        with session_scope() as session:
            InspectionRequirementModel.delete_requirement(requirement_id, session)
            InspectionReqSourceDetailModel.delete_by_requirement_id(
                requirement_id, session
            )
            InspectionReqDetailDocumentModel.delete_by_requirement_id(
                requirement_id, session
            )
            # Querying the latest requirements after deleting the item
            requirements = InspectionRequirementModel.get_by_inspection_id(
                inspection_id
            )
            cls.insert_or_update_enforcements(
                requirement_id, enforcement_ids=[], session=session
            )
            _update_sort_order_subsequent(requirements)

    @classmethod
    def update_sort_order(cls, inspection_id, requirement_id, sort_order_data):
        """Update the sort order of the inspection requirement."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.inspection_status_check(inspection)
        requirement = _requirement_check(requirement_id)
        ServiceUtils.access_check_update_for_inspection(inspection)

        new_sort_order = sort_order_data.get("order")
        requirements = InspectionRequirementModel.get_by_inspection_id(inspection_id)
        if new_sort_order > len(requirements):
            raise BadRequestError(
                f"Invaid order. The order should be less than or equal to {len(requirements)}"
            )
        del requirements[requirement.sort_order - 1]
        requirements.insert(new_sort_order - 1, requirement)
        _update_sort_order_subsequent(requirements, commit=True)

    @classmethod
    def insert_or_update_enforcements(
        cls, requirement_id: int, enforcement_ids: list[int], session=None
    ):
        """Insert/Update enforcement_ids associated with a given requirement."""
        if enforcement_ids is not None:
            existing_enforecements = (
                InspectionReqEnforcementMapModel.get_all_by_requirement_id(
                    requirement_id
                )
            )
            existing_enf_ids = {
                enf.enforcement_action_id for enf in existing_enforecements
            }

            new_enf_ids = set(enforcement_ids)
            enf_ids_to_be_deleted = existing_enf_ids.difference(new_enf_ids)
            enf_ids_to_be_added = new_enf_ids.difference(existing_enf_ids)
            if enf_ids_to_be_deleted:
                InspectionReqEnforcementMapModel.bulk_delete(
                    requirement_id, list(enf_ids_to_be_deleted), session
                )
            if enf_ids_to_be_added:
                InspectionReqEnforcementMapModel.bulk_insert(
                    requirement_id, list(enf_ids_to_be_added), session
                )

    @classmethod
    def get_all_images(cls, inspection_id, requirement_id, image_type: ImageTypeEnum):
        """Get all photos."""
        ServiceUtils.inspection_exist_check(inspection_id)
        _requirement_check(requirement_id)
        images = InspectionRequirementImageModel.find_all_images(
            requirement_id=requirement_id, image_type=image_type
        )
        images = _set_signed_url(images)
        return images

    @classmethod
    def get_all_images_by_inspection(cls, inspection_id):
        """Get all images per inspection."""
        ServiceUtils.inspection_exist_check(inspection_id)
        images = InspectionRequirementImageModel.get_all_images_by_inspection(
            inspection_id
        )
        images = _set_signed_url(images)
        return images

    @classmethod
    def get_all_requirement_detail_images(cls, inspection_id, requirement_id):
        """Get all images for a requirement source detail."""
        ServiceUtils.inspection_exist_check(inspection_id)
        _requirement_check(requirement_id)
        images = InspectionReqDetailImageModel.find_all_req_detail_images_by_req(
            requirement_id
        )
        images = _set_signed_url(images)
        return images

    @classmethod
    def get_all_requirement_detail_doc_images(cls, inspection_id, requirement_id):
        """Get all images for requirement detail documents by requirement_id."""
        ServiceUtils.inspection_exist_check(inspection_id)
        _requirement_check(requirement_id)
        images = InspectionReqDetailDocImageModel.find_all_req_detail_doc_images_by_req(
            requirement_id
        )
        images = _set_signed_url(images)
        return images

    @classmethod
    def delete_image(cls, inspection_id, requirement_id, relative_url, image_type):
        """Delete image."""
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.inspection_status_check(inspection)
        _requirement_check(requirement_id)
        image = InspectionRequirementImageModel.find_image_by_url(
            requirement_id, relative_url, image_type
        )
        if not image:
            raise UnprocessableEntityError(
                f"No {image_type.value} found for the given relative url"
            )
        # Delete from cloud storage and database
        delete_response = _delete_image_from_storage_and_db(
            image, InspectionRequirementImageModel
        )
        return delete_response

    @classmethod
    def update_requirements(cls, inspection_id: int, requirements_data: List[dict]):
        """Update multiple inspection requirements and their images.

        Args:
            inspection_id (int): The ID of the inspection
            requirements_data (List[dict]): List of requirement updates

        Raises:
            ResourceNotFoundError: If inspection or requirement not found
        """
        # Verify inspection exists and check access
        inspection = ServiceUtils.inspection_exist_check(inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)

        with session_scope() as session:
            for req_data in requirements_data:
                requirement_id = req_data["requirement_id"]
                findings = req_data.get("findings")
                images = req_data.get("images", [])

                # Update requirement findings
                requirement = _requirement_check(requirement_id)
                if requirement.inspection_id != inspection_id:
                    raise ResourceNotFoundError(
                        f"Requirement with id {requirement_id} not found for inspection {inspection_id}"
                    )

                # Update requirement findings using model method
                InspectionRequirementModel.update_requirement(
                    requirement_id, {"findings": findings}, session
                )

                # Update image sort orders using model method
                for image_data in images:
                    image = InspectionRequirementImageModel.query.filter_by(
                        id=image_data["image_id"],
                        requirement_id=requirement_id,
                        is_deleted=False,
                    ).first()

                    if not image:
                        raise ResourceNotFoundError(
                            f"Image with id {image_data['image_id']} not found for requirement {requirement_id}"
                        )

                    InspectionRequirementImageModel.update_image(
                        image_data["image_id"],
                        {"sort_order": image_data["sort_order"]},
                        session,
                    )


def _create_excel_from_dataframe(data_frame):
    """Create Excel file from DataFrame with proper column formatting."""
    # Print columns for debugging
    print(f"Available columns: {data_frame.columns.tolist()}")

    # Get existing columns and headers
    existing_columns, headers = _get_excel_columns_and_headers(data_frame)

    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data_frame.to_excel(
            writer,
            sheet_name="Inspection Requirements",
            columns=existing_columns,
            header=headers,
            index=False,
        )
    output.seek(0)
    return output.getvalue()


def _get_excel_columns_and_headers(data_frame):
    """Get existing columns and their headers for Excel export."""
    preferred_columns = [
        ("topic.name", "Topic"),
        ("summary", "Summary"),
        ("compliance_finding.name", "Compliance Finding"),
        ("enforcement_action.name", "Enforcement Action"),
        ("enforcement_number", "Enforcement Document #"),
        ("status.name", "Enforcement Status"),
        ("requirement_number", "Condition #"),
        ("requirement_source.name", "Requirement Source"),
        ("ir_number", "IR Number"),
        ("date_issued", "Date Issued"),
        ("primary_officer.name", "Primary Officer"),
        ("project.name", "Project"),
        ("inspection_status.name", "Inspection Status"),
    ]

    # Filter for columns that actually exist in the DataFrame
    existing_columns = []
    headers = []
    for col, header in preferred_columns:
        if col in data_frame.columns:
            existing_columns.append(col)
            headers.append(header)

    return existing_columns, headers


def _get_first_requirement_source_sub_query():
    """Get first requirement source sub query."""
    return (
        db.session.query(
            InspectionReqSourceDetailModel.requirement_id,
            func.min(InspectionReqSourceDetailModel.id).label("min_id"),
        )
        .filter(
            InspectionReqSourceDetailModel.is_active.is_(True),
            InspectionReqSourceDetailModel.is_deleted.is_(False),
        )
        .group_by(InspectionReqSourceDetailModel.requirement_id)
        .subquery("first_requirement_source")
    )


def _get_requirement_order_sub_query():
    """Get requirement order sub query."""
    return (
        db.session.query(
            OrderInspectionRequirementMapModel.inspection_requirement_id,
            OrderInspectionRequirementMapModel.order_id,
        )
        .join(
            OrderModel,
            OrderModel.id == OrderInspectionRequirementMapModel.order_id,
        )
        .filter(
            OrderInspectionRequirementMapModel.is_active.is_(True),
            OrderInspectionRequirementMapModel.is_deleted.is_(False),
            OrderModel.is_active.is_(True),
            OrderModel.is_deleted.is_(False),
            OrderModel.order_replace_status == OrderReplaceStatusEnum.ORIGINAL,
        )
        .subquery("requirement_order")
    )


def _get_requirement_warning_letter_sub_query():
    """Get requirement warning letter sub query."""
    return (
        db.session.query(
            WarningLetterInspectionRequirementMapModel.inspection_requirement_id,
            WarningLetterInspectionRequirementMapModel.warning_letter_id,
        )
        .join(
            WarningLetterModel,
            WarningLetterModel.id
            == WarningLetterInspectionRequirementMapModel.warning_letter_id,
        )
        .filter(
            WarningLetterInspectionRequirementMapModel.is_active.is_(True),
            WarningLetterInspectionRequirementMapModel.is_deleted.is_(False),
            WarningLetterModel.is_active.is_(True),
            WarningLetterModel.is_deleted.is_(False),
        )
        .subquery("requirement_warning_letter")
    )


def _get_requirement_violation_ticket_sub_query():
    """Get requirement violation ticket sub query."""
    return (
        db.session.query(
            ViolationTicketInspectionRequirementMapModel.inspection_requirement_id,
            ViolationTicketInspectionRequirementMapModel.violation_ticket_id,
        )
        .join(
            ViolationTicketModel,
            ViolationTicketModel.id
            == ViolationTicketInspectionRequirementMapModel.violation_ticket_id,
        )
        .filter(
            ViolationTicketInspectionRequirementMapModel.is_active.is_(True),
            ViolationTicketInspectionRequirementMapModel.is_deleted.is_(False),
            ViolationTicketModel.is_active.is_(True),
            ViolationTicketModel.is_deleted.is_(False),
        )
        .subquery("requirement_violation_ticket")
    )


def _get_requirement_admin_penalty_sub_query():
    """Get requirement administrative penalty sub query."""
    return (
        db.session.query(
            AdministrativePenaltyInspectionRequirementMapModel.inspection_requirement_id,
            AdministrativePenaltyInspectionRequirementMapModel.administrative_penalty_id,
        )
        .join(
            AdministrativePenaltyModel,
            AdministrativePenaltyModel.id
            == AdministrativePenaltyInspectionRequirementMapModel.administrative_penalty_id,
        )
        .filter(
            AdministrativePenaltyInspectionRequirementMapModel.is_active.is_(True),
            AdministrativePenaltyInspectionRequirementMapModel.is_deleted.is_(False),
            AdministrativePenaltyModel.is_active.is_(True),
            AdministrativePenaltyModel.is_deleted.is_(False),
        )
        .subquery("requirement_admin_penalty")
    )


def _get_requirement_charge_rec_sub_query():
    """Get requirement charge recommendation sub query."""
    return (
        db.session.query(
            ChargeRecommendationInspectionRequirementMapModel.inspection_requirement_id,
            ChargeRecommendationInspectionRequirementMapModel.charge_recommendation_id,
        )
        .join(
            ChargeRecommendationModel,
            ChargeRecommendationModel.id
            == ChargeRecommendationInspectionRequirementMapModel.charge_recommendation_id,
        )
        .filter(
            ChargeRecommendationInspectionRequirementMapModel.is_active.is_(True),
            ChargeRecommendationInspectionRequirementMapModel.is_deleted.is_(False),
            ChargeRecommendationModel.is_active.is_(True),
            ChargeRecommendationModel.is_deleted.is_(False),
        )
        .subquery("requirement_charge_rec")
    )


def _get_requirement_restorative_justice_sub_query():
    """Get requirement restorative justice sub query."""
    return (
        db.session.query(
            RestorativeJusticeInspectionRequirementMapModel.inspection_requirement_id,
            RestorativeJusticeInspectionRequirementMapModel.restorative_justice_id,
        )
        .join(
            RestorativeJusticeModel,
            RestorativeJusticeModel.id
            == RestorativeJusticeInspectionRequirementMapModel.restorative_justice_id,
        )
        .filter(
            RestorativeJusticeInspectionRequirementMapModel.is_active.is_(True),
            RestorativeJusticeInspectionRequirementMapModel.is_deleted.is_(False),
            RestorativeJusticeModel.is_active.is_(True),
            RestorativeJusticeModel.is_deleted.is_(False),
        )
        .subquery("requirement_restorative_justice")
    )


def _create_model_aliases():
    """Create and return all model aliases needed for the query."""
    return {
        # Core models
        "topic": aliased(TopicModel),
        "cmp_finding": aliased(ComplianceFindingOptionModel),
        "req_source_option": aliased(RequirementSourceOptionModel),
        "req": aliased(InspectionRequirementModel),
        "insp": aliased(InspectionModel),
        "enf_map": aliased(InspectionReqEnforcementMapModel),
        "insp_rec": aliased(InspectionRecordModel),
        "req_source": aliased(InspectionReqSourceDetailModel),
        "enf_action": aliased(EnforcementActionOptionModel),
        "staff": aliased(StaffUserModel),
        # Order models
        "order": aliased(OrderModel),
        "req_source_order": aliased(OrderModel),
        # Warning Letter models
        "warning_letter": aliased(WarningLetterModel),
        # Violation Ticket models
        "violation_ticket": aliased(ViolationTicketModel),
        # Administrative Penalty models
        "admin_penalty": aliased(AdministrativePenaltyModel),
        # Charge Recommendation models
        "charge_rec": aliased(ChargeRecommendationModel),
        # Restorative Justice models
        "restorative_justice": aliased(RestorativeJusticeModel),
    }


def _build_inspection_requirements_query(args, enable_pagination=True):
    """Build the query for inspection requirements.

    Args:
        args: Query arguments
        enable_pagination: Whether to enable pagination
    """
    # Get subqueries
    subqueries = {
        "first_requirement_source": _get_first_requirement_source_sub_query(),
        "requirement_order": _get_requirement_order_sub_query(),
        "requirement_warning_letter": _get_requirement_warning_letter_sub_query(),
        "requirement_violation_ticket": _get_requirement_violation_ticket_sub_query(),
        "requirement_admin_penalty": _get_requirement_admin_penalty_sub_query(),
        "requirement_charge_rec": _get_requirement_charge_rec_sub_query(),
        "requirement_restorative_justice": _get_requirement_restorative_justice_sub_query(),
    }

    # Create model aliases
    models = _create_model_aliases()

    # Build the base query with all necessary joins
    base_query = (
        db.session.query(
            models["req"],
            models["insp"].ir_number.label("ir_number"),
            models["insp_rec"].date_issued.label("date_issued"),
            models["enf_map"].enforcement_action_id.label("enforcement_action_id"),
            models["enf_action"].name.label("enforcement_action_name"),
            models["staff"].id.label("staff_id"),
            models["staff"].first_name.label("staff_first_name"),
            models["staff"].last_name.label("staff_last_name"),
            models["staff"].auth_user_guid.label("staff_auth_user_guid"),
            models["insp"].inspection_status.label("inspection_status"),
            # Individual status fields for all enforcement types
            models["order"].order_status.label("order_status"),
            models["order"].order_progress.label("order_progress"),
            models["warning_letter"].status.label("warning_letter_status"),
            models["warning_letter"].progress.label("warning_letter_progress"),
            models["violation_ticket"].status.label("violation_ticket_status"),
            models["admin_penalty"].referral_status.label("admin_penalty_status"),
            models["charge_rec"].status.label("charge_rec_status"),
            models["restorative_justice"].status.label("restorative_justice_status"),
            models["topic"].name.label("topic_name"),
            models["cmp_finding"].name.label("compliance_finding"),
            models["req_source_option"].name.label("requirement_source_option"),
            models["req_source"].section_number.label("section_number"),
            models["req_source"].condition_number.label("condition_number"),
            models["req_source"].clause_number.label("clause_number"),
            models["order"].order_number.label("order_number"),
            models["req_source_order"].order_number.label("req_order_number"),
            models["warning_letter"].warning_letter_number.label(
                "warning_letter_number"
            ),
            models["violation_ticket"].vt_number.label("violation_ticket_number"),
            models["admin_penalty"].administrative_penalty_number.label(
                "admin_penalty_number"
            ),
            models["charge_rec"].charge_recommendation_number.label(
                "charge_rec_number"
            ),
            models["restorative_justice"].restorative_justice_number.label(
                "restorative_justice_number"
            ),
        )
        .join(
            models["topic"],
            models["topic"].id == models["req"].topic_id,
        )
        .join(
            models["cmp_finding"],
            models["cmp_finding"].id == models["req"].compliance_finding_id,
        )
        .join(
            models["insp"],
            and_(
                models["req"].inspection_id == models["insp"].id,
                models["insp"].is_deleted.is_(False),
                models["insp"].is_active.is_(True),
            ),
        )
        .join(
            models["enf_map"],
            and_(
                models["req"].id == models["enf_map"].requirement_id,
                models["enf_map"].is_deleted.is_(False),
                models["enf_map"].is_active.is_(True),
            ),
        )
        .join(
            models["enf_action"],
            models["enf_map"].enforcement_action_id == models["enf_action"].id,
        )
        .join(
            models["staff"],
            models["insp"].primary_officer_id == models["staff"].id,
        )
        .outerjoin(
            models["insp_rec"],
            models["insp"].id == models["insp_rec"].inspection_id,
        )
        .outerjoin(
            subqueries["first_requirement_source"],
            models["req"].id == subqueries["first_requirement_source"].c.requirement_id,
        )
        .outerjoin(
            models["req_source"],
            and_(
                models["req_source"].requirement_id == models["req"].id,
                models["req_source"].id
                == subqueries["first_requirement_source"].c.min_id,
            ),
        )
        .join(
            models["req_source_option"],
            models["req_source"].requirement_source_id
            == models["req_source_option"].id,
        )
        .outerjoin(
            models["req_source_order"],
            and_(
                models["req_source"].order_id == models["req_source_order"].id,
                models["req_source_order"].is_deleted.is_(False),
                models["req_source_order"].is_active.is_(True),
            ),
        )
        .outerjoin(
            subqueries["requirement_order"],
            subqueries["requirement_order"].c.inspection_requirement_id
            == models["req"].id,
        )
        .outerjoin(
            models["order"],
            and_(
                models["order"].id == subqueries["requirement_order"].c.order_id,
                models["order"].is_deleted.is_(False),
                models["order"].is_active.is_(True),
            ),
        )
        .outerjoin(
            subqueries["requirement_warning_letter"],
            subqueries["requirement_warning_letter"].c.inspection_requirement_id
            == models["req"].id,
        )
        .outerjoin(
            models["warning_letter"],
            and_(
                models["warning_letter"].id
                == subqueries["requirement_warning_letter"].c.warning_letter_id,
                models["warning_letter"].is_deleted.is_(False),
                models["warning_letter"].is_active.is_(True),
            ),
        )
        .outerjoin(
            subqueries["requirement_violation_ticket"],
            subqueries["requirement_violation_ticket"].c.inspection_requirement_id
            == models["req"].id,
        )
        .outerjoin(
            models["violation_ticket"],
            and_(
                models["violation_ticket"].id
                == subqueries["requirement_violation_ticket"].c.violation_ticket_id,
                models["violation_ticket"].is_deleted.is_(False),
                models["violation_ticket"].is_active.is_(True),
            ),
        )
        .outerjoin(
            subqueries["requirement_admin_penalty"],
            subqueries["requirement_admin_penalty"].c.inspection_requirement_id
            == models["req"].id,
        )
        .outerjoin(
            models["admin_penalty"],
            and_(
                models["admin_penalty"].id
                == subqueries["requirement_admin_penalty"].c.administrative_penalty_id,
                models["admin_penalty"].is_deleted.is_(False),
                models["admin_penalty"].is_active.is_(True),
            ),
        )
        .outerjoin(
            subqueries["requirement_charge_rec"],
            subqueries["requirement_charge_rec"].c.inspection_requirement_id
            == models["req"].id,
        )
        .outerjoin(
            models["charge_rec"],
            and_(
                models["charge_rec"].id
                == subqueries["requirement_charge_rec"].c.charge_recommendation_id,
                models["charge_rec"].is_deleted.is_(False),
                models["charge_rec"].is_active.is_(True),
            ),
        )
        .outerjoin(
            subqueries["requirement_restorative_justice"],
            subqueries["requirement_restorative_justice"].c.inspection_requirement_id
            == models["req"].id,
        )
        .outerjoin(
            models["restorative_justice"],
            and_(
                models["restorative_justice"].id
                == subqueries[
                    "requirement_restorative_justice"
                ].c.restorative_justice_id,
                models["restorative_justice"].is_deleted.is_(False),
                models["restorative_justice"].is_active.is_(True),
            ),
        )
        .filter(models["req"].is_active.is_(True), models["req"].is_deleted.is_(False))
        .order_by(models["req"].id, models["enf_map"].enforcement_action_id)
        .options(
            selectinload(models["req"].requirement_source_details).selectinload(
                InspectionReqSourceDetailModel.documents
            ),
            selectinload(models["req"].enforcement_actions),
        )
    )

    # Apply filters based on query parameters
    base_query = _apply_filters(base_query, args, **models)

    # Apply pagination if requested
    if enable_pagination:
        return _apply_pagination(base_query, args, **models)
    return base_query


def _apply_requirement_filters(query, args, **kwargs):
    """Apply requirement-related filters."""
    # Topic IDs filter
    if args.get("tpc_ids"):
        query = query.filter(kwargs.get("req").topic_id.in_(args["tpc_ids"].split(",")))

    # Summary text search filter
    if args.get("summary"):
        search_term = args["summary"].lower().strip()
        query = query.filter(
            func.lower(kwargs.get("req").summary).contains(search_term)
        )

    # Compliance finding IDs filter
    if args.get("cmd_fnd_ids"):
        query = query.filter(
            kwargs.get("req").compliance_finding_id.in_(args["cmd_fnd_ids"].split(","))
        )

    # Enforcement action IDs filter
    if args.get("enf_actn_ids"):
        query = query.filter(
            kwargs.get("enf_map").enforcement_action_id.in_(
                args["enf_actn_ids"].split(",")
            )
        )

    # Requirement source IDs filter
    if args.get("req_src_ids"):
        query = query.filter(
            kwargs.get("req_source").requirement_source_id.in_(
                args["req_src_ids"].split(",")
            )
        )
    return query


def _apply_inspection_filters(query, args, **kwargs):
    """Apply inspection-related filters."""
    # IR number filter
    if args.get("ir_no") and args.get("ir_no").strip():
        query = query.filter(kwargs.get("insp").ir_number.ilike(f'%{args["ir_no"]}%'))

    # Primary officer IDs filter
    if args.get("prm_offc_ids"):
        query = query.filter(
            kwargs.get("insp").primary_officer_id.in_(args["prm_offc_ids"].split(","))
        )

    # Inspection status filter
    if args.get("insp_sts"):
        inspection_status = [st.upper().strip() for st in args["insp_sts"].split(",")]
        query = query.filter(
            kwargs.get("insp").inspection_status.in_(inspection_status)
        )

    # Project IDs filter
    if args.get("project_ids"):
        query = query.filter(
            kwargs.get("insp").project_id.in_(args["project_ids"].split(","))
        )

    # Date issued filter
    if args.get("date_issued"):
        query = query.filter(
            func.date(kwargs.get("insp_rec").date_issued) == args["date_issued"]
        )
    return query


def _get_enforcement_status_filters(enforcement_statuses, **kwargs):
    """Get enforcement status filter conditions for all enforcement types."""
    or_conditions = []

    # Define enum mappings with their model attributes
    enum_mappings = [
        (OrderStatusEnum, kwargs.get("order"), "order_status"),
        (OrderProgressEnum, kwargs.get("order"), "order_progress"),
        (WarningLetterStatusEnum, kwargs.get("warning_letter"), "status"),
        (WarningLetterProgressEnum, kwargs.get("warning_letter"), "progress"),
        (ViolationTicketStatusEnum, kwargs.get("violation_ticket"), "status"),
        (ReferralStatusEnum, kwargs.get("admin_penalty"), "referral_status"),
        (ChargeRecommendationStatusEnum, kwargs.get("charge_rec"), "status"),
        (RestorativeJusticeStatusEnum, kwargs.get("restorative_justice"), "status"),
    ]

    # Process each enum type
    for enum_class, model, attr_name in enum_mappings:
        matching_values = [
            status
            for status in enforcement_statuses
            if any(status == e.name.upper() for e in enum_class)
        ]
        if matching_values and model:
            or_conditions.append(getattr(model, attr_name).in_(matching_values))

    return or_conditions


def _apply_approval_and_source_filters(query, args, **kwargs):
    """Apply approval and source-related filters."""
    # Enforcement status filter - searches across all enforcement action status fields
    if args.get("enf_stats"):
        enforcement_statuses = [
            st.upper().strip() for st in args["enf_stats"].split(",")
        ]
        or_conditions = _get_enforcement_status_filters(enforcement_statuses, **kwargs)
        if or_conditions:
            query = query.filter(or_(*or_conditions))

    # Requirement source number filter
    if args.get("req_src_num") and args.get("req_src_num").strip():
        search_pattern = f'%{args["req_src_num"]}%'
        query = query.filter(
            or_(
                kwargs.get("req_source").section_number.ilike(search_pattern),
                kwargs.get("req_source").clause_number.ilike(search_pattern),
                kwargs.get("req_source").condition_number.ilike(search_pattern),
                kwargs.get("req_source").order.has(
                    OrderModel.order_number.ilike(search_pattern)
                ),
            )
        )

    # Enforcement number filter
    if args.get("enf_number") and args.get("enf_number").strip():
        search_pattern = f'%{args["enf_number"]}%'
        query = query.filter(
            or_(
                kwargs.get("order").order_number.ilike(search_pattern),
                kwargs.get("warning_letter").warning_letter_number.ilike(
                    search_pattern
                ),
                kwargs.get("violation_ticket").vt_number.ilike(search_pattern),
                kwargs.get("admin_penalty").administrative_penalty_number.ilike(
                    search_pattern
                ),
                kwargs.get("charge_rec").charge_recommendation_number.ilike(
                    search_pattern
                ),
                kwargs.get("restorative_justice").restorative_justice_number.ilike(
                    search_pattern
                ),
            )
        )

    return query


def _apply_filters(query, args, **kwargs):  # pylint: disable=too-many-arguments
    """Apply filters to the query based on arguments.

    Args:
        query: The SQLAlchemy query to filter
        args: Query arguments containing filter parameters
        **kwargs: Model aliases

    Returns:
        Filtered SQLAlchemy query
    """
    # Apply requirement-related filters
    query = _apply_requirement_filters(query, args, **kwargs)

    # Apply inspection-related filters
    query = _apply_inspection_filters(query, args, **kwargs)

    # Apply approval and source-related filters
    query = _apply_approval_and_source_filters(query, args, **kwargs)

    return query


def _apply_pagination(query, args, **kwargs):
    """Apply pagination to the query.

    Args:
        query: The SQLAlchemy query to paginate
        args: Query arguments containing pagination parameters
        **kwargs: Model aliases

    Returns:
        Tuple of (paginated_query, total_count)
    """
    # Extract pagination parameters
    pg_params = {
        "page": int(args.get("page_no", 1)),
        "per_page": int(args.get("page_size", 15)),
    }

    # Group core model references
    core_models = {
        "req": kwargs.get("req"),
        "enf_map": kwargs.get("enf_map"),
        "insp": kwargs.get("insp"),
        "insp_rec": kwargs.get("insp_rec"),
    }

    # Group reference data models
    reference_models = {
        "staff": kwargs.get("staff"),
        "project": kwargs.get("project"),
        "enf_action": kwargs.get("enf_action"),
        "topic": kwargs.get("topic"),
        "cmp_finding": kwargs.get("cmp_finding"),
        "req_source_option": kwargs.get("req_source_option"),
        "req_source": kwargs.get("req_source"),
        "order": kwargs.get("order"),
        "req_source_order": kwargs.get("req_source_order"),
        "warning_letter": kwargs.get("warning_letter"),
        "violation_ticket": kwargs.get("violation_ticket"),
        "admin_penalty": kwargs.get("admin_penalty"),
        "charge_rec": kwargs.get("charge_rec"),
        "restorative_justice": kwargs.get("restorative_justice"),
    }

    # Get distinct count by requirement ID and specific enforcement document
    # Include mapping table IDs to allow same requirement with multiple documents of same type
    distinct_count_query = query.with_entities(
        core_models["req"].id,
        core_models["enf_map"].enforcement_action_id,
        # Include enforcement mapping IDs to distinguish different documents
        reference_models["order"].id.label("order_id"),
        reference_models["warning_letter"].id.label("warning_letter_id"),
        reference_models["violation_ticket"].id.label("violation_ticket_id"),
        reference_models["admin_penalty"].id.label("admin_penalty_id"),
        reference_models["charge_rec"].id.label("charge_rec_id"),
        reference_models["restorative_justice"].id.label("restorative_justice_id"),
    ).distinct()
    total_count = distinct_count_query.count()

    # Create distinct query with all required columns
    # Use enforcement document IDs to allow same requirement with multiple documents
    distinct_query = query.with_entities(
        core_models["req"],
        core_models["insp"].ir_number.label("ir_number"),
        core_models["insp_rec"].date_issued.label("date_issued"),
        core_models["enf_map"].enforcement_action_id.label("enforcement_action_id"),
        reference_models["enf_action"].name.label("enforcement_action_name"),
        reference_models["staff"].id.label("staff_id"),
        reference_models["staff"].first_name.label("staff_first_name"),
        reference_models["staff"].last_name.label("staff_last_name"),
        reference_models["staff"].auth_user_guid.label("staff_auth_user_guid"),
        core_models["insp"].inspection_status.label("inspection_status"),
        # Individual status fields for all enforcement types
        reference_models["order"].order_status.label("order_status"),
        reference_models["order"].order_progress.label("order_progress"),
        reference_models["warning_letter"].status.label("warning_letter_status"),
        reference_models["warning_letter"].progress.label("warning_letter_progress"),
        reference_models["violation_ticket"].status.label("violation_ticket_status"),
        reference_models["admin_penalty"].referral_status.label("admin_penalty_status"),
        reference_models["charge_rec"].status.label("charge_rec_status"),
        reference_models["restorative_justice"].status.label(
            "restorative_justice_status"
        ),
        reference_models["topic"].name.label("topic_name"),
        reference_models["cmp_finding"].name.label("compliance_finding"),
        reference_models["req_source_option"].name.label("requirement_source_option"),
        reference_models["req_source"].section_number.label("section_number"),
        reference_models["req_source"].condition_number.label("condition_number"),
        reference_models["req_source"].clause_number.label("clause_number"),
        reference_models["order"].order_number.label("order_number"),
        reference_models["req_source_order"].order_number.label("req_order_number"),
        reference_models["warning_letter"].warning_letter_number.label(
            "warning_letter_number"
        ),
        reference_models["violation_ticket"].vt_number.label("violation_ticket_number"),
        reference_models["admin_penalty"].administrative_penalty_number.label(
            "admin_penalty_number"
        ),
        reference_models["charge_rec"].charge_recommendation_number.label(
            "charge_rec_number"
        ),
        reference_models["restorative_justice"].restorative_justice_number.label(
            "restorative_justice_number"
        ),
        # Include enforcement document IDs for distinct key
        reference_models["order"].id.label("order_id"),
        reference_models["warning_letter"].id.label("warning_letter_id"),
        reference_models["violation_ticket"].id.label("violation_ticket_id"),
        reference_models["admin_penalty"].id.label("admin_penalty_id"),
        reference_models["charge_rec"].id.label("charge_rec_id"),
        reference_models["restorative_justice"].id.label("restorative_justice_id"),
    ).distinct(
        core_models["req"].id,
        core_models["enf_map"].enforcement_action_id,
        reference_models["order"].id,
        reference_models["warning_letter"].id,
        reference_models["violation_ticket"].id,
        reference_models["admin_penalty"].id,
        reference_models["charge_rec"].id,
        reference_models["restorative_justice"].id,
    )
    subq = distinct_query.subquery("distinct_q")

    # Create final query by joining with subquery
    final_query = db.session.query(
        core_models["req"],
        subq.c.ir_number.label("ir_number"),
        subq.c.date_issued.label("date_issued"),
        subq.c.enforcement_action_id.label("enforcement_action_id"),
        subq.c.enforcement_action_name.label("enforcement_action_name"),
        subq.c.staff_id.label("staff_id"),
        subq.c.staff_first_name.label("staff_first_name"),
        subq.c.staff_last_name.label("staff_last_name"),
        subq.c.staff_auth_user_guid.label("staff_auth_user_guid"),
        subq.c.inspection_status.label("inspection_status"),
        subq.c.order_status.label("order_status"),
        subq.c.order_progress.label("order_progress"),
        subq.c.warning_letter_status.label("warning_letter_status"),
        subq.c.warning_letter_progress.label("warning_letter_progress"),
        subq.c.violation_ticket_status.label("violation_ticket_status"),
        subq.c.admin_penalty_status.label("admin_penalty_status"),
        subq.c.charge_rec_status.label("charge_rec_status"),
        subq.c.restorative_justice_status.label("restorative_justice_status"),
        subq.c.topic_name.label("topic_name"),
        subq.c.compliance_finding.label("compliance_finding"),
        subq.c.requirement_source_option.label("requirement_source_option"),
        subq.c.section_number.label("section_number"),
        subq.c.condition_number.label("condition_number"),
        subq.c.clause_number.label("clause_number"),
        subq.c.order_number.label("order_number"),
        subq.c.warning_letter_number.label("warning_letter_number"),
        subq.c.violation_ticket_number.label("violation_ticket_number"),
        subq.c.admin_penalty_number.label("admin_penalty_number"),
        subq.c.charge_rec_number.label("charge_rec_number"),
        subq.c.restorative_justice_number.label("restorative_justice_number"),
        subq.c.order_id.label("order_id"),
        subq.c.warning_letter_id.label("warning_letter_id"),
        subq.c.violation_ticket_id.label("violation_ticket_id"),
        subq.c.admin_penalty_id.label("admin_penalty_id"),
        subq.c.charge_rec_id.label("charge_rec_id"),
        subq.c.restorative_justice_id.label("restorative_justice_id"),
    ).join(
        subq,
        core_models["req"].id == subq.c.id,
    )
    # Apply sorting
    sorted_query = _apply_sort(final_query, args, subq=subq)
    # Apply pagination
    paginated_query = sorted_query.offset(
        (pg_params["page"] - 1) * pg_params["per_page"]
    ).limit(pg_params["per_page"])
    return paginated_query, total_count


def _apply_sort(query, args, subq):
    """Apply sorting to the query based on arguments."""
    if not (args.get("sort_by") and args.get("sort_order", "asc")):
        return query

    sort_field, sort_order = args["sort_by"], args["sort_order"]

    # When using DISTINCT in a query with ORDER BY, PostgreSQL requires that
    # all ORDER BY expressions must appear in the SELECT list.
    # To work around this, we need to ensure our query includes the columns we're sorting by

    # Handle special case for enforcement status which could be in multiple tables
    if sort_field == "enf_stats":
        query = _apply_enforcement_status_sort(query, subq, sort_order)
    elif sort_field == "req_src_num":
        query = _apply_requirement_source_number_sort(query, subq, sort_order)
    elif sort_field == "insp_sts":
        query = _apply_inspection_status_sort(query, subq, sort_order)
    elif sort_field == "enf_number":
        query = _apply_enforcement_number_sort(query, subq, sort_order)
    else:
        # Field mapping for simple column sorts
        field_map = {
            "tpc": "topic_name",
            "summary": "summary",
            "cmd_fnd": "compliance_finding",
            "enf_actn": "enforcement_action_name",
            "req_src": "requirement_source_option",
            "ir_no": "ir_number",
            "prm_offc": "staff_first_name",
            "project": "project_name",
            "date_issued": "date_issued",
        }

        if field_map.get(sort_field):
            sort_column = getattr(subq.c, field_map[sort_field])
            query = query.add_columns(sort_column.label(f"{sort_field}_sort"))
            query = query.order_by(
                sort_column.asc() if sort_order == "asc" else sort_column.desc()
            )

    return query


def _apply_enforcement_status_sort(query, subq, sort_order):
    """Apply enforcement status sorting logic across all enforcement action status fields."""
    # Use case statement to get the correct status based on enforcement action type
    enforcement_status_expr = case(
        (
            subq.c.enforcement_action_id == EnforcementActionOptionEnum.ORDER.value,
            cast(subq.c.order_status, String),
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.WARNING_LETTER.value,
            cast(subq.c.warning_letter_status, String),
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.VIOLATION_TICKET.value,
            cast(subq.c.violation_ticket_status, String),
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
            cast(subq.c.admin_penalty_status, String),
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value,
            cast(subq.c.charge_rec_status, String),
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.RESTORATIVE_JUSTICE.value,
            cast(subq.c.restorative_justice_status, String),
        ),
        else_="",
    ).label("enforcement_status_sort")
    query = query.add_columns(enforcement_status_expr)
    return query.order_by(
        enforcement_status_expr.asc()
        if sort_order == "asc"
        else enforcement_status_expr.desc()
    )


def _apply_requirement_source_number_sort(query, subq, sort_order):
    """Apply requirement source number sorting logic."""
    req_src_num_expr = func.coalesce(
        null_if_empty(subq.c.section_number),
        null_if_empty(subq.c.clause_number),
        null_if_empty(subq.c.condition_number),
        null_if_empty(subq.c.req_order_number),
        "",  # Provide empty string as final fallback
    ).label("req_src_num_sort")
    query = query.add_columns(req_src_num_expr)
    order_key = func.natural_sort_key(req_src_num_expr)
    return query.order_by(
        nullslast(order_key.asc())
        if sort_order == "asc"
        else nullslast(order_key.desc())
    )


def _get_enforcement_number_by_type(result):
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


def _get_enforcement_status_by_type(
    result,
):  # pylint: disable=too-many-return-statements
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
    if enforcement_action_id == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value:
        return result.charge_rec_status
    if enforcement_action_id == EnforcementActionOptionEnum.RESTORATIVE_JUSTICE.value:
        return result.restorative_justice_status
    return None


def _get_enforcement_progress_by_type(result):
    """Get the correct enforcement progress based on the enforcement action type."""
    enforcement_action_id = result.enforcement_action_id

    # Only Order and Warning Letter have progress fields
    if enforcement_action_id == EnforcementActionOptionEnum.ORDER.value:
        return result.order_progress
    if enforcement_action_id == EnforcementActionOptionEnum.WARNING_LETTER.value:
        return result.warning_letter_progress
    return None


def _apply_enforcement_number_sort(query, subq, sort_order):
    """Apply enforcement number sorting logic."""
    # Use case statement to get the correct enforcement number based on enforcement action type
    enforcement_number_expr = case(
        (
            subq.c.enforcement_action_id == EnforcementActionOptionEnum.ORDER.value,
            subq.c.order_number,
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.WARNING_LETTER.value,
            subq.c.warning_letter_number,
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.VIOLATION_TICKET.value,
            subq.c.violation_ticket_number,
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value,
            subq.c.admin_penalty_number,
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value,
            subq.c.charge_rec_number,
        ),
        (
            subq.c.enforcement_action_id
            == EnforcementActionOptionEnum.RESTORATIVE_JUSTICE.value,
            subq.c.restorative_justice_number,
        ),
        else_="",
    ).label("enforcement_number_sort")
    query = query.add_columns(enforcement_number_expr)
    order_key = func.natural_sort_key(enforcement_number_expr)
    return query.order_by(
        nullslast(order_key.asc())
        if sort_order == "asc"
        else nullslast(order_key.desc())
    )


def _apply_inspection_status_sort(query, subq, sort_order):
    """Apply inspection status sorting logic."""
    status_order = list(reversed([e.name for e in InspectionStatusEnum]))
    inspection_status_case = case(
        {status: idx for idx, status in enumerate(status_order)},
        value=cast(subq.c.inspection_status, String),
        else_=len(status_order),
    ).label("inspection_status_order")

    query = query.add_columns(inspection_status_case)
    return query.order_by(
        inspection_status_case.asc()
        if sort_order == "asc"
        else inspection_status_case.desc()
    )


def _process_inspection_requirement_query_results(query_results):
    """Process inspection requirement query results."""
    # Process results
    processed_requirements = []
    for result in query_results:
        requirement = result[0]
        item = {
            "id": requirement.id,
            "topic": requirement.topic,
            "summary": requirement.summary,
            "compliance_finding": requirement.compliance_finding,
            "sort_order": requirement.sort_order,
            "requirement_source_details": requirement.requirement_source_details,
        }
        # Add additional attributes to the requirement object
        item["ir_number"] = result.ir_number
        item["date_issued"] = result.date_issued
        # Create a simple dict with enforcement action data
        item["enforcement_action"] = {
            "id": result.enforcement_action_id,
            "name": result.enforcement_action_name,
        }

        # Add primary officer full name
        item["primary_officer"] = {
            "id": result.staff_id,
            "first_name": result.staff_first_name or "",
            "last_name": result.staff_last_name or "",
            "auth_user_guid": result.staff_auth_user_guid,
        }

        item["inspection_status"] = result.inspection_status

        # Convert enforcement status to proper object format
        raw_status = _get_enforcement_status_by_type(result)
        item["status"] = _convert_enum_to_object(raw_status) if raw_status else None

        # Convert enforcement progress to proper object format
        raw_progress = _get_enforcement_progress_by_type(result)
        item["progress"] = (
            _convert_enum_to_object(raw_progress) if raw_progress else None
        )
        item["enforcement_number"] = _get_enforcement_number_by_type(result)

        processed_requirements.append(item)
    return processed_requirements


def _convert_enum_to_object(enum_value):
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


def _convert_enum_string_to_object(enum_string, enum_class_map):
    """Convert enum string back to proper enum object structure."""
    if not enum_string:
        return None

    # Try to find the enum in any of the provided enum classes
    for enum_class in enum_class_map:
        try:
            for enum_item in enum_class:
                if enum_item.name == enum_string:
                    return {
                        "id": enum_item.name,
                        "name": enum_item.value,
                    }
        except (AttributeError, TypeError, ValueError):
            continue

    # If no enum found, return as string
    return {
        "id": enum_string,
        "name": enum_string,
    }


def _make_requirement_detail_object(requirements: list):
    """Make requirement detail object."""
    requirement_details = []
    for requirement in requirements:
        item = {
            "id": requirement["id"],
            "topic": requirement["topic"],
            "summary": requirement["summary"],
            "sort_order": requirement["sort_order"],
            "ir_number": requirement["ir_number"],
            "date_issued": (
                datetime.strftime(requirement["date_issued"], "%Y-%m-%d")
                if requirement["date_issued"]
                else None
            ),
            "compliance_finding": requirement["compliance_finding"],
            "enforcement_action": requirement["enforcement_action"],
            "primary_officer": requirement["primary_officer"],
            "inspection_status": {
                "id": requirement["inspection_status"].name,
                "name": requirement["inspection_status"].value,
            },
            "enforcement_number": requirement["enforcement_number"],
        }

        # Handle status field - already converted to proper object format in
        # _process_inspection_requirement_query_results
        status = requirement.get("status")
        item["status"] = status

        # Handle progress field - already converted to proper object format in
        # _process_inspection_requirement_query_results
        progress = requirement.get("progress")
        item["progress"] = progress
        if requirement["requirement_source_details"]:
            first_requirement_details = requirement["requirement_source_details"][0]
            number_field = ServiceUtils.get_requirement_source_number_field(
                first_requirement_details
            )
            item["requirement_number"] = (
                number_field.split(" ")[1] if number_field else None
            )
            item["requirement_source"] = first_requirement_details.requirement_source
        requirement_details.append(item)
    return requirement_details


def _validate_and_delete_enforcement_action(
    enforcement_action_config, requirement_id, inspection_id, session
):
    """
    Validate and delete a specific enforcement action type.

    @param enforcement_action_config: Configuration dict containing model, status_field,
                                    allowed_status, map_field, update_method, and error_message
    @param requirement_id: Requirement id
    @param inspection_id: Inspection id
    @param session: Database session
    """
    model = enforcement_action_config["model"]
    status_field = enforcement_action_config["status_field"]
    allowed_status = enforcement_action_config["allowed_status"]
    map_field = enforcement_action_config["map_field"]
    update_method = enforcement_action_config["update_method"]
    error_message = enforcement_action_config["error_message"]

    # Get all enforcement actions of this type for the inspection
    enforcement_actions = model.get_by_inspection_id(inspection_id)

    # Filter to only those mapped to this requirement
    requirement_enforcement_actions = [
        action
        for action in enforcement_actions
        if requirement_id
        in [map_obj.inspection_requirement_id for map_obj in getattr(action, map_field)]
    ]

    # Check if any are not in the allowed status
    if any(
        getattr(action, status_field) != allowed_status
        for action in requirement_enforcement_actions
    ):
        raise UnprocessableEntityError(error_message)

    # Delete all enforcement actions of this type for this requirement
    for action in requirement_enforcement_actions:
        update_method(action.id, {"is_deleted": True, "is_active": False}, session)


def _check_enforcement_action_existennce(
    new_enforcement_ids, requirement_id, inspection_id, session
):
    """
    Check if the corresponding enforcement action such as Order, Warning Letter, Administrative Penalty etc.

    are created. This method throws validation error when these actions are not in DRAFTING status.
    @param new_enforcement_ids: List of new enforcement action ids
    @param requirement_id: Requirement id
    @param inspection_id: Inspection id
    @param session: Database session
    """
    existing_enforcement_maps = (
        InspectionReqEnforcementMapModel.get_all_by_requirement_id(requirement_id)
    )
    existing_enforcement_ids = [
        map.enforcement_action_id for map in existing_enforcement_maps
    ]
    removed_action_ids = set(existing_enforcement_ids).difference(
        set(new_enforcement_ids)
    )

    if not removed_action_ids:
        return

    # Configuration for each enforcement action type
    enforcement_configs = {
        EnforcementActionOptionEnum.ORDER.value: {
            "model": OrderModel,
            "status_field": "order_progress",
            "allowed_status": OrderProgressEnum.DRAFTING,
            "map_field": "order_requirement_maps",
            "update_method": OrderModel.update_order,
            "error_message": "You cannot change enforcement action as order exists and is not in DRAFTING status.",
        },
        EnforcementActionOptionEnum.WARNING_LETTER.value: {
            "model": WarningLetterModel,
            "status_field": "progress",
            "allowed_status": WarningLetterProgressEnum.DRAFTING,
            "map_field": "warning_letter_requirement_maps",
            "update_method": WarningLetterModel.update_warning_letter,
            "error_message": (
                "You cannot change enforcement action as warning letter exists and is not in DRAFTING status."
            ),
        },
        EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value: {
            "model": AdministrativePenaltyModel,
            "status_field": "referral_status",
            "allowed_status": ReferralStatusEnum.DRAFTING,
            "map_field": "administrative_penalty_requirement_maps",
            "update_method": AdministrativePenaltyModel.update_administrative_penalty,
            "error_message": (
                "You cannot change enforcement action as administrative penalty exists and is not in DRAFTING status."
            ),
        },
        EnforcementActionOptionEnum.VIOLATION_TICKET.value: {
            "model": ViolationTicketModel,
            "status_field": "status",
            "allowed_status": ViolationTicketStatusEnum.ISSUED,
            "map_field": "violation_ticket_requirement_maps",
            "update_method": ViolationTicketModel.update_violation_ticket,
            "error_message": (
                "You cannot change enforcement action as violation ticket exists and is not in ISSUED status."
            ),
        },
        EnforcementActionOptionEnum.CHARGE_RECOMMENDATION.value: {
            "model": ChargeRecommendationModel,
            "status_field": "status",
            "allowed_status": ChargeRecommendationStatusEnum.DRAFTING,
            "map_field": "charge_recommendation_requirement_maps",
            "update_method": ChargeRecommendationModel.update_charge_recommendation,
            "error_message": (
                "You cannot change enforcement action as charge recommendation exists and is not in DRAFTING status."
            ),
        },
    }

    # Process each removed enforcement action
    for action_id in removed_action_ids:
        if action_id in enforcement_configs:
            _validate_and_delete_enforcement_action(
                enforcement_configs[action_id], requirement_id, inspection_id, session
            )


def _update_the_findigs_by_images(
    photos: list[InspectionRequirementImageModel],
    figures: list[InspectionRequirementImageModel],
    requirement: InspectionRequirementModel,
    session,
):
    """Update the findings by images."""
    findings = requirement.findings
    if not findings:
        return

    # Check if findings contains the data-lexical-mention attribute
    if "data-lexical-mention=" in findings:
        soup = BeautifulSoup(findings, "html.parser")
        # Find all spans with data-lexical-mention attribute set to "true"
        mention_spans = soup.find_all("span", {"data-lexical-mention": "true"})

        for span in mention_spans:
            # Find the photo/figure reference in the span
            mention = span.get("data-mention", "")

            # Check if it's a photo mention
            if mention and mention.lower().startswith("photo "):
                # Extract the photo number
                try:
                    photo_num = int(mention.split(" ")[1])
                    # Find the corresponding photo by sort_order
                    matching_photo = next(
                        (p for p in photos if p.sort_order == photo_num), None
                    )
                    if matching_photo:
                        # Update the image ID in the span
                        span["data-imageid"] = str(matching_photo.id)
                except (ValueError, IndexError):
                    # Invalid photo number format
                    pass

            # Check if it's a figure mention
            elif mention and mention.lower().startswith("figure "):
                # Extract the figure number
                try:
                    figure_num = int(mention.split(" ")[1])
                    # Find the corresponding figure by sort_order
                    matching_figure = next(
                        (f for f in figures if f.sort_order == figure_num), None
                    )
                    if matching_figure:
                        # Update the image ID in the span
                        span["data-imageid"] = str(matching_figure.id)
                except (ValueError, IndexError):
                    # Invalid figure number format
                    pass

        # Update the findings with the modified spans
        requirement.findings = str(soup)
        InspectionRequirementModel.update_requirement(
            requirement.id, {"findings": requirement.findings}, session
        )


def _set_signed_url(images):
    """Set the signed url in the image list."""
    for image in images:
        presigned_url_reponse = DocService.get_presigned_url(
            {
                "relative_url": image.relative_url,
                "action": ActionOnFileEnum.GET.value,
            }
        )
        setattr(
            image,
            "url",
            presigned_url_reponse["presigned_url"],
        )
    return images


def _delete_image_from_storage_and_db(image, model_class, session=None):
    """
    Delete image from cloud storage and database.

    Args:
        image: Image object with relative_url and id attributes
        model_class: Model class (InspectionRequirementImageModel or InspectionReqDetailImageModel)
        session: Database session (optional)

    Returns:
        Response from cloud storage deletion
    """
    # Get the presigned delete url for the file
    presigned_url_response = DocService.get_presigned_url(
        {
            "relative_url": image.relative_url,
            "action": ActionOnFileEnum.DELETE.value,
        }
    )
    presigned_delete_url = presigned_url_response.get("presigned_url")

    # Delete the actual file from cloud storage
    delete_response = requests.delete(presigned_delete_url, timeout=120)

    # Mark the deletion in the database
    model_class.delete_image(image.id, session=session)

    return delete_response


def _create_image_obj(requirement_id, img: dict, image_type):
    """Prepare the image object."""
    return {
        "requirement_id": requirement_id,
        "image_type": image_type,
        "sort_order": img.get("sort_order"),
        "original_file_name": img.get("original_file_name"),
        "date_taken": img.get("date_taken"),
        "taken_by_id": img.get("taken_by_id"),
        "taken_by_text": img.get("taken_by_text"),
        "caption": img.get("caption", None),
        "relative_url": img.get("relative_url"),
    }


def _insert_or_update_images(
    requirement_id, images: list[dict], image_type: ImageTypeEnum, session=None
):
    """Update the images."""
    # Fetch existing images from the database
    existing_images = InspectionRequirementImageModel.find_all_images(
        requirement_id=requirement_id, image_type=image_type
    )
    existing_image_ids = {img.id for img in existing_images}

    # Track incoming image IDs (existing ones)
    incoming_image_ids = {img["id"] for img in images if "id" in img}

    # DELETE: Remove images that exist in DB but are not in the new list
    images_to_delete = existing_image_ids - incoming_image_ids
    for image_id in images_to_delete:
        # Find the image object to get relative_url for cloud storage deletion
        image = next((img for img in existing_images if img.id == image_id), None)
        if image:
            _delete_image_from_storage_and_db(
                image, InspectionRequirementImageModel, session=session
            )

    # INSERT or UPDATE images while maintaining order
    inserted_images = []
    for img in images:

        if "id" in img:  # Update existing image
            InspectionRequirementImageModel.update_image(
                img["id"], img, session=session
            )
        else:  # Insert new image
            image_obj = _create_image_obj(
                requirement_id=requirement_id,
                img=img,
                image_type=image_type,
            )
            created_image = InspectionRequirementImageModel.create_image(
                image_obj=image_obj, session=session
            )
            inserted_images.append(created_image)

    return inserted_images


def _update_sort_order_subsequent(requirements, commit=False):
    """Update the new sort order for the requirement."""
    for index, req in enumerate(requirements):
        req.update({"sort_order": index + 1}, commit=commit)


def _requirement_check(requirement_id):
    """Check if requirement exists."""
    requirement = InspectionRequirementModel.find_by_id(requirement_id)
    if not requirement:
        raise ResourceNotFoundError(
            f"Inspection requirement with given ID {requirement_id} not found"
        )
    return requirement


def _validate_appendix(appendix_id, inspection):
    """Validate appendix exists and belongs to the inspection."""
    if appendix_id is not None:
        appendix = AppendixModel.find_by_id(appendix_id)
        if not appendix:
            raise ResourceNotFoundError(
                f"Appendix with given ID {appendix_id} not found"
            )
        if appendix.inspection_id != inspection.id:
            raise ResourceNotFoundError(
                f"Appendix with given ID {appendix_id} does not belong to this inspection"
            )


def _create_or_update_source_detail(
    requirement_id, source_detail_data, inspection, session
):
    """Create or update a source detail."""
    req_detail_id = source_detail_data.get("id", None)
    _validate_appendix(source_detail_data.get("appendix_id"), inspection)
    source_detail_obj = _create_requirement_source_detail_obj(
        requirement_id, source_detail_data, inspection
    )
    if not req_detail_id:
        created_source_detail = InspectionReqSourceDetailModel.create_source_detail(
            source_detail_obj, session
        )
        return created_source_detail.id

    source_detail_obj = {**source_detail_obj, "id": req_detail_id}
    InspectionReqSourceDetailModel.update_requirement_source_detail(
        req_detail_id, source_detail_obj, session
    )
    return req_detail_id


def _process_documents(req_detail_id, source_detail_data, inspection, session):
    """Process documents for a source detail."""
    for doc_detail_data in source_detail_data.get("documents", []):
        _validate_appendix(doc_detail_data.get("appendix_id"), inspection)
        doc_detail_id = doc_detail_data.get("id", None)
        doc_detail_obj = _create_requirement_source_doc_obj(
            req_detail_id, doc_detail_data
        )
        if not doc_detail_id:
            created_doc = InspectionReqDetailDocumentModel.create_doc_detail(
                doc_detail_obj, session
            )
            doc_detail_id = created_doc.id
        else:
            doc_detail_obj = {**doc_detail_obj, "id": doc_detail_id}
            InspectionReqDetailDocumentModel.update_doc_detail(
                doc_detail_id, doc_detail_obj, session
            )
        # Process images for this document
        _process_doc_images(doc_detail_id, doc_detail_data, session)


def _process_images(req_detail_id, source_detail_data, session):
    """Process images for a source detail."""
    for image_detail_data in source_detail_data.get("images", []):
        image_detail_id = image_detail_data.get("id", None)
        image_detail_obj = _create_requirement_source_image_obj(
            req_detail_id, image_detail_data
        )
        if not image_detail_id:
            InspectionReqDetailImageModel.create_image(image_detail_obj, session)
        else:
            image_detail_obj = {**image_detail_obj, "id": image_detail_id}
            InspectionReqDetailImageModel.update_image(
                image_detail_id, image_detail_obj, session
            )


def _create_update_source_details_nd_docs(
    inspection, requirement_id, requirement_data, session=None
):
    """
    Persist the source details and related document/image details.

    This function processes requirement source details and their associated documents and images.
    """
    for source_detail_data in requirement_data.get("requirement_source_details", []):
        req_detail_id = _create_or_update_source_detail(
            requirement_id, source_detail_data, inspection, session
        )
        _process_documents(req_detail_id, source_detail_data, inspection, session)
        _process_images(req_detail_id, source_detail_data, session)


def _handle_deletion_req_detail_nd_doc(
    requirement_id,
    requirement_data,
    session=None,
):
    """Handle the deletion of requirement details and related document/image entry."""
    existing_details = InspectionReqSourceDetailModel.get_all_by_requirement_id(
        requirement_id
    )

    # Group existing IDs together
    existing_ids = {
        "details": {detail.id for detail in existing_details},
        "docs": {doc.id for detail in existing_details for doc in detail.documents},
        "images": {img.id for detail in existing_details for img in detail.images},
        "images_map": {
            img.id: img for detail in existing_details for img in detail.images
        },
        "doc_images": {
            doc_img.id
            for detail in existing_details
            for doc in detail.documents
            for doc_img in doc.images
        },
        "doc_images_map": {
            doc_img.id: doc_img
            for detail in existing_details
            for doc in detail.documents
            for doc_img in doc.images
        },
    }

    # Group incoming IDs together
    incoming_ids = {
        "details": {
            detail.get("id", None)
            for detail in requirement_data.get("requirement_source_details", [])
            if detail.get("id", None) is not None
        },
        "docs": set(
            doc.get("id", None)
            for detail in requirement_data.get("requirement_source_details", [])
            for doc in detail.get("documents", [])
            if doc.get("id", None) is not None
        ),
        "images": set(
            img.get("id", None)
            for detail in requirement_data.get("requirement_source_details", [])
            for img in detail.get("images", [])
            if img.get("id", None) is not None
        ),
        "doc_images": set(
            doc_img.get("id", None)
            for detail in requirement_data.get("requirement_source_details", [])
            for doc in detail.get("documents", [])
            for doc_img in doc.get("images", [])
            if doc_img.get("id", None) is not None
        ),
    }

    # Calculate items to delete
    to_delete = {
        "details": existing_ids["details"].difference(incoming_ids["details"]),
        "docs": existing_ids["docs"].difference(incoming_ids["docs"]),
        "images": existing_ids["images"].difference(incoming_ids["images"]),
        "doc_images": existing_ids["doc_images"].difference(incoming_ids["doc_images"]),
    }

    # Perform deletions
    InspectionReqSourceDetailModel.delete_req_details_by_ids(
        to_delete["details"], session
    )
    InspectionReqDetailDocumentModel.delete_req_doc_details_by_ids(
        to_delete["docs"], session
    )
    if to_delete["images"]:
        for image_id in to_delete["images"]:
            image = existing_ids["images_map"].get(image_id)
            if image:
                _delete_image_from_storage_and_db(
                    image, InspectionReqDetailImageModel, session=session
                )
    if to_delete["doc_images"]:
        for doc_image_id in to_delete["doc_images"]:
            doc_image = existing_ids["doc_images_map"].get(doc_image_id)
            if doc_image:
                _delete_image_from_storage_and_db(
                    doc_image, InspectionReqDetailDocImageModel, session=session
                )


def _create_requirement_obj(inspection_id, requirement_data):
    """Create inspection requirement object."""
    return {
        "inspection_id": inspection_id,
        "summary": requirement_data.get("summary"),
        "topic_id": requirement_data.get("topic_id"),
        "compliance_finding_id": requirement_data.get("compliance_finding_id", None),
        "findings": requirement_data.get("findings"),
        "agency_id": requirement_data.get("agency_id", None),
        "req_type": requirement_data.get("req_type"),
    }


def _create_requirement_source_detail_obj(
    requirement_id, requirement_source_data, inspection
):
    """Create requirement source details object."""
    #  Check to see if the project is the same for the order and inspection
    _validate_order(requirement_source_data.get("order_id", None), inspection)
    return {
        "requirement_id": requirement_id,
        "requirement_source_id": requirement_source_data.get("requirement_source_id"),
        "appendix_id": requirement_source_data.get("appendix_id", None),
        "section_number": requirement_source_data.get("section_number", None),
        "condition_number": requirement_source_data.get("condition_number", None),
        "clause_number": requirement_source_data.get("clause_number", None),
        "regulation_number": requirement_source_data.get("regulation_number", None),
        "compliance_number": requirement_source_data.get("compliance_number", None),
        "source_title": requirement_source_data.get("source_title", None),
        "order_id": requirement_source_data.get("order_id", None),
        "amendment_number": requirement_source_data.get("amendment_number", None),
        "title": requirement_source_data.get("title", None),
        "description": requirement_source_data.get("description"),
    }


def _validate_order(order_id, inspection):
    """Validate order."""
    if order_id:
        order = OrderModel.find_by_id(order_id)
        inspection_on_order = ServiceUtils.inspection_exist_check(order.inspection_id)
        project_details_on_order = ServiceUtils.get_project_by_case_file_id(
            inspection_on_order.case_file_id
        )
        project_details_on_inspection = ServiceUtils.get_project_by_case_file_id(
            inspection.case_file_id
        )
        if project_details_on_order.get("project"):
            if (
                project_details_on_order.get("project").id
                != project_details_on_inspection.get("project").id
            ):
                raise UnprocessableEntityError(
                    "Project on order and inspection are different"
                )
        if project_details_on_order.get("unapproved_project"):
            if (
                project_details_on_order.get("unapproved_project").id
                != project_details_on_inspection.get("unapproved_project").id
            ):
                raise UnprocessableEntityError(
                    "Unapproved project on order and inspection are different"
                )


def _create_requirement_source_doc_obj(
    requirement_source_detail_id, requirement_source_doc_data
):
    """Create requirement source doc details object."""
    return {
        "req_detail_id": requirement_source_detail_id,
        "document_type_id": requirement_source_doc_data.get("document_type_id"),
        "appendix_id": requirement_source_doc_data.get("appendix_id", None),
        "document_title": requirement_source_doc_data.get("document_title"),
        "section_number": requirement_source_doc_data.get("section_number", None),
        "section_title": requirement_source_doc_data.get("section_title", None),
        "description": requirement_source_doc_data.get("description", None),
    }


def _create_requirement_source_image_obj(
    requirement_source_detail_id, requirement_source_image_data
):
    """Create requirement source image details object."""
    return {
        "req_detail_id": requirement_source_detail_id,
        "original_file_name": requirement_source_image_data.get("original_file_name"),
        "relative_url": requirement_source_image_data.get("relative_url"),
    }


def _create_requirement_source_doc_image_obj(
    requirement_source_doc_id, requirement_source_doc_image_data
):
    """Create requirement source document image details object."""
    return {
        "req_detail_doc_id": requirement_source_doc_id,
        "original_file_name": requirement_source_doc_image_data.get(
            "original_file_name"
        ),
        "relative_url": requirement_source_doc_image_data.get("relative_url"),
    }


def _process_doc_images(doc_detail_id, doc_detail_data, session):
    """Process images for a document detail."""
    for image_detail_data in doc_detail_data.get("images", []):
        image_detail_id = image_detail_data.get("id", None)
        image_detail_obj = _create_requirement_source_doc_image_obj(
            doc_detail_id, image_detail_data
        )
        if not image_detail_id:
            InspectionReqDetailDocImageModel.create_image(image_detail_obj, session)
        else:
            image_detail_obj = {**image_detail_obj, "id": image_detail_id}
            InspectionReqDetailDocImageModel.update_image(
                image_detail_id, image_detail_obj, session
            )


def _check_orders_and_warning_letters(requirement):
    """Check if the requirement has orders or warning letters with restricted statuses.

    Prevents deletion if:
    - Orders with progress: Deputy Review, Approved, or status: Open
    - Warning Letters with progress: Issued

    Args:
        requirement_id (int): The inspection requirement ID to check

    Raises:
        UnprocessableEntityError: If enforcement actions prevent deletion
    """
    enforcement_actions = requirement.enforcement_actions
    enforcement_action_ids = [
        action.enforcement_action_id for action in enforcement_actions
    ]
    if EnforcementActionOptionEnum.ORDER.value in enforcement_action_ids:
        order_map = OrderInspectionRequirementMapModel.get_by_requirement_id(
            requirement.id
        )
        if order_map and (
            order_map.order.order_progress
            in [OrderProgressEnum.DEPUTY_REVIEW, OrderProgressEnum.APPROVED]
            or order_map.order.order_status == OrderStatusEnum.OPEN
        ):
            raise UnprocessableEntityError("Active order found")
    if EnforcementActionOptionEnum.WARNING_LETTER.value in enforcement_action_ids:
        warning_letter_map = (
            WarningLetterInspectionRequirementMapModel.get_by_requirement_id(
                requirement.id
            )
        )
        if warning_letter_map and warning_letter_map.warning_letter.progress in [
            WarningLetterProgressEnum.ISSUED,
            WarningLetterProgressEnum.APPROVED,
            WarningLetterProgressEnum.DEPUTY_REVIEW,
        ]:
            raise UnprocessableEntityError("Active warning letter found")
