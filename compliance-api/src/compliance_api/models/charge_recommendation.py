"""Charge Recommendation Model."""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index, Integer, String, and_, or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from compliance_api.models.base_model import BaseModelVersioned
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.utils import with_session
from compliance_api.utils.constant import DELETE_DIC_PARAMS


class ChargeRecommendationStatusEnum(Enum):
    """Enum for Charge Recommendation Status."""

    DRAFTING = "Drafting"
    DEPUTY_REVIEW = "Deputy Review"
    SUBMITTED_TO_CROWN_COUNSEL = "Submitted to Crown Counsel"
    CEB_NOT_PROCEEDING = "CEB Not Proceeding"


class ChargeDecisionEnum(Enum):
    """Enum for Charge Recommendation Decision."""

    APPROVED = "Approved"
    NOT_PROCEEDING = "Not Proceeding"


class CourtDecisionEnum(Enum):
    """Enum for Charge Recommendation Court Decision."""

    GUILTY = "Guilty"
    NOT_GUILTY = "Not Guilty"
    WITHDRAWN = "Withdrawn"


# Removed SentenceTypeEnum - sentence_type is now a text field


class ChargeRecommendationInspectionRequirementMap(BaseModelVersioned):
    """ChargeRecommendationInspectionRequirementMap Model."""

    __tablename__ = "charge_recommendation_inspection_requirement_maps"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    charge_recommendation_id = Column(
        Integer,
        ForeignKey(
            "charge_recommendations.id",
            name="charge_recommendation_inspection_map_recommendation_id_fkey",
        ),
    )
    inspection_requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id",
            name="charge_recommendation_inspection_map_requirement_id_fkey",
        ),
    )

    # Relationships
    charge_recommendation = relationship(
        "ChargeRecommendation", back_populates="charge_recommendation_requirement_maps"
    )
    inspection_requirement = relationship(
        "InspectionRequirement", foreign_keys=[inspection_requirement_id], lazy="joined"
    )

    @classmethod
    @with_session
    def create_charge_recommendation_requirement_map(
        cls, charge_recommendation_requirement_map_data, session=None
    ):
        """Create the charge recommendation requirement map."""
        charge_recommendation_requirement_map = cls(
            **charge_recommendation_requirement_map_data
        )
        session.add(charge_recommendation_requirement_map)
        session.commit()
        return charge_recommendation_requirement_map

    @classmethod
    @with_session
    def get_by_charge_recommendation_id(cls, charge_recommendation_id, session=None):
        """Find all charge recommendation requirement maps by charge recommendation id."""
        return (
            session.query(cls)
            .filter(
                and_(
                    cls.charge_recommendation_id == charge_recommendation_id,
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                )
            )
            .all()
        )

    @classmethod
    @with_session
    def delete_by_charge_recommendation_id(cls, charge_recommendation_id, session=None):
        """Delete all charge recommendation requirement maps by charge recommendation id."""
        session.query(cls).filter(
            cls.charge_recommendation_id == charge_recommendation_id
        ).update(DELETE_DIC_PARAMS)
        session.commit()

    @classmethod
    @with_session
    def bulk_delete(
        cls,
        charge_recommendation_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Delete inspection requirement ids by id per charge recommendation."""
        query = session.query(cls) if session else cls.query
        requirements = query.filter(
            cls.charge_recommendation_id == charge_recommendation_id,
            cls.inspection_requirement_id.in_(inspection_requirement_ids),
        )
        for requirement in requirements:
            requirement.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls,
        charge_recommendation_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert inspection requirements per charge recommendation."""
        charge_recommendation_inspection_requirement_map_data = [
            ChargeRecommendationInspectionRequirementMap(
                **{
                    "charge_recommendation_id": charge_recommendation_id,
                    "inspection_requirement_id": inspection_requirement_id,
                }
            )
            for inspection_requirement_id in inspection_requirement_ids
        ]
        session.add_all(charge_recommendation_inspection_requirement_map_data)
        session.flush()
        return charge_recommendation_inspection_requirement_map_data


class ChargeRecommendation(BaseModelVersioned):
    """Charge Recommendation Model."""

    __tablename__ = "charge_recommendations"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    inspection_id = Column(
        ForeignKey("inspections.id", name="cr_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    charge_recommendation_number = Column(String)
    status = Column(
        SqlEnum(ChargeRecommendationStatusEnum),
        nullable=True,
        comment="Status of the charge recommendation",
        default=ChargeRecommendationStatusEnum.DRAFTING,
    )
    date_to_crown_counsel = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the charge recommendation was sent to crown counsel",
    )
    charge_decision = Column(
        SqlEnum(ChargeDecisionEnum),
        nullable=True,
        comment="Decision on the charge recommendation",
    )
    charge_decision_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the charge decision was made",
    )
    court_file_number = Column(
        String,
        nullable=True,
        comment="Court file number",
    )
    court_decision = Column(
        SqlEnum(CourtDecisionEnum),
        nullable=True,
        comment="Court decision on the charge recommendation",
    )
    court_decision_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the court decision was made",
    )
    sentence_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the sentence was given",
    )
    sentence_description = Column(
        String,
        nullable=True,
        comment="Description of the fine",
    )
    # Relationships
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="joined")
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    charge_recommendation_requirement_maps = relationship(
        "ChargeRecommendationInspectionRequirementMap",
        back_populates="charge_recommendation",
        lazy="select",
        primaryjoin=(
            "and_(ChargeRecommendationInspectionRequirementMap.charge_recommendation_id == "
            "ChargeRecommendation.id, "
            "ChargeRecommendationInspectionRequirementMap.is_active == True, "
            "ChargeRecommendationInspectionRequirementMap.is_deleted == False)"
        ),
    )
    sentence_type_mappings = relationship(
        "CRSentenceTypeMapping",
        back_populates="charge_recommendation",
        lazy="select",
        primaryjoin=(
            "and_(CRSentenceTypeMapping.charge_recommendation_id == "
            "ChargeRecommendation.id, "
            "CRSentenceTypeMapping.is_active == True, "
            "CRSentenceTypeMapping.is_deleted == False)"
        ),
    )

    __table_args__ = (
        Index(
            "unique_non_deleted_charge_recommendation_number",  # Index name
            "charge_recommendation_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @property
    def is_closed(self):
        """
        Check if the charge recommendation is in a closed state.

        A charge recommendation is considered closed if any of these conditions are true:
        - Status is CEB_NOT_PROCEEDING
        - Charge decision exists and is NOT_PROCEEDING
        - Sentence date exists (case has been sentenced)

        Returns:
            bool: True if the charge recommendation is closed, False otherwise
        """
        return (
            self.status == ChargeRecommendationStatusEnum.CEB_NOT_PROCEEDING
            or (
                self.charge_decision is not None
                and self.charge_decision == ChargeDecisionEnum.NOT_PROCEEDING
            )
            or self.sentence_date is not None
        )

    @classmethod
    def get_closed_conditions(cls):
        """Get the SQLAlchemy conditions for closed charge recommendations.

        Used for database queries to filter closed charge recommendations.

        Returns:
            sqlalchemy.sql.elements.BooleanClauseList: OR conditions for closed state
        """
        return or_(
            cls.status == ChargeRecommendationStatusEnum.CEB_NOT_PROCEEDING,
            and_(
                cls.charge_decision.isnot(None),
                cls.charge_decision == ChargeDecisionEnum.NOT_PROCEEDING,
            ),
            cls.sentence_date.isnot(None),
        )

    @classmethod
    @with_session
    def create_charge_recommendation(cls, charge_recommendation_data, session=None):
        """Create the charge recommendation."""
        charge_recommendation = cls(**charge_recommendation_data)
        session.add(charge_recommendation)
        session.commit()
        return charge_recommendation

    @classmethod
    @with_session
    def update_charge_recommendation(
        cls, charge_recommendation_id, charge_recommendation_update_data, session=None
    ):
        """Update the charge recommendation."""
        charge_recommendation_update_data.pop("inspection_requirement_ids", None)
        query = session.query(cls) if session else cls.query
        charge_recommendation = query.filter_by(id=charge_recommendation_id).first()
        if not charge_recommendation:
            return None

        charge_recommendation.update(
            charge_recommendation_update_data, commit=not session
        )
        return charge_recommendation

    @classmethod
    @with_session
    def get_by_inspection_id(cls, inspection_id, session=None):
        """Find all charge recommendations by inspection id."""
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
    def get_by_charge_recommendation_number(
        cls, charge_recommendation_number, session=None
    ):
        """Find charge recommendation by charge recommendation number."""
        return (
            session.query(cls)
            .filter(
                and_(
                    cls.charge_recommendation_number == charge_recommendation_number,
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
        """Get count of charge recommendations by project and case file id."""
        result = (
            session.query(cls)
            .join(InspectionModel, InspectionModel.id == cls.inspection_id)
            .join(CaseFileModel, CaseFileModel.id == InspectionModel.case_file_id)
            .with_entities(
                InspectionModel.case_file_id,
                CaseFileModel.project_id,
                func.count(cls.id).label(  # pylint: disable=not-callable
                    "charge_recommendation_count"
                ),
            )
            .filter(
                and_(
                    CaseFileModel.project_id == project_id,
                    InspectionModel.case_file_id == case_file_id,
                    cls.is_active.is_(True),
                    cls.is_deleted.is_(False),
                )
            )
            .group_by(InspectionModel.case_file_id, CaseFileModel.project_id)
            .first()
        )
        return result.charge_recommendation_count if result else 0
