"""Resources for inspection record."""

from datetime import datetime
from http import HTTPStatus
from io import BytesIO

from flask import request, send_file
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import (
    CreateInspectionRecordApprovalSchema, CreateIRDownloadRequestSchema, InspectionRecordApprovalSchema,
    InspectionRecordCreateSchema, InspectionRecordSchema, IRDownloadRequestSchema, ResetInspectionRecordFieldSchema,
    UpdateInspectionRecordApprovalSchema, UpdateInspectionRecordApprovalStatusSchema, UpdateInspectionRecordSchema)
from compliance_api.services import InspectionRecordApprovalService, InspectionRecordService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("inspection-records", description="Endpoints for Inspection Record")

ir_create_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRecordCreateSchema(), "IRCreateRequest"
)
ir_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRecordSchema(), "IRlist"
)
ir_update_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, UpdateInspectionRecordSchema(), "UpdateInspection"
)
ir_approval_create_request = ApiHelper.convert_ma_schema_to_restx_model(
    API, CreateInspectionRecordApprovalSchema(), "IRApproval"
)
ir_approval_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRecordApprovalSchema(), "IRApproval"
)
ir_approval_update_request = ApiHelper.convert_ma_schema_to_restx_model(
    API, UpdateInspectionRecordApprovalSchema(), "IRApprovalUpdate"
)
ir_reset_field_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ResetInspectionRecordFieldSchema(), "ResetInspectionField"
)
ir_approval_status_update_request = ApiHelper.convert_ma_schema_to_restx_model(
    API, UpdateInspectionRecordApprovalStatusSchema(), "IRApprovalStatusUpdate"
)
ir_download_request_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, IRDownloadRequestSchema(), "IRDownloadRequest"
)
ir_download_request_create_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, CreateIRDownloadRequestSchema(), "CreateIRDownloadRequest"
)


@cors_preflight("GET, OPTIONS, POST, PATCH")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class InspectionRecords(Resource):
    """Resource for managing inspection records."""

    @staticmethod
    @API.response(code=200, description="Success", model=[ir_list_model])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all inspection records"
    )
    @auth.require
    def get(inspection_id):
        """Fetch all inspection records."""
        irs = InspectionRecordService.get_by_inspection_id(inspection_id)
        inspection_record_schema = InspectionRecordSchema(many=False)
        return inspection_record_schema.dump(irs), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create an inspection record"
    )
    @API.expect(ir_create_request_model)
    @API.response(code=201, model=ir_list_model, description="IRCreated")
    @API.response(400, "Bad Request")
    def post(inspection_id):
        """Create a agency."""
        ir_create_request = InspectionRecordCreateSchema().load(API.payload)
        created_ir = InspectionRecordService.create(ir_create_request, inspection_id)
        return InspectionRecordSchema().dump(created_ir), HTTPStatus.CREATED


@cors_preflight("PATCH,GET,DELETE, OPTIONS")
@API.route("/<int:inspection_record_id>", methods=["PATCH", "GET", "DELETE", "OPTIONS"])
class InspectionRecord(Resource):
    """InspectionRecord resource."""

    @staticmethod
    @API.response(code=200, description="Success", model=ir_list_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch inspection record by id"
    )
    @auth.require
    def get(inspection_record_id):
        """Fetch inspection record by id."""
        inspection_record = InspectionRecordService.get_by_id(inspection_record_id)
        if not inspection_record:
            raise ResourceNotFoundError(
                f"No inspection found for the given ID : {inspection_record_id}"
            )
        return InspectionRecordSchema().dump(inspection_record), HTTPStatus.OK

    @staticmethod
    @API.response(code=200, description="Sucess", model=ir_list_model)
    @API.expect(ir_update_request_model)
    @ApiHelper.swagger_decorators(API, endpoint_description="Update inspection record")
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(inspection_id, inspection_record_id):
        """Update inspection record."""
        ir_update_data = UpdateInspectionRecordSchema().load(API.payload)
        updated_ir = InspectionRecordService.update(
            inspection_id, inspection_record_id, ir_update_data
        )
        return InspectionRecordSchema().dump(updated_ir), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete an inspection record by id"
    )
    @API.response(code=204, description="Success")
    @API.response(404, "Not Found")
    @API.response(422, "Unprocessable Entity")
    def delete(inspection_id, inspection_record_id):
        """Delete inspection record."""
        InspectionRecordService.delete_inspection_record(
            inspection_id, inspection_record_id
        )
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:inspection_record_id>/switch-to-final", methods=["PATCH", "OPTIONS"])
class InspectionRecordFinal(Resource):
    """Resource to handle InspectionRecord."""

    @staticmethod
    @API.response(code=200, description="Sucess", model=ir_list_model)
    @ApiHelper.swagger_decorators(API, endpoint_description="Switch to FINAL IR")
    @API.response(404, "Not Found")
    @auth.require
    def patch(inspection_id, inspection_record_id):
        """Swith IR to FINAL."""
        final_ir = InspectionRecordService.switch_to_final(
            inspection_id, inspection_record_id
        )
        return InspectionRecordSchema().dump(final_ir), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST, PATCH")
