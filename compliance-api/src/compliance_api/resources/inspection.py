# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoints for managing inspection resource."""

from http import HTTPStatus

from flask import current_app, request, send_file
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import (
    InspectionAttendanceSchema, InspectionCreateSchema, InspectionFilterSchema, InspectionMoreDetailsSchema,
    InspectionOfficerSchema, InspectionReqImageSchema, InspectionRequirementBulkUpdateSchema, InspectionSchema,
    InspectionStatusSchema, InspectionUpdateSchema, KeyValueSchema, StaffUserSchema)
from compliance_api.services import InspectionRequirementService, InspectionService
from compliance_api.utils.enum import PermissionEnum
from compliance_api.utils.schema_utils import get_pagination_schema
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("inspections", description="Endpoints for Inspection Management")

keyvalue_list_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)

inspection_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionCreateSchema(), "Inspection"
)
inspection_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionSchema(), "InspectionList"
)
inspection_filter_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionFilterSchema(), "InspectionFilter"
)
inspection_officer_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionOfficerSchema(), "InspectionOfficer"
)
staff_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, StaffUserSchema(), "StaffList"
)
inspection_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionUpdateSchema(), "InspectionUpdate"
)
inspection_status_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionStatusSchema(), "InspectionStatus"
)
inspesction_req_image_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionReqImageSchema(), "InspectionReqImageSchema"
)
inspection_requirement_bulk_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRequirementBulkUpdateSchema(), "InspectionRequirementBulkUpdate"
)
inspection_more_details_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionMoreDetailsSchema(), "InspectionMoreDetails"
)


@cors_preflight("GET, OPTIONS")
@API.route("/attendance-options", methods=["GET", "OPTIONS"])
class AttendanceOptions(Resource):
    """Resource for managing attendance options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all inspection attendance options"
    )
    @auth.require
    def get():
        """Fetch all inspection attendance options."""
        attendance_options = InspectionService.get_all_attendance_options()
        attendance_options_schema = KeyValueSchema(many=True)
        return attendance_options_schema.dump(attendance_options), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/type-options", methods=["GET", "OPTIONS"])
class IRTypeOptions(Resource):
    """Resource for managing IRType options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all inspection IRType options"
    )
    @auth.require
    def get():
        """Fetch all inspection IRType options."""
        ir_type_options = InspectionService.get_inspection_type_options()
        ir_type_options_schema = KeyValueSchema(many=True)
        return ir_type_options_schema.dump(ir_type_options), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/initiation-options", methods=["GET", "OPTIONS"])
class InitiationOptions(Resource):
    """Resource for managing initiation options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all inspection initiation options"
    )
    @auth.require
    def get():
        """Fetch all inspection initiation options."""
        initiation_options = InspectionService.get_initiation_options()
        initiation_options_schema = KeyValueSchema(many=True)
        return initiation_options_schema.dump(initiation_options), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/ir-status-options", methods=["GET", "OPTIONS"])
class IRStatusOptions(Resource):
    """Resource for managing IRStatus options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all IRStatus options"
    )
    @auth.require
    def get():
        """Fetch all IRStatus options."""
        ir_status_options = InspectionService.get_ir_status_options()
        ir_status_options_schema = KeyValueSchema(many=True)
        return ir_status_options_schema.dump(ir_status_options), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class Inspections(Resource):
    """Resource for managing inspections."""

    @staticmethod
    @API.response(code=200, description="Success")
    @API.doc(
        params={
            "case_file_id": {
                "description": "The unique identifier of the case file",
                "type": "integer",
                "required": False,
            },
            "ir_number": {
                "description": "Filter by inspection record number",
                "type": "string",
                "required": False,
            },
            "project_ids": {
                "description": "Filter by project ID(s). Can be a single value or comma-separated list "
                "(supports 'null' or 'none' for unapproved projects)",
                "type": "string",
                "required": False,
            },
            "start_date": {
                "description": "Filter by inspection start date",
                "type": "string",
                "required": False,
            },
            "initiation_ids": {
                "description": "Filter by initiation option ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "ir_progresses": {
                "description": "Filter by IR progress status(es). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "approval_statuses": {
                "description": "Filter by approval status(es). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "primary_officer_ids": {
                "description": "Filter by primary officer ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "statuses": {
                "description": "Filter by inspection status(es). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "case_file_number": {
                "description": "Filter by case file number",
                "type": "string",
                "required": False,
            },
            "approved_by_ids": {
                "description": "Filter by reviewer/approver ID(s). Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            **get_pagination_schema("ir_number"),
        }
    )
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch all inspections with pagination, filtering, and sorting",
    )
    @auth.require
    def get():
        """Fetch all inspections with pagination, filtering, and sorting."""
        args = request.args
        inspections, total_count = InspectionService.get_inspections_paginated(args)
        inspection_list_schema = InspectionSchema(many=True)
        return {
            "items": inspection_list_schema.dump(inspections),
            "total": total_count,
        }, HTTPStatus.OK

    @staticmethod
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an inspection")
    @API.expect(inspection_create_model)
    @API.response(
        code=201, model=inspection_list_model, description="InspectionCreated"
    )
    @API.response(400, "Bad Request")
    @auth.require
    def post():
        """Create an inspection."""
        current_app.logger.info(f"Creating Inspection with payload: {API.payload}")
        inspection_data = InspectionCreateSchema().load(API.payload)
        created_inspection = InspectionService.create(inspection_data)
        return InspectionSchema().dump(created_inspection), HTTPStatus.CREATED


