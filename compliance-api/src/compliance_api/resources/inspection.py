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

from flask import current_app, request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import (
    InspectionAttendanceSchema, InspectionCreateSchema, InspectionOfficerSchema, InspectionSchema, KeyValueSchema,
    StaffUserSchema)
from compliance_api.services import InspectionService
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
inspection_officer_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionOfficerSchema(), "InspectionOfficer"
)
staff_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, StaffUserSchema(), "StaffList"
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
    @API.response(code=200, description="Success", model=[inspection_list_model])
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
        if case_file_id:
            inspections = InspectionService.get_by_case_file_id(case_file_id)
        else:
            inspections = InspectionService.get_all()
        inspection_list_schema = InspectionSchema(many=True)
        return inspection_list_schema.dump(inspections), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an inspection")
    @API.expect(inspection_create_model)
    @API.response(
        code=201, model=inspection_list_model, description="InspectionCreated"
    )
    @API.response(400, "Bad Request")
    def post():
        """Create an inspection."""
        current_app.logger.info(f"Creating Inspection with payload: {API.payload}")
        inspection_data = InspectionCreateSchema().load(API.payload)
        created_inspection = InspectionService.create(inspection_data)
        return InspectionSchema().dump(created_inspection), HTTPStatus.CREATED


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


@cors_preflight("GET, OPTIONS")
@API.route("/<int:inspection_id>", methods=["GET", "OPTIONS"])
class Inspection(Resource):
    """Inspection resource."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspection_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch inspection by id")
    @auth.require
    def get(inspection_id):
        """Fetch all inspections."""
        inspection = InspectionService.get_by_id(inspection_id)
        inspection_list_schema = InspectionSchema()
        return inspection_list_schema.dump(inspection), HTTPStatus.OK


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


@cors_preflight("GET, OPTIONS")
@API.route("/<int:inspection_id>/officers", methods=["GET", "OPTIONS"])
class InspectionOfficers(Resource):
    """Inspection resource."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspection_list_model])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch officers of inspection by id"
    )
    @auth.require
    def get(inspection_id):
        """Fetch all inspections."""
        officers = InspectionService.get_other_officers(inspection_id)
        staff_list_schema = StaffUserSchema(many=True)
        return staff_list_schema.dump(officers), HTTPStatus.OK
