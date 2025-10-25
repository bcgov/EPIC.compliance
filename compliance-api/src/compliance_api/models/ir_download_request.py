"""Model for IR download request."""

from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base_model import BaseModel, BaseModelVersioned
from .utils import with_session


class DownloadStatusEnum(Enum):
    """Enum for IR Download Request Status."""

    NOT_STARTED = "Not Started"
    PENDING = "Pending"
    GENERATED = "Generated"
    DOWNLOADED = "Downloaded"


class IRDownloadRequest(BaseModelVersioned):
    """Definition of the IRDownloadRequest."""

    __tablename__ = "ir_download_requests"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    inspection_record_id = Column(
        ForeignKey("inspection_records.id", name="ir_download_request_ir_id_fkey"),
        nullable=False,
        comment="The unique identifier of the inspection record",
    )
    download_status = Column(
        SqlEnum(DownloadStatusEnum),
        nullable=False,
        comment="Status of the download request",
        default=DownloadStatusEnum.NOT_STARTED,
    )
    relative_url = Column(
        String(500),
        nullable=True,
        comment="Relative URL of the generated document",
    )
    generated_timestamp = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when the document was generated",
    )

    inspection_record = relationship(
        "InspectionRecord", foreign_keys=[inspection_record_id], lazy="joined"
    )
    error_logs = relationship(
        "IRDownloadRequestErrorLog",
        foreign_keys="IRDownloadRequestErrorLog.download_request_id",
        back_populates="download_request",
        cascade="all, delete-orphan",
    )

    @classmethod
    @with_session
    def create_download_request(cls, request_data, session=None):
        """Create a download request."""
        download_request = IRDownloadRequest(**request_data)
        session.add(download_request)
        session.flush()
        return download_request

    @classmethod
    @with_session
    def update_download_request(cls, request_id, update_data, session=None):
        """Update a download request."""
        download_request = cls.find_by_id(request_id)
        if not download_request:
            return None
        download_request.update(update_data, commit=False)
        session.flush()
        return download_request

    @classmethod
    def get_latest_by_inspection_record_and_staff(cls, inspection_record_id, staff_id):
        """Find the latest download request by inspection record and staff."""
        return (
            cls.query.filter_by(
                inspection_record_id=inspection_record_id,
                created_by=staff_id,
                is_deleted=False,
                is_active=True,
            )
            .order_by(cls.created_date.desc())
            .first()
        )

    @with_session
    def log_error(
        self, error_message, error_code=None, error_context=None, session=None
    ):
        """Log an error for this download request."""
        error_data = {
            "download_request_id": self.id,
            "error_message": error_message,
            "error_code": error_code,
            "error_context": error_context,
            "created_by": self.created_by,
        }
        return IRDownloadRequestErrorLog.create_error_log(error_data, session=session)


class IRDownloadRequestErrorLog(BaseModel):
    """Definition of the IRDownloadRequestErrorLog."""

    __tablename__ = "ir_download_request_error_logs"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    download_request_id = Column(
        ForeignKey("ir_download_requests.id", name="ir_error_log_request_id_fkey"),
        nullable=False,
        comment="The unique identifier of the download request",
    )
    error_message = Column(
        Text,
        nullable=False,
        comment="The error message that occurred during processing",
    )
    error_code = Column(
        String(100),
        nullable=True,
        comment="Optional error code for categorizing errors",
    )
    error_context = Column(
        Text,
        nullable=True,
        comment="Additional context about when/where the error occurred",
    )

    download_request = relationship(
        "IRDownloadRequest",
        foreign_keys=[download_request_id],
        back_populates="error_logs",
        lazy="joined",
    )

    @classmethod
    @with_session
    def create_error_log(cls, error_data, session=None):
        """Create an error log entry."""
        error_log = IRDownloadRequestErrorLog(**error_data)
        session.add(error_log)
        session.flush()
        return error_log

    @classmethod
    def get_errors_by_request_id(cls, download_request_id):
        """Get all error logs for a specific download request."""
        return (
            cls.query.filter_by(
                download_request_id=download_request_id,
                is_deleted=False,
                is_active=True,
            )
            .order_by(cls.created_date.desc())
            .all()
        )

    @classmethod
    def get_latest_error_by_request_id(cls, download_request_id):
        """Get the latest error log for a specific download request."""
        return (
            cls.query.filter_by(
                download_request_id=download_request_id,
                is_deleted=False,
                is_active=True,
            )
            .order_by(cls.created_date.desc())
            .first()
        )
