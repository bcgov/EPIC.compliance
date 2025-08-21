"""Administrative Penalty Model."""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from compliance_api.models.base_model import BaseModelVersioned
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.utils import with_session
from compliance_api.utils.constant import DELETE_DIC_PARAMS


class ReferralStatusEnum(Enum):
    """Enum for Administrative Penalty Referral Status."""

    DRAFTING = "Drafting"
    DEPUTY_REVIEW = "Deputy Review"
    CEB_NOT_PROCEEDING = "CEB Not Proceeding"
    REFERRED_TO_DM = "Referred to DM"


class DecisionEnum(Enum):
    """Enum for Administrative Penalty Decision."""

    AP_ISSUED = "AP Issued"
    AP_NOT_PROCEEDING = "AP Not Proceeding"


class AdministrativePenaltyInspectionRequirementMap(BaseModelVersioned):
    """AdministrativePenaltyInspectionRequirementMap Model."""

    __tablename__ = "administrative_penalty_inspection_requirement_maps"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    administrative_penalty_id = Column(
        Integer,
        ForeignKey(
            "administrative_penalties.id",
            name="administrative_penalty_inspection_map_penalty_id_fkey",
        ),
    )
    inspection_requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id",
            name="administrative_penalty_inspection_map_requirement_id_fkey",
        ),
    )
    administrative_penalty = relationship(
        "AdministrativePenalty",
        foreign_keys=[administrative_penalty_id],
        lazy="joined",
    )
    inspection_requirement = relationship(
        "InspectionRequirement", foreign_keys=[inspection_requirement_id], lazy="joined"
    )

    @classmethod
    def get_by_administrative_penalty_id(cls, administrative_penalty_id):
        """Get inspection requirements by administrative penalty id."""
        return cls.query.filter_by(
            administrative_penalty_id=administrative_penalty_id,
            is_deleted=False,
            is_active=True,
        ).all()

    @classmethod
    @with_session
    def bulk_delete(
        cls,
        administrative_penalty_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Delete inspection requirement ids by id per administrative penalty."""
        query = session.query(cls) if session else cls.query
        requirements = query.filter(
            cls.administrative_penalty_id == administrative_penalty_id,
            cls.inspection_requirement_id.in_(inspection_requirement_ids),
        )
        for requirement in requirements:
            requirement.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def delete_by_administrative_penalty(
        cls, administrative_penalty_id: int, session=None
    ):
        """Delete administrative penalty."""
        query = session.query(cls) if session else cls.query
        maps = query.filter_by(
            administrative_penalty_id=administrative_penalty_id
        ).all()
        for map_item in maps:
            map_item.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls,
        administrative_penalty_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert inspection requirements per administrative penalty."""
        administrative_penalty_inspection_requirement_map_data = [
            AdministrativePenaltyInspectionRequirementMap(
                **{
                    "administrative_penalty_id": administrative_penalty_id,
                    "inspection_requirement_id": inspection_requirement_id,
                }
            )
            for inspection_requirement_id in inspection_requirement_ids
        ]
        session.add_all(administrative_penalty_inspection_requirement_map_data)
        session.flush()
        return administrative_penalty_inspection_requirement_map_data


class AdministrativePenalty(BaseModelVersioned):
    """Administrative Penalty Model."""

    __tablename__ = "administrative_penalties"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    inspection_id = Column(
        ForeignKey("inspections.id", name="ap_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    administrative_penalty_number = Column(String)
    referral_status = Column(
        SqlEnum(ReferralStatusEnum),
        nullable=True,
        comment="Referral status of the administrative penalty",
        default=ReferralStatusEnum.DRAFTING,
    )
    date_referred = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the administrative penalty was referred to decision maker",
    )
    decision_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the decision was made",
    )
    decision = Column(
        SqlEnum(DecisionEnum),
        nullable=True,
        comment="Decision on the administrative penalty",
    )
    penalty_amount = Column(
        Numeric(precision=10, scale=2),
        nullable=True,
        comment="Amount of the administrative penalty",
    )
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="joined")
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    administrative_penalty_requirement_maps = relationship(
        "AdministrativePenaltyInspectionRequirementMap",
        back_populates="administrative_penalty",
        lazy="select",
        primaryjoin=(
            "and_(AdministrativePenaltyInspectionRequirementMap.administrative_penalty_id == "
            "AdministrativePenalty.id, "
            "AdministrativePenaltyInspectionRequirementMap.is_active == True, "
            "AdministrativePenaltyInspectionRequirementMap.is_deleted == False)"
        ),
    )
    __table_args__ = (
        Index(
            "unique_non_deleted_administrative_penalty_number",  # Index name
            "administrative_penalty_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    @with_session
    def create_administrative_penalty(cls, administrative_penalty_data, session=None):
        """Create the administrative penalty."""
        administrative_penalty = AdministrativePenalty(**administrative_penalty_data)
        session.add(administrative_penalty)
        session.flush()
        return administrative_penalty

    @classmethod
    @with_session
    def update_administrative_penalty(
        cls, administrative_penalty_id, administrative_penalty_update_data, session=None
    ):
        """Update the administrative penalty."""
        administrative_penalty_update_data.pop("inspection_requirement_ids", [])
        administrative_penalty = cls.find_by_id(administrative_penalty_id)
        if not administrative_penalty:
            return None

        administrative_penalty.update(administrative_penalty_update_data, commit=False)
        session.flush()

        return administrative_penalty

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Find all administrative penalties by inspection id."""
        return (
            cls.query.filter_by(inspection_id=inspection_id, is_deleted=False)
            .order_by(cls.created_date.desc())
            .all()
        )

    @classmethod
    def get_by_administrative_penalty_number(cls, administrative_penalty_number):
        """Find administrative penalty by administrative penalty number."""
        return cls.query.filter_by(
            administrative_penalty_number=administrative_penalty_number,
            is_deleted=False,
        ).first()

    @classmethod
    def get_count_by_project_nd_case_file_id(cls, project_id: int, case_file_id: int):
        """Get count of administrative penalties by project and case file id."""
        result = (
            cls.query.join(InspectionModel, InspectionModel.id == cls.inspection_id)
            .join(CaseFileModel, CaseFileModel.id == InspectionModel.case_file_id)
            .with_entities(
                InspectionModel.case_file_id,
                CaseFileModel.project_id,
                func.count(cls.id).label(
                    "administrative_penalty_count"
                ),  # pylint: disable=not-callable
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
        return result.administrative_penalty_count if result else 0

    @classmethod
    def does_administrative_penalty_exists_by_requirement_ids(
        cls, requirement_ids: list[int], administrative_penalty_id: int = None
    ):
        """Check if an administrative penalty exists by requirement ids."""
        query = cls.query.join(
            AdministrativePenaltyInspectionRequirementMap,
            AdministrativePenaltyInspectionRequirementMap.administrative_penalty_id
            == cls.id,
        ).filter(
            AdministrativePenaltyInspectionRequirementMap.inspection_requirement_id.in_(
                requirement_ids
            ),
            AdministrativePenaltyInspectionRequirementMap.is_deleted.is_(False),
            AdministrativePenaltyInspectionRequirementMap.is_active.is_(True),
            cls.is_deleted.is_(False),
        )

        if administrative_penalty_id:
            query = query.filter(cls.id != administrative_penalty_id)

        return query.first() is not None
