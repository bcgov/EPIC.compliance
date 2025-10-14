"""Sentence Type Option Model."""

from compliance_api.models.option_base_model import OptionModel
from compliance_api.models.utils import with_session


class SentenceTypeOption(OptionModel):
    """Sentence Type Option Model."""

    __tablename__ = "sentence_type_options"

    @classmethod
    @with_session
    def get_all_active(cls, session=None):
        """Get all active sentence type options."""
        return (
            session.query(cls)
            .filter(cls.is_active.is_(True), cls.is_deleted.is_(False))
            .order_by(cls.sort_order)
            .all()
        )

    @classmethod
    @with_session
    def find_by_name(cls, name, session=None):
        """Find sentence type option by name."""
        return (
            session.query(cls)
            .filter(
                cls.name == name, cls.is_active.is_(True), cls.is_deleted.is_(False)
            )
            .first()
        )
