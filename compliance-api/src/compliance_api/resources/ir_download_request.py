"""Resources for IR download request."""

from http import HTTPStatus

from flask import g
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import CreateIRDownloadRequestSchema, IRDownloadRequestSchema
from compliance_api.services import IRDownloadRequestService

from .apihelper import Api as ApiHelper


API = Namespace("inspection-records", description="Endpoints for IR Download Requests")

ir_download_request_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, IRDownloadRequestSchema(), "IRDownloadRequest"
)
ir_download_request_create_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, CreateIRDownloadRequestSchema(), "CreateIRDownloadRequest"
)


@API.route("/<int:inspection_record_id>/download-requests", methods=["POST"])
class IRDownloadRequests(Resource):
    """Resource for creating IR download requests."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create an IR download request"
    )
    @API.expect(ir_download_request_create_schema)
    @API.response(code=201, model=ir_download_request_schema, description="Created")
    @API.response(400, "Bad Request")
    @API.response(409, "Conflict - Request already exists")
    def post(inspection_id, inspection_record_id):  # pylint: disable=unused-argument
        """Create an IR download request.

        Creates a new download request for the specified inspection record.
        Prevents duplicate requests by checking if a pending/not-started request
        already exists for the same inspection record and user.
        """
        # Staff ID will be extracted from user context in the service layer
        created_request = IRDownloadRequestService.create_download_request(
            inspection_record_id
        )
        return (
            IRDownloadRequestSchema().dump(created_request),
            HTTPStatus.CREATED,
        )


@API.route(
    "/<int:inspection_record_id>/download-requests/latest",
    methods=["GET"],
)
class IRDownloadRequestLatest(Resource):
    """Resource for fetching the latest IR download request."""

    @staticmethod
    @API.response(code=200, description="Success", model=ir_download_request_schema)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch the latest IR download request for the calling user",
    )
    @auth.require
    def get(inspection_id, inspection_record_id):  # pylint: disable=unused-argument
        """Fetch the latest IR download request by inspection record for the calling user.

        Returns the most recent download request for the specified inspection record
        and the authenticated caller, ordered by creation date descending.
        """
        staff_id = g.token_info.get("preferred_username")

        download_request = IRDownloadRequestService.get_latest_download_request(
            inspection_record_id, staff_id
        )

        if not download_request:
            raise ResourceNotFoundError(
                f"No download request found for inspection record {inspection_record_id}"
            )

        return IRDownloadRequestSchema().dump(download_request), HTTPStatus.OK
