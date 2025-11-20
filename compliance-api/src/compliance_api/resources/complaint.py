"""API endpoints for managing complaints."""

from http import HTTPStatus

from flask import current_app, make_response, request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import (
    ComplaintCreateSchema, ComplaintFilterSchema, ComplaintSchema, ComplaintSourceContactSchema, ComplaintStatusSchema,
    ComplaintUpdateSchema, KeyValueSchema, RequirementSourceDetailSchema)
from compliance_api.services import ComplaintService
from compliance_api.utils.enum import PermissionEnum
from compliance_api.utils.schema_utils import get_pagination_schema
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("complaints", description="Endpoints for Complaints")

keyvalue_list_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)

complaint_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ComplaintCreateSchema(), "Complaint"
)

complaint_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ComplaintSchema(), "ComplaintList"
)

complaint_source_contact_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ComplaintSourceContactSchema(), "SourceContact"
)

complaint_requirement_details = ApiHelper.convert_ma_schema_to_restx_model(
    API, RequirementSourceDetailSchema(), "RequirementDetails"
)
complaint_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ComplaintUpdateSchema(), "ComplaintUpdate"
)
complaint_status_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ComplaintStatusSchema(), "ComplaintStatus"
)
complaint_filter_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ComplaintFilterSchema(), "ComplaintFilter"
)


@cors_preflight("GET, OPTIONS")
@API.route("/sources", methods=["GET", "OPTIONS"])
class ComplaintSources(Resource):
    """Resource for complaint sources."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all complaint sources"
    )
    @auth.require
    def get():
        """Fetch all complaint sources."""
        complaint_sources = ComplaintService.get_complaint_sources()
        complaint_sources_schema = KeyValueSchema(many=True)
        return complaint_sources_schema.dump(complaint_sources), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/resolutions", methods=["GET", "OPTIONS"])
class ComplaintResolutions(Resource):
    """Resource for complaint resolutions."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all complaint resolutions"
    )
    @auth.require
    def get():
        """Fetch all complaint resolutions."""
        complaint_resolutions = ComplaintService.get_complaint_resolutions()
        complaint_resolutions_schema = KeyValueSchema(many=True)
        return complaint_resolutions_schema.dump(complaint_resolutions), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class Complaints(Resource):
    """Resource for managing complaints."""

    @staticmethod
    @API.response(code=200, description="Success", model=[complaint_list_model])
    @API.doc(
        params={
            "complaint_number": {
                "description": "Filter by complaint number",
                "type": "string",
                "required": False,
            },
            "project_ids": {
                "description": "Filter by project ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "topic_ids": {
                "description": "Filter by topic ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "source_type_ids": {
                "description": "Filter by source type ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "date_received": {
                "description": "Filter by date received (YYYY-MM-DD)",
                "type": "string",
                "required": False,
            },
            "primary_officer_ids": {
                "description": "Filter by primary officer ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "statuses": {
                "description": "Filter by complaint status(es). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "case_file_number": {
                "description": "Filter by case file number",
                "type": "string",
                "required": False,
            },
            "case_file_id": {
                "description": "Filter by case file ID",
                "type": "integer",
                "required": False,
            },
            "resolution_ids": {
                "description": "Filter by resolution ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            **get_pagination_schema("complaint_number"),
        }
    )
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch all complaints with pagination, filtering, and sorting",
    )
    @auth.require
    def get():
        """Fetch all complaints with pagination, filtering, and sorting."""
        args = request.args
        complaints, total_count = ComplaintService.get_complaints_paginated(args)
        complaint_list_schema = ComplaintSchema(many=True)
        return {
            "items": complaint_list_schema.dump(complaints),
            "total": total_count,
        }, HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an complaint")
    @API.expect(complaint_create_model)
    @API.response(code=201, model=complaint_list_model, description="ComplaintCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create an complaint."""
        current_app.logger.info(f"Creating Complaint with payload: {API.payload}")
        complaint_data = ComplaintCreateSchema().load(API.payload)
        created_complaint = ComplaintService.create(complaint_data)
        return ComplaintSchema().dump(created_complaint), HTTPStatus.CREATED


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route("/<int:complaint_id>", methods=["OPTIONS", "GET", "PATCH", "DELETE"])
@API.doc(params={"complaint_id": "The unique identifier for the complaint"})
class Complaint(Resource):
    """Resource for managing a single Complaint."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch a complaint by id")
    @API.response(code=200, model=complaint_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(complaint_id):
        """Fetch a complaint by id."""
        complaint = ComplaintService.get_by_id(complaint_id)
        if not complaint:
            raise ResourceNotFoundError(f"Complaint with {complaint} not found")
        return ComplaintSchema().dump(complaint), HTTPStatus.OK

    @staticmethod
    @API.response(code=200, description="Sucess", model=[complaint_list_model])
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.expect(complaint_update_model)
    @ApiHelper.swagger_decorators(API, endpoint_description="Update complaint")
    @auth.require
    def patch(complaint_id):
        """Update complaint."""
        complaint_data = ComplaintUpdateSchema().load(API.payload)
        updated_complaint = ComplaintService.update(complaint_id, complaint_data)
        return ComplaintSchema().dump(updated_complaint), HTTPStatus.OK

    @staticmethod
    @auth.require
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER])
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete a Complaint by id")
    @API.response(code=204, description="Success")
    @API.response(404, "Not Found")
    def delete(complaint_id):
        """Delete complaint."""
        deleted_complaint = ComplaintService.delete_complaint(complaint_id)
        if not deleted_complaint:
            raise ResourceNotFoundError(f"Complaint with ID {complaint_id} not found")
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS")
@API.route("/<int:complaint_id>/requirement-details", methods=["OPTIONS", "GET"])
@API.doc(params={"complaint_id": "The unique identifier for the complaint"})
class ComplaintRequirementDetails(Resource):
    """Resource for managing a Complaint requirement details.."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a complaint requirement details"
    )
    @API.response(code=200, model=complaint_requirement_details, description="Success")
    def get(complaint_id):
        """Fetch a complaint requirement details."""
        requirements = ComplaintService.get_requirement_details(complaint_id)
        return RequirementSourceDetailSchema().dump(requirements), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/<int:complaint_id>/source-contacts", methods=["OPTIONS", "GET"])
