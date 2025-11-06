"""Staff user model class.

Manages the staff user
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModelVersioned
from .utils import with_session


class StaffUser(BaseModelVersioned):
    """Definition of the Staff User entity."""

    __tablename__ = "staff_users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the staff user.",
    )
    first_name = Column(String(50), comment="The firstname of the staff user.")
    last_name = Column(String(50), comment="The lastname of the staff user.")
    position_id = Column(
        Integer,
        ForeignKey("positions.id", name="staff_users_position_id_fkey"),
        nullable=False,
        comment="The unique identifier of the position of the staff user.",
    )
    deputy_director_id = Column(
        Integer,
        ForeignKey("staff_users.id", name="staff_users_deputy_director_id_fkey"),
        nullable=True,
        comment="The unique identifier of the deputy director.",
    )
    supervisor_id = Column(
        Integer,
        ForeignKey("staff_users.id", name="staff_users_supervisor_id_fkey"),
        nullable=True,
        comment="The unique identifier of the supervisor.",
    )
    auth_user_guid = Column(
        String(100),
        index=True,
        comment="The unique identifier from the identity provider.",
    )
    position = relationship("Position", foreign_keys=[position_id], lazy="joined")
    deputy_director = relationship(
        "StaffUser", remote_side=[id], foreign_keys=[deputy_director_id]
    )
    supervisor = relationship(
        "StaffUser", remote_side=[id], foreign_keys=[supervisor_id]
    )
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    __table_args__ = (
        Index(
            "uq_auth_user_guid_is_deleted_false",
            "auth_user_guid",
            unique=True,
            postgresql_where=(is_deleted is False),
        ),
    )

    @classmethod
    @with_session
    def create_staff(cls, user_data, session=None) -> StaffUser:
        """Create user."""
        staff_user = StaffUser(**user_data)
        session.add(staff_user)
        session.flush()
        return staff_user

    @classmethod
    @with_session
    def update_staff(cls, user_id, user_dict, session=None) -> Optional[StaffUser]:
        """Update user."""
        query = StaffUser.query.filter_by(id=user_id)
        user: StaffUser = query.first()
        if not user or user.is_deleted:
            return None
        user.update(user_dict, commit=False)
        session.flush()
        return user

    @classmethod
    def get_by_auth_guid(cls, auth_guid: str) -> StaffUser:
        """Retrieve the staff user by auth_guid."""
        staff_user = StaffUser.query.filter_by(
            auth_user_guid=auth_guid, is_deleted=False, is_active=True
        ).first()
        return staff_user

    @classmethod
    @with_session
    def delete_staff_user(cls, staff_user_id, session=None):
        """Delete the staff user."""
        user = cls.find_by_id(staff_user_id)
        if not user:
            return None
        user.is_deleted = True
        user.is_active = False
        session.flush()
        return user
