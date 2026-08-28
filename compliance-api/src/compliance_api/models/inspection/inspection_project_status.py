"""Model class to handle the project statuses of the inspection."""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..inspection.inspection import Inspection as InspectionModel
from ..utils import with_session


class InspectionProjectStatus(BaseModelVersioned):
    """Model class for the project statuses associated with the inspection."""

    __tablename__ = "inspection_project_statuses"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    project_status_id = Column(
        Integer,
        nullable=False,
        comment="The unique identifier of the project status in EPIC.track",
    )
    inspection_id = Column(
        Integer,
        ForeignKey(
            "inspections.id", name="inspection_project_statuses_inspection_id_fkey"
        ),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="select")

    @classmethod
    def get_all_by_inspection(cls, inspection_id: int):
        """Retrieve all project statuses by inspection id."""
        return cls.query.filter_by(inspection_id=inspection_id, is_deleted=False).all()

    @classmethod
    @with_session
    def bulk_delete(cls, inspection_id: int, project_status_ids: list[int], session=None):
        """Delete project statuses per inspection."""
        statuses = cls.query.filter(
            cls.inspection_id == inspection_id,
            cls.project_status_id.in_(project_status_ids),
        ).all()
        for status in statuses:
            status.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(cls, inspection_id: int, project_status_ids: list[int], session=None):
        """Insert project status per inspection."""
        project_status_data = [
            InspectionProjectStatus(
                **{"inspection_id": inspection_id, "project_status_id": status_id}
            )
            for status_id in project_status_ids
        ]
        session.add_all(project_status_data)
        session.flush()

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete project statuses by case_file_id."""
        statuses = (
            cls.query.join(InspectionModel)
            .filter(
                InspectionModel.case_file_id == case_file_id,
                InspectionProjectStatus.is_deleted.is_(False),
            )
            .all()
        )
        for status in statuses:
            status.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_inspection_project_status(cls, inspection_id, session=None):
        """Delete project statuses of an inspection."""
        statuses = cls.query.filter_by(
            inspection_id=inspection_id, is_deleted=False
        ).all()
        for status in statuses:
            status.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
