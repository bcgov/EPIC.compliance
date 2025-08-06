"""ComplaintReqOrderDetail model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..utils import with_session


class ComplaintReqOrderDetail(BaseModelVersioned):
    """ComplaintReqOrderDetail Model Class."""

    __tablename__ = "complaint_req_order_details"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the complaints",
    )
    complaint_id = Column(
        Integer,
        ForeignKey(
            "complaints.id",
            name="details_complaint_id_complaints_id",
        ),
        nullable=False,
        comment="The unique id of the complaint",
    )
    order_number = Column(String, nullable=True, comment="The order number")
    complaint = relationship(
        "Complaint", foreign_keys=[complaint_id], back_populates="order_detail", lazy="select"
    )

    def to_dict(self):
        """Convert model instance to a dictionary for JSON serialization."""
        return {"id": self.id, "complaint_id": self.complaint_id, "order_number": self.order_number}

    @classmethod
    @with_session
    def create(cls, requirement_obj, session=None):
        """Create order details."""
        requirement_more = ComplaintReqOrderDetail(**requirement_obj)
        session.add(requirement_more)
        session.flush()
        return requirement_more

    @classmethod
    @with_session
    def update_details(cls, complaint_id, requirement_obj, session=None):
        """Update order details."""
        query = cls.query.filter_by(complaint_id=complaint_id, is_deleted=False)
        order_requirement = query.first()
        order_requirement.update(requirement_obj, commit=False)
        session.flush()
        return order_requirement

    @classmethod
    @with_session
    def delete_details(cls, complaint_id, session=None):
        """Mark the details as deleted."""
        order_requirement = cls.query.filter_by(
            complaint_id=complaint_id, is_deleted=False
        ).first()
        order_requirement.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    def get_by_complaint(cls, complaint_id):
        """Get additional requirement source details."""
        return cls.query.filter_by(complaint_id=complaint_id, is_deleted=False).first()
