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
"""Continuation Report Model."""
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from compliance_api.utils.constant import DELETE_DIC_PARAMS
from compliance_api.utils.enum import ContextEnum

from .base_model import BaseModelVersioned
from .utils import with_session


class ContinuationReport(BaseModelVersioned):
    """Continuation Report Model Class."""

    __tablename__ = "continuation_reports"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    case_file_id = Column(
        Integer,
        ForeignKey("case_files.id", name="inspections_case_file_id_case_file_id_fkey"),
        nullable=False,
        index=True,
        comment="The unique identifier of the case file associated with the inspection",
    )
    text = Column(String, comment="The plane text version of the string")
    rich_text = Column(String, comment="The html formatted version of the text")
    context_type = Column(
        Enum(ContextEnum),
        nullable=False,
        comment="Indicates the context in which the entry is made",
    )
    context_id = Column(
        Integer,
        nullable=False,
        comment="The identifier of the entity referred by the context type",
    )
    system_generated = Column(
        Boolean,
        default=False,
        comment="To indicate if the entry is generated as part of the service invocation",
    )
    date_created = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="The created date of the entry",
    )
    created_by = Column(String(100), nullable=False)
    created_by_user = relationship(
        "StaffUser",
        primaryjoin="ContinuationReport.created_by == foreign(StaffUser.auth_user_guid)",
        lazy="joined",
        uselist=False,
    )
    case_file = relationship("CaseFile", foreign_keys=[case_file_id], lazy="joined")
    keys = relationship(
        "ContinuationReportKey",
        backref="report",
        lazy="select",
        cascade="all, delete-orphan",
        foreign_keys="[ContinuationReportKey.report_id]",
    )

    @classmethod
    @with_session
    def create_entry(cls, report_entry_obj, session=None):
        """Persist continuation report entry in database."""
        report_entry = ContinuationReport(**report_entry_obj)
        session.add(report_entry)
        session.flush()
        return report_entry

    @classmethod
    @with_session
    def update_entry(cls, entry_id, report_entry_obj, session=None):
        """Update continuation report entry."""
        query = cls.query.filter_by(id=entry_id)
        report_entry: ContinuationReport = query.first()
        if not report_entry or report_entry.is_deleted:
            return None
        report_entry.update(report_entry_obj, commit=False)
        session.flush()
        return report_entry

    @classmethod
    @with_session
    def delete_by_case_file(cls, case_file_id, session=None):
        """Delete continuation report entries by case file id."""
        case_files = cls.query.filter_by(
            case_file_id=case_file_id, is_deleted=False
        ).all()
        for case_file in case_files:
            case_file.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_by_context(cls, context_id, context_type, session=None):
        """
        Delete continuation report entries.

        :param context_id: The unique ID of the context type.
        :param context_type: One of the context_type enums.
        :param session: SQLAlchemy session object (optional).
        """
        entries = cls.query.filter_by(
            context_id=context_id, context_type=context_type
        ).all()
        for entry in entries:
            entry.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    def get_by_case_file_paginated(cls, case_file_id, page_no, page_size, search_text):
        """Get crs by case file id paginated."""
        query = cls.query.filter_by(case_file_id=case_file_id, is_deleted=False)
        if search_text:
            query = query.filter(cls.text.ilike(f"%{search_text}%"))
        query = query.order_by(cls.date_created.desc())
        pagination = query.paginate(page=page_no, per_page=page_size)
        return pagination.items, pagination.total

    @classmethod
    def get_all_by_case_file(cls, case_file_id):
        """Get all crs by case file id."""
        query = cls.query.filter_by(case_file_id=case_file_id, is_deleted=False)
        query = query.order_by(cls.date_created.asc())
        return query.all()


class ContinuationReportKey(BaseModelVersioned):
    """ContinationReportKey Model."""

    __tablename__ = "continuation_report_keys"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier",
    )
    report_id = Column(
        Integer,
        ForeignKey(
            "continuation_reports.id",
            name="continuation_report_keys_report_id_continuation_report_id_fkey",
        ),
        index=True,
        nullable=False,
        comment="The unique identifier of the report entry",
    )
    key = Column(
        String,
        nullable=False,
        comment="The key which is used to provide hyperlink to other entities",
    )
    key_context = Column(
        Enum(ContextEnum),
        nullable=False,
        comment="The context of the key which is used to create hyperlinks using the key",
    )

    @classmethod
    def get_by_report_id(cls, report_id: int):
        """Get keys by report id."""
        return cls.query.filter_by(report_id=report_id, is_deleted=False).all()

    @classmethod
    @with_session
    def bulk_delete(cls, report_id, keys, session=None):
        """Delete continuation report keys."""
        keys = cls.query.filter(cls.report_id == report_id, cls.key.in_(keys)).all()
        for key_item in keys:
            key_item.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_keys_by_case_file(cls, case_file_id: int, session=None):
        """
        Delete continuation report keys by case file id.

        :param case_file_id: ID of the case file whose keys should be deleted.
        :param session: SQLAlchemy session object (optional).
        """
        keys = (
            cls.query.join(ContinuationReport)
            .filter(ContinuationReport.case_file_id == case_file_id)
            .all()
        )
        key_ids = [key.id for key in keys]
        if key_ids:
            keys = cls.query.filter(ContinuationReportKey.id.in_(key_ids)).all()
            for key_item in keys:
                key_item.update(DELETE_DIC_PARAMS, commit=False)
        session.flush()

    @classmethod
    @with_session
    def delete_keys_by_context(cls, context_id, context_type, session=None):
        """
        Delete continuation report entries.

        :param context_id: The unique ID of the context type.
        :param context_type: One of the context_type enums.
        :param session: SQLAlchemy session object (optional).
        """
        keys = (
            cls.query.join(ContinuationReport)
            .filter(
                ContinuationReport.context_id == context_id,
                ContinuationReport.context_type == context_type,
            )
            .all()
        )
        key_ids = [key.id for key in keys]
        if key_ids:
            cls.query.filter(ContinuationReportKey.id.in_(key_ids)).update(
                {cls.is_deleted: True, cls.is_active: False}
            )
        session.flush()

    @classmethod
    @with_session
    def bulk_insert(cls, report_id: int, keys: list[int], session=None):
        """Insert keys for the continuation report."""
        key_data = [
            ContinuationReportKey(
                **{
                    "report_id": report_id,
                    "key": key.get("key"),
                    "key_context": key.get("key_context"),
                }
            )
            for key in keys
        ]
        session.add_all(key_data)
        session.flush()
