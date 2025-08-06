"""Complaint source contact model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..type import EncryptedType
from ..utils import with_session
from .complaint import Complaint as ComplaintModel


class ComplaintSourceContact(BaseModelVersioned):
    """Complaint source contact."""

    __tablename__ = "complaint_source_contacts"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the source contact",
    )
    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id", name="contact_complaint_id_complaints_id"),
        nullable=False,
    )
    description = Column(
        String(), nullable=True, comment="Any description about the contact"
    )
    full_name = Column(
        EncryptedType(), nullable=True, comment="The full name of the contact person"
    )
    email = Column(
        EncryptedType(),
        nullable=True,
        comment="The email address of the contact person",
    )
    phone = Column(
        EncryptedType(), nullable=True, comment="The phone number of the contact person"
    )
    comment = Column(EncryptedType(), nullable=True, comment="The comments")
    complaint = relationship(
        "Complaint",
        foreign_keys=[complaint_id],
        lazy="joined",
    )

    @classmethod
    @with_session
    def create_contact(cls, contact_data, session=None):
        """Persist contact info in database."""
        contact = ComplaintSourceContact(**contact_data)
        session.add(contact)
        session.flush()
        return contact

    @classmethod
    @with_session
    def update_contact(cls, complaint_id, contact_data, session=None):
        """Update contact."""
        query = cls.query.filter_by(complaint_id=complaint_id, is_deleted=False)
        contact: ComplaintSourceContact = query.first()
        if not contact:
            return None
        contact.update(contact_data, commit=False)
        session.flush()
        return contact

    @classmethod
    def get_by_complaint(cls, complaint_id):
        """Get source contact by complaint id."""
        return cls.query.filter_by(complaint_id=complaint_id, is_deleted=False).first()

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete the source contact based on case file."""
        contacts = (
            cls.query.join(ComplaintModel)
            .filter(
                ComplaintModel.case_file_id == case_file_id,
                ComplaintSourceContact.is_deleted is False,
            )
            .all()
        )
        contact_ids = [contact.id for contact in contacts]
        if contact_ids:
            contact_details = cls.query.filter(
                ComplaintSourceContact.id.in_(contact_ids)
            ).all()
            for contact in contact_details:
                contact.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_by_complaint(cls, complaint_id, session=None):
        """Delete by complaint id."""
        contact = cls.query.filter(
            ComplaintSourceContact.complaint_id == complaint_id
        ).first()
        contact.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
