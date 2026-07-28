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
"""API endpoints for managing Appendix resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import AppendixCreateSchema, AppendixSchema
from compliance_api.services import AppendixService

from .apihelper import Api as ApiHelper


API = Namespace("appendices", description="Endpoints for Appendix Management")

appendix_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AppendixCreateSchema(), "Appendix"
)
appendix_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AppendixSchema(), "AppendixList"
)


@API.route("", methods=["POST", "GET"])
class Appendices(Resource):
    """Resource for managing appendices."""

    @staticmethod
    @API.response(code=200, description="Success", model=[appendix_list_model])
    @API.doc(
        params={
            "inspection_id": {
                "description": "The unique identifier of the inspection",
                "type": "integer",
                "required": False,
            }
        }
    )
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all appendices")
    @auth.require
    def get():
        """Fetch all appendices."""
        inspection_id = request.args.get("inspection_id", None)
        if inspection_id:
            appendices = AppendixService.get_by_inspection_id(inspection_id)
        else:
            appendices = AppendixService.get_all()
        appendix_list_schema = AppendixSchema(many=True)
        return appendix_list_schema.dump(appendices), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an Appendix")
    @API.expect(appendix_request_model)
    @API.response(code=201, model=appendix_list_model, description="AppendixCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create a Appendix."""
        appendix_data = AppendixCreateSchema().load(API.payload)
        created_appendix = AppendixService.create(appendix_data)
        return AppendixSchema().dump(created_appendix), HTTPStatus.CREATED


@API.route("/<int:appendix_id>", methods=["PATCH", "GET", "DELETE"])
@API.doc(params={"appendix_id": "The unique identifier of appendix"})
class Appendix(Resource):
    """Resource for managing a single Appendix."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch an appendix by id")
    @API.response(code=200, model=appendix_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(appendix_id):
        """Fetch an appendix by id."""
        appendix = AppendixService.get_by_id(appendix_id)
        if not appendix:
            raise ResourceNotFoundError(f"Appendix with {appendix_id} not found")
        return AppendixSchema().dump(appendix), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Update an appendix by id")
    @API.expect(appendix_request_model)
    @API.response(code=200, model=appendix_list_model, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def patch(appendix_id):
        """Update an Appendix by id."""
        appendix_data = AppendixCreateSchema().load(API.payload)
        updated_appendix = AppendixService.update(appendix_id, appendix_data)
        if not updated_appendix:
            raise ResourceNotFoundError(f"Appendix with {appendix_id} not found")
        return AppendixSchema().dump(updated_appendix), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete an appendix by id")
    @API.response(code=200, model=appendix_list_model, description="Deleted")
    @API.response(404, "Not Found")
    def delete(appendix_id):
        """Delete an appendix by id."""
        deleted_appendix = AppendixService.delete(appendix_id)
        if not deleted_appendix:
            raise ResourceNotFoundError(f"Appendix with {appendix_id} not found")
        return AppendixSchema().dump(deleted_appendix), HTTPStatus.OK
