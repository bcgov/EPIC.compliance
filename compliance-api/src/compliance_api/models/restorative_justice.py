"""Restorative Justice Model."""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index, Integer, String, Text, and_
from sqlalchemy.orm import relationship

from compliance_api.models.base_model import BaseModelVersioned
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.utils import with_session
from compliance_api.utils.constant import DELETE_DIC_PARAMS


class RestorativeJusticeStatusEnum(Enum):
    """Enum for Restorative Justice Status."""

    DRAFTING = "Drafting"
    OPEN = "Open"
    CLOSED = "Closed"


class RestorativeJusticeInspectionRequirementMap(BaseModelVersioned):
    """RestorativeJusticeInspectionRequirementMap Model."""

    __tablename__ = "restorative_justice_inspection_requirement_maps"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    restorative_justice_id = Column(
        Integer,
        ForeignKey(
            "restorative_justices.id",
            name="restorative_justice_inspection_map_justice_id_fkey",
        ),
    )
    inspection_requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id",
            name="restorative_justice_inspection_map_requirement_id_fkey",
        ),
    )

    # Relationships
    restorative_justice = relationship(
        "RestorativeJustice", back_populates="restorative_justice_requirement_maps"
    )
    inspection_requirement = relationship(
        "InspectionRequirement", foreign_keys=[inspection_requirement_id], lazy="joined"
    )

    @classmethod
    @with_session
    def create_restorative_justice_requirement_map(
        cls, restorative_justice_requirement_map_data, session=None
    ):
        """Create the restorative justice requirement map."""
        restorative_justice_requirement_map = cls(
            **restorative_justice_requirement_map_data
        )
        session.add(restorative_justice_requirement_map)
        session.commit()
        return restorative_justice_requirement_map

    @classmethod
    @with_session
    def get_by_restorative_justice_id(cls, restorative_justice_id, session=None):
        """Find all restorative justice requirement maps by restorative justice id."""
        return (
            session.query(cls)
            .filter(
                and_(
                    cls.restorative_justice_id == restorative_justice_id,
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                )
            )
            .all()
        )

    @classmethod
    @with_session
    def delete_by_restorative_justice_id(cls, restorative_justice_id, session=None):
        """Delete all restorative justice requirement maps by restorative justice id."""
        query = session.query(cls) if session else cls.query
        maps = query.filter_by(restorative_justice_id=restorative_justice_id).all()
        for map_item in maps:
            map_item.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def bulk_delete(
        cls,
        restorative_justice_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Delete inspection requirement ids by id per restorative justice."""
        query = session.query(cls) if session else cls.query
        requirements = query.filter(
            cls.restorative_justice_id == restorative_justice_id,
            cls.inspection_requirement_id.in_(inspection_requirement_ids),
        )
        for requirement in requirements:
            requirement.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls,
        restorative_justice_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert inspection requirements per restorative justice."""
        restorative_justice_inspection_requirement_map_data = [
            RestorativeJusticeInspectionRequirementMap(
                **{
                    "restorative_justice_id": restorative_justice_id,
                    "inspection_requirement_id": inspection_requirement_id,
                }
            )
            for inspection_requirement_id in inspection_requirement_ids
        ]
        session.add_all(restorative_justice_inspection_requirement_map_data)
        session.flush()
        return restorative_justice_inspection_requirement_map_data


class RestorativeJustice(BaseModelVersioned):
    """Restorative Justice Model."""

    __tablename__ = "restorative_justices"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    inspection_id = Column(
        ForeignKey("inspections.id", name="rj_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    restorative_justice_number = Column(String)
    status = Column(
        SqlEnum(RestorativeJusticeStatusEnum),
        nullable=True,
        comment="Status of the restorative justice",
        default=RestorativeJusticeStatusEnum.DRAFTING,
    )
    restitution_details = Column(
        Text,
        nullable=True,
        comment="Restitution details",
    )
    date_restitution_complete = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the restitution was completed",
    )

    # Relationships
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="joined")
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    restorative_justice_requirement_maps = relationship(
        "RestorativeJusticeInspectionRequirementMap",
        back_populates="restorative_justice",
        lazy="select",
        primaryjoin=(
            "and_(RestorativeJusticeInspectionRequirementMap.restorative_justice_id == "
            "RestorativeJustice.id, "
            "RestorativeJusticeInspectionRequirementMap.is_active == True, "
            "RestorativeJusticeInspectionRequirementMap.is_deleted == False)"
        ),
    )

    __table_args__ = (
        Index(
            "unique_non_deleted_restorative_justice_number",  # Index name
            "restorative_justice_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    def _determine_status(
        cls, restitution_details=None, date_restitution_complete=None
    ):
        """Determine the status based on provided fields."""
        if date_restitution_complete:
            return RestorativeJusticeStatusEnum.CLOSED
        if restitution_details:
            return RestorativeJusticeStatusEnum.OPEN
        return RestorativeJusticeStatusEnum.DRAFTING

    @classmethod
    @with_session
    def create_restorative_justice(cls, restorative_justice_data, session=None):
        """Create the restorative justice."""
        # Auto-set status if not provided
        if (
            "status" not in restorative_justice_data
            or restorative_justice_data["status"] is None
        ):
            restorative_justice_data["status"] = cls._determine_status(
                restorative_justice_data.get("restitution_details"),
                restorative_justice_data.get("date_restitution_complete"),
            )

        restorative_justice = cls(**restorative_justice_data)
        session.add(restorative_justice)
        session.flush()
        return restorative_justice

    @classmethod
    @with_session
    def update_restorative_justice(
        cls, restorative_justice_id, restorative_justice_update_data, session=None
    ):
        """Update the restorative justice."""
        # Get current record to check existing values
        restorative_justice = cls.find_by_id(restorative_justice_id)

        # Auto-set status if not explicitly provided
        if (
            "status" not in restorative_justice_update_data
            or restorative_justice_update_data["status"] is None
        ):
            # Use updated values if provided, otherwise use current values
            restitution_details = restorative_justice_update_data.get(
                "restitution_details", restorative_justice.restitution_details
            )
            date_restitution_complete = restorative_justice_update_data.get(
                "date_restitution_complete",
                restorative_justice.date_restitution_complete,
            )

            restorative_justice_update_data["status"] = cls._determine_status(
                restitution_details, date_restitution_complete
            )

        restorative_justice.update(restorative_justice_update_data, commit=False)
        session.flush()
        return restorative_justice

    @classmethod
    @with_session
    def get_by_inspection_id(cls, inspection_id, session=None):
        """Find all restorative justices by inspection id."""
        return (
            session.query(cls)
            .filter(
                and_(
                    cls.inspection_id == inspection_id,
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                )
            )
            .all()
        )

    @classmethod
    @with_session
    def get_by_restorative_justice_number(
        cls, restorative_justice_number, session=None
    ):
        """Find restorative justice by restorative justice number."""
        return (
            session.query(cls)
            .filter(
                and_(
                    cls.restorative_justice_number == restorative_justice_number,
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                )
            )
            .first()
        )

    @classmethod
    @with_session
    def get_count_by_project_nd_case_file_id(
        cls, project_id: int, case_file_id: int, session=None
    ):
        """Get count of restorative justices by project and case file id."""
        return (
            session.query(cls)
            .join(InspectionModel, cls.inspection_id == InspectionModel.id)
            .filter(
                and_(
                    InspectionModel.project_id == project_id,
                    InspectionModel.case_file_id == case_file_id,
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                )
            )
            .count()
        )

    @classmethod
    @with_session
    def does_restorative_justice_exists_by_requirement_ids(
        cls,
        requirement_ids: list[int],
        restorative_justice_id: int = None,
        session=None,
    ):
        """Check if a restorative justice exists by requirement ids."""
        query = (
            session.query(cls)
            .join(
                RestorativeJusticeInspectionRequirementMap,
                cls.id
                == RestorativeJusticeInspectionRequirementMap.restorative_justice_id,
            )
            .filter(
                and_(
                    RestorativeJusticeInspectionRequirementMap.inspection_requirement_id.in_(
                        requirement_ids
                    ),
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                    RestorativeJusticeInspectionRequirementMap.is_active.is_(True),
                    RestorativeJusticeInspectionRequirementMap.is_deleted.is_(False),
                )
            )
        )

        if restorative_justice_id:
            query = query.filter(cls.id != restorative_justice_id)

        return query.first() is not None