@cors_preflight("POST, OPTIONS")
@API.route("/export", methods=["POST", "OPTIONS"])
class InspectionExport(Resource):
    """Resource for exporting inspections to Excel."""

    @staticmethod
    @API.expect(inspection_filter_model)
    @API.response(code=200, description="Excel file generated successfully")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Export inspections to Excel"
    )
    @auth.require
    def post():
        """Export inspections to Excel based on filters."""
        filter_data = InspectionFilterSchema().load(API.payload or {})
        excel_file = InspectionService.generate_inspections_excel(filter_data)

        return send_file(
            excel_file,
            as_attachment=True,
            download_name="inspections_export.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


@cors_preflight("GET, OPTIONS")
@API.route("/more-details", methods=["POST", "GET", "OPTIONS"])
class InspectionDetails(Resource):
    """Resource for managing inspections."""

    @staticmethod
    @API.response(
        code=200, description="Success", model=[inspection_more_details_model]
    )
    @API.doc(
        params={
            "case_file_id": {
                "description": "The unique identifier of the case file",
                "type": "integer",
                "required": False,
            }
        }
    )
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all inspections")
    @auth.require
    def get():
        """Fetch all inspections."""
        case_file_id = request.args.get("case_file_id")
        inspections = InspectionService.get_inspection_details(case_file_id)
        inspection_more_details_schema = InspectionMoreDetailsSchema(many=True)
        return inspection_more_details_schema.dump(inspections), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST")
@API.route(
    "/<int:inspection_id>/attendance-options", methods=["POST", "GET", "OPTIONS"]
)
class InspectionAttendances(Resource):
    """Resource for managing inspections."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspection_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all inspections")
    @auth.require
    def get(inspection_id):
        """Fetch all inspections."""
        attendances = InspectionService.get_attendance_options(inspection_id)
        inspection_attendance_schema = InspectionAttendanceSchema(many=True)
        return inspection_attendance_schema.dump(attendances), HTTPStatus.OK


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route("/<int:inspection_id>", methods=["GET", "PATCH", "OPTIONS", "DELETE"])
class Inspection(Resource):
    """Inspection resource."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspection_list_model])
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch inspection by id")
    @auth.require
    def get(inspection_id):
        """Fetch all inspections."""
        inspection = InspectionService.get_by_id(inspection_id)
        if not inspection:
            raise ResourceNotFoundError(
                f"No inspection found for the given ID : {inspection_id}"
            )
        inspection_list_schema = InspectionSchema()
        return inspection_list_schema.dump(inspection), HTTPStatus.OK

    @staticmethod
    @API.response(code=200, description="Sucess", model=[inspection_list_model])
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @API.expect(inspection_update_model)
    @ApiHelper.swagger_decorators(API, endpoint_description="Update inspection")
    @auth.require
    def patch(inspection_id):
        """Update inspection."""
        inspection_data = InspectionUpdateSchema().load(API.payload)
        updated_inspection = InspectionService.update(inspection_id, inspection_data)
        return InspectionSchema().dump(updated_inspection), HTTPStatus.OK

    @staticmethod
    @auth.require
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER])
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete a Inspection by id")
    @API.response(code=204, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def delete(inspection_id):
        """Delete complaint."""
        InspectionService.delete_inspection(inspection_id)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS")
@API.route("/ir-numbers/<string:ir_number>", methods=["GET", "OPTIONS"])
class InspectionByIRNumber(Resource):
    """Inspection resource."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspection_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch inspection by id")
    @auth.require
    def get(ir_number):
        """Fetch all inspections."""
        inspection = InspectionService.get_by_ir_number(ir_number)
        inspection_list_schema = InspectionSchema()
        return inspection_list_schema.dump(inspection), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:inspection_id>/status", methods=["PATCH", "OPTIONS"])
@API.doc(params={"inspection_id": "The unique identifier for the inspection"})
class InspectionStatus(Resource):
    """Update the inspection status."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(inspection_status_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Change inspection status")
    @API.response(code=204, description="Inspection status changed")
    def patch(inspection_id):
        """Change Inspection Status."""
        status = InspectionStatusSchema().load(API.payload)
        InspectionService.change_status(inspection_id, status)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS")
@API.route("/<int:inspection_id>/images", methods=["GET", "OPTIONS"])
class InspectionImages(Resource):
    """Resource for fetching images resource per inspection."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspesction_req_image_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all images per inspection"
    )
    @auth.require
    def get(inspection_id):
        """Fetch all inspection images."""
        images = InspectionRequirementService.get_all_images_by_inspection(
            inspection_id
        )
        image_schema = InspectionReqImageSchema(many=True)
        return image_schema.dump(images), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:inspection_id>/requirements", methods=["PATCH", "OPTIONS"])
class InspectionRequirements(Resource):
    """Resource for updating inspection requirements."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(inspection_requirement_bulk_update_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update inspection requirements"
    )
    @API.response(code=204, description="Requirements updated successfully")
    def patch(inspection_id):
        """Update inspection requirements and their images."""
        data = InspectionRequirementBulkUpdateSchema().load(API.payload)
        InspectionRequirementService.update_requirements(
            inspection_id, data["requirements"]
        )
        return {}, HTTPStatus.NO_CONTENT
