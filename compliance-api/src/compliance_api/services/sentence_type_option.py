"""Sentence Type Option Service."""

from compliance_api.models.sentence_type_option import SentenceTypeOption as SentenceTypeOptionModel


class SentenceTypeOptionService:
    """Sentence Type Option Service class."""

    @classmethod
    def get_all_active(cls):
        """Get all active sentence type options."""
        return SentenceTypeOptionModel.get_all_active()

    @classmethod
    def find_by_name(cls, name):
        """Find sentence type option by name."""
        return SentenceTypeOptionModel.find_by_name(name)
