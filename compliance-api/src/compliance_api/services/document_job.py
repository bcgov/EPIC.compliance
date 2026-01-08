"""Service for managing document jobs."""

import uuid
from datetime import datetime, timezone

import requests

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
    def get_most_recent_document_job_for_user(user_id, inspection_record_id):
        """Get the most recently generated PDF for a user."""
        jobs = DocumentJob.get_by_params({
            "user_id": user_id,
            "inspection_record_id": inspection_record_id,
        })
        return jobs[-1] if jobs else None

    @staticmethod
    def get_last_generated_time_for_user(user_id, inspection_record_id):
        """Get the last time a document was generated for a user."""
        jobs = DocumentJob.query.filter_by(
            user_id=user_id,
            inspection_record_id=inspection_record_id,
        ).order_by(DocumentJob.completed_at.desc()).all()
        document_job = jobs[0] if jobs else None
        return document_job.completed_at.isoformat() if document_job else None

    @staticmethod
    def update(document_job_id, user_id, update_data):
        """Update a document job by its ID."""
        document_job = DocumentJob.get_by_params({
            "id": document_job_id,
            "user_id": user_id,
        })
        document_job = document_job[0] if document_job else None
        if not document_job:
            raise ResourceNotFoundError(
                f"Document Job with id: {document_job_id} not found"
            )
        document_job.update(update_data)
        return document_job

    @staticmethod
    def delete(document_job_id, user_id):
        """Delete a document job by its ID."""
        document_job = DocumentJob.get_by_params({
            "id": document_job_id,
            "user_id": user_id
        })

        if not document_job:
            raise ResourceNotFoundError(
                f"Document Job with id: {document_job_id} not found"
            )

        document_job = document_job[0]

        document_job.update({
            "is_active": False,
            "is_deleted": True
        })
        return document_job

    @staticmethod
    def invalidate_all_previous_documents_for_user(staff_user_id, inspection_record_id):
        """Mark previous document jobs for a user as deleted and inactive."""
        jobs = DocumentJob.get_by_params({"user_id": staff_user_id, "inspection_record_id": inspection_record_id})
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
    ):
        """Handle background job process for rendering and storing a document in EPIC.document."""
        with app.app_context():
            from flask import g  # pylint: disable=import-outside-toplevel
            g.access_token = access_token
            g.jwt_oidc_token_info = jwt_oidc_token_info
            try:
                response, inspection = InspectionRecordService.render(
                    inspection_id, inspection_record_id, "pdf"
                )

                relative_url = f"inspection_records/{uuid.uuid4().hex}.pdf"
                payload = {
                    "action": "PUT",
                    "relative_url": relative_url
                }
                params = {
                    "public-read": True
                }
                presigned_put_request = DocService.get_presigned_url(payload, params)

                put_request = requests.put(
                    presigned_put_request["presigned_url"],
                    data=response.content,
                    headers={
                        "Content-Type": "application/octet-stream",
                        "x-amz-acl": "public-read",
                    }
                )

                if put_request.status_code != 200:
                    raise BusinessError("Failed to upload document to storage service", 500)

                DocumentJobService.update(job_id, staff_user_id, {
                    "status": DocumentJobStatusEnum.COMPLETED.value,
                    "download_name": f"{inspection.ir_number}.pdf",
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
