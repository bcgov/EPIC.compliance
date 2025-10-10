"""Sentence Type Option Schema."""

from marshmallow import EXCLUDE

from ..models.sentence_type_option import SentenceTypeOption
from .base_schema import AutoSchemaBase


class SentenceTypeOptionSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Schema for sentence type option model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to auto generate schema."""

        model = SentenceTypeOption
        load_instance = True
        include_fk = True
        unknown = EXCLUDE
