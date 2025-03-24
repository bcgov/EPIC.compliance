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
"""Super class to handle all operations related to base model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, asc
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from .db import db


class BaseModel(db.Model):
    """This class manages all of the base model functions."""

    __abstract__ = True

    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, server_default="t", nullable=False)
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)

    @classmethod
    def get_all(cls, default_filters=True, sort_by=None):
        """Fetch list of users by access type."""
        query = {}
        if default_filters and hasattr(cls, "is_active"):
            query["is_active"] = True
        if hasattr(cls, "is_deleted"):
            query["is_deleted"] = False
        query_obj = cls.query.filter_by(**query)  # pylint: disable=no-member
        if sort_by and hasattr(cls, sort_by):
            query_obj = query_obj.order_by(getattr(cls, sort_by))
        return query_obj.all()

    @classmethod
    def get_by_params(cls, params: dict, default_filters=True):
        """Return based on the params."""
        query = {}
        for key, value in params.items():
            query[key] = value
        if default_filters and hasattr(cls, "is_active"):
            query["is_active"] = True
        if hasattr(cls, "is_deleted"):
            query["is_deleted"] = False
        rows = cls.query.filter_by(**query).order_by(asc("id")).all()
        return rows

    @classmethod
    def find_by_id(cls, identifier: int):
        """Return model by id."""
        query = cls.query.filter_by(id=identifier)
        if hasattr(cls, "is_deleted"):
            query = query.filter_by(is_deleted=False)
        return query.first()

    @staticmethod
    def commit():
        """Commit the session."""
        db.session.commit()

    def flush(self):
        """Save and flush."""
        db.session.add(self)
        db.session.flush()
        return self

    def add_to_session(self):
        """Save and flush."""
        return self.flush()

    def save(self):
        """Save and commit."""
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()
            return self  # Return self for method chaining
        except (SQLAlchemyError, DBAPIError) as e:
            db.session.rollback()
            raise e

    def update(self, payload: dict, commit=True):
        """Update and commit."""
        for key, value in payload.items():
            if key != "id":
                setattr(self, key, value)
        if commit:
            self.commit()

    def delete(self):
        """Delete and commit."""
        try:
            db.session.delete(self)
            db.session.flush()
            db.session.commit()
        except (SQLAlchemyError, DBAPIError) as e:
            db.session.rollback()
            raise e

    @staticmethod
    def rollback():
        """RollBack."""
        db.session.rollback()


class BaseModelVersioned(BaseModel):
    """Versioned models."""

    __abstract__ = True
    __versioned__ = {}
