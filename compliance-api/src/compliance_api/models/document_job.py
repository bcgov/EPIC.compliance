"""Document Jobs Model."""

from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from .base_model import BaseModelVersioned


class DocumentJobStatusEnum(Enum):
    """Document Job Status Enum."""

    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class DocumentJob(BaseModelVersioned):
    """Document Jobs Model."""

    __tablename__ = "document_jobs"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="The unique identifier"
    )
    user_id = Column(
        Integer,
        ForeignKey(
            "staff_users.id", name="document_jobs_user_id_staff_user_id_fkey"
        ),
        nullable=False,
        comment="The unique identifier of the user who initiated the document job",
    )
    inspection_record_id = Column(
        Integer,
        ForeignKey(
            "inspection_records.id", name="document_jobs_inspection_record_id_inspection_records_id_fkey"
        ),
        nullable=True,
        comment="The unique identifier of the inspection associated with the document job",
    )
    status = Column(
        String,
        nullable=False,
        comment="The status of the document job",
        default=DocumentJobStatusEnum.IN_PROGRESS,
    )
    output_format = Column(
        String,
        nullable=False,
        default="pdf",
        comment="The output format of the document job (pdf or docx)",
    )
    download_name = Column(
        String,
        nullable=True,
        comment="The name of the document to be downloaded",
    )
    relative_url = Column(
        String,
        nullable=True,
        comment="The unique key where the document is stored",
    )
    started_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="The timestamp when the document job started",
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="The timestamp when the document was generated",
    )
