"""API endpoints for managing continuation report resource."""

from http import HTTPStatus

from flask import current_app, request, send_file
from flask_restx import Namespace, Resource, ValidationError

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import (
    ContinuationReportCreateSchema, ContinuationReportSchema, ContinuationReportUpdateSchema, CRGetQueryParamSchema)
from compliance_api.schemas.continuation_report import CRExport
from compliance_api.services import ContinuationReportService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("continuation-reports", description="Endpoints for Continuation Report")

cr_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ContinuationReportCreateSchema(), "ContinuationReport"
)
cr_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ContinuationReportSchema(), "ContinuationReportList"
)
cr_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ContinuationReportUpdateSchema(), "UpdateSchema"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class ContinuationReports(Resource):
    """Resource for managing continuation report."""

    @staticmethod
    @API.response(code=200, description="Success", model=[cr_list_model])
    @API.doc(
        params={
            "case_file_id": {
                "description": "The unique identifier of the case file",
                "type": "integer",
                "required": True,
            },
            "page_no": {
                "description": "The number of page to be returned",
                "type": "integer",
                "required": True,
            },
            "page_size": {
                "description": "The number of items in the page",
                "type": "integer",
                "required": True,
            },
            "search_text": {
                "description": "The text to be searched",
                "type": "string",
                "required": False,
            },
        }
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all continuation report"
    )
    @auth.require
    def get():
        """Fetch all complaints."""
        request_params = CRGetQueryParamSchema().load(request.args)
        case_file_id = request_params.get("case_file_id")
        page_no = request_params.get("page_no")
        page_size = request_params.get("page_size")
        search_text = request_params.get("search_text")
        crs, total = ContinuationReportService.get_by_case_file_id(
            case_file_id, page_no, page_size, search_text
        )
        return {
            "items": ContinuationReportSchema(many=True).dump(crs),
            "total": total,
        }, HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create an continuation report entry"
    )
    @API.expect(cr_request_model)
    @API.response(code=201, model=cr_list_model, description="ReportEntryCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create a agency."""
        report_data = ContinuationReportCreateSchema().load(API.payload)
        created_entry = ContinuationReportService.create(report_data)
        return ContinuationReportSchema().dump(created_entry), HTTPStatus.CREATED


@cors_preflight("OPTIONS, DELETE, PATCH")
@API.route("/<int:entry_id>", methods=["PATCH", "DELETE", "OPTIONS"])
@API.doc(params={"entry_id": "The unique identifier of continuation report entry"})
class ContinuationReport(Resource):
    """Resource for managing a single continuation report entry."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update a continuation report entry by id"
    )
    @API.expect(cr_request_model)
    @API.response(code=200, model=cr_list_model, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def patch(entry_id):
        """Update an agency by id."""
        cr_data = ContinuationReportUpdateSchema().load(API.payload)
        updated_cr = ContinuationReportService.update(entry_id, cr_data)
        if not updated_cr:
            raise ResourceNotFoundError(
                f"Continuation report entry with {entry_id} not found"
            )
        return ContinuationReportSchema().dump(updated_cr), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete a continuation report by id"
    )
    @API.response(code=200, model=cr_list_model, description="Deleted")
    @API.response(404, "Not Found")
    def delete(entry_id):
        """Delete a continuation report entry by id."""
        deleted_cr = ContinuationReportService.delete(entry_id)
        if not deleted_cr:
            raise ResourceNotFoundError(
                f"Continuation report entry with {entry_id} not found"
            )
        return ContinuationReportSchema().dump(deleted_cr), HTTPStatus.OK


@cors_preflight("OPTIONS, POST")
@API.route("/render", methods=["POST", "OPTIONS"])
class ContinuationReportExport(Resource):
    """Resource for exporting continuation report."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Export continuation report as PDF"
    )
    @API.response(code=200, description="Success")
    @API.response(400, "Bad Request")
    def post():
        """Export continuation report as PDF."""
        current_app.logger.info(f"Received request to export continuation report with payload: {API.payload}")
        try:
            request_params = CRExport().load(API.payload)
            case_file_number = request_params.get("case_file_number")
            pdf_data = ContinuationReportService.render(case_file_number)
            return send_file(
                pdf_data,
                as_attachment=True,
                download_name=f'{case_file_number}.pdf',
                mimetype='application/pdf'
            )
        except ValidationError as validation_error:
            return {"message": str(validation_error)}, HTTPStatus.BAD_REQUEST
        except ValueError as value_error:
            return {"message": str(value_error)}, HTTPStatus.BAD_REQUEST