@API.route("/<int:inspection_record_id>/approvals", methods=["POST", "GET", "OPTIONS"])
class InspectionRecordApprovals(Resource):
    """Resource for managing inspection records."""

    @staticmethod
    @API.response(code=200, description="Success", model=[ir_approval_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all inspection record approvals"
    )
    @auth.require
    def get(
        inspection_id, inspection_record_id
    ):  # pylint: disable=no-self-use, unused-argument
        """Fetch all inspection record approvals."""
        approvals = InspectionRecordApprovalService.get_all_approvals(
            inspection_record_id
        )
        approval_schema = InspectionRecordApprovalSchema(many=True)
        return approval_schema.dump(approvals), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create an inspection record approval"
    )
    @API.expect(ir_approval_create_request)
    @API.response(
        code=201, model=ir_approval_schema, description="IRApprovalRequestCreated"
    )
    @API.response(400, "Bad Request")
    def post(inspection_id, inspection_record_id):
        """Create a agency."""
        ir_approval_request = CreateInspectionRecordApprovalSchema().load(API.payload)
        created_aproval = InspectionRecordApprovalService.create_approval(
            ir_approval_request, inspection_id, inspection_record_id
        )
        return (
            InspectionRecordApprovalSchema().dump(created_aproval),
            HTTPStatus.CREATED,
        )


@cors_preflight("OPTIONS, PATCH, GET")
@API.route(
    "/<int:inspection_record_id>/approvals/<int:approval_id>",
    methods=["PATCH", "GET", "OPTIONS"],
)
class InspectionRecordApproval(Resource):
    """Resource for managing inspection record approval."""

    @staticmethod
    @API.response(code=200, description="Sucess", model=ir_approval_schema)
    @API.expect(ir_approval_update_request)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update inspection record approval"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(inspection_id, inspection_record_id, approval_id):
        """Update inspection record approval."""
        approval_update_data = UpdateInspectionRecordApprovalSchema().load(API.payload)
        updated_approval = InspectionRecordApprovalService.update_approval(
            inspection_id, inspection_record_id, approval_id, approval_update_data
        )
        return InspectionRecordApprovalSchema().dump(updated_approval), HTTPStatus.OK


@cors_preflight("OPTIONS, PATCH, GET")
@API.route(
    "/<int:inspection_record_id>/approvals/<int:approval_id>/status",
    methods=["PATCH", "OPTIONS"],
)
class InspectionRecordApprovalStatus(Resource):
    """Resource for managing inspection record approval status."""

    @staticmethod
    @API.response(code=200, description="Sucess", model=ir_approval_schema)
    @API.expect(ir_approval_status_update_request)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update inspection record approval status"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(inspection_id, inspection_record_id, approval_id):
        """Update inspection record approval."""
        approval_update_data = UpdateInspectionRecordApprovalStatusSchema().load(
            API.payload
        )
        updated_approval = InspectionRecordApprovalService.update_approval_status(
            inspection_id, inspection_record_id, approval_id, approval_update_data
        )
        return InspectionRecordApprovalSchema().dump(updated_approval), HTTPStatus.OK


