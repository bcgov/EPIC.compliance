"""Order Service."""

from typing import List

from compliance_api.exceptions import ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.db import session_scope
from compliance_api.models.department_detail import DepartmentDetail as DepartmentDetailModel
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.models.inspection import InspectionRequirement as InspectionRequirementModel
from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderInspectionRequirementMap as OrderInspectionRequirementMapModel
from compliance_api.models.order import OrderProgressEnum, OrderStatusEnum
from compliance_api.models.section import Section as SectionModel
from compliance_api.services.docgen_service.docgen_service import DocGenService
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.utils.constant import OFFICE_BRANCH, OFFICE_NAME
from compliance_api.utils.datetime import convert_to_full_month_format
from compliance_api.utils.pdf_style_converter import convert_inline_styles_for_pdf
from compliance_api.utils.template_renderer import render_template_with_data

from .order_constant import DEFAULT_ACT, DEFAULT_CHAPTER, DEFAULT_SECTION
from .order_template_constant import NOW_THEREFORE, WHERE_AS


class OrderService:
    """Service layer for Order operations."""

    @classmethod
    def get_all(cls, inspection_id: int = None) -> List[OrderModel]:
        """Get all orders for an inspection."""
        if inspection_id is None:
            return OrderModel.get_all()
        return OrderModel.get_by_params(
            {"inspection_id": inspection_id}, default_filters=False
        )

    @classmethod
    def get_projectwise_orders(cls, case_file_id: int) -> List[OrderModel]:
        """
        Get all orders with OPEN status for the project associated to the case file.

        param case_file_id: int
        return List[OrderModel]
        """
        case_file = CaseFileModel.find_by_id(case_file_id)
        if case_file is None:
            raise ResourceNotFoundError(f"Case file with ID {case_file_id} not found")
        case_file_ids_to_be_queried = [case_file.id]
        if case_file.project_id is not None:
            case_files = CaseFileModel.get_by_project(case_file.project_id)
            case_file_ids_to_be_queried = [
                case_file.id
                for case_file in case_files
                if case_file.is_active and not case_file.is_deleted
            ]
        return OrderModel.get_orders_by_case_files(case_file_ids_to_be_queried)

    @classmethod
    def create_order(cls, order_data: dict) -> OrderModel:
        """Create a new order."""
        inspection_id = order_data.get("inspection_id")
        inspection = ServiceUtils.inspection_exist_check(inspection_id=inspection_id)
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        ServiceUtils.officer_check(order_data.get("issuing_officer_id"), inspection)
        requirement_ids = order_data.get("inspection_requirement_ids", [])
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids, EnforcementActionOptionEnum.ORDER.value
        )
        if OrderModel.does_order_exists_by_requirement_ids(requirement_ids):
            raise UnprocessableEntityError(
                "Order already exists for these requirements."
            )
        order_obj = _create_order_obj(inspection, order_data)
        with session_scope() as session:
            from compliance_api.services.order.order_approval import (  # pylint: disable=import-outside-toplevel
                OrderApprovalService)

            created_order = OrderModel.create(order_obj, session)
            cls.insert_or_update_inspection_requirements(
                created_order.id,
                order_data.get("inspection_requirement_ids", []),
                session,
            )
            if inspection.is_history:
                OrderApprovalService.create_approval(
                    {
                        "approved_by_id": None,
                    },
                    created_order.id,
                    session,
                )
        return created_order

    @classmethod
    def get_order(cls, order_id: int) -> OrderModel:
        """Retrieve an order by ID."""
        return ServiceUtils.order_exist_check(order_id)

    @classmethod
    def get_order_by_order_number(cls, order_number: str) -> OrderModel:
        """Retrieve an order by order number."""
        return OrderModel.get_by_order_number(order_number)

    @classmethod
    def update_order(cls, order_id: int, update_data: dict) -> OrderModel:
        """Update an existing order."""
        ServiceUtils.order_exist_check(order_id)
        inspection = ServiceUtils.inspection_exist_check(
            inspection_id=update_data.get("inspection_id")
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        ServiceUtils.officer_check(update_data.get("issuing_officer_id"), inspection)
        requirement_ids = update_data.get("inspection_requirement_ids", [])
        ServiceUtils.check_requirement_for_enforcement_action(
            requirement_ids, EnforcementActionOptionEnum.ORDER.value
        )
        if OrderModel.does_order_exists_by_requirement_ids(requirement_ids, order_id):
            raise UnprocessableEntityError(
                "Order already exists for these requirements."
            )
        with session_scope() as session:
            updated_order = OrderModel.update_order(order_id, update_data, session)
            cls.insert_or_update_inspection_requirements(
                updated_order.id,
                update_data.get("inspection_requirement_ids", []),
                session,
            )
        return updated_order

    @classmethod
    def delete_order(cls, order_id: int) -> OrderModel:
        """Delete an order by ID."""
        order = ServiceUtils.order_exist_check(order_id)
        ServiceUtils.access_check_update_for_inspection(order.inspection)
        ServiceUtils.inspection_status_check(order.inspection)
        if order.order_status == OrderStatusEnum.OPEN:
            raise UnprocessableEntityError(
                "Order cannot be deleted as it is in OPEN status"
            )
        if order.order_progress == OrderProgressEnum.ISSUED:
            raise UnprocessableEntityError(
                f"Order cannot be deleted as it is in {order.order_progress.value} progress"
            )
        with session_scope() as session:
            OrderModel.update_order(
                order_id, {"is_deleted": True, "is_active": False}, session
            )
            OrderInspectionRequirementMapModel.delete_by_order(order_id, session)
        return order

    @classmethod
    def insert_or_update_inspection_requirements(
        cls, order_id: int, inspection_requirement_ids: list[int], session=None
    ):
        """Insert/Update inspection requirements associated with a given order."""
        if inspection_requirement_ids is not None:
            existing_requirements = OrderInspectionRequirementMapModel.get_by_order_id(
                order_id
            )
            existing_requirement_ids = {
                req.inspection_requirement_id for req in existing_requirements
            }

            new_requirement_ids = set(inspection_requirement_ids)
            requirement_ids_to_be_deleted = existing_requirement_ids.difference(
                new_requirement_ids
            )
            requirement_ids_to_be_added = new_requirement_ids.difference(
                existing_requirement_ids
            )

            if requirement_ids_to_be_deleted:
                OrderInspectionRequirementMapModel.bulk_delete(
                    order_id, list(requirement_ids_to_be_deleted), session
                )
            if requirement_ids_to_be_added:
                OrderInspectionRequirementMapModel.bulk_insert(
                    order_id, list(requirement_ids_to_be_added), session
                )

    @classmethod
    def change_status(cls, order_id, status):
        """Close the order."""
        order = ServiceUtils.order_exist_check(order_id)
        ServiceUtils.access_check_update_for_inspection(order.inspection)
        ServiceUtils.inspection_status_check(order.inspection)
        status_enum = OrderStatusEnum(status.get("status"))
        if order.order_status == status_enum:
            raise UnprocessableEntityError(
                "The order is already in the requested status"
            )
        possible_status_change = {
            OrderStatusEnum.OPEN: [OrderStatusEnum.CLOSED, OrderStatusEnum.RESCINDED],
            OrderStatusEnum.CLOSED: [OrderStatusEnum.OPEN],
        }
        if status_enum not in possible_status_change.get(order.order_status, []):
            raise UnprocessableEntityError("Invalid status change requested")
        updated_order = OrderModel.update_order(
            order_id,
            {"order_status": OrderStatusEnum(status_enum.value)},
        )
        return updated_order

    @classmethod
    def issue_order(cls, order_id, issue):
        """Issue an order."""
        order = ServiceUtils.order_exist_check(order_id)
        inspection = ServiceUtils.inspection_exist_check(
            inspection_id=order.inspection_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)
        ServiceUtils.inspection_status_check(inspection)
        OrderModel.update_order(
            order_id,
            {
                "order_status": OrderStatusEnum.OPEN,
                "order_progress": OrderProgressEnum.ISSUED,
                "date_issued": issue.get("date_issued"),
            },
        )
        return order

    @classmethod
    def render(cls, order_id, output_format):
        """Preview order."""
        order = ServiceUtils.order_exist_check(order_id)
        if output_format == "pdf":
            ServiceUtils.access_check_update_for_inspection(order.inspection)
            ServiceUtils.inspection_status_check(order.inspection)
        order_data = _create_order_data(order.inspection, order)
        response = DocGenService.render_template(
            "ORDER_TEMPLATE", order_data, output_format
        )
        return response, order

    @classmethod
    def reset_field(cls, order_id: int, field_names: List[str]) -> OrderModel:
        """Reset a field in the order to its default generated value.

        Args:
            order_id: The order ID
            field_names: The fields to reset (where_as or now_therefore)

        Returns:
            OrderModel: The updated order

        Raises:
            ResourceNotFoundError: If the order is not found
            UnprocessableEntityError: If the order is not in drafting status
        """
        order = ServiceUtils.order_exist_check(order_id)
        inspection = ServiceUtils.inspection_exist_check(
            inspection_id=order.inspection_id
        )
        ServiceUtils.access_check_update_for_inspection(inspection)

        # Check if the order is in drafting status
        if order.order_progress != OrderProgressEnum.DRAFTING:
            raise UnprocessableEntityError(
                f"Order cannot be reset as it is in {order.order_progress.value} progress"
            )

        # Get the section and requirements for generating content
        section_id = order.section_id
        requirement_maps = OrderInspectionRequirementMapModel.get_by_order_id(order_id)
        requirement_ids = [req.inspection_requirement_id for req in requirement_maps]

        # Generate the where_as and now_therefore content
        where_as, now_therefore = _create_where_as_and_now_therefore(
            inspection, order.order_number, section_id, requirement_ids
        )

        # Update only the requested field
        update_data = {}
        if "where_as" in field_names:
            update_data["where_as"] = where_as
        if "now_therefore" in field_names:
            update_data["now_therefore"] = now_therefore

        # Update the order in the database
        updated_order = OrderModel.update_order(order_id, update_data)

        return updated_order


def _create_order_data(inspection, order):
    """Create order data."""
    department_details = DepartmentDetailModel.query.filter_by(
        is_active=True, is_deleted=False
    ).first()
    order_date = (
        order.date_issued if order.date_issued else order.intended_issuance_date
    )
    return {
        "order_details": {
            "order_number": order.order_number,
            "where_as": convert_inline_styles_for_pdf(order.where_as),
            "now_therefore": convert_inline_styles_for_pdf(order.now_therefore),
            "issued_date": (
                order_date.strftime("%Y-%m-%d")
                if order_date
                else (
                    order.intended_issuance_date.strftime("%Y-%m-%d")
                    if order.intended_issuance_date
                    else None
                )
            ),
        },
        "officer_details": {
            "officer_name": order.issuing_officer.first_name
            + " "
            + order.issuing_officer.last_name,
            "officer_position": order.issuing_officer.position.name,
        },
        "department_details": {
            "logo_url": department_details.logo_url,
            "email": department_details.email,
            "address_line1": department_details.address_line1,
            "address_line2": department_details.address_line2,
            "phone": department_details.phone,
            "website": department_details.website,
            "office_name": OFFICE_NAME,
            "office_branch": OFFICE_BRANCH,
        },
    }


def _create_order_obj(inspection, order_data: dict) -> dict:
    """
    Create an order object as a dictionary.

    If where_as and now_therefore are not provided, they will be generated.
    If issuing_officer_id is not provided, it will be set to the primary officer of the inspection.
    If section_id is not provided, it will be set to the default section.
    """
    section_id = order_data.get("section_id", None)
    requirement_ids = order_data.get("inspection_requirement_ids", None)
    if not section_id:
        default_section = SectionModel.get_by_name_act(DEFAULT_SECTION, DEFAULT_ACT)
        section_id = default_section.id
    order_number = order_data.get("order_number", None)
    if not order_number:
        order_number = _create_order_number(
            inspection.case_file.project_id, inspection.case_file.id
        )
    where_as = order_data.get("where_as")
    now_therefore = order_data.get("now_therefore")
    if not where_as or not now_therefore:
        generated_where_as, generated_now_therefore = (
            _create_where_as_and_now_therefore(
                inspection, order_number, section_id, requirement_ids
            )
        )
        where_as = where_as or generated_where_as
        now_therefore = now_therefore or generated_now_therefore
    return {
        "order_number": order_number,
        "inspection_id": inspection.id,
        "issuing_officer_id": order_data.get(
            "issuing_officer_id", inspection.primary_officer_id
        ),
        "section_id": section_id,
        "where_as": where_as,
        "now_therefore": now_therefore,
        "intended_issuance_date": order_data.get("intended_issuance_date"),
        "order_status": OrderStatusEnum.CREATED,
        "order_progress": OrderProgressEnum.DRAFTING,
    }


def _create_where_as_and_now_therefore(
    inspection, order_number, section_id, requirement_ids
):
    """Create where_as and now_therefore."""
    section = SectionModel.find_by_id(section_id)
    project_details = ServiceUtils.get_project_details(
        inspection.case_file.project_id, inspection.case_file.id
    )
    whereas_data = {
        "project_details": project_details,
        "inspection_details": {
            "id": inspection.id,
            "inspection_type": " and ".join(
                [inspection_type.type.name for inspection_type in inspection.types]
            ),
            "start_date": convert_to_full_month_format(inspection.start_date),
            "end_date": (
                convert_to_full_month_format(inspection.end_date)
                if inspection.end_date
                else ""
            ),
            "ir_number": ServiceUtils.strip_project_code(inspection.ir_number),
        },
        "order_details": {
            "order_number": order_number,
            "section": section.name,
            "chapter": DEFAULT_CHAPTER,
            "act": section.act,
            "ea_certificate": project_details.get("eac_certificate", ""),
            "has_certificate": project_details.get("has_certificate", False),
        },
    }
    requirements = InspectionRequirementModel.get_requirement_by_ids(requirement_ids)
    requirement_details = ServiceUtils.get_formatted_requirement_details(requirements)
    requirement_numbers = []
    requirement_summaries = []
    requirement_sources = []
    for requirement in requirement_details:
        requirement_summaries.append(requirement["requirement_summary"])
        for detail in requirement["requirement_source_details"]:
            if detail["requirement_source_name"]:
                requirement_sources.append(detail["requirement_source_name"])
            if detail["requirement_source_number"]:
                requirement_numbers.append(detail["requirement_source_number"])
            # break after first requirement source detail
            break
    whereas_data["requirement_details"] = {
        "requirement_numbers": ", ".join(requirement_numbers),
        "requirement_summaries": ", ".join(requirement_summaries),
        "requirement_sources": ", ".join(requirement_sources),
    }

    where_as = render_template_with_data("WHERE_AS", WHERE_AS, whereas_data)
    now_therefore = render_template_with_data(
        "NOW_THEREFORE", NOW_THEREFORE, whereas_data
    )
    return where_as, now_therefore


def _create_order_number(project_id: int, case_file_id: int) -> str:
    """Generate the order number."""
    project_code = ServiceUtils.get_project_abbreviation(project_id)
    case_file = CaseFileModel.find_by_id(case_file_id)
    if not case_file:
        raise ResourceNotFoundError("Given case file doesn't exist")
    if case_file.project_id != project_id:
        raise UnprocessableEntityError("Given project and case file don't match")

    count = OrderModel.get_count_by_project_nd_case_file_id(project_id, case_file_id)
    serial_number = f"{count + 1:03}"
    return f"{project_code}_{case_file.case_file_number}_OR{serial_number}"
