"""Order model."""

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from .base_model import BaseModelVersioned
from .case_file import CaseFile as CaseFileModel
from .inspection import Inspection as InspectionModel
from .utils import with_session


class OrderStatusEnum(enum.Enum):
    """Order status enum."""

    CREATED = "Created"  # When you create the order
    OPEN = "Open"  # When the order is issued
    CLOSED = "Closed"  # When the order is closed
    RESCINDED = "Rescinded"  # When the order is rescinded


class OrderProgressEnum(enum.Enum):
    """Order progress enum."""

    DRAFTING = "Drafting"  # When you create the order
    DEPUTY_REVIEW = "Deputy Review"  # When the deputy reviews the order
    APPROVED = "Approved"  # When the order is approved
    ISSUED = "Issued"  # When the order is issued


class OrderReplaceStatusEnum(enum.Enum):
    """Order replace status enum."""

    ORIGINAL = "Original"  # When the order is original
    REPLACED = "Replaced"  # When the order is replaced
    REPLACEMENT = "Replacement"  # When the order is replacement of another order


class OrderInspectionRequirementMap(BaseModelVersioned):
    """OrderInspectionRequirementMap Model."""

    __tablename__ = "order_inspection_requirement_maps"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    order_id = Column(
        Integer, ForeignKey("orders.id", name="order_inspection_map_order_id_fkey")
    )
    inspection_requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id",
            name="order_inspection_map_requirement_id_fkey",
        ),
    )
    order = relationship("Order", foreign_keys=[order_id], lazy="joined")
    inspection_requirement = relationship(
        "InspectionRequirement", foreign_keys=[inspection_requirement_id], lazy="joined"
    )

    @classmethod
    def get_by_order_id(cls, order_id):
        """Get inspection requirements by order id."""
        return cls.query.filter_by(
            order_id=order_id, is_deleted=False, is_active=True
        ).all()

    @classmethod
    def get_by_requirement_id(cls, requirement_id):
        """Get inspection requirements by requirement id."""
        return cls.query.filter_by(
            inspection_requirement_id=requirement_id, is_deleted=False, is_active=True
        ).first()

    @classmethod
    @with_session
    def bulk_delete(
        cls, order_id: int, inspection_requirement_ids: list[int], session=None
    ):
        """Delete inspection requirement ids by id per order."""
        query = session.query(cls) if session else cls.query
        requirements = query.filter(
            cls.order_id == order_id,
            cls.inspection_requirement_id.in_(inspection_requirement_ids),
        )
        for requirement in requirements:
            requirement.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    def delete_by_order(cls, order_id: int, session=None):
        """Delete an order by ID."""
        query = session.query(cls) if session else cls.query
        maps = query.filter(
            cls.order_id == order_id, cls.is_deleted.is_(False), cls.is_active.is_(True)
        )
        for map_item in maps:
            map_item.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls, order_id: int, inspection_requirement_ids: list[int], session=None
    ):
        """Insert inspection requirements per order."""
        order_inspection_requirement_map_data = [
            OrderInspectionRequirementMap(
                **{
                    "order_id": order_id,
                    "inspection_requirement_id": inspection_requirement_id,
                }
            )
            for inspection_requirement_id in inspection_requirement_ids
        ]
        session.add_all(order_inspection_requirement_map_data)
        session.flush()