@cors_preflight("OPTIONS, PATCH")
@API.route("/<int:inspection_record_id>/reset", methods=["PATCH", "OPTIONS"])
class InspectionRecordReset(Resource):
    """Resource for resetting inspection record fields."""

    @staticmethod
    @API.response(code=200, description="Success", model=ir_list_model)
    @API.expect(ir_reset_field_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Reset inspection record field"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(inspection_id, inspection_record_id):
        """Reset a specific field in the inspection record."""
        reset_data = ResetInspectionRecordFieldSchema().load(API.payload)
        updated_ir = InspectionRecordService.reset_field(
            inspection_id, inspection_record_id, reset_data["field_name"]
        )
        if not updated_ir:
            raise ResourceNotFoundError("Inspection record not found")
        return InspectionRecordSchema().dump(updated_ir), HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/<int:inspection_record_id>/render", methods=["POST", "OPTIONS"])
class InspectionRecordPreview(Resource):
    """Resource for managing inspection records."""

    @staticmethod
    @API.response(code=200, description="Success")
    @ApiHelper.swagger_decorators(API, endpoint_description="Preview inspection record")
    @API.doc(
        params={
            "output_format": {
                "description": "The output format of the inspection record",
                "type": "string",
                "required": False,
                "default": "html",
                "enum": ["html", "pdf"],
            }
        }
    )
    @auth.require
    def post(
        inspection_id, inspection_record_id
    ):  # pylint: disable=no-self-use, unused-argument
        """Preview inspection record."""
        output_format = request.json.get("output_format", "html")
        response, inspection = InspectionRecordService.render(
            inspection_id, inspection_record_id, output_format
        )
        if output_format == "pdf":
            return send_file(
                BytesIO(response.content),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{inspection.ir_number}.pdf",
            )
        return response.json(), HTTPStatus.OK


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
    @API.response(
        code=201,
        model=ir_download_request_schema,
        description="Download request created",
    )
    @API.response(400, "Bad Request")
    @API.response(409, "Conflict - Request already exists")
    def post(inspection_id, inspection_record_id):
        """Create an IR download request.

        Creates a new download request for the specified inspection record.
        Prevents duplicate requests by checking if a pending/not-started request
        already exists for the same inspection record and user.
        """
        # TEMPORARY: Fake response for development
        # TODO: Uncomment the service call below when ready
        # created_request = IRDownloadRequestService.create_download_request(
        #     inspection_record_id
        # )
        # return (
        #     IRDownloadRequestSchema().dump(created_request),
        #     HTTPStatus.CREATED,
        # )

        # Fake JSON response
        fake_response = {
            "id": 101,
            "inspection_record_id": inspection_record_id,
            "download_status": {"id": "NOT_STARTED", "name": "Not Started"},
            "relative_url": None,
            "generated_timestamp": None,
            "created_date": datetime.utcnow().isoformat() + "Z",
            "updated_date": None,
            "created_by": "fake-staff-guid-12345",
            "updated_by": None,
            "is_active": True,
            "is_deleted": False,
        }

        return fake_response, HTTPStatus.CREATED


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
    def get(inspection_id, inspection_record_id):
        """Fetch the latest IR download request by inspection record and staff ID.

        Returns the most recent download request for the specified inspection record
        and staff member, ordered by creation date descending.
        """
        # TEMPORARY: Fake response for development
        # TODO: Uncomment the service call below when ready
        # query_schema = IRDownloadRequestQuerySchema()
        # query_params = query_schema.load(request.args)
        # staff_id = query_params.get("created_by")

        # download_request = IRDownloadRequestService.get_latest_download_request(
        #     inspection_record_id, staff_id
        # )

        # if not download_request:
        #     raise ResourceNotFoundError(
        #         f"No download request found for inspection record {inspection_record_id} "
        #         f"and staff ID {staff_id}"
        #     )

        # return IRDownloadRequestSchema().dump(download_request), HTTPStatus.OK

        # Get staff_id from query params for the fake response
        staff_id = request.args.get("created_by", "fake-staff-guid-12345")
        fake_response = {
            "id": 204,
            "inspection_record_id": inspection_record_id,
            "download_status": {"id": "DOWNLOADED", "name": "Downloaded"},
            "relative_url": f"/downloads/ir_{inspection_record_id}_report.pdf",
            "generated_timestamp": "2024-10-24T14:15:00Z",
            "created_date": "2024-10-24T14:10:00Z",
            "updated_date": "2024-10-24T14:18:00Z",
            "created_by": staff_id,
            "updated_by": staff_id,
            "is_active": True,
            "is_deleted": False,
        }

        return fake_response, HTTPStatus.OK
