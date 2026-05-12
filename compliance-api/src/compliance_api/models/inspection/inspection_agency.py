"""Model class to handle the attendance of agencies to an inspection."""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import joinedload, relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..inspection.inspection import Inspection as InspectionModel
from ..utils import with_session


class InspectionAgency(BaseModelVersioned):
    """Model class for agencies associted with the inspection."""

    __tablename__ = "inspection_agencies"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    agency_id = Column(
        Integer,
        ForeignKey("agencies.id", name="inspection_agencies_agency_id_agency_id_fkey"),
        nullable=False,
        comment="The unique identifier of agency",
    )
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id", name="inspection_agencies_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="select")
    agency = relationship("Agency", foreign_keys=[agency_id], lazy="select")

    @classmethod
    def get_all_by_inspection(cls, inspection_id: int):
        """Retrieve all agencies by inspection id."""
        return (
            cls.query
            .options(joinedload(cls.agency))
            .filter_by(inspection_id=inspection_id, is_deleted=False)
            .all()
        )

    @classmethod
    @with_session
    def bulk_delete(cls, inspection_id: int, agency_ids: list[int], session=None):
        """Delete agency ids by id per inspection."""
        agencies = cls.query.filter(
            cls.inspection_id == inspection_id, cls.agency_id.in_(agency_ids)
        ).all()
        for agency in agencies:
            agency.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(cls, inspection_id: int, agency_ids: list[int], session=None):
        """Insert agencies per inspection."""
        inspection_agency_data = [
            InspectionAgency(**{"inspection_id": inspection_id, "agency_id": agency_id})
            for agency_id in agency_ids
        ]
        session.add_all(inspection_agency_data)
        session.flush()

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete agency by case_file_id."""
        agencies = (
            cls.query.join(InspectionModel)
            .filter(
                InspectionModel.case_file_id == case_file_id,
                InspectionAgency.is_deleted.is_(False),
            )
            .all()
        )
        agency_ids = [agency.id for agency in agencies]
        if agency_ids:
            agencies = cls.query.filter(InspectionAgency.id.in_(agency_ids)).all()
            for agency in agencies:
                agency.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_inspection_agency(cls, inspection_id, session=None):
        """Delete inspection Agency."""
        agencies = cls.query.filter_by(
            inspection_id=inspection_id, is_deleted=False
        ).all()
        for agency in agencies:
            agency.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
