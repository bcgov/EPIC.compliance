"""Staff user model class.

Manages the staff user
"""

from __future__ import annotations

import enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class PermissionEnum(enum.Enum):
    """Enum for Staff User Permissions."""

    VIEWER = "VIEWER"
    USER = "USER"
    SUPERUSER = "SUPERUSER"


PERMISSION_MAP = {
    PermissionEnum.SUPERUSER: "Superuser",
    PermissionEnum.VIEWER: "Viewer",
    PermissionEnum.USER: "User",
}


class StaffUser(BaseModel):
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
        unique=True,
        comment="The unique identifier from the identity provider.",
    )
    position = relationship("Position", foreign_keys=[position_id], lazy="select")

    @classmethod
    def create_user(cls, user_data, session=None) -> StaffUser:
        """Create user."""
        staff_user = StaffUser(**user_data)
        if session:
            session.add(staff_user)
            session.flush()
        else:
            staff_user.save()
        return staff_user

    @classmethod
    def update_user(cls, user_id, user_dict, session=None) -> Optional[StaffUser]:
        """Update user."""
        query = StaffUser.query.filter_by(id=user_id)
        user: StaffUser = query.first()
        if not user:
            return None
        query.update(user_dict)
        if session:
            session.flush()
        else:
            cls.session.commit()
        return user