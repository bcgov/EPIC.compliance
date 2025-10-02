"""Order fixtures for testing."""

import random

import pytest

from compliance_api.models.order import Order as OrderModel
from compliance_api.models.order import OrderInspectionRequirementMap, OrderProgressEnum, OrderStatusEnum
from compliance_api.models.section import Section as SectionModel


@pytest.fixture
def created_section(app, db):
    """Return a section."""
    section = SectionModel(
        name="Test Section", act=52, is_active=True, is_deleted=False
    )
    db.session.add(section)
    db.session.commit()
    return section


@pytest.fixture
def created_order(app, db, created_inspection, created_section):
    """Return an order."""
    order = OrderModel(
        inspection_id=created_inspection.id,
        issuing_officer_id=created_inspection.primary_officer_id,
        section_id=created_section.id,
        where_as="Test where as",
        now_therefore="Test now therefore",
        order_number=f"TEST-ORDER-{random.randint(100000, 999999)}",
        order_status=OrderStatusEnum.CREATED,
        order_progress=OrderProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(order)
    db.session.commit()
    return order


@pytest.fixture
def created_order_requirement_map(
    app, db, created_order, created_inspection_requirement
):
    """Return an order inspection requirement map."""
    order_req_map = OrderInspectionRequirementMap(
        order_id=created_order.id,
        inspection_requirement_id=created_inspection_requirement.id,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(order_req_map)
    db.session.commit()
    return order_req_map
