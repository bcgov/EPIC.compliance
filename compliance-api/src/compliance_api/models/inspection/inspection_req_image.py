"""Model to handle the image uploads in inspection requirements."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..utils import with_session
from .inspection_enum import ImageTypeEnum


class InspectionRequirementImage(BaseModelVersioned):
    """InspectionRequirementImage."""

    __tablename__ = "inspection_req_images"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id", name="inspection_req_images_req_id_fkey"
        ),
        nullable=False,
        index=True,
        comment="The requirement id",
    )
    sort_order = Column(
        Integer, nullable=False, comment="The order of images. grouped by the type."
    )
    image_type = Column(Enum(ImageTypeEnum), nullable=False)
    original_file_name = Column(
        String, nullable=False, comment="The original filename of the uploaded image"
    )
    date_taken = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="The time of the image when it is captured",
    )
    taken_by_id = Column(
        Integer,
        ForeignKey("staff_users.id", name="inspection_images_taken_by_fkey"),
        nullable=False,
        comment="The unique identifier of the staff who captured the image",
    )
    caption = Column(String, nullable=True, comment="The caption of the image")
    relative_url = Column(
        String, nullable=False, comment="The actual url of the final uploaded image"
    )
    taken_by = relationship("StaffUser", foreign_keys=[
                            taken_by_id], lazy="joined")
    inspection_requirement = relationship(
        "InspectionRequirement", foreign_keys=[requirement_id], lazy="select"
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
        img_obj = InspectionRequirementImage(**image_obj)
        session.add(img_obj)
        session.flush()
        return img_obj

    @classmethod
    @with_session
    def update_image(cls, image_id, image_data, session=None):
        """Update image details."""
        query = cls.query.filter_by(id=image_id)
        image_detail: InspectionRequirementImage = query.first()
        if not image_detail or image_detail.is_deleted:
            return None
        image_detail.update(image_data, commit=False)
        session.flush()
        return image_detail

    @classmethod
    def find_all_images(cls, requirement_id, image_type: ImageTypeEnum):
        """Get all images by requirement_id."""
        return (
            cls.query.filter_by(
                requirement_id=requirement_id,
                image_type=image_type,
                is_active=True,
                is_deleted=False,
            )
            .order_by(cls.sort_order)
            .all()
        )

    @classmethod
    def find_image_by_url(cls, requirement_id, relative_url, image_type):
        """Get image object by url."""
        return cls.query.filter(
            cls.requirement_id == requirement_id,
            func.lower(cls.relative_url) == relative_url.lower(),
            cls.image_type == image_type,
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

    @classmethod
    def get_all_images_by_inspection(cls, inspection_id):
        """Get all images for a specific inspection.

        Args:
            inspection_id (int): The ID of the inspection

        Returns:
            list: List of InspectionRequirementImage objects
        """
        from .inspection_requirement import InspectionRequirement

        return (
            cls.query
            .join(
                InspectionRequirement,
                cls.requirement_id == InspectionRequirement.id
            )
            .filter(
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
                InspectionRequirement.inspection_id == inspection_id,
                InspectionRequirement.is_deleted.is_(False),
                InspectionRequirement.is_active.is_(True)
            )
            .order_by(
                InspectionRequirement.id,
                cls.image_type,
                cls.sort_order
            )
            .all()
        )
