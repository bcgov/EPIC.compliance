"""Warning Letter Resource."""

from http import HTTPStatus
from io import BytesIO

from flask import request, send_file
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import RenderRequestSchema
from compliance_api.schemas.warning_letter import (
    ResetWarningLetterFieldSchema, WarningLetterCreateSchema, WarningLetterIssueSchema, WarningLetterSchema,
    WarningLetterStatusSchema, WarningLetterUpdateSchema)
from compliance_api.schemas.warning_letter_approval import (
    CreateWarningLetterApprovalSchema, UpdateWarningLetterApprovalStatusSchema, WarningLetterApprovalSchema)
from compliance_api.services.warning_letter.warning_letter import WarningLetterService
from compliance_api.services.warning_letter.warning_letter_approval import WarningLetterApprovalService

from ..utils.util import cors_preflight
from .apihelper import Api as ApiHelper


API = Namespace("warning-letters", description="Endpoints for Warning Letters")

warning_letter_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, WarningLetterCreateSchema(), "WarningLetterCreate"
)

warning_letter_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, WarningLetterSchema(), "WarningLetterList"
)
warning_letter_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, WarningLetterUpdateSchema(), "WarningLetterUpdate"
)
warning_letter_status_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, WarningLetterStatusSchema(), "WarningLetterStatus"
)
warning_letter_issue_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, WarningLetterIssueSchema(), "WarningLetterIssue"
)
reset_warning_letter_field_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ResetWarningLetterFieldSchema(), "ResetWarningLetterField"
)
warning_letter_render_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RenderRequestSchema(), "WarningLetterRenderRequest"
)
warning_letter_approval_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, WarningLetterApprovalSchema(), "WarningLetterApproval"
)
warning_letter_approval_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CreateWarningLetterApprovalSchema(), "WarningLetterApprovalCreate"
)
warning_letter_approval_status_update_model = (
    ApiHelper.convert_ma_schema_to_restx_model(
        API,
        UpdateWarningLetterApprovalStatusSchema(),
        "WarningLetterApprovalStatusUpdate",
    )
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class WarningLetters(Resource):
    """Resource for managing warning letters."""

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=[warning_letter_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all warning letters")
    @API.doc(
        params={
            "inspection_id": {
                "description": "The unique identifier of the inspection",
                "type": "integer",
                "required": True,
            }
        }
    )
    def get():
        """Fetch all warning letters."""
        inspection_id = request.args.get("inspection_id")
        warning_letters = WarningLetterService.get_all(inspection_id, sort_by="warning_letter_number")
        warning_letter_list_schema = WarningLetterSchema(many=True)
        return warning_letter_list_schema.dump(warning_letters), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create a warning letter")
    @API.expect(warning_letter_create_model)
    @API.response(
        code=201, model=warning_letter_list_model, description="WarningLetterCreated"
    )
    @API.response(400, "Bad Request")
    def post():
        """Create a warning letter."""
        warning_letter_data = WarningLetterCreateSchema().load(API.payload)
        created_warning_letter = WarningLetterService.create_warning_letter(
            warning_letter_data
        )
        return WarningLetterSchema().dump(created_warning_letter), HTTPStatus.CREATED


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route("/<int:warning_letter_id>", methods=["OPTIONS", "GET", "PATCH", "DELETE"])
@API.doc(params={"warning_letter_id": "The unique identifier for the warning letter"})
class WarningLetter(Resource):
    """Resource for managing a single Warning Letter."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a warning letter by id"
    )
    @API.response(code=200, model=warning_letter_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(warning_letter_id):
        """Fetch a warning letter by id."""
        warning_letter = WarningLetterService.get_warning_letter(warning_letter_id)
        if not warning_letter:
            raise ResourceNotFoundError(
                f"Warning letter with {warning_letter_id} not found"
            )
        return WarningLetterSchema().dump(warning_letter), HTTPStatus.OK

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=[warning_letter_list_model])
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.expect(warning_letter_update_model)
    @ApiHelper.swagger_decorators(API, endpoint_description="Update warning letter")
    def patch(warning_letter_id):
        """Update warning letter."""
        warning_letter_data = WarningLetterUpdateSchema().load(API.payload)
        updated_warning_letter = WarningLetterService.update_warning_letter(
            warning_letter_id, warning_letter_data
        )
        return WarningLetterSchema().dump(updated_warning_letter), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete a warning letter by id"
    )
    @API.response(code=204, description="Success")
    @API.response(404, "Not Found")
    def delete(warning_letter_id):
        """Delete warning letter."""
        WarningLetterService.delete_warning_letter(warning_letter_id)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route(
    "/warning-letter-numbers/<string:warning_letter_number>", methods=["GET", "OPTIONS"]
)
@API.doc(
    params={"warning_letter_number": "The unique identifier for the warning letter"}
)
class WarningLetterByWarningLetterNumber(Resource):
    """Resource for managing a single Warning Letter."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a warning letter by id"
    )
    @API.response(code=200, model=warning_letter_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(warning_letter_number):
        """Fetch a warning letter by id."""
        warning_letter = (
            WarningLetterService.get_warning_letter_by_warning_letter_number(
                warning_letter_number
            )
        )
        if not warning_letter:
            raise ResourceNotFoundError(
                f"Warning letter with {warning_letter_number} not found"
            )
        return WarningLetterSchema().dump(warning_letter), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:warning_letter_id>/reset", methods=["PATCH", "OPTIONS"])
@API.doc(params={"warning_letter_id": "The unique identifier for the warning letter"})
class WarningLetterReset(Resource):
    """Reset specific fields in a warning letter."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(reset_warning_letter_field_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Reset warning letter field"
    )
    @API.response(code=200, description="Success", model=warning_letter_list_model)
    def patch(warning_letter_id):
        """Reset a specific field in the warning letter."""
        reset_data = ResetWarningLetterFieldSchema().load(API.payload)
        updated_warning_letter = WarningLetterService.reset_field(
            warning_letter_id, reset_data["field_name"]
        )
        return WarningLetterSchema().dump(updated_warning_letter), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:warning_letter_id>/issue", methods=["PATCH", "OPTIONS"])
@API.doc(params={"warning_letter_id": "The unique identifier for the warning letter"})
class WarningLetterIssue(Resource):
    """Update the inspection status."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(warning_letter_issue_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Issue warning letter")
    @API.response(code=204, description="Warning letter issued")
    def patch(warning_letter_id):
        """Issue Warning Letter."""
        issue = WarningLetterIssueSchema().load(API.payload)
        WarningLetterService.issue_warning_letter(warning_letter_id, issue)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("POST, OPTIONS")
@API.route("/<int:warning_letter_id>/render", methods=["POST", "OPTIONS"])
class WarningLetterPreview(Resource):
    """Resource for managing warning letter preview and pdf."""

    @staticmethod
    @API.response(code=200, description="Success")
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Preview warning letter")
    @API.expect(warning_letter_render_request_model)
    @auth.require
    def post(warning_letter_id):  # pylint: disable=unused-argument
        """Preview warning letter."""
        render_request = RenderRequestSchema().load(API.payload or {})
        output_format = render_request.get("output_format", "html")
        response, warning_letter = WarningLetterService.render(
            warning_letter_id, output_format
        )
        if output_format == "pdf":
            return send_file(
                BytesIO(response.content),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{warning_letter.warning_letter_number}.pdf",
            )
        return response.json(), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST, PATCH")
@API.route("/<int:warning_letter_id>/approvals", methods=["POST", "GET", "OPTIONS"])
class WarningLetterApprovals(Resource):
    """Resource for managing warning letter approvals."""

    @staticmethod
    @API.response(404, "Not Found")
    @API.response(
        code=200, description="Success", model=[warning_letter_approval_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all warning letter approvals"
    )
    @auth.require
    def get(warning_letter_id):  # pylint: disable=unused-argument
        """Fetch all warning letter approvals."""
        approvals = WarningLetterApprovalService.get_all_approvals(warning_letter_id)
        approval_schema = WarningLetterApprovalSchema(many=True)
        return approval_schema.dump(approvals), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create an warning letter approval"
    )
    @API.expect(warning_letter_approval_create_model)
    @API.response(
        code=201,
        model=warning_letter_approval_model,
        description="WarningLetterApprovalRequestCreated",
    )
    @API.response(400, "Bad Request")
    def post(warning_letter_id):
        """Create a agency."""
        warning_letter_approval_request = CreateWarningLetterApprovalSchema().load(
            API.payload
        )
        created_aproval = WarningLetterApprovalService.create_approval(
            warning_letter_approval_request, warning_letter_id
        )
        return (
            WarningLetterApprovalSchema().dump(created_aproval),
            HTTPStatus.CREATED,
        )


@cors_preflight("OPTIONS, PATCH, GET")
@API.route(
    "/<int:warning_letter_id>/approvals/<int:approval_id>/status",
    methods=["PATCH", "OPTIONS"],
)
class WarningLetterApprovalStatus(Resource):
    """Resource for managing warning letter approval status."""

    @staticmethod
    @API.response(code=200, description="Sucess", model=warning_letter_approval_model)
    @API.expect(warning_letter_approval_status_update_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update warning letter approval status"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(warning_letter_id, approval_id):
        """Update warning letter approval."""
        approval_update_data = UpdateWarningLetterApprovalStatusSchema().load(
            API.payload
        )
        updated_approval = WarningLetterApprovalService.update_approval_status(
            warning_letter_id, approval_id, approval_update_data
        )
        return WarningLetterApprovalSchema().dump(updated_approval), HTTPStatus.OK
