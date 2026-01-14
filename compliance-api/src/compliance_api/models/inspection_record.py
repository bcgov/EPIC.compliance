"""Model for inspection record."""

from enum import Enum

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from compliance_api.models.inspection.inspection_enum import InspectionStatusEnum

from .base_model import BaseModelVersioned
from .utils import with_session


class IRStatusEnum(Enum):
    """Enum for IR Status."""

    PRELIMINARY = 1
    FINAL = 2


class IRProgressEnum(Enum):
    """Enum for IR Progress.

    PRELIMINARY_DRAFTING: When you create the IR with PRELIMINARY status.
    PRELIMINARY_DEPUTY_REVIEW: When the PRELIMINARY IR is reviewed by the deputy.
    PRELIMINARY_APPROVED: When the PRELIMINARY IR is approved by the deputy.
    HOLDER_PRELIMINARY_REVIEW: When the PRELIMINARY IR is sent to the holder.
    FINALIZING_RECORD: When you switch the IR to FINAL status or create the IR with FINAL status.
    FINAL_DEPUTY_REVIEW: When the FINAL IR is reviewed by the deputy.
    FINAL_APPROVED: When the FINAL IR is approved by the deputy.
    ISSUED: When the IR is issued.
    """

    PRELIMINARY_DRAFTING = "Preliminary Drafting"
    PRELIMINARY_DEPUTY_REVIEW = "Preliminary Deputy Review"
    PRELIMINARY_APPROVED = "Preliminary Approved"
    HOLDER_PRELIMINARY_REVIEW = "Holder Preliminary Review"
    FINALIZING_RECORD = "Finalizing Record"
    FINAL_DEPUTY_REVIEW = "Final Deputy Review"
    FINAL_APPROVED = "Final Approved"
    ISSUED = "Issued"

    @classmethod
    def ordered_values(cls):
        """Return ordered values for IR Progress."""
        return [
            cls.FINAL_APPROVED.name,
            cls.FINAL_DEPUTY_REVIEW.name,
            cls.FINALIZING_RECORD.name,
            cls.HOLDER_PRELIMINARY_REVIEW.name,
            cls.ISSUED.name,
            cls.PRELIMINARY_APPROVED.name,
            cls.PRELIMINARY_DEPUTY_REVIEW.name,
            cls.PRELIMINARY_DRAFTING.name,
        ]


class InspectionRecord(BaseModelVersioned):
    """Definition of the InspectionRecord."""

    __tablename__ = "inspection_records"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    inspection_id = Column(
        ForeignKey("inspections.id", name="ir_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    ir_status_id = Column(
        ForeignKey("ir_status_options.id", name="ir_status_id_status_options_fkey"),
        nullable=False,
        comment="Status of the inspection record",
    )
    mailing_address = Column(
        String(255),
        nullable=True,
        comment="Mailing address of the associated proponent",
    )
    inspection_scope = Column(String, nullable=True, comment="Scope of the inspection")
    preliminary_review_details = Column(
        String, nullable=True, comment="Details of the preliminary review"
    )
    finding_statement = Column(
        String, nullable=True, comment="Finding statement from the inspection"
    )
    field_change_info = Column(
        JSON,
        nullable=True,
        comment="To indicate if selected fields have changed or not",
    )
    enforcement_summary = Column(
        String, nullable=True, comment="Summary of enforcement action"
    )
    action_required_by_rp = Column(
        String, nullable=True, comment="Action required by Regulated Party"
    )
    intended_issuance_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the inspection report was intended to be issued",
    )
    date_issued = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the inspection report was issued",
    )
    ir_progress = Column(
        SqlEnum(IRProgressEnum),
        nullable=True,
        comment="State of the inspection record",
        default=IRProgressEnum.PRELIMINARY_DRAFTING,
    )
    record_prepared_by_id = Column(
        ForeignKey("staff_users.id", name="ir_record_prepared_by_id_fkey"),
        nullable=True,
        comment="The unique identifier of the user who prepared the record",
    )
    record_prepared_by_position_id = Column(
        ForeignKey("positions.id", name="ir_record_prepared_by_position_id_fkey"),
        nullable=True,
        comment="The unique identifier of the position of the user who prepared the record",
    )
    record_prepared_by = relationship(
        "StaffUser", foreign_keys=[record_prepared_by_id], lazy="joined"
    )
    record_prepared_by_position = relationship(
        "Position", foreign_keys=[record_prepared_by_position_id], lazy="joined"
    )
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="joined")
    ir_status = relationship(
        "IRStatusOption", foreign_keys=[ir_status_id], lazy="joined"
    )

    @classmethod
    @with_session
    def create_inspection_record(cls, ir_data, session=None):
        """Create the inspection record."""
        inspection_record = InspectionRecord(**ir_data)
        session.add(inspection_record)
        session.flush()
        return inspection_record

    @classmethod
    @with_session
    def update_inspection_record(
        cls, inspection_record_id, ir_update_data, session=None
    ):
        """Update the inspection record."""
        inspection_record = cls.find_by_id(inspection_record_id)
        if not inspection_record:
            return None
        inspection_record.update(ir_update_data, commit=False)
        session.flush()
        return inspection_record

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Find all inspection records by inspection id."""
        return cls.query.filter_by(
            inspection_id=inspection_id, is_deleted=False, is_active=True
        ).first()

    @property
    def is_open_for_editing(self):
        """Check if the associated inspection has been reopened."""
        return self.inspection.inspection_status == InspectionStatusEnum.OPEN and self.date_issued is None
