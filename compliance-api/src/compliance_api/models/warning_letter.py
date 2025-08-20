"""Warning Letter Model."""

from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from compliance_api.models.base_model import BaseModelVersioned
from compliance_api.models.case_file import CaseFile as CaseFileModel
from compliance_api.models.inspection import Inspection as InspectionModel
from compliance_api.models.utils import with_session
from compliance_api.utils.constant import DELETE_DIC_PARAMS


class WarningLetterStatusEnum(Enum):
    """Enum for Warning Letter Status."""

    CREATED = "Created"
    ISSUED = "Issued"


class WarningLetterProgressEnum(Enum):
    """Enum for Warning Letter Progress."""

    DRAFTING = "Drafting"
    DEPUTY_REVIEW = "Deputy Review"
    APPROVED = "Approved"
    ISSUED = "Issued"


class WarningLetterInspectionRequirementMap(BaseModelVersioned):
    """WarningLetterInspectionRequirementMap Model."""

    __tablename__ = "warning_letter_inspection_requirement_maps"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    warning_letter_id = Column(
        Integer,
        ForeignKey(
            "warning_letters.id", name="warning_letter_inspection_map_order_id_fkey"
        ),
    )
    inspection_requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id",
            name="order_inspection_map_requirement_id_fkey",
        ),
    )
    warning_letter = relationship(
        "WarningLetter", foreign_keys=[warning_letter_id], lazy="joined"
    )
    inspection_requirement = relationship(
        "InspectionRequirement", foreign_keys=[inspection_requirement_id], lazy="joined"
    )

    @classmethod
    def get_by_warning_letter_id(cls, warning_letter_id):
        """Get inspection requirements by warning letter id."""
        return cls.query.filter_by(
            warning_letter_id=warning_letter_id, is_deleted=False, is_active=True
        ).all()

    @classmethod
    @with_session
    def bulk_delete(
        cls, warning_letter_id: int, inspection_requirement_ids: list[int], session=None
    ):
        """Delete inspection requirement ids by id per warning letter."""
        query = session.query(cls) if session else cls.query
        requirements = query.filter(
            cls.warning_letter_id == warning_letter_id,
            cls.inspection_requirement_id.in_(inspection_requirement_ids),
        )
        for requirement in requirements:
            requirement.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def delete_by_warning_letter(cls, warning_letter_id: int, session=None):
        """Delete warning letter."""
        query = session.query(cls) if session else cls.query
        maps = query.filter_by(warning_letter_id=warning_letter_id).all()
        for map_item in maps:
            map_item.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls, warning_letter_id: int, inspection_requirement_ids: list[int], session=None
    ):
        """Insert inspection requirements per warning letter."""
        warning_letter_inspection_requirement_map_data = [
            WarningLetterInspectionRequirementMap(
                **{
                    "warning_letter_id": warning_letter_id,
                    "inspection_requirement_id": inspection_requirement_id,
                }
            )
            for inspection_requirement_id in inspection_requirement_ids
        ]
        session.add_all(warning_letter_inspection_requirement_map_data)
        session.flush()


class WarningLetter(BaseModelVersioned):
    """Warning Letter Model."""

    __tablename__ = "warning_letters"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    inspection_id = Column(
        ForeignKey("inspections.id", name="ir_inspection_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection",
    )
    warning_letter_number = Column(String)
    content = Column(String, nullable=True, comment="Content of the warning letter")
    date_issued = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the warning letter was issued",
    )
    intended_issuance_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date when the warning letter was intended to be issued",
    )
    issuing_officer_id = Column(Integer, ForeignKey("staff_users.id"), nullable=False)
    issuing_officer = relationship(
        "StaffUser", foreign_keys=[issuing_officer_id], lazy="joined"
    )
    status = Column(
        SqlEnum(WarningLetterStatusEnum),
        nullable=True,
        comment="Status of the warning letter",
        default=WarningLetterStatusEnum.CREATED,
    )
    progress = Column(
        SqlEnum(WarningLetterProgressEnum),
        nullable=True,
        comment="Progress of the warning letter",
        default=WarningLetterProgressEnum.DRAFTING,
    )

    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="joined")
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    warning_letter_requirement_maps = relationship(
        "WarningLetterInspectionRequirementMap",
        back_populates="warning_letter",
        lazy="select",
        primaryjoin="and_(WarningLetterInspectionRequirementMap.warning_letter_id == WarningLetter.id, "
        "WarningLetterInspectionRequirementMap.is_active == True, "
        "WarningLetterInspectionRequirementMap.is_deleted == False)",
    )
    warning_letter_approvals = relationship(
        "WarningLetterApproval",
        back_populates="warning_letter",
        lazy="select",
        primaryjoin="and_(WarningLetterApproval.warning_letter_id == WarningLetter.id, "
        "WarningLetterApproval.is_active == True, "
        "WarningLetterApproval.is_deleted == False)",
        order_by="desc(WarningLetterApproval.created_date)",
    )
    __table_args__ = (
        Index(
            "unique_non_deleted_warning_letter_number",  # Index name
            "warning_letter_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    @with_session
    def create_warning_letter(cls, warning_letter_data, session=None):
        """Create the warning letter."""
        warning_letter = WarningLetter(**warning_letter_data)
        session.add(warning_letter)
        session.flush()
        return warning_letter

    @classmethod
    @with_session
    def update_warning_letter(
        cls, warning_letter_id, warning_letter_update_data, session=None
    ):
        """Update the warning letter."""
        warning_letter = cls.find_by_id(warning_letter_id)
        if not warning_letter:
            return None
        warning_letter.update(warning_letter_update_data, commit=False)
        session.flush()
        return warning_letter

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Find all warning letters by inspection id."""
        return cls.query.filter_by(
            inspection_id=inspection_id, is_deleted=False, is_active=True
        ).all()

    @classmethod
    def get_by_warning_letter_number(cls, warning_letter_number):
        """Find warning letter by warning letter number."""
        return cls.query.filter_by(
            warning_letter_number=warning_letter_number,
            is_deleted=False,
            is_active=True,
        ).first()

    @classmethod
    def get_count_by_project_nd_case_file_id(cls, project_id: int, case_file_id: int):
        """Get count of warning letters by project and case file id."""
        result = (
            cls.query.join(InspectionModel, InspectionModel.id == cls.inspection_id)
            .join(CaseFileModel, CaseFileModel.id == InspectionModel.case_file_id)
            .with_entities(
                InspectionModel.case_file_id,
                CaseFileModel.project_id,
                func.count(cls.id).label(
                    "warning_letter_count"
                ),  # pylint: disable=not-callable
            )
            .filter(
                CaseFileModel.project_id == project_id,
                InspectionModel.case_file_id == case_file_id,
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .group_by(InspectionModel.case_file_id, CaseFileModel.project_id)
            .first()
        )
        return result.warning_letter_count if result else 0

    @classmethod
    def does_warning_letter_exists_by_requirement_ids(
        cls, requirement_ids: list[int], warning_letter_id: int = None
    ):
        """Check if a warning letter exists by requirement ids."""
        query = cls.query.join(
            WarningLetterInspectionRequirementMap,
            WarningLetterInspectionRequirementMap.warning_letter_id == cls.id,
        ).filter(
            WarningLetterInspectionRequirementMap.inspection_requirement_id.in_(
                requirement_ids
            ),
            cls.is_deleted.is_(False),
        )
        if warning_letter_id:
            query = query.filter(cls.id != warning_letter_id)
        return query.first()
