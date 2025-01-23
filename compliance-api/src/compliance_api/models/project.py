"""Project Model."""

from sqlalchemy import Column, Integer, String

from .base_model import BaseModelVersioned


class Project(BaseModelVersioned):
    """Project Model Class."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
