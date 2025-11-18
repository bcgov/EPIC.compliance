# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Complaint Model."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..case_file import CaseFile as CaseFileModel
from ..utils import with_session


class ComplaintStatusEnum(enum.Enum):
    """Inspection Status."""

    OPEN = "Open"
    CLOSED = "Closed"


class Complaint(BaseModelVersioned):
    """Complaint Model Class."""

    __tablename__ = "complaints"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the complaints",
    )
    complaint_number = Column(
        String(50),
        comment="The unique complaint number",
        unique=False,
        index=True,
        nullable=False,
    )
    case_file_id = Column(
        Integer,
        ForeignKey("case_files.id", name="complaints_case_file_id_case_file_id_fkey"),
        nullable=False,
        comment="The unique identifier of the case file associated with the complaint",
    )
    concern_description = Column(
        String, nullable=False, comment="The concern description of the complaint"
    )
    location_description = Column(
        String, nullable=True, comment="The location details of the complaint"
    )
    primary_officer_id = Column(
        Integer,
        ForeignKey(
            "staff_users.id", name="inspection_primary_officer_id_staff_id_fkey"
        ),
        nullable=True,
        comment="The primary officer who created the inspection",
    )
    date_received = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="The complaint received date",
    )
    requirement_source_id = Column(
        Integer,
        ForeignKey(
            "requirement_sources.id",
            name="requirement_source_id_requirement_sources_id",
        ),
        nullable=True,
        comment="The selected requirement source of the complaint",
    )
    requirement_source_description = Column(
        String,
        nullable=True,
        comment="The requirement source description of the complaint",
    )
    topic_id = Column(
        Integer,
        ForeignKey("topics.id", name="complaints_topic_id_topics_id"),
        nullable=True,
        comment="The topic of the complaint",
    )
    source_type_id = Column(
        Integer,
        ForeignKey(
            "complaint_sources.id", name="complaints_source_id_complaint_sources_id"
        ),
        nullable=False,
        comment="The selected source of the complaint",
    )
    source_agency_id = Column(
        Integer,
        ForeignKey(
            "agencies.id",
            name="complaints_agency_id_agencies_id",
        ),
        nullable=True,
        comment="The unique Id of the agency if the complaint source is selected as agency",
    )
    source_first_nation_id = Column(
        Integer,
        nullable=True,
        comment="The unique Id of the first nation if the complaint source is selected as first nation",
    )
    status = Column(Enum(ComplaintStatusEnum), nullable=False)
    resolution_id = Column(
        Integer,
        ForeignKey(
            "complaint_resolutions.id",
            name="complaint_resolution_id_complaint_resolutions_id",
        ),
        nullable=True,
        comment="The unique Id of the complaint resolution",
    )
    resolution_agency_id = Column(
        Integer,
        ForeignKey("agencies.id", name="complaint_resolution_agency_id_agencies_id"),
        nullable=True,
        comment="The unique Id of the agency if the complaint resolution is selected as agency",
    )
    case_file = relationship("CaseFile", foreign_keys=[case_file_id], lazy="joined")
    requirement_source = relationship(
        "RequirementSource", foreign_keys=[requirement_source_id], lazy="joined"
    )
    source_type = relationship(
        "ComplaintSource", foreign_keys=[source_type_id], lazy="joined"
    )
    agency = relationship("Agency", foreign_keys=[source_agency_id], lazy="joined")
    primary_officer = relationship(
        "StaffUser", foreign_keys=[primary_officer_id], lazy="joined"
    )
    case_file = relationship("CaseFile", foreign_keys=[case_file_id], lazy="joined")
    topic = relationship("Topic", foreign_keys=[topic_id], lazy="joined")
    order_detail = relationship(
        "ComplaintReqOrderDetail",
        foreign_keys="ComplaintReqOrderDetail.complaint_id",
        back_populates="complaint",
        lazy="joined",
        uselist=False,
        cascade="all, delete-orphan",
    )
    resolution = relationship(
        "ComplaintResolution", foreign_keys=[resolution_id], lazy="joined"
    )
    resolution_agency = relationship(
        "Agency", foreign_keys=[resolution_agency_id], lazy="joined"
    )
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)

    __table_args__ = (
        Index(
            "unique_non_deleted_complaint_file_number",  # Index name
            "complaint_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    def get_count_by_project_nd_case_file_id(cls, project_id: int, case_file_id: int):
        """Return the number of complaint based on the project and case file id."""
        result = (
            cls.query.with_entities(
                Complaint.case_file_id,
                CaseFileModel.project_id,
                func.count(Complaint.id).label(  # pylint: disable=not-callable
                    "complaint_count"
                ),
            )
            .join(CaseFileModel, CaseFileModel.id == Complaint.case_file_id)
            .filter(
                CaseFileModel.project_id == project_id,
                Complaint.case_file_id == case_file_id,
                Complaint.is_active.is_(True),
                Complaint.is_deleted.is_(False),
            )
            .group_by(Complaint.case_file_id, CaseFileModel.project_id)
            .first()
        )
        return result.complaint_count if result else 0

    @classmethod
    @with_session
    def create_complaint(cls, complaint_obj, session=None):
        """Persist inspection in database."""
        complaint = Complaint(**complaint_obj)
        session.add(complaint)
        session.flush()
        return complaint

    @classmethod
    @with_session
    def update_complaint(cls, complaint_id, complaint_data, session=None):
        """Update inspection."""
        query = cls.query.filter_by(id=complaint_id)
        complaint: Complaint = query.first()
        if not complaint or complaint.is_deleted:
            return None
        complaint.update(complaint_data, commit=False)
        session.flush()
        return complaint

    @classmethod
    @with_session
    def change_status(cls, complaint_id, update_data, session=None):
        """Update the complaint status and related fields."""
        complaint = cls.query.filter(cls.id == complaint_id).first()
        complaint.update(update_data, commit=False)
        session.flush()

    @classmethod
    def get_by_complaint_number(cls, complaint_number):
        """Retrieve complaint by number."""
        return cls.query.filter_by(
            complaint_number=complaint_number, is_deleted=False
        ).first()

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete complaint by case file."""
        complaints = cls.query.filter(
            Complaint.case_file_id == case_file_id, Complaint.is_deleted.is_(False)
        ).all()
        for complaint in complaints:
            complaint.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_complaint(cls, complaint_id, session=None):
        """Delete complaint."""
        complaint = cls.query.filter(Complaint.id == complaint_id).first()
        complaint.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
