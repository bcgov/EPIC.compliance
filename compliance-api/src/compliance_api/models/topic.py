"""Staff topic model class.

Manages the topic
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String

from .base_model import BaseModelVersioned


class Topic(BaseModelVersioned):
    """Definition of the Topic entity."""

    __tablename__ = "topics"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    name = Column(String(150), nullable=False, comment="Name of the topic")

    @classmethod
    def get_by_name(cls, topic: str) -> Topic:
        """Get topic by name."""
        return cls.query.filter_by(name=topic).first()
