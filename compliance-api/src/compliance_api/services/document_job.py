"""Service for managing document jobs."""

import uuid
from datetime import datetime, timezone

import requests
from flask import current_app
from sqlalchemy.exc import IntegrityError

from compliance_api.exceptions import BusinessError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.db import db
from compliance_api.models.document_job import DocumentJob, DocumentJobStatusEnum
from compliance_api.models.inspection_record import InspectionRecord as InspectionRecordModel
from compliance_api.models.inspection_record import IRStatusEnum
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

        Returns ``(document_job, created)``. A partial unique index allows only
        one active IN_PROGRESS job per (user, inspection_record, output_format),
        so a request that loses that race gets the existing job back with
        ``created`` false and must not spawn a second background render.
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
        """Get the last time a document was generated for a user.

        Scoped to active jobs, so a cancelled or failed run leaves no stale
        timestamp advertising a document that is no longer downloadable.
        """
        jobs = DocumentJob.query.filter_by(
            user_id=user_id,
            inspection_record_id=inspection_record_id,
            output_format=output_format,
            is_active=True,
            is_deleted=False,
        ).filter(DocumentJob.completed_at.isnot(None)).order_by(DocumentJob.completed_at.desc()).all()
        document_job = jobs[0] if jobs else None
        return document_job.completed_at.isoformat() if document_job else None

    @staticmethod
    def update(document_job_id, user_id, update_data):
        """Update a document job by its ID.

        Idempotent: an already invalidated job is a no-op success rather than a
        404. Won't downgrade a COMPLETED job to FAILED, which guards against the
        frontend's "stuck job" watchdog racing the worker's own completion.
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

        Idempotent: an already deleted job is a no-op success rather than a 404,
        since the desired end state already holds.
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
    def cancel(document_job_id, user_id):
        """Cancel an in-progress document job.

        Marked CANCELLED and soft deleted, so it drops out of the active job
        lookups, frees the partial unique index for an immediate re-generate,
        and can never be flipped to COMPLETED by the worker thread.

        An already COMPLETED job is returned untouched - the render beat the
        click, and the caller surfaces it for download.
        """
        document_job = DocumentJob.query.filter_by(
            id=document_job_id,
            user_id=user_id,
        ).first()

        if not document_job:
            raise ResourceNotFoundError(
                f"Document Job with id: {document_job_id} not found"
            )

        if document_job.status == DocumentJobStatusEnum.COMPLETED.value:
            return document_job

        if document_job.is_deleted:
            return document_job

        document_job.update({
            "status": DocumentJobStatusEnum.CANCELLED.value,
            "is_active": False,
            "is_deleted": True,
        })
        return document_job

    @staticmethod
    def is_cancelled(document_job_id, user_id):
        """Check whether a job has been cancelled out from under the worker thread.

        ``expire_all`` discards the worker session's stale copy, without which
        it would never see the cancellation committed by the request thread.
        """
        db.session.expire_all()
        document_job = DocumentJob.query.filter_by(
            id=document_job_id,
            user_id=user_id,
        ).first()

        if not document_job:
            return True

        return (
            document_job.is_deleted
            or document_job.status == DocumentJobStatusEnum.CANCELLED.value
        )

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
        """Handle background job process for rendering and storing a document in EPIC.document.

        Cancellation is cooperative: the render can't be interrupted mid-call,
        so the status is re-checked at each step boundary. Bailing out before
        the upload is what avoids orphaning a document in EPIC.document.
        """
        with app.app_context():
            from flask import g  # pylint: disable=import-outside-toplevel
            g.access_token = access_token
            g.jwt_oidc_token_info = jwt_oidc_token_info

            def abandon_if_cancelled(stage):
                """Return True when the job was cancelled, logging where we stopped."""
                if not DocumentJobService.is_cancelled(job_id, staff_user_id):
                    return False
                current_app.logger.info(
                    f"Document job {job_id} cancelled - abandoning {output_format} generation at: {stage}"
                )
                return True

            try:
                if abandon_if_cancelled("before render"):
                    return

                response, inspection = InspectionRecordService.render(
                    inspection_id, inspection_record_id, output_format
                )

                if abandon_if_cancelled("after render"):
                    return

                relative_url = f"inspection_records/{uuid.uuid4().hex}.{output_format}"
                payload = {
                    "action": "PUT",
                    "relative_url": relative_url
                }
                params = {
                    "public-read": True
                }
                presigned_put_request = DocService.get_presigned_url(payload, params)

                if abandon_if_cancelled("before upload"):
                    return

                # PDF renders to a requests-style response; DOCX renders to a
                # BytesIO stream requests can upload directly.
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

                if abandon_if_cancelled("after upload"):
                    return

                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.COMPLETED.value,
                    "download_name": _build_download_name(
                        inspection, inspection_record_id, output_format
                    ),
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


def _build_download_name(inspection, inspection_record_id, output_format):
    """Build the download filename for a generated inspection record document.

    Preliminary DOCX records keep the _PRELIMINARY suffix so they are
    distinguishable from the final record once downloaded.
    """
    base_name = inspection.ir_number
    if output_format == "docx":
        inspection_record = InspectionRecordModel.find_by_id(inspection_record_id)
        if (
            inspection_record
            and inspection_record.ir_status_id == IRStatusEnum.PRELIMINARY.value
        ):
            base_name = f"{base_name}_PRELIMINARY"
    return f"{base_name}.{output_format}"
