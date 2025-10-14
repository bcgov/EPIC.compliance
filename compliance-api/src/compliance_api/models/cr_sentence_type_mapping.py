"""Charge Recommendation Sentence Type Mapping Model."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from compliance_api.models.base_model import BaseModelVersioned
from compliance_api.models.utils import with_session
from compliance_api.utils.constant import DELETE_DIC_PARAMS


class CRSentenceTypeMapping(BaseModelVersioned):
    """Charge Recommendation Sentence Type Mapping Model."""

    __tablename__ = "cr_sentence_type_mappings"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    charge_recommendation_id = Column(
        Integer,
        ForeignKey(
            "charge_recommendations.id",
            name="cr_sentence_type_mapping_cr_id_fkey",
        ),
        nullable=False,
        comment="The charge recommendation ID",
    )
    sentence_type_option_id = Column(
        Integer,
        ForeignKey(
            "sentence_type_options.id",
            name="cr_sentence_type_mapping_sentence_type_id_fkey",
        ),
        nullable=False,
        comment="The sentence type option ID",
    )
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)

    # Relationships
    charge_recommendation = relationship(
        "ChargeRecommendation", back_populates="sentence_type_mappings"
    )
    sentence_type_option = relationship(
        "SentenceTypeOption", foreign_keys=[sentence_type_option_id], lazy="joined"
    )

    @classmethod
    @with_session
    def create_mapping(cls, mapping_data, session=None):
        """Create sentence type mapping."""
        mapping = cls(**mapping_data)
        session.add(mapping)
        session.commit()
        return mapping

    @classmethod
    @with_session
    def get_by_charge_recommendation_id(cls, charge_recommendation_id, session=None):
        """Get all sentence type mappings by charge recommendation ID."""
        return (
            session.query(cls)
            .filter(
                cls.charge_recommendation_id == charge_recommendation_id,
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .all()
        )

    @classmethod
    @with_session
    def delete_by_charge_recommendation_id(cls, charge_recommendation_id, session=None):
        """Delete all sentence type mappings by charge recommendation ID."""
        session.query(cls).filter(
            cls.charge_recommendation_id == charge_recommendation_id
        ).update(DELETE_DIC_PARAMS)
        session.commit()

    @classmethod
    @with_session
    def bulk_delete(
        cls,
        charge_recommendation_id: int,
        sentence_type_option_ids: list[int],
        session=None,
    ):
        """Delete sentence type mappings by IDs."""
        query = session.query(cls) if session else cls.query
        mappings = query.filter(
            cls.charge_recommendation_id == charge_recommendation_id,
            cls.sentence_type_option_id.in_(sentence_type_option_ids),
        )
        for mapping in mappings:
            mapping.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls,
        charge_recommendation_id: int,
        sentence_type_option_ids: list[int],
        session=None,
    ):
        """Insert sentence type mappings."""
        mapping_data = [
            cls(
                charge_recommendation_id=charge_recommendation_id,
                sentence_type_option_id=sentence_type_option_id,
            )
            for sentence_type_option_id in sentence_type_option_ids
        ]
        session.add_all(mapping_data)
        session.flush()
        return mapping_data
