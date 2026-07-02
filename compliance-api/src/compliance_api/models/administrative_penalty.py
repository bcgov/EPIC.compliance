"""Administrative Penalty Model."""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import and_, not_, or_

from compliance_api.models.base_model import BaseModelVersioned, db
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.inspection import InspectionRequirement
from compliance_api.models.utils import with_session
from compliance_api.utils.constant import DELETE_DIC_PARAMS
from compliance_api.utils.util import get_sorted_numbers_from_generated_code


class ReferralStatusEnum(Enum):
    """Enum for Administrative Penalty Referral Status."""

    DRAFTING = "Drafting"
    REFERRED_TO_AMP_UNIT = "Referred to AMP Unit"
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
    def get_by_requirement_id(cls, requirement_id):
        """Get inspection requirements by requirement id."""
        return cls.query.filter_by(
            inspection_requirement_id=requirement_id, is_deleted=False, is_active=True
        ).first()

    @classmethod
    def get_by_administrative_penalty_id(cls, administrative_penalty_id):
        """Get inspection requirements by administrative penalty id."""
        return cls.query.filter_by(
            administrative_penalty_id=administrative_penalty_id,
            is_deleted=False,
            is_active=True,
        ).all()

    @classmethod
    def get_by_inspection_and_administrative_penalty_id(
        cls, inspection_id, administrative_penalty_id
    ):
        """Get inspection requirement maps by inspection id and administrative penalty id."""
        return (
            cls.query.join(
                InspectionRequirement,
                InspectionRequirement.id == cls.inspection_requirement_id,
            )
            .filter(
                InspectionRequirement.inspection_id == inspection_id,
                cls.administrative_penalty_id == administrative_penalty_id,
                cls.is_deleted.is_(False),
                cls.is_active.is_(True),
                InspectionRequirement.is_deleted.is_(False),
                InspectionRequirement.is_active.is_(True),
            )
            .all()
        )

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

    @property
    def is_closed(self):
        """
        Check if the administrative penalty is in a closed state.

        An administrative penalty is considered closed if:
        - Referral status is CEB_NOT_PROCEEDING
        - Referral status is REFERRED_TO_DM and a decision has been made

        Returns:
            bool: True if the administrative penalty is closed, False otherwise
        """
        return self.referral_status == ReferralStatusEnum.CEB_NOT_PROCEEDING or (
            self.referral_status == ReferralStatusEnum.REFERRED_TO_DM
            and self.decision is not None
        )

    @classmethod
    def get_closed_conditions(cls):
        """Get the SQLAlchemy conditions for closed administrative penalties.

        Used for database queries to filter closed administrative penalties.

        An administrative penalty is considered closed if:
        - CEB_NOT_PROCEEDING status
        - REFERRED_TO_DM status with a decision made

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: OR conditions for closed state
        """
        return or_(
            cls.referral_status == ReferralStatusEnum.CEB_NOT_PROCEEDING,
            and_(
                cls.referral_status == ReferralStatusEnum.REFERRED_TO_DM,
                cls.decision.isnot(None),
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
    def get_by_inspection_id(cls, inspection_id, sort_by: str = None):
        """Find all administrative penalties that have entries in the requirement map for the given inspection."""
        query = (
            cls.query.join(
                AdministrativePenaltyInspectionRequirementMap,
                AdministrativePenaltyInspectionRequirementMap.administrative_penalty_id
                == cls.id,
            )
            .join(
                InspectionRequirement,
                InspectionRequirement.id
                == AdministrativePenaltyInspectionRequirementMap.inspection_requirement_id,
            )
            .filter(
                InspectionRequirement.inspection_id == inspection_id,
                AdministrativePenaltyInspectionRequirementMap.is_active.is_(True),
                AdministrativePenaltyInspectionRequirementMap.is_deleted.is_(False),
                cls.is_deleted.is_(False),
            )
            .distinct()
        )

        if sort_by and hasattr(cls, sort_by):
            query = query.order_by(getattr(cls, sort_by).asc())
        else:
            query = query.order_by(cls.created_date.desc())

        return query.all()

    @classmethod
    def get_by_administrative_penalty_number(cls, administrative_penalty_number):
        """Find administrative penalty by administrative penalty number."""
        return cls.query.filter_by(
            administrative_penalty_number=administrative_penalty_number,
            is_deleted=False,
        ).first()

    @classmethod
    def get_latest_administrative_penalty_number_count(
        cls, case_file_id: int, project_id: int, pattern
    ):
        """Return administrative penalty numbers for the case file/project.

        Only numbers matching the provided pattern are returned.
        """
        rows = (
            db.session.query(cls.administrative_penalty_number)
            .join(InspectionModel, InspectionModel.id == cls.inspection_id)
            .join(CaseFileModel, CaseFileModel.id == InspectionModel.case_file_id)
            .filter(
                CaseFileModel.project_id == project_id,
                InspectionModel.case_file_id == case_file_id,
                cls.administrative_penalty_number.op("~")(pattern),
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .all()
        )
        return get_sorted_numbers_from_generated_code(rows, "AP")

    @classmethod
    def get_administrative_penalties_by_case_files(
        cls, case_file_ids: list[int], open_aps_only: bool = False
    ):
        """Get all administrative penalties by case file ids.

        Args:
            case_file_ids: List of case file IDs
            open_aps_only: If True, only return open administrative penalties
        Returns:
            List of AdministrativePenalty objects
        """
        query = cls.query.join(InspectionModel, InspectionModel.id == cls.inspection_id)

        filters = [
            InspectionModel.case_file_id.in_(case_file_ids),
            cls.is_active.is_(True),
            cls.is_deleted.is_(False),
            InspectionModel.is_active.is_(True),
            InspectionModel.is_deleted.is_(False),
        ]

        # Add open AP filter condition if requested
        if open_aps_only:
            filters.append(not_(cls.get_closed_conditions()))

        return query.filter(*filters).order_by(cls.created_date.desc()).all()
