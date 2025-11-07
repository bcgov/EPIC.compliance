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
"""Inspection Officer Model."""
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS

from ..base_model import BaseModelVersioned
from ..inspection.inspection import Inspection as InspectionModel
from ..staff_user import StaffUser as StaffUserModel
from ..utils import with_session


class InspectionOfficer(BaseModelVersioned):
    """Other officers associated with the inspection."""

    __tablename__ = "inspection_officers"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the inspection officers",
    )
    inspection_id = Column(
        Integer,
        ForeignKey(
            "inspections.id",
            name="inspection_officers_inspection_id_inspection_id_fkey",
        ),
        nullable=False,
        comment="The unique identifier of the associated inspection",
    )
    officer_id = Column(
        Integer,
        ForeignKey("staff_users.id", name="case_file_officers_staff_users_id_fkey"),
        nullable=False,
        comment="The unique identifier of the associated staff user",
    )
    officer_position_id = Column(
        Integer,
        ForeignKey("positions.id", name="inspection_officers_position_id_fkey"),
        nullable=True,
        comment="The position ID of the officer when added to this inspection",
    )

    inspection = relationship(
        "Inspection",
        foreign_keys=[inspection_id],
        lazy="select",
    )
    officer = relationship("StaffUser", foreign_keys=[officer_id], lazy="joined")
    officer_position = relationship(
        "Position", foreign_keys=[officer_position_id], lazy="joined"
    )

    @classmethod
    def get_all_by_inspection(cls, inspection_id: int):
        """Retrieve all case file officers by inspection id."""
        return cls.query.filter_by(inspection_id=inspection_id, is_deleted=False).all()

    @classmethod
    @with_session
    def bulk_delete(cls, inspection_id: int, officer_ids: list[int], session=None):
        """Delete officer ids by id per inspection."""
        officers = cls.query.filter(
            cls.inspection_id == inspection_id, cls.officer_id.in_(officer_ids)
        ).all()
        for officer in officers:
            officer.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(cls, inspection_id: int, officer_ids: list[int], session=None):
        """Insert officers per inspection."""
        inspection_officer_data = []
        for officer_id in officer_ids:
            # Get the officer's current position_id
            staff_user = StaffUserModel.find_by_id(officer_id)
            officer_position_id = staff_user.position_id if staff_user else None

            inspection_officer_data.append(
                InspectionOfficer(
                    inspection_id=inspection_id,
                    officer_id=officer_id,
                    officer_position_id=officer_position_id,
                )
            )

        session.add_all(inspection_officer_data)
        session.flush()

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete other officers by case_file_id."""
        officers = (
            cls.query.join(InspectionModel)
            .filter(
                InspectionModel.case_file_id == case_file_id,
                InspectionOfficer.is_deleted is False,
            )
            .all()
        )
        officer_ids = [officer.id for officer in officers]
        if officer_ids:
            officers = cls.query.filter(InspectionOfficer.id.in_(officer_ids)).all()
            for officer in officers:
                officer.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_inspection_officer(cls, inspection_id, session=None):
        """Delete inspection Officer."""
        officers = cls.query.filter_by(
            inspection_id=inspection_id, is_deleted=False
        ).all()
        for officer in officers:
            officer.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()
