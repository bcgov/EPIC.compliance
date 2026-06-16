"""Service for IR download request."""

from flask import g

from compliance_api.exceptions import UnprocessableEntityError
from compliance_api.models import DownloadStatusEnum
from compliance_api.models import InspectionRecord as InspectionRecordModel
from compliance_api.models import IRDownloadRequest as IRDownloadRequestModel


class IRDownloadRequestService:
    """IRDownloadRequestService."""

    @classmethod
    def create_download_request(cls, inspection_record_id):
        """Create a download request for an inspection record.

        Args:
            inspection_record_id: ID of the inspection record

        Returns:
            Created download request
        """
        # Verify inspection record exists
        inspection_record = InspectionRecordModel.find_by_id(inspection_record_id)
        if not inspection_record:
            raise UnprocessableEntityError(
                f"Inspection record with ID {inspection_record_id} not found"
            )

        created_by = g.token_info.get("preferred_username")

        # Create new download request
        request_data = {
            "inspection_record_id": inspection_record_id,
            "download_status": DownloadStatusEnum.NOT_STARTED,
            "created_by": created_by,
        }

        download_request = IRDownloadRequestModel.create_download_request(request_data)
        return download_request

    @classmethod
    def get_latest_download_request(cls, inspection_record_id, staff_id):
        """Get the latest download request for an inspection record and staff member.

        Args:
            inspection_record_id: ID of the inspection record
            staff_id: Staff ID (GUID) of the user

        Returns:
            Latest download request or None if not found
        """
        # Verify inspection record exists
        inspection_record = InspectionRecordModel.find_by_id(inspection_record_id)
        if not inspection_record:
            raise UnprocessableEntityError(
                f"Inspection record with ID {inspection_record_id} not found"
            )

        return IRDownloadRequestModel.get_latest_by_inspection_record_and_staff(
            inspection_record_id, staff_id
        )

    @classmethod
    def update_download_request(cls, request_id, update_data):
        """Update a download request.

        Args:
            request_id: ID of the download request
            update_data: Dictionary containing fields to update

        Returns:
            Updated download request
        """
        download_request = IRDownloadRequestModel.find_by_id(request_id)
        if not download_request:
            raise UnprocessableEntityError(
                f"Download request with ID {request_id} not found"
            )

        return IRDownloadRequestModel.update_download_request(request_id, update_data)
