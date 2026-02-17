"""Model to handle the image uploads in inspection requirement detail documents."""

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..utils import with_session
from .inspection_req_detail_doc import InspectionReqDetailDocument
from .inspection_req_source_detail import InspectionReqSourceDetail


class InspectionRequirementDetailDocImage(BaseModelVersioned):
    """InspectionRequirementDetailDocImage."""

    __tablename__ = "inspection_req_detail_doc_images"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    req_detail_doc_id = Column(
        Integer,
        ForeignKey(
            "inspection_req_detail_documents.id",
            name="inspection_req_detail_doc_images_req_detail_doc_id_fkey",
        ),
        nullable=False,
        index=True,
        comment="The requirement detail document id",
    )
    original_file_name = Column(
        String, nullable=False, comment="The original filename of the uploaded image"
    )
    relative_url = Column(
        String, nullable=False, comment="The actual url of the final uploaded image"
    )

    is_deleted = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index(
            "unique_non_deleted_req_detail_doc_relative_url",  # Index name
            "req_detail_doc_id",
            "relative_url",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    @with_session
    def bulk_insert(cls, images, session=None):
        """Insert images."""
        session.add_all(images)
        session.flush()

    @classmethod
    @with_session
    def create_image(cls, image_obj, session=None):
        """Persist the image object."""
        img_obj = InspectionRequirementDetailDocImage(**image_obj)
        session.add(img_obj)
        session.flush()
        return img_obj

    @classmethod
    @with_session
    def update_image(cls, image_id, image_data, session=None):
        """Update image details."""
        query = cls.query.filter_by(id=image_id)
        image_detail: InspectionRequirementDetailDocImage = query.first()
        if not image_detail or image_detail.is_deleted:
            return None
        image_detail.update(image_data, commit=False)
        session.flush()
        return image_detail

    @classmethod
    def find_all_images_by_req_detail_doc_id(cls, req_detail_doc_id):
        """Get all images by req_detail_doc_id."""
        return (
            cls.query.filter_by(
                req_detail_doc_id=req_detail_doc_id,
                is_active=True,
                is_deleted=False,
            )
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def find_all_req_detail_doc_images_by_req(cls, requirement_id):
        """Get all document images by requirement_id via joins."""
        return (
            cls.query.join(
                InspectionReqDetailDocument,
                cls.req_detail_doc_id == InspectionReqDetailDocument.id,
            )
            .join(
                InspectionReqSourceDetail,
                InspectionReqDetailDocument.req_detail_id
                == InspectionReqSourceDetail.id,
            )
            .filter(
                InspectionReqSourceDetail.requirement_id == requirement_id,
                InspectionReqSourceDetail.is_active.is_(True),
                InspectionReqSourceDetail.is_deleted.is_(False),
                InspectionReqDetailDocument.is_active.is_(True),
                InspectionReqDetailDocument.is_deleted.is_(False),
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def find_image_by_url(cls, req_detail_doc_id, relative_url):
        """Get image object by url."""
        return cls.query.filter(
            cls.req_detail_doc_id == req_detail_doc_id,
            cls.relative_url == relative_url,
            cls.is_active.is_(True),
            cls.is_deleted.is_(False),
        ).first()

    @classmethod
    @with_session
    def delete_image(cls, image_id, session=None):
        """Delete the image."""
        image = cls.find_by_id(image_id)
        if not image:
            return None
        image.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
        return image
