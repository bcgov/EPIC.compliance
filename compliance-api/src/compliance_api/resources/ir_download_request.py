"""Resources for IR download request."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import CreateIRDownloadRequestSchema, IRDownloadRequestQuerySchema, IRDownloadRequestSchema
from compliance_api.services import IRDownloadRequestService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("inspection-records", description="Endpoints for IR Download Requests")

ir_download_request_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, IRDownloadRequestSchema(), "IRDownloadRequest"
)
ir_download_request_create_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, CreateIRDownloadRequestSchema(), "CreateIRDownloadRequest"
)


@cors_preflight("POST, OPTIONS")
@API.route("/<int:inspection_record_id>/download-requests", methods=["POST", "OPTIONS"])
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
    def post(inspection_record_id):
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


@cors_preflight("GET, OPTIONS")
@API.route(
    "/<int:inspection_record_id>/download-requests/latest",
    methods=["GET", "OPTIONS"],
)
class IRDownloadRequestLatest(Resource):
    """Resource for fetching the latest IR download request."""

    @staticmethod
    @API.response(code=200, description="Success", model=ir_download_request_schema)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch the latest IR download request for a staff member",
    )
    @API.doc(
        params={
            "created_by": {
                "description": "Staff ID (GUID) of the user who created the request",
                "in": "query",
                "type": "string",
                "required": True,
            }
        }
    )
    @auth.require
    def get(inspection_record_id):
        """Fetch the latest IR download request by inspection record and staff ID.

        Returns the most recent download request for the specified inspection record
        and staff member, ordered by creation date descending.
        """
        # Validate query parameters
        query_schema = IRDownloadRequestQuerySchema()
        query_params = query_schema.load(request.args)
        staff_id = query_params.get("created_by")

        download_request = IRDownloadRequestService.get_latest_download_request(
            inspection_record_id, staff_id
        )

        if not download_request:
            raise ResourceNotFoundError(
                f"No download request found for inspection record {inspection_record_id} "
                f"and staff ID {staff_id}"
            )

        return IRDownloadRequestSchema().dump(download_request), HTTPStatus.OK
