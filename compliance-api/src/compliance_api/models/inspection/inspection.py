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
"""Inspection Model."""
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, and_, func
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS
from compliance_api.utils.util import get_sorted_numbers_from_generated_code

from ..base_model import BaseModelVersioned, db
from ..case_file import CaseFile as CaseFileModel
from ..inspection_record import InspectionRecord
from ..inspection_record_approval import InspectionRecordApproval
from ..staff_user import StaffUser
from ..utils import with_session
from .inspection_enum import InspectionStatusEnum


class Inspection(BaseModelVersioned):
    """Inspection Model Class."""

    __tablename__ = "inspections"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the inspection",
    )
    ir_number = Column(
        String(50),
        comment="The unique inspection record number",
        unique=False,
        index=True,
        nullable=False,
    )
    case_file_id = Column(
        Integer,
        ForeignKey("case_files.id", name="inspections_case_file_id_case_file_id_fkey"),
        nullable=False,
        comment="The unique identifier of the case file associated with the inspection",
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", name="inspections_project_id_projects_id_fkey"),
        nullable=True,
        comment="The unique identifier of the project associated with the inspection",
    )
    project_description = Column(
        String,
        nullable=True,
        comment="The description of the project associated with the inspection",
    )
    location_description = Column(
        String, nullable=True, comment="The location details of the inspection"
    )
    utm = Column(String, nullable=True, comment="The UTM value of the location")
    primary_officer_id = Column(
        Integer,
        ForeignKey(
            "staff_users.id", name="inspection_primary_officer_id_staff_id_fkey"
        ),
        nullable=False,
        comment="The primary officer who created the inspection",
    )
    start_date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="The inspection start date",
    )
    end_date = Column(
        DateTime(timezone=True), nullable=False, comment="The inspection end date"
    )
    debrief_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="The debrief date of the inspection",
    )
    initiation_id = Column(
        Integer,
        ForeignKey(
            "inspection_initiation_options.id",
            name="inspection_initiation_id_inspection_initiation_options_id_fkey",
        ),
        nullable=False,
    )
    is_history = Column(Boolean, nullable=True)
    inspection_status = Column(Enum(InspectionStatusEnum), nullable=True)
    project_status_id = Column(
        Integer,
        nullable=True,
    )

    initiation = relationship(
        "InspectionInitiationOption", foreign_keys=[initiation_id], lazy="joined"
    )
    case_file = relationship("CaseFile", foreign_keys=[case_file_id], lazy="joined")
    other_officers = relationship(
        "InspectionOfficer",
        back_populates="inspection",
        lazy="select",
    )
    attendance = relationship(
        "InspectionAttendance", back_populates="inspection", lazy="select"
    )
    agencies = relationship(
        "InspectionAgency", back_populates="inspection", lazy="select"
    )
    first_nations = relationship(
        "InspectionFirstnation", back_populates="inspection", lazy="select"
    )
    types = relationship(
        "InspectionType",
        back_populates="inspection",
        lazy="selectin",
        primaryjoin="and_(InspectionType.inspection_id == Inspection.id, "
        "InspectionType.is_active == True, "
        "InspectionType.is_deleted == False)",
    )
    inspection_requirements = relationship(
        "InspectionRequirement",
        back_populates="inspection",
        lazy="select",
        primaryjoin="and_(InspectionRequirement.inspection_id == Inspection.id, "
        "InspectionRequirement.is_active == True, "
        "InspectionRequirement.is_deleted == False)",
        order_by="InspectionRequirement.sort_order",
    )
    project = relationship("Project", foreign_keys=[project_id], lazy="joined")
    primary_officer = relationship(
        "StaffUser", foreign_keys=[primary_officer_id], lazy="joined"
    )
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    __table_args__ = (
        Index(
            "unique_non_deleted_ir_number",  # Index name
            "ir_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    def get_count_by_project_nd_case_file_id(cls, project_id: int, case_file_id: int):
        """Return the number of inspection based on the project and case file id."""
        result = (
            cls.query.join(CaseFileModel, Inspection.case_file_id == CaseFileModel.id)
            .with_entities(
                Inspection.case_file_id,
                CaseFileModel.project_id,
                func.count(Inspection.id).label(  # pylint: disable=not-callable
                    "inspection_count"
                ),
            )
            .filter(
                CaseFileModel.project_id == project_id,
                Inspection.case_file_id == case_file_id,
                Inspection.is_active.is_(True),
                Inspection.is_deleted.is_(False),
            )
            .group_by(Inspection.case_file_id, CaseFileModel.project_id)
            .first()
        )
        return result.inspection_count if result else 0

    @classmethod
    def get_latest_ir_number_count(cls, case_file_id: int, project_id: int, pattern):
        """Return all ir numbers based on the case file and project id where irno follows the given pattern."""
        rows = (
            db.session.query(cls.ir_number)
            .filter(
                cls.case_file_id == case_file_id,
                cls.project_id == project_id,
                cls.ir_number.op("~")(pattern),
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .all()
        )
        return get_sorted_numbers_from_generated_code(rows, "IR")

    @classmethod
    @with_session
    def create_inspection(cls, inspection_obj, session=None):
        """Persist inspection in database."""
        inspection = Inspection(**inspection_obj)
        session.add(inspection)
        session.flush()
        return inspection

    @classmethod
    @with_session
    def update_inspection(cls, inspection_id, inspection_data, session=None):
        """Update inspection."""
        query = cls.query.filter_by(id=inspection_id)
        inspection: Inspection = query.first()
        if not inspection or inspection.is_deleted:
            return None
        inspection.update(inspection_data, commit=False)
        session.flush()
        return inspection

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete inspection by case file id."""
        inspections = cls.query.filter_by(
            case_file_id=case_file_id, is_deleted=False
        ).all()
        for inspection in inspections:
            inspection.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_inspection(cls, inspection_id, session=None):
        """Delete inspection."""
        inspection = cls.query.filter_by(id=inspection_id, is_deleted=False).first()
        inspection.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    def get_by_ir_number(cls, ir_number):
        """Retrieve inspection by ir number."""
        return cls.query.filter_by(ir_number=ir_number, is_deleted=False).first()

    @classmethod
    def get_all_inspections(cls):
        """Retrieve all inspections with their latest approval status and ir_progress."""
        # Subquery to get the latest approval record for each inspection record
        latest_approval_subquery = (
            db.session.query(
                InspectionRecordApproval.inspection_record_id,
                func.max(InspectionRecordApproval.created_date).label("latest_date"),
            )
            .filter(
                InspectionRecordApproval.is_active.is_(True),
                InspectionRecordApproval.is_deleted.is_(False),
            )
            .group_by(InspectionRecordApproval.inspection_record_id)
            .subquery()
        )

        # Main query with filters for active and non-deleted records
        query = (
            db.session.query(cls)
            .outerjoin(
                InspectionRecord,
                and_(
                    cls.id == InspectionRecord.inspection_id,
                    InspectionRecord.is_deleted.is_(False),
                    InspectionRecord.is_active.is_(True),
                ),
            )
            .outerjoin(
                latest_approval_subquery,
                latest_approval_subquery.c.inspection_record_id == InspectionRecord.id,
            )
            .outerjoin(
                InspectionRecordApproval,
                (InspectionRecordApproval.inspection_record_id == InspectionRecord.id)
                & (
                    InspectionRecordApproval.created_date
                    == latest_approval_subquery.c.latest_date
                ),
            )
            .outerjoin(
                StaffUser,
                InspectionRecordApproval.approved_by_id == StaffUser.id,
            )
            .filter(cls.is_deleted.is_(False), cls.is_active.is_(True))
            .add_columns(
                InspectionRecord.ir_progress,
                InspectionRecordApproval.approval_status,
                StaffUser.auth_user_guid,
                StaffUser.first_name,
                StaffUser.last_name,
                StaffUser.id,
            )
        )

        # Convert results to list of dictionaries
        results = []
        for result in query.all():
            inspection = result[0]
            inspection.ir_progress = result[1]
            inspection.approval_status = result[2]
            if result[3] is not None:
                inspection.approved_by = {
                    "auth_user_guid": result[3],
                    "first_name": result[4],
                    "last_name": result[5],
                    "id": result[6],
                }
            results.append(inspection)

        return results
