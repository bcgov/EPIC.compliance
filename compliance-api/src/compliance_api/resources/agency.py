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
"""API endpoints for managing agency resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import AgencyCreateSchema, AgencySchema
from compliance_api.services import AgencyService
from compliance_api.utils.enum import PermissionEnum

from .apihelper import Api as ApiHelper


API = Namespace("agencies", description="Endpoints for Agency Management")

agency_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AgencyCreateSchema(), "Agency"
)
agency_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AgencySchema(), "AgencyList"
)


@API.route("", methods=["POST", "GET"])
class Agencies(Resource):
    """Resource for managing agencies."""

    @staticmethod
    @API.response(code=200, description="Success", model=[agency_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all agencies")
    @auth.require
    def get():
        """Fetch all agencies."""
        agencies = AgencyService.get_all()
        agency_list_schema = AgencySchema(many=True)
        return agency_list_schema.dump(agencies), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an agency")
    @API.expect(agency_request_model)
    @API.response(code=201, model=agency_list_model, description="AgencyCreated")
    @API.response(400, "Bad Request")
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER, PermissionEnum.ADMIN])
    def post():
        """Create a agency."""
        agency_data = AgencyCreateSchema().load(API.payload)
        created_agency = AgencyService.create(agency_data)
        return AgencySchema().dump(created_agency), HTTPStatus.CREATED


@API.route("/<int:agency_id>", methods=["PATCH", "GET", "DELETE"])
@API.doc(params={"agency_id": "The unique identifier of agency"})
class Agency(Resource):
    """Resource for managing a single agency."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch an agency by id")
    @API.response(code=200, model=agency_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(agency_id):
        """Fetch an agency by id."""
        agency = AgencyService.get_by_id(agency_id)
        if not agency:
            raise ResourceNotFoundError(f"Agency with {agency_id} not found")
        return AgencySchema().dump(agency), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Update an agency by id")
    @API.expect(agency_request_model)
    @API.response(code=200, model=agency_list_model, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER, PermissionEnum.ADMIN])
    def patch(agency_id):
        """Update an agency by id."""
        agency_data = AgencyCreateSchema().load(API.payload)
        updated_agency = AgencyService.update(agency_id, agency_data)
        if not updated_agency:
            raise ResourceNotFoundError(f"Agency with {agency_id} not found")
        return AgencySchema().dump(updated_agency), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete an agency by id")
    @API.response(code=200, model=agency_list_model, description="Deleted")
    @API.response(404, "Not Found")
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER, PermissionEnum.ADMIN])
    def delete(agency_id):
        """Delete an agency by id."""
        deleted_agency = AgencyService.delete(agency_id)
        if not deleted_agency:
            raise ResourceNotFoundError(f"Agency with {agency_id} not found")
        return AgencySchema().dump(deleted_agency), HTTPStatus.OK
