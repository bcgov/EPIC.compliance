"""InspectionRequirementDetailDocument Model."""

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..utils import with_session
from .inspection_req_source_detail import InspectionReqSourceDetail


class InspectionReqDetailDocument(BaseModelVersioned):
    """InspectionReqDetailDocument Model."""

    __tablename__ = "inspection_req_detail_documents"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    req_detail_id = Column(
        Integer,
        ForeignKey(
            "inspection_req_source_details.id",
            name="inspection_req_detail_documents_req_detail_id_fkey",
        ),
        comment="The unique identifier of the requirement detail",
        nullable=False,
    )
    appendix_id = Column(
        Integer,
        ForeignKey(
            "appendices.id", name="inspection_req_detail_documents_appendix_id_fkey"
        ),
        comment="The unique identifier of the appendix",
        nullable=True,
    )
    document_type_id = Column(
        Integer,
        ForeignKey(
            "document_types.id", name="inspection_req_detail_documents_document_id_fkey"
        ),
        comment="The unique identifier of the document type",
        nullable=False,
    )
    document_title = Column(String, nullable=True, comment="The title of the document")
    section_number = Column(
        String,
        nullable=True,
        comment="The highlighted section number in the uploaded document",
    )
    section_title = Column(
        String,
        nullable=True,
        comment="The title of the section associated with the document",
    )
    description = Column(
        String, nullable=True, comment="Additional description of the document"
    )
    is_deleted = Column(Boolean, nullable=False, default=False)
    requirement_source_detail = relationship(
        "InspectionReqSourceDetail",
        back_populates="documents",
        lazy="select",
        uselist=False,
    )
    document_type = relationship(
        "DocumentType", foreign_keys=[document_type_id], lazy="select"
    )
    appendix = relationship("Appendix", foreign_keys=[appendix_id], lazy="joined")
    images = relationship(
        "InspectionRequirementDetailDocImage",
        foreign_keys="InspectionRequirementDetailDocImage.req_detail_doc_id",
        lazy="select",
        primaryjoin="and_(InspectionRequirementDetailDocImage.req_detail_doc_id == InspectionReqDetailDocument.id, "
        "InspectionRequirementDetailDocImage.is_active == True, "
        "InspectionRequirementDetailDocImage.is_deleted == False)",
        order_by="InspectionRequirementDetailDocImage.id.asc()",
    )

    __table_args__ = (
        Index(
            "unique_non_deleted_req_detail_document_title",  # Index name
            "req_detail_id",
            "document_title",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    @with_session
    def create_doc_detail(cls, doc_detail_obj, session=None):
        """Persist doc detail in database."""
        doc_detail = InspectionReqDetailDocument(**doc_detail_obj)
        session.add(doc_detail)
        session.flush()
        return doc_detail

    @classmethod
    @with_session
    def update_doc_detail(cls, doc_detail_id, doc_detail_data, session=None):
        """Update requirement doc detail."""
        query = cls.query.filter_by(id=doc_detail_id)
        doc_detail: InspectionReqDetailDocument = query.first()
        if not doc_detail or doc_detail.is_deleted:
            return None
        doc_detail.update(doc_detail_data, commit=False)
        session.flush()
        return doc_detail

    @classmethod
    @with_session
    def delete_req_doc_details_by_ids(cls, req_doc_detail_ids, session=None):
        """Delete the requirement doc details by req_doc_detail_ids."""
        details = cls.query.filter(
            InspectionReqDetailDocument.id.in_(req_doc_detail_ids)
        ).all()
        for detail in details:
            detail.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_by_requirement_id(cls, requirement_id, session=None):
        """Delete requirement doc details by requirement_id."""
        requirement_details = (
            session.query(InspectionReqSourceDetail)
            .filter_by(requirement_id=requirement_id, is_deleted=False)
            .all()
        )
        requirement_detail_ids = [detail.id for detail in requirement_details]
        details = cls.query.filter(cls.req_detail_id.in_(requirement_detail_ids)).all()
        for detail in details:
            detail.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