@API.doc(params={"complaint_id": "The unique identifier for the complaint"})
class ComplaintContact(Resource):
    """Resource for managing a Complaint Contact."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a complaint source contact"
    )
    @API.response(code=200, model=complaint_source_contact_model, description="Success")
    @API.response(404, "Not Found")
    def get(complaint_id):
        """Fetch a complaint source contact."""
        contact = ComplaintService.get_source_contact(complaint_id)
        if not contact:
            raise ResourceNotFoundError("Complaint source contact doesn't found")
        return ComplaintSourceContactSchema().dump(contact), HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/export", methods=["POST", "OPTIONS"])
class ComplaintExport(Resource):
    """Resource for exporting complaints to Excel."""

    @staticmethod
    @API.expect(complaint_filter_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Export complaints to Excel with filtering"
    )
    @auth.require
    def post():
        """Export complaints to Excel with filtering."""
        # Get filter data from request body
        filter_data = ComplaintFilterSchema().load(API.payload or {})

        # Generate Excel file
        excel_file = ComplaintService.generate_complaints_excel(filter_data)

        # Create response
        response = make_response(excel_file.getvalue())
        response.headers["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=complaints_export.xlsx"
        )

        return response


@cors_preflight("GET, OPTIONS")
@API.route("/complaint-numbers/<string:complaint_number>", methods=["GET", "OPTIONS"])
class ComplaintByNumber(Resource):
    """Complaint resource."""

    @staticmethod
    @API.response(code=200, description="Success", model=[complaint_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch complaint by number")
    @auth.require
    def get(complaint_number):
        """Fetch all complaint."""
        complaint = ComplaintService.get_by_complaint_no(complaint_number)
        if not complaint:
            raise ResourceNotFoundError(f"Complaint with {complaint_number} not found")
        complaint_list_schema = ComplaintSchema()
        return complaint_list_schema.dump(complaint), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:complaint_id>/status", methods=["PATCH", "OPTIONS"])
@API.doc(params={"complaint_id": "The unique identifier for the complaint"})
class ComplaintStatus(Resource):
    """Update the complaint status."""

    @staticmethod
    @auth.require
    @API.expect(complaint_status_model)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Change the complaint status"
    )
    @API.response(code=204, description="Complaint status updated successfully")
    def patch(complaint_id):
        """Change complaint status.

        When status is 'Closed', resolution_id and resolution_agency_id can be provided.
        When status is 'Open', these fields are automatically cleared.
        """
        status = ComplaintStatusSchema().load(API.payload)
        ComplaintService.change_complaint_status(complaint_id, status)
        return {}, HTTPStatus.NO_CONTENT
