"""Resources for inspection record."""

import threading
from datetime import datetime, timezone
from http import HTTPStatus

from flask import current_app, g
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.models.document_job import DocumentJobStatusEnum
from compliance_api.schemas import (
    CreateInspectionRecordApprovalSchema, DocumentJobSchema, InspectionRecordApprovalSchema,
    InspectionRecordCreateSchema, InspectionRecordSchema, RenderRequestSchema, ResetInspectionRecordFieldSchema,
    UpdateInspectionRecordApprovalSchema, UpdateInspectionRecordApprovalStatusSchema, UpdateInspectionRecordSchema)
from compliance_api.services import (
    DocumentJobService, InspectionRecordApprovalService, InspectionRecordService, StaffUserService)
from compliance_api.services.service_utils import ServiceUtils
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
ir_render_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RenderRequestSchema(), "IRRenderRequest"
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
    @API.expect(ir_render_request_model)
    @auth.require
    def post(
        inspection_id, inspection_record_id
    ):  # pylint: disable=no-self-use, unused-argument
        """Preview inspection record."""
        render_request = RenderRequestSchema().load(API.payload or {})
        output_format = render_request.get("output_format", "html")
        auth_user_guid = g.token_info["preferred_username"]
        current_staff_user = StaffUserService.get_user_by_auth_guid(auth_user_guid)
        staff_user_id = current_staff_user.id if current_staff_user else None

        if not staff_user_id:
            raise ResourceNotFoundError("Staff user not found for the current user")

        if output_format == "pdf":
            inspection = ServiceUtils.inspection_exist_check(inspection_id)
            ServiceUtils.access_check_update_for_inspection(inspection)
            DocumentJobService.invalidate_all_previous_documents_for_user(staff_user_id, inspection_record_id)
            document_job = DocumentJobService.create({
                "user_id": staff_user_id,
                "inspection_record_id": inspection_record_id,
                "status": DocumentJobStatusEnum.IN_PROGRESS.value,
                "started_at": datetime.now(timezone.utc),
            })
            access_token = getattr(g, "access_token", None)
            jwt_oidc_token_info = getattr(g, "jwt_oidc_token_info", None)
            thread = threading.Thread(
                target=DocumentJobService.handle_background_job,
                args=(
                    current_app._get_current_object(),  # pylint: disable=protected-access
                    document_job.id,
                    access_token,
                    jwt_oidc_token_info,
                    inspection_id,
                    inspection_record_id,
                    staff_user_id,
                ),
            )
            thread.start()
            return DocumentJobSchema().dump(document_job), HTTPStatus.ACCEPTED

        response, _ = InspectionRecordService.render(
            inspection_id,
            inspection_record_id,
            output_format,
        )
        return response.json(), HTTPStatus.OK
