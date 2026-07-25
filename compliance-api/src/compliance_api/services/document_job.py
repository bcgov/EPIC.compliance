"""Service for managing document jobs."""

import uuid
from datetime import datetime, timezone

import requests
from flask import current_app
from sqlalchemy.exc import IntegrityError

from compliance_api.exceptions import BusinessError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.document_job import DocumentJob, DocumentJobStatusEnum
from compliance_api.services.document_service.doc_service import DocService
from compliance_api.services.inspection_record.inspection_record import InspectionRecordService


class DocumentJobService:
    """Service for managing document jobs."""

    @staticmethod
    def create(document_job_data):
        """Create a new document job."""
        document_job = DocumentJob(**document_job_data)
        return document_job.save()

    @staticmethod
    def start_job(staff_user_id, inspection_record_id, output_format, document_job_data):
        """Invalidate any previous job and create a new one.

        Returns ``(document_job, created)``. A DB-level partial unique index
        allows at most one active IN_PROGRESS job per (user, inspection_record,
        output_format), so two near-simultaneous requests (e.g. a double-click
        before the UI disables the generate button) can't both create a job:
        the second one loses the race with an IntegrityError, and this returns
        the job the first request already created instead, with ``created``
        false so the caller knows not to spawn a second background render for
        the same job.
        """
        DocumentJobService.invalidate_all_previous_documents_for_user(
            staff_user_id, inspection_record_id, output_format
        )
        try:
            return DocumentJobService.create(document_job_data), True
        except IntegrityError:
            existing = DocumentJobService.get_most_recent_document_job_for_user(
                staff_user_id, inspection_record_id, output_format
            )
            return existing, False

    @staticmethod
    def get_most_recent_document_job_for_user(user_id, inspection_record_id, output_format):
        """Get the most recently generated document for a user."""
        return DocumentJob.query.filter_by(
            user_id=user_id,
            inspection_record_id=inspection_record_id,
            output_format=output_format,
            is_active=True,
            is_deleted=False,
        ).order_by(DocumentJob.id.desc()).first()

    @staticmethod
    def get_last_generated_time_for_user(user_id, inspection_record_id, output_format):
        """Get the last time a document was generated for a user."""
        jobs = DocumentJob.query.filter_by(
            user_id=user_id,
            inspection_record_id=inspection_record_id,
            output_format=output_format,
        ).filter(DocumentJob.completed_at.isnot(None)).order_by(DocumentJob.completed_at.desc()).all()
        document_job = jobs[0] if jobs else None
        return document_job.completed_at.isoformat() if document_job else None

    @staticmethod
    def update(document_job_id, user_id, update_data):
        """Update a document job by its ID.

        Idempotent: a job already invalidated (e.g. by
        ``invalidate_all_previous_documents_for_user`` racing with this call)
        is treated as a no-op success rather than a 404. Also refuses to
        downgrade an already-COMPLETED job to FAILED, which guards against
        the frontend's "stuck job" watchdog racing the background thread's
        own completion update.
        """
        document_job = DocumentJob.query.filter_by(
            id=document_job_id,
            user_id=user_id,
        ).first()

        if not document_job:
            raise ResourceNotFoundError(
                f"Document Job with id: {document_job_id} not found"
            )

        if document_job.is_deleted:
            return document_job

        if (
            update_data.get("status") == DocumentJobStatusEnum.FAILED.value
            and document_job.status == DocumentJobStatusEnum.COMPLETED.value
        ):
            return document_job

        document_job.update(update_data)
        return document_job

    @staticmethod
    def delete(document_job_id, user_id):
        """Delete a document job by its ID.

        Idempotent: a job already deleted (e.g. by
        ``invalidate_all_previous_documents_for_user`` racing with this call)
        is treated as a no-op success rather than a 404, since the desired
        end state - the job being deleted - already holds.
        """
        document_job = DocumentJob.query.filter_by(
            id=document_job_id,
            user_id=user_id,
        ).first()

        if not document_job:
            raise ResourceNotFoundError(
                f"Document Job with id: {document_job_id} not found"
            )

        if document_job.is_deleted:
            return document_job

        document_job.update({
            "is_active": False,
            "is_deleted": True
        })
        return document_job

    @staticmethod
    def invalidate_all_previous_documents_for_user(staff_user_id, inspection_record_id, output_format):
        """Mark previous document jobs for a user as deleted and inactive."""
        jobs = DocumentJob.get_by_params({
            "user_id": staff_user_id,
            "inspection_record_id": inspection_record_id,
            "output_format": output_format,
        })
        for job in jobs:
            job.update({
                "is_active": False,
                "is_deleted": True
            })

    @staticmethod
    def handle_background_job(
        app,
        job_id,
        access_token,
        jwt_oidc_token_info,
        inspection_id,
        inspection_record_id,
        staff_user_id,
        output_format,
    ):
        """Handle background job process for rendering and storing a document in EPIC.document."""
        with app.app_context():
            from flask import g  # pylint: disable=import-outside-toplevel
            g.access_token = access_token
            g.jwt_oidc_token_info = jwt_oidc_token_info
            try:
                response, inspection = InspectionRecordService.render(
                    inspection_id, inspection_record_id, output_format
                )

                relative_url = f"inspection_records/{uuid.uuid4().hex}.{output_format}"
                payload = {
                    "action": "PUT",
                    "relative_url": relative_url
                }
                params = {
                    "public-read": True
                }
                presigned_put_request = DocService.get_presigned_url(payload, params)

                # PDF rendering returns a requests-style response with `.content`;
                # DOCX rendering returns an already fully-built BytesIO stream that
                # requests can upload directly without an extra in-memory copy.
                upload_data = response.content if output_format == "pdf" else response

                put_request = requests.put(
                    presigned_put_request["presigned_url"],
                    data=upload_data,
                    headers={
                        "Content-Type": "application/octet-stream",
                        "x-amz-acl": "public-read",
                    },
                    timeout=60
                )

                if put_request.status_code != 200:
                    raise BusinessError("Failed to upload document to storage service", 500)

                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.COMPLETED.value,
                    "download_name": f"{inspection.ir_number}.{output_format}",
                    "relative_url": presigned_put_request["relative_url"],
                    "completed_at": datetime.now(timezone.utc),
                })
            except UnprocessableEntityError:
                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.FAILED.value,
                })
            except BusinessError:
                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.FAILED.value,
                })
            except ValueError:
                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.FAILED.value,
                })
            except Exception:  # noqa: B902  pylint: disable=broad-except
                current_app.logger.exception(
                    f"Unexpected error generating {output_format} document for job {job_id}"
                )
                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.FAILED.value,
                })