class Order(BaseModelVersioned):
    """Order model."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    where_as = Column(String, nullable=True)
    now_therefore = Column(String, nullable=True)
    order_number = Column(String, nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    date_issued = Column(DateTime(timezone=True), nullable=True)
    intended_issuance_date = Column(DateTime(timezone=True), nullable=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)
    issuing_officer_id = Column(Integer, ForeignKey("staff_users.id"), nullable=False)
    issuing_officer = relationship(
        "StaffUser", foreign_keys=[issuing_officer_id], lazy="joined"
    )
    section = relationship("Section", foreign_keys=[section_id], lazy="joined")
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="select")
    order_status = Column(Enum(OrderStatusEnum), nullable=True)
    order_progress = Column(Enum(OrderProgressEnum), nullable=True)
    order_replace_status = Column(Enum(OrderReplaceStatusEnum), nullable=True)
    replacement_for_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    order_requirement_maps = relationship(
        "OrderInspectionRequirementMap",
        back_populates="order",
        lazy="select",
        primaryjoin="and_(OrderInspectionRequirementMap.order_id == Order.id, "
        "OrderInspectionRequirementMap.is_active == True, "
        "OrderInspectionRequirementMap.is_deleted == False)",
    )
    order_approvals = relationship(
        "OrderApproval",
        back_populates="order",
        lazy="select",
        primaryjoin="and_(OrderApproval.order_id == Order.id, "
        "OrderApproval.is_active == True, "
        "OrderApproval.is_deleted == False)",
        order_by="desc(OrderApproval.created_date)",
    )
    __table_args__ = (
        Index(
            "unique_non_deleted_order_number",  # Index name
            "order_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @property
    def is_closed(self):
        """Check if the order is in a closed state.

        An order is considered closed if its status is:
        - OPEN: Order has been issued and is open
        - CLOSED: Order has been closed
        - RESCINDED: Order has been rescinded

        Returns:
            bool: True if the order is closed, False otherwise
        """
        closed_statuses = [
            OrderStatusEnum.OPEN,
            OrderStatusEnum.CLOSED,
            OrderStatusEnum.RESCINDED,
        ]
        return self.order_status in closed_statuses

    @classmethod
    def get_closed_statuses(cls):
        """Get list of order statuses that are considered closed.

        Returns:
            list: List of OrderStatusEnum values for closed statuses
        """
        return [
            OrderStatusEnum.OPEN,
            OrderStatusEnum.CLOSED,
            OrderStatusEnum.RESCINDED,
        ]

    @classmethod
    @with_session
    def create(cls, order_data: dict, session=None):
        """Create a new order."""
        order = Order(**order_data)
        session.add(order)
        session.flush()
        return order

    @classmethod
    @with_session
    def update_order(cls, order_id, order_data, session=None):
        """Update order."""
        query = cls.query.filter_by(id=order_id)
        order: Order = query.first()
        if not order or order.is_deleted:
            return None
        order.update(order_data, commit=False)
        session.flush()
        return order

    @classmethod
    def get_count_by_project_nd_case_file_id(cls, project_id: int, case_file_id: int):
        """Get count of orders by project and case file id."""
        result = (
            cls.query.join(InspectionModel, InspectionModel.id == cls.inspection_id)
            .join(CaseFileModel, CaseFileModel.id == InspectionModel.case_file_id)
            .with_entities(
                InspectionModel.case_file_id,
                CaseFileModel.project_id,
                func.count(cls.id).label("order_count"),  # pylint: disable=not-callable
            )
            .filter(
                CaseFileModel.project_id == project_id,
                InspectionModel.case_file_id == case_file_id,
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .group_by(InspectionModel.case_file_id, CaseFileModel.project_id)
            .first()
        )
        return result.order_count if result else 0

    @classmethod
    def get_by_order_number(cls, order_number: str):
        """Find an order by order number."""
        return cls.query.filter_by(order_number=order_number, is_deleted=False).first()

    @classmethod
    def get_orders_by_case_files(cls, case_file_ids: list[int]):
        """Get orders by case file ids."""
        return (
            cls.query.join(InspectionModel, InspectionModel.id == cls.inspection_id)
            .join(CaseFileModel, CaseFileModel.id == InspectionModel.case_file_id)
            .filter(CaseFileModel.id.in_(case_file_ids), cls.is_deleted.is_(False))
            .all()
        )

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Find all orders by inspection id."""
        return cls.query.filter_by(
            inspection_id=inspection_id, is_deleted=False, is_active=True
        ).all()

    @classmethod
    def has_replacement_order(cls, original_order_id: int):
        """Check if a replacement order already exists for the given original order."""
        # First, get the original order to find its inspection
        original_order = cls.query.filter_by(
            id=original_order_id, is_deleted=False
        ).first()
        if not original_order:
            return False

        # Look for any replacement orders in the same inspection
        replacement_order = cls.query.filter_by(
            inspection_id=original_order.inspection_id,
            order_replace_status=OrderReplaceStatusEnum.REPLACEMENT,
            is_deleted=False,
        ).first()

        return replacement_order is not None
