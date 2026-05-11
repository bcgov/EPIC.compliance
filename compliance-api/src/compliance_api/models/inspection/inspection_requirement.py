"""InspectionRequirement Model."""

import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..utils import with_session


class InspectionRequirementTypeEnum(enum.Enum):
    """Type of inspection requirements."""

    REQ = "Requirement"
    REG = "Regulatory Considerations"


class InspectionRequirement(BaseModelVersioned):
    """InspectionRequirementModel."""

    __tablename__ = "inspection_requirements"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id", name="inspection_requirements_inspection_id_fkey"),
        nullable=False,
        index=True,
        comment="The unique identifier of the inspection",
    )
    summary = Column(String, nullable=False, comment="The summary of the requirement")
    topic_id = Column(
        Integer,
        ForeignKey("topics.id", name="inspection_requirements_topic_id_fkey"),
        nullable=False,
        comment="The topic of the requirement",
    )
    agency_id = Column(
        Integer,
        ForeignKey("agencies.id", name="inspection_req_agency_id"),
        nullable=True,
        comment="Associated agency if the type is regulatory considerations",
    )
    req_type = Column(
        Enum(InspectionRequirementTypeEnum),
        nullable=False,
        default=InspectionRequirementTypeEnum.REG,
    )
    compliance_finding_id = Column(
        Integer,
        ForeignKey(
            "compliance_finding_options.id",
            name="inspection_req_compliance_finding_fkey",
        ),
        nullable=True,
        comment="Compliance finding of the requirement",
    )
    findings = Column(String, nullable=True, comment="The findings of the requirement")
    sort_order = Column(Integer, nullable=False, comment="The order of requirements")
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)

    inspection = relationship(
        "Inspection",
        back_populates="inspection_requirements",
        lazy="joined",
    )
    topic = relationship("Topic", foreign_keys=[topic_id], lazy="joined")
    compliance_finding = relationship(
        "ComplianceFindingOption", foreign_keys=[compliance_finding_id], lazy="joined"
    )
    agency = relationship("Agency", foreign_keys=[agency_id], lazy="joined")
    requirement_source_details = relationship(
        "InspectionReqSourceDetail",
        back_populates="inspection_requirement",
        lazy="selectin",
        primaryjoin="and_(InspectionReqSourceDetail.requirement_id == InspectionRequirement.id, "
        "InspectionReqSourceDetail.is_active == True, "
        "InspectionReqSourceDetail.is_deleted == False)",
        order_by="InspectionReqSourceDetail.id.asc()",
    )
    enforcement_actions = relationship(
        "InspectionReqEnforcementMap",
        back_populates="requirement",
        lazy="selectin",
        primaryjoin="and_(InspectionReqEnforcementMap.requirement_id == InspectionRequirement.id, "
        "InspectionReqEnforcementMap.is_active == True, "
        "InspectionReqEnforcementMap.is_deleted == False)",
    )
    orders_requirement_maps = relationship(
        "OrderInspectionRequirementMap",
        back_populates="inspection_requirement",
        lazy="selectin",
        primaryjoin="and_(OrderInspectionRequirementMap.inspection_requirement_id == InspectionRequirement.id, "
        "OrderInspectionRequirementMap.is_active == True, "
        "OrderInspectionRequirementMap.is_deleted == False)",
        order_by="OrderInspectionRequirementMap.id.asc()",
    )

    warning_letter_requirement_maps = relationship(
        "WarningLetterInspectionRequirementMap",
        back_populates="inspection_requirement",
        lazy="selectin",
        primaryjoin="and_(WarningLetterInspectionRequirementMap.inspection_requirement_id == InspectionRequirement.id, "
        "WarningLetterInspectionRequirementMap.is_active == True, "
        "WarningLetterInspectionRequirementMap.is_deleted == False)",
        order_by="WarningLetterInspectionRequirementMap.id.asc()",
    )

    violation_ticket_requirement_maps = relationship(
        "ViolationTicketInspectionRequirementMap",
        back_populates="inspection_requirement",
        lazy="selectin",
        primaryjoin="and_(ViolationTicketInspectionRequirementMap.inspection_requirement_id == InspectionRequirement.id, "  # noqa: E501
        "ViolationTicketInspectionRequirementMap.is_active == True, "
        "ViolationTicketInspectionRequirementMap.is_deleted == False)",
        order_by="ViolationTicketInspectionRequirementMap.id.asc()",
    )

    @property
    def sorted_enforcement_actions(self):
        """Return enforcement actions with ORDER first."""
        return sorted(
            self.enforcement_actions,
            key=lambda x: (x.enforcement_action_id != EnforcementActionOptionEnum.ORDER.value, x.id)
        )

    @classmethod
    @with_session
    def create_requirement(cls, requirement_obj, session=None):
        """Persist inspection requirement in database."""
        requirement = InspectionRequirement(**requirement_obj)
        session.add(requirement)
        session.flush()
        return requirement

    @classmethod
    @with_session
    def delete_requirement(cls, requirement_id, session=None):
        """Delete the requirement."""
        requirement = cls.find_by_id(requirement_id)
        if not requirement:
            return None
        requirement.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
        return requirement

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Get requirements by inspection id."""
        return (
            cls.query.filter_by(
                inspection_id=inspection_id, is_deleted=False, is_active=True
            )
            .order_by(cls.sort_order)
            .all()
        )

    @classmethod
    @with_session
    def update_requirement(cls, requirement_id, requirement_data, session=None):
        """Update inspection requirement."""
        query = cls.query.filter_by(id=requirement_id)
        requirement: InspectionRequirement = query.first()
        if not requirement or requirement.is_deleted:
            return None
        requirement.update(requirement_data, commit=False)
        session.flush()
        return requirement

    @classmethod
    def get_requirement_by_ids(cls, requirement_ids):
        """Get requirements by ids."""
        return cls.query.filter(
            cls.id.in_(requirement_ids),
            cls.is_deleted.is_(False),
            cls.is_active.is_(True),
        ).all()
