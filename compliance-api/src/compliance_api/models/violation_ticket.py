"""ViolationTicket model."""

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from .base_model import BaseModelVersioned
from .case_file import CaseFile as CaseFileModel
from .inspection import Inspection as InspectionModel
from .utils import with_session


class ViolationTicketStatusEnum(enum.Enum):
    """Violation ticket status enum."""

    ISSUED = "Issued"
    PAID = "Paid"
    DISPUTED = "Disputed"
    DEEMED_GUILTY = "Deemed Guilty"


class ViolationTicketInspectionRequirementMap(BaseModelVersioned):
    """ViolationTicketInspectionRequirementMap Model."""

    __tablename__ = "violation_ticket_inspection_requirement_maps"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    violation_ticket_id = Column(
        Integer, ForeignKey("violation_tickets.id", name="vt_inspection_map_vt_id_fkey")
    )
    inspection_requirement_id = Column(
        Integer,
        ForeignKey(
            "inspection_requirements.id",
            name="vt_inspection_map_requirement_id_fkey",
        ),
    )

    # Relationships
    violation_ticket = relationship(
        "ViolationTicket",
        back_populates="violation_ticket_requirement_maps",
        lazy="select",
    )
    inspection_requirement = relationship(
        "InspectionRequirement",
        back_populates="violation_ticket_requirement_maps",
        lazy="select",
    )

    @classmethod
    @with_session
    def create_bulk(cls, violation_ticket_requirement_maps: list, session=None):
        """Create multiple violation ticket requirement maps."""
        violation_ticket_requirement_map_objects = []
        for violation_ticket_requirement_map in violation_ticket_requirement_maps:
            violation_ticket_requirement_map_obj = cls(
                **violation_ticket_requirement_map
            )
            violation_ticket_requirement_map_objects.append(
                violation_ticket_requirement_map_obj
            )
        session.add_all(violation_ticket_requirement_map_objects)
        session.commit()
        return violation_ticket_requirement_map_objects

    @classmethod
    @with_session
    def delete_by_violation_ticket_id(cls, violation_ticket_id: int, session=None):
        """Delete all violation ticket requirement maps by violation ticket id."""
        query = session.query(cls) if session else cls.query
        maps = query.filter(
            cls.violation_ticket_id == violation_ticket_id,
            cls.is_deleted.is_(False),
            cls.is_active.is_(True),
        )
        for map_item in maps:
            map_item.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    def get_by_violation_ticket_id(cls, violation_ticket_id: int):
        """Get all violation ticket requirement maps by violation ticket id."""
        return cls.get_by_params(
            {"violation_ticket_id": violation_ticket_id}, default_filters=True
        )

    @classmethod
    @with_session
    def bulk_delete(
        cls,
        violation_ticket_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Delete inspection requirement ids by id per violation ticket."""
        query = session.query(cls) if session else cls.query
        requirements = query.filter(
            cls.violation_ticket_id == violation_ticket_id,
            cls.inspection_requirement_id.in_(inspection_requirement_ids),
        )
        for requirement in requirements:
            requirement.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(
        cls,
        violation_ticket_id: int,
        inspection_requirement_ids: list[int],
        session=None,
    ):
        """Insert inspection requirements per violation ticket."""
        violation_ticket_inspection_requirement_map_data = [
            ViolationTicketInspectionRequirementMap(
                **{
                    "violation_ticket_id": violation_ticket_id,
                    "inspection_requirement_id": inspection_requirement_id,
                }
            )
            for inspection_requirement_id in inspection_requirement_ids
        ]
        session.add_all(violation_ticket_inspection_requirement_map_data)
        session.flush()


class ViolationTicket(BaseModelVersioned):
    """ViolationTicket model."""

    __tablename__ = "violation_tickets"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    vt_number = Column(String, nullable=False, comment="System generated VT number")
    date_issued = Column(
        DateTime(timezone=True), nullable=True, comment="Date the ticket was issued"
    )
    ticket_number = Column(String, nullable=False, comment="Manual ticket number")
    fine_amount = Column(Numeric(10, 2), nullable=True, comment="Fine amount")
    status = Column(
        Enum(ViolationTicketStatusEnum), nullable=True, comment="Ticket status"
    )
    status_date = Column(DateTime(timezone=True), nullable=True, comment="Status date")
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id"),
        nullable=False,
        comment="Associated inspection",
    )
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)

    # Relationships
    inspection = relationship("Inspection", foreign_keys=[inspection_id], lazy="select")
    violation_ticket_requirement_maps = relationship(
        "ViolationTicketInspectionRequirementMap",
        back_populates="violation_ticket",
        lazy="select",
        primaryjoin="and_(ViolationTicketInspectionRequirementMap.violation_ticket_id == ViolationTicket.id, "
        "ViolationTicketInspectionRequirementMap.is_active == True, "
        "ViolationTicketInspectionRequirementMap.is_deleted == False)",
    )

    __table_args__ = (
        Index(
            "unique_non_deleted_vt_number",
            "vt_number",
            unique=True,
            postgresql_where=(is_deleted is False),
        ),
        Index(
            "unique_non_deleted_ticket_number",
            "ticket_number",
            unique=True,
            postgresql_where=(is_deleted is False),
        ),
    )

    @property
    def is_closed(self):
        """
        Check if the violation ticket is in a closed state.

        A violation ticket is considered closed if its status is:
        - PAID: Ticket has been paid
        - DISPUTED: Ticket is under dispute
        - DEEMED_GUILTY: Ticket has been deemed guilty

        Returns:
            bool: True if the violation ticket is closed, False otherwise
        """
        closed_statuses = [
            ViolationTicketStatusEnum.PAID,
            ViolationTicketStatusEnum.DISPUTED,
            ViolationTicketStatusEnum.DEEMED_GUILTY,
        ]
        return self.status in closed_statuses

    @classmethod
    def get_closed_statuses(cls):
        """
        Get list of violation ticket statuses that are considered closed.

        Returns:
            list: List of ViolationTicketStatusEnum values for closed statuses
        """
        return [
            ViolationTicketStatusEnum.PAID,
            ViolationTicketStatusEnum.DISPUTED,
            ViolationTicketStatusEnum.DEEMED_GUILTY,
        ]

    @classmethod
    def get_non_deletable_statuses(cls):
        """
        Get list of violation ticket statuses where deletion is not allowed.

        Returns:
            list: List of ViolationTicketStatusEnum values for non-deletable statuses
        """
        return [
            ViolationTicketStatusEnum.PAID,
            ViolationTicketStatusEnum.DISPUTED,
        ]

    @classmethod
    @with_session
    def create(cls, violation_ticket_data: dict, session=None):
        """Create a new violation ticket."""
        violation_ticket = cls(**violation_ticket_data)
        session.add(violation_ticket)
        session.commit()
        return violation_ticket

    @classmethod
    @with_session
    def update_violation_ticket(
        cls, violation_ticket_id, violation_ticket_data, session=None
    ):
        """Update violation ticket."""
        violation_ticket = cls.find_by_id(violation_ticket_id)
        if violation_ticket:
            for key, value in violation_ticket_data.items():
                setattr(violation_ticket, key, value)
            session.commit()
        return violation_ticket

    @classmethod
    def get_count_by_project_and_case_file_id(cls, project_id: int, case_file_id: int):
        """Get count of violation tickets by project and case file id."""
        query = (
            cls.query.join(InspectionModel, cls.inspection_id == InspectionModel.id)
            .join(CaseFileModel, InspectionModel.case_file_id == CaseFileModel.id)
            .filter(
                CaseFileModel.project_id == project_id,
                CaseFileModel.id == case_file_id,
                cls.is_deleted.is_(False),
            )
        )
        return query.count()

    @classmethod
    def does_violation_ticket_exists_by_requirement_ids(
        cls, requirement_ids: list[int], violation_ticket_id: int = None
    ):
        """Check if a violation ticket exists by requirement ids."""
        query = cls.query.join(
            ViolationTicketInspectionRequirementMap,
            ViolationTicketInspectionRequirementMap.violation_ticket_id == cls.id,
        ).filter(
            ViolationTicketInspectionRequirementMap.inspection_requirement_id.in_(
                requirement_ids
            ),
            cls.is_deleted.is_(False),
        )
        if violation_ticket_id:
            query = query.filter(cls.id != violation_ticket_id)
        return query.first()

    @classmethod
    def get_by_vt_number(cls, vt_number: str):
        """Find a violation ticket by vt number."""
        return cls.get_by_params({"vt_number": vt_number}, default_filters=True)

    @classmethod
    def get_by_inspection_id(cls, inspection_id):
        """Find all violation tickets by inspection id."""
        return cls.query.filter(
            cls.inspection_id == inspection_id, cls.is_deleted.is_(False)
        ).all()

    @classmethod
    def get_violation_tickets_by_case_files(cls, case_file_ids: list[int]):
        """Get violation tickets by case file ids."""
        query = (
            cls.query.join(InspectionModel, cls.inspection_id == InspectionModel.id)
            .join(CaseFileModel, InspectionModel.case_file_id == CaseFileModel.id)
            .filter(
                CaseFileModel.id.in_(case_file_ids),
                cls.is_deleted.is_(False),
            )
        )
        return query.all()

    def to_dict(self):
        """Convert violation ticket to dictionary."""
        return {
            "id": self.id,
            "vt_number": self.vt_number,
            "date_issued": self.date_issued,
            "ticket_number": self.ticket_number,
            "fine_amount": float(self.fine_amount) if self.fine_amount else None,
            "status": self.status.value if self.status else None,
            "status_date": self.status_date,
            "inspection_id": self.inspection_id,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "is_closed": self.is_closed,
        }
