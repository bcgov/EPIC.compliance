"""Model to handle unapproved projects of inspection."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..base_model import BaseModelVersioned


class ComplaintUnapprovedProject(BaseModelVersioned):
    """Unapproved project model for complaint."""

    __tablename__ = "complaint_unapproved_projects"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    name = Column(String, nullable=False, comment="The title of the unapproved project")
    authorization = Column(
        String, nullable=True, comment="The details of authorization for the project"
    )
    type = Column(String, nullable=True, comment="The type of project")
    sub_type = Column(String, nullable=True, comment="The sub type of the project")
    regulated_party = Column(
        String,
        nullable=True,
        comment="The details of regulated party associated with the project",
    )
    complaint_id = Column(
        Integer,
        ForeignKey(
            "complaints.id", name="complaint_unapproved_projects_complaint_id_fkey"
        ),
        nullable=False,
    )
    complaint = relationship("Complaint", foreign_keys=[complaint_id], lazy="select")

    @classmethod
    def create_project_info(cls, project_data, session=None):
        """Persist project info in database."""
        unapproved_project = ComplaintUnapprovedProject(**project_data)
        if session:
            session.add(unapproved_project)
            session.flush()
        else:
            unapproved_project.save()
        return unapproved_project

    @classmethod
    def get_by_complaint_id(cls, complaint_id):
        """Find unapproved project info based on complaint_id."""
        return cls.query.filter_by(
            complaint_id=complaint_id, is_deleted=False
        ).first()
