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

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import KeyValueSchema
from compliance_api.services import InspectionService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("inspections", description="Endpoints for Inspection Management")

keyvalue_list_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
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
        attendance_options = InspectionService.get_attendance_options()
        attendance_options_schema = KeyValueSchema(many=True)
        return attendance_options_schema.dump(attendance_options), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/ir-type-options", methods=["GET", "OPTIONS"])
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
        ir_type_options = InspectionService.get_ir_type_options()
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