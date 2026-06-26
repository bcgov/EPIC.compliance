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
"""Case file Model."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, cast, func
from sqlalchemy.orm import joinedload, relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from .base_model import BaseModelVersioned
from .utils import with_session


class CaseFileInitiationEnum(enum.Enum):
    """Enum for case file initiation."""

    INSPECTION = 1
    COMPLIANT = 2
    OTHER = 3


class CaseFileStatusEnum(enum.Enum):
    """Casefile Status."""

    OPEN = "Open"
    CLOSED = "Closed"


class CaseFile(BaseModelVersioned):
    """Definition of CaseFile Entity."""

    __tablename__ = "case_files"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the case file",
    )
    project_description = Column(
        String,
        nullable=True,
        comment="The description of the project associated with the case file",
    )
    project_id = Column(
        Integer,
        ForeignKey("projects.id", name="case_files_project_id_projects_id_fkey"),
        nullable=True,
        comment="The unique identifier of the project associated with the case file",
    )
    date_created = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="The date on which the case file is created",
    )
    primary_officer_id = Column(
        Integer,
        ForeignKey("staff_users.id", name="case_files_primary_staff_id_fkey"),
        nullable=True,
        comment="The primary officer who created the case file",
    )
    initiation_id = Column(
        Integer,
        ForeignKey(
            "case_file_initiation_options.id",
            name="case_files_initation_id_case_file_initiation_options_id_fkey",
        ),
        nullable=False,
        comment="Case file initiation options",
    )
    case_file_number = Column(
        String,
        unique=False,
        index=True,
        nullable=False,
        comment="The unique case file number",
    )
    case_file_status = Column(Enum(CaseFileStatusEnum), nullable=True)
    link_case_file_id = Column(
        Integer,
        ForeignKey("case_files.id", name="casefile_link_link_case_file_id_fk"),
        nullable=True,
        comment="The case file to link to",
    )
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)

    primary_officer = relationship(
        "StaffUser", foreign_keys=[primary_officer_id], lazy="joined"
    )
    project = relationship("Project", foreign_keys=[project_id], lazy="joined")
    case_file_officers = relationship(
        "CaseFileOfficer",
        back_populates="case_file",
        lazy="select",
    )
    initiation = relationship(
        "CaseFileInitiationOption", foreign_keys=[initiation_id], lazy="joined"
    )

    __table_args__ = (
        Index(
            "unique_non_deleted_case_file_number",  # Index name
            "case_file_number",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    @with_session
    def create_case_file(cls, case_file_data, session=None):
        """Persist case file data in database."""
        case_file = CaseFile(**case_file_data)
        session.add(case_file)
        session.flush()
        return case_file

    @classmethod
    @with_session
    def update_case_file(cls, case_file_id, case_file_data, session=None):
        """Update the case file data in database."""
        query = cls.query.filter_by(id=case_file_id)
        case_file: CaseFile = query.first()
        if not case_file or case_file.is_deleted:
            return None
        case_file.update(case_file_data, commit=False)
        session.flush()
        return case_file

    @classmethod
    def get_by_file_number(cls, case_file_number):
        """Retrieve case file information based on given case file number."""
        return cls.query.filter_by(
            case_file_number=case_file_number, is_deleted=False
        ).first()

    @classmethod
    @with_session
    def change_status(
        cls, case_file_id, case_file_status: CaseFileStatusEnum, session=None
    ):
        """Update the case file status."""
        query = cls.query.filter(cls.id == case_file_id)
        case_file: CaseFile = query.first()
        if not case_file or case_file.is_deleted:
            return None
        case_file.update({"case_file_status": case_file_status}, commit=False)
        session.flush()
        return case_file

    @classmethod
    def get_by_project(cls, project_id: int):
        """Retrieve case files by project."""
        return cls.query.filter_by(project_id=project_id).all()

    @classmethod
    def get_max_case_file_number_by_year(cls, year: int):
        """Get the max case file number generated so far."""
        max_number = (
            cls.query.with_entities(
                func.max(
                    cast(
                        func.regexp_replace(cls.case_file_number, "[^0-9]", "", "g"),
                        Integer,
                    )
                ).label("max_number")
            )
            .filter(
                func.regexp_replace(cls.case_file_number, "[^0-9]", "", "g").op("~")(
                    f"^{year}[0-9]{{4}}$"
                ),
                cls.is_active.is_(True),
                cls.is_deleted.is_(False),
            )
            .scalar()
        )
        return max_number if max_number is not None else 0


class CaseFileOfficer(BaseModelVersioned):
    """Other officers associated with the Casefile."""

    __tablename__ = "case_file_officers"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the case file officers",
    )
    case_file_id = Column(
        Integer,
        ForeignKey("case_files.id", name="case_file_officers_case_files_id_fkey"),
        nullable=False,
        comment="The unique identifier of the associated case file",
    )
    officer_id = Column(
        Integer,
        ForeignKey("staff_users.id", name="case_file_officers_staff_users_id_fkey"),
        nullable=False,
        comment="The unique identifier of the associated staff user",
    )

    case_file = relationship(
        "CaseFile",
        back_populates="case_file_officers",
        lazy="joined",
    )
    officer = relationship(
        "StaffUser",
        foreign_keys=[officer_id],
        lazy="select",
        primaryjoin="and_(StaffUser.id == CaseFileOfficer.officer_id, "
        "StaffUser.is_active == True, "
        "StaffUser.is_deleted == False)",
    )

    @classmethod
    def get_all_by_case_file_id(cls, case_file_id: int):
        """Retrieve all case file officers by case file id."""
        return (
            cls.query
            .options(joinedload(cls.officer))
            .filter_by(case_file_id=case_file_id, is_deleted=False)
            .all()
        )

    @classmethod
    @with_session
    def bulk_delete(cls, case_file_id: int, officer_ids: list[int], session=None):
        """Delete officer ids by id per case file."""
        query = session.query(CaseFileOfficer) if session else cls.query
        officers = query.filter(
            cls.case_file_id == case_file_id, cls.officer_id.in_(officer_ids)
        )
        for officer in officers:
            officer.update(DELETE_DIC_PARAMS, commit=not session)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(cls, case_file_id: int, officer_ids: list[int], session=None):
        """Insert officers per case file."""
        case_file_officer_data = [
            CaseFileOfficer(**{"case_file_id": case_file_id, "officer_id": officer_id})
            for officer_id in officer_ids
        ]
        session.add_all(case_file_officer_data)
        session.flush()


class CaseFileInitiationOption(BaseModelVersioned):
    """Initiation Options for creating CaseFile."""

    __tablename__ = "case_file_initiation_options"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the case file initiation options",
    )
    name = Column(String, unique=True, comment="The name of the option")
    sort_order = Column(
        Integer,
        comment="Order of priority. Mainly used order the options while listing",
    )


class CaseFileLink(BaseModelVersioned):
    """CaseFileLinks Model."""

    __tablename__ = "case_file_links"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the case file link",
    )
    source_case_id = Column(
        Integer,
        ForeignKey("case_files.id", name="source_case_id_case_files_id_fk"),
        index=True,
        nullable=False,
    )
    target_case_id = Column(
        Integer,
        ForeignKey("case_files.id", name="target_case_id_case_files_id_fk"),
        index=True,
        nullable=False,
    )
    source = relationship("CaseFile", foreign_keys=[source_case_id], lazy="joined")
    target = relationship("CaseFile", foreign_keys=[target_case_id], lazy="joined")

    @classmethod
    def get_links_by_source_id(cls, source_case_file_id):
        """Get all case file links by source case file id."""
        return cls.query.filter(
            cls.source_case_id == source_case_file_id, cls.is_deleted.is_(False)
        ).all()

    @classmethod
    def get_links_by_source_and_target(cls, source_id, target_id):
        """Get case file link by both source case file and target case file id."""
        return cls.query.filter(
            cls.source_case_id == source_id,
            cls.target_case_id == target_id,
            cls.is_deleted.is_(False),
        ).first()

    @classmethod
    @with_session
    def delete_link(cls, source_id, target_id, session=None):
        """Delete the case file link."""
        links = cls.query.filter(
            cls.source_case_id == source_id,
            cls.target_case_id == target_id,
            cls.is_deleted.is_(False),
        ).all()
        for link in links:
            link.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_all_links(cls, case_file_id, session=None):
        """Delete all links associated with the given case file."""
        links = cls.query.filter(
            (cls.source_case_id == case_file_id) | (cls.target_case_id == case_file_id),
            cls.is_deleted.is_(False),
        ).all()
        for link in links:
            link.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def create_link(cls, link_data, session=None):
        """Persist case file link data in database."""
        case_file = CaseFileLink(**link_data)
        session.add(case_file)
        session.flush()
        return case_file
