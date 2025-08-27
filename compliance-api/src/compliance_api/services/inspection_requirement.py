"""Service for inspection requirement operations."""

# pylint: disable=too-many-lines

from datetime import datetime
from io import BytesIO
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import String, and_, case, cast, func, nullslast, or_
from sqlalchemy.orm import aliased

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
from compliance_api.models.compliance_finding import ComplianceFindingOption as ComplianceFindingOptionModel
from compliance_api.models.db import db, session_scope
from compliance_api.models.inspection_record import InspectionRecord as InspectionRecordModel
from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models.order import OrderProgressEnum, OrderStatusEnum
from compliance_api.models.order_approval import OrderApproval as OrderApprovalModel
from compliance_api.models.requirement_source import RequirementSource as RequirementSourceOptionModel
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.models.topic import Topic as TopicModel
from compliance_api.models.warning_letter import \
    WarningLetterInspectionRequirementMap as WarningLetterInspectionRequirementMapModel
from compliance_api.models.warning_letter_approval import WarningLetterApproval as WarningLetterApprovalModel
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
        paginated_query, _ = _build_inspection_requirements_query(
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
        #  Get the presigned delete url for the file
        presigned_url_response = DocService.get_presigned_url(
            {
                "relative_url": image.relative_url,
                "action": ActionOnFileEnum.DELETE.value,
            }
        )
        presigned_delete_url = presigned_url_response.get("presigned_url")
        #  Delete the actual file from cloud storage
        delete_response = requests.delete(presigned_delete_url, timeout=120)
        #  Mark the deletion in the inspection_req_images table
        InspectionRequirementImageModel.delete_image(image.id)
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
        ("approval_status.name", "Approval Status"),
        ("requirement_number", "Condition #"),
        ("requirement_source.name", "Requirement Source"),
        ("ir_number", "IR Number"),
        ("date_issued", "Date Issued"),
        ("primary_officer.name", "Primary Officer"),
        ("approved_by.name", "Approved By"),
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
        "approved_by_staff": aliased(StaffUserModel),
        "order_app": aliased(OrderApprovalModel),
        "warning_app": aliased(WarningLetterApprovalModel),
        "order": aliased(OrderModel),
        "warning_letter": aliased(WarningLetterModel),
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
            models["order_app"].approval_status.label("order_approval_status"),
            models["warning_app"].approval_status.label("warning_approval_status"),
            models["approved_by_staff"].id.label("approver_id"),
            models["approved_by_staff"].first_name.label("approver_first_name"),
            models["approved_by_staff"].last_name.label("approver_last_name"),
            models["approved_by_staff"].auth_user_guid.label("approver_auth_user_guid"),
            models["topic"].name.label("topic_name"),
            models["cmp_finding"].name.label("compliance_finding"),
            models["req_source_option"].name.label("requirement_source_option"),
            models["req_source"].section_number.label("section_number"),
            models["req_source"].condition_number.label("condition_number"),
            models["req_source"].clause_number.label("clause_number"),
            models["order"].order_number.label("order_number"),
            models["warning_letter"].warning_letter_number.label(
                "warning_letter_number"
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
            models["order_app"],
            and_(
                models["order_app"].order_id
                == subqueries["requirement_order"].c.order_id,
                models["enf_map"].enforcement_action_id
                == EnforcementActionOptionEnum.ORDER.value,
                models["order_app"].is_deleted.is_(False),
                models["order_app"].is_active.is_(True),
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
            models["warning_app"],
            and_(
                models["warning_app"].warning_letter_id
                == subqueries["requirement_warning_letter"].c.warning_letter_id,
                models["enf_map"].enforcement_action_id
                == EnforcementActionOptionEnum.WARNING.value,
                models["warning_app"].is_deleted.is_(False),
                models["warning_app"].is_active.is_(True),
            ),
        )
        .outerjoin(
            models["approved_by_staff"],
            or_(
                models["approved_by_staff"].id == models["order_app"].approved_by_id,
                models["approved_by_staff"].id == models["warning_app"].approved_by_id,
            ),
        )
        .filter(models["req"].is_active.is_(True), models["req"].is_deleted.is_(False))
        .order_by(models["req"].id, models["enf_map"].enforcement_action_id)
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


def _apply_approval_and_source_filters(query, args, **kwargs):
    """Apply approval and source-related filters."""
    # Approval status filter
    if args.get("apprv_sts"):
        approval_status = [st.upper().strip() for st in args["apprv_sts"].split(",")]
        query = query.filter(
            or_(
                kwargs.get("order_app").approval_status.in_(approval_status),
                kwargs.get("warning_app").approval_status.in_(approval_status),
            )
        )

    # Requirement source number filter
    if args.get("req_src_num"):
        query = query.filter(
            or_(
                kwargs.get("req_source").section_number.in_(
                    args["req_src_num"].split(",")
                ),
                kwargs.get("req_source").clause_number.in_(
                    args["req_src_num"].split(",")
                ),
                kwargs.get("req_source").condition_number.in_(
                    args["req_src_num"].split(",")
                ),
                kwargs.get("order").order_number.in_(args["req_src_num"].split(",")),
            )
        )

    # Approver IDs filter
    if args.get("approver_ids"):
        query = query.filter(
            or_(
                kwargs.get("order_app").approved_by_id.in_(
                    args["approver_ids"].split(",")
                ),
                kwargs.get("warning_app").approved_by_id.in_(
                    args["approver_ids"].split(",")
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

    # Group approval-related models
    approval_models = {
        "order_app": kwargs.get("order_app"),
        "warning_app": kwargs.get("warning_app"),
        "approved_by_staff": kwargs.get("approved_by_staff"),
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
        "warning_letter": kwargs.get("warning_letter"),
    }

    # Get distinct count by requirement ID to avoid duplicates
    distinct_count_query = query.with_entities(
        core_models["req"].id, core_models["enf_map"].enforcement_action_id
    ).distinct()
    total_count = distinct_count_query.count()

    # Create distinct query with all required columns
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
        approval_models["order_app"].approval_status.label("order_approval_status"),
        approval_models["warning_app"].approval_status.label("warning_approval_status"),
        approval_models["approved_by_staff"].id.label("approver_id"),
        approval_models["approved_by_staff"].first_name.label("approver_first_name"),
        approval_models["approved_by_staff"].last_name.label("approver_last_name"),
        approval_models["approved_by_staff"].auth_user_guid.label(
            "approver_auth_user_guid"
        ),
        reference_models["topic"].name.label("topic_name"),
        reference_models["cmp_finding"].name.label("compliance_finding"),
        reference_models["req_source_option"].name.label("requirement_source_option"),
        reference_models["req_source"].section_number.label("section_number"),
        reference_models["req_source"].condition_number.label("condition_number"),
        reference_models["req_source"].clause_number.label("clause_number"),
        reference_models["order"].order_number.label("order_number"),
        reference_models["warning_letter"].warning_letter_number.label(
            "warning_letter_number"
        ),
    ).distinct(core_models["req"].id, core_models["enf_map"].enforcement_action_id)
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
        subq.c.order_approval_status.label("order_approval_status"),
        subq.c.warning_approval_status.label("warning_approval_status"),
        subq.c.approver_id.label("approver_id"),
        subq.c.approver_first_name.label("approver_first_name"),
        subq.c.approver_last_name.label("approver_last_name"),
        subq.c.approver_auth_user_guid.label("approver_auth_user_guid"),
        subq.c.topic_name.label("topic_name"),
        subq.c.compliance_finding.label("compliance_finding"),
        subq.c.requirement_source_option.label("requirement_source_option"),
        subq.c.section_number.label("section_number"),
        subq.c.condition_number.label("condition_number"),
        subq.c.clause_number.label("clause_number"),
        subq.c.order_number.label("order_number"),
        subq.c.warning_letter_number.label("warning_letter_number"),
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

    # Handle special case for approval status which could be in either order_app or warning_app
    if sort_field == "apprv_sts":
        return _apply_approval_status_sort(query, subq, sort_order)

    if sort_field == "req_src_num":
        return _apply_requirement_source_number_sort(query, subq, sort_order)

    if sort_field == "insp_sts":
        return _apply_inspection_status_sort(query, subq, sort_order)

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
        "approver": "approver_first_name",
    }

    if field_map.get(sort_field):
        sort_column = getattr(subq.c, field_map[sort_field])
        query = query.add_columns(sort_column.label(f"{sort_field}_sort"))
        return query.order_by(
            sort_column.asc() if sort_order == "asc" else sort_column.desc()
        )

    return query


def _apply_approval_status_sort(query, subq, sort_order):
    """Apply approval status sorting logic."""
    approval_status_expr = case(
        (
            subq.c.order_approval_status.isnot(None),
            cast(subq.c.order_approval_status, String),
        ),
        (
            subq.c.warning_approval_status.isnot(None),
            cast(subq.c.warning_approval_status, String),
        ),
        else_=None,
    ).label("approval_status_sort")
    query = query.add_columns(approval_status_expr)
    return query.order_by(
        approval_status_expr.asc()
        if sort_order == "asc"
        else approval_status_expr.desc()
    )


def _apply_requirement_source_number_sort(query, subq, sort_order):
    """Apply requirement source number sorting logic."""
    req_src_num_expr = func.coalesce(
        null_if_empty(subq.c.section_number),
        null_if_empty(subq.c.clause_number),
        null_if_empty(subq.c.condition_number),
        null_if_empty(subq.c.order_number),
        null_if_empty(subq.c.warning_letter_number),
    ).label("req_src_num_sort")
    query = query.add_columns(req_src_num_expr)
    order_key = func.natural_sort_key(req_src_num_expr)
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
        item["order_approval_status"] = result.order_approval_status
        item["warning_letter_approval_status"] = result.warning_approval_status

        # Structure approved_by as a StaffUser object from individual fields
        approved_by_id = result.approver_id
        approved_by_first_name = result.approver_first_name
        approved_by_last_name = result.approver_last_name
        approved_by_auth_guid = result.approver_auth_user_guid

        if approved_by_id:
            item["approved_by"] = {
                "id": approved_by_id,
                "first_name": approved_by_first_name or "",
                "last_name": approved_by_last_name or "",
                "auth_user_guid": approved_by_auth_guid,
            }
        else:
            item["approved_by"] = None

        processed_requirements.append(item)
    return processed_requirements


def _make_requirement_detail_object(requirements: list):
    """Make requirement detail object."""
    requirement_details = []
    for requirement in requirements:
        item = {
            "id": requirement["id"],
            "topic": requirement["topic"],
            "summary": requirement["summary"],
            "approved_by": requirement["approved_by"],
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
        }
        approval_status = (
            requirement["order_approval_status"]
            or requirement["warning_letter_approval_status"]
        )
        if approval_status:
            item["approval_status"] = {
                "id": approval_status.name,
                "name": approval_status.value,
            }
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


def _check_enforcement_action_existennce(
    new_enforcement_ids, requirement_id, inspection_id, session
):
    """
    Check if the corresponding enforcement action such as Order, Warning Letter etc.

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
    if removed_action_ids:
        # If the removed enforcement action is either ORDER or WARNING LETTER, then check if
        # the order or warning letter is in DRAFTING status. If not, throw validation error.
        # If the order or warning letter is in DRAFTING status, then delete the order or warning letter.
        if EnforcementActionOptionEnum.ORDER.value in removed_action_ids:
            orders = OrderModel.get_by_inspection_id(inspection_id)
            requirement_orders = [
                order
                for order in orders
                if requirement_id
                in [
                    order_map.inspection_requirement_id
                    for order_map in order.order_requirement_maps
                ]
            ]
            if any(
                order.order_progress != OrderProgressEnum.DRAFTING
                for order in requirement_orders
            ):
                raise UnprocessableEntityError(
                    "You cannot change enforcement action as order exists and is not in DRAFTING status."
                )
            for order in requirement_orders:
                OrderModel.update_order(
                    order.id, {"is_deleted": True, "is_active": False}, session
                )
        if EnforcementActionOptionEnum.WARNING_LETTER.value in removed_action_ids:
            warnings = WarningLetterModel.get_by_inspection_id(inspection_id)
            requirement_warnings = [
                warning
                for warning in warnings
                if requirement_id
                in [
                    warning_map.inspection_requirement_id
                    for warning_map in warning.warning_letter_requirement_maps
                ]
            ]
            if any(
                warning.progress != WarningLetterProgressEnum.DRAFTING
                for warning in requirement_warnings
            ):
                raise UnprocessableEntityError(
                    "You cannot change enforcement action as warning letter exists and is not in DRAFTING status."
                )

            for warning in requirement_warnings:
                WarningLetterModel.update_warning_letter(
                    warning.id, {"is_deleted": True, "is_active": False}, session
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


def _create_image_obj(requirement_id, img: dict, image_type):
    """Prepare the image object."""
    return {
        "requirement_id": requirement_id,
        "image_type": image_type,
        "sort_order": img.get("sort_order"),
        "original_file_name": img.get("original_file_name"),
        "date_taken": img.get("date_taken"),
        "taken_by_id": img.get("taken_by_id"),
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
        InspectionRequirementImageModel.delete_image(image_id, session=session)

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


def _create_update_source_details_nd_docs(
    inspection, requirement_id, requirement_data, session=None
):
    """
    Persist the source details and related document details.

    This function check if the id is present in the data. If it is present, no need to
    create object again.
    """
    for source_detail_data in requirement_data.get("requirement_source_details", []):
        req_detail_id = source_detail_data.get("id", None)
        appendix_id = source_detail_data.get("appendix_id", None)
        if appendix_id is not None:
            appendix = AppendixModel.find_by_id(appendix_id)
            if not appendix:
                raise ResourceNotFoundError(
                    f"Appendix with given ID {source_detail_data.get('appendix_id')} not found"
                )
            if appendix.inspection_id != inspection.id:
                raise ResourceNotFoundError(
                    f"Appendix with given ID {source_detail_data.get('appendix_id')} does not belong to this inspection"
                )
        source_detail_obj = _create_requirement_source_detail_obj(
            requirement_id, source_detail_data, inspection
        )
        if not req_detail_id:
            created_source_detail = InspectionReqSourceDetailModel.create_source_detail(
                source_detail_obj, session
            )
            req_detail_id = created_source_detail.id
        else:
            source_detail_obj = {**source_detail_obj, "id": req_detail_id}
            InspectionReqSourceDetailModel.update_requirement_source_detail(
                req_detail_id, source_detail_obj, session
            )
        for doc_detail_data in source_detail_data.get("documents", []):
            appendix_id = doc_detail_data.get("appendix_id", None)
            if appendix_id is not None:
                appendix = AppendixModel.find_by_id(appendix_id)
                if not appendix:
                    raise ResourceNotFoundError(
                        f"Appendix with given ID {doc_detail_data.get('appendix_id')} not found"
                    )
                if appendix.inspection_id != inspection.id:
                    raise ResourceNotFoundError(
                        f"Appendix with given ID {doc_detail_data.get('appendix_id')} not belong to this inspection"
                    )
            doc_detail_id = doc_detail_data.get("id", None)
            doc_detail_obj = _create_requirement_source_doc_obj(
                req_detail_id, doc_detail_data
            )
            if not doc_detail_id:
                InspectionReqDetailDocumentModel.create_doc_detail(
                    doc_detail_obj, session
                )
            else:
                doc_detail_obj = {**doc_detail_obj, "id": doc_detail_id}
                InspectionReqDetailDocumentModel.update_doc_detail(
                    doc_detail_id, doc_detail_obj, session
                )


def _handle_deletion_req_detail_nd_doc(
    requirement_id,
    requirement_data,
    session=None,
):
    """Handle the deletion of requirement details and related document entry."""
    existing_details = InspectionReqSourceDetailModel.get_all_by_requirement_id(
        requirement_id
    )
    existing_detail_ids = {detail.id for detail in existing_details}
    incoming_details_ids = {
        detail.get("id", None)
        for detail in requirement_data.get("requirement_source_details", [])
        if detail.get("id", None) is not None
    }
    incoming_doc_detail_ids = set(
        doc.get("id", None)
        for detail in requirement_data.get("requirement_source_details", [])
        for doc in detail.get("documents", [])
        if doc.get("id", None) is not None
    )
    existing_doc_detail_ids = {
        doc.id for detail in existing_details for doc in detail.documents
    }
    details_to_be_deleted = existing_detail_ids.difference(incoming_details_ids)
    doc_details_to_be_deleted = existing_doc_detail_ids.difference(
        incoming_doc_detail_ids
    )
    InspectionReqSourceDetailModel.delete_req_details_by_ids(
        details_to_be_deleted, session
    )
    InspectionReqDetailDocumentModel.delete_req_doc_details_by_ids(
        doc_details_to_be_deleted, session
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
