"""Model class to handle the types of the inspection."""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..inspection.inspection import Inspection as InspectionModel
from ..utils import with_session


class InspectionType(BaseModelVersioned):
    """Model class for types associted with the inspection."""

    __tablename__ = "inspection_types"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    type_id = Column(
        Integer,
        ForeignKey(
            "inspection_type_options.id", name="inspection_types_type_id_type_id_fkey"
        ),
        nullable=False,
        comment="The unique identifier of inspection type option",
    )
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id", name="inspection_agencies_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="select")
    type = relationship("InspectionTypeOption", foreign_keys=[type_id], lazy="select")

    @classmethod
    def get_all_by_inspection(cls, inspection_id: int):
        """Retrieve all inspection types by inspection id."""
        return cls.query.filter_by(inspection_id=inspection_id, is_deleted=False).all()

    @classmethod
    @with_session
    def bulk_delete(cls, inspection_id: int, type_ids: list[int], session=None):
        """Delete inspection type."""
        types = cls.query.filter(
            cls.inspection_id == inspection_id, cls.type_id.in_(type_ids)
        ).all()
        for type_item in types:
            type_item.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(cls, inspection_id: int, type_ids: list[int], session=None):
        """Insert type per inspection."""
        inspection_ir_type_data = [
            InspectionType(**{"inspection_id": inspection_id, "type_id": type_id})
            for type_id in type_ids
        ]
        session.add_all(inspection_ir_type_data)
        session.flush()

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete unapproved project details by case_file_id."""
        types = (
            cls.query.join(InspectionModel)
            .filter(
                InspectionModel.case_file_id == case_file_id,
                InspectionType.is_deleted.is_(False),
            )
            .all()
        )
        type_ids = [type.id for type in types]
        if type_ids:
            types = cls.query.filter(InspectionType.id.in_(type_ids)).all()
            for type_item in types:
                type_item.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_inspection_type(cls, inspection_id, session=None):
        """Delete inspection Type."""
        types = cls.query.filter_by(inspection_id=inspection_id, is_deleted=False).all()
        for type_item in types:
            type_item.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
