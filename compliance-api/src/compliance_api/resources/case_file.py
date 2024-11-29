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
"""API endpoints for managing CaseFile resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import (
    CaseFileCreateSchema, CaseFileOfficerSchema, CaseFileSchema, CaseFileStatusSchema, CaseFileUpdateSchema,
    KeyValueSchema, StaffUserSchema)
from compliance_api.services import CaseFileService
from compliance_api.services.case_file_aggregate import CaseFileAggregateService
from compliance_api.utils.enum import PermissionEnum
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("case-files", description="Endpoints for CaseFile Resource Management")

key_value_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)
case_file_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileCreateSchema(), "CaseFile"
)
case_file_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileSchema(), "CaseFileList"
)
case_file_officer_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileOfficerSchema(), "OtherOfficers"
)
staff_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, StaffUserSchema(), "StaffList"
)
case_file_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileSchema(), "CaseFileUpdate"
)
case_file_status_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileStatusSchema(), "CaseFileStatus"
)


@cors_preflight("GET, OPTIONS")
@API.route("/initiation-options", methods=["POST", "GET", "OPTIONS"])
class CaseFileInitiation(Resource):
    """Resource for managing initiation options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[key_value_list_model])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all initiation options"
    )
    @auth.require
    def get():
        """Fetch all case initiation optoins."""
        initiation_options = CaseFileService.get_initiation_options()
        key_val_schema = KeyValueSchema(many=True)
        return key_val_schema.dump(initiation_options), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class CaseFiles(Resource):
    """Resource for managing CaseFiles."""

    @staticmethod
    @API.doc(
        params={
            "project_id": {
                "description": "The unique identifier of the project",
                "type": "integer",
                "required": False,
            }
        }
    )
    @API.response(code=200, description="Success", model=[case_file_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all case files")
    @auth.require
    def get():
        """Fetch all casefiles."""
        project_id = request.args.get("project_id", None)
        if project_id:
            case_files = CaseFileService.get_by_project(project_id)
        else:
            case_files = CaseFileService.get_all()
        case_file_list_schema = CaseFileSchema(many=True)
        return case_file_list_schema.dump(case_files), HTTPStatus.OK

    @staticmethod
    @auth.require
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER, PermissionEnum.USER])
    @ApiHelper.swagger_decorators(API, endpoint_description="Create a case file")
    @API.expect(case_file_create_model)
    @API.response(code=201, model=case_file_list_model, description="CaseFileCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create a case file."""
        case_file_data = CaseFileCreateSchema().load(API.payload)
        created_case_file = CaseFileService.create(case_file_data)
        return CaseFileSchema().dump(created_case_file), HTTPStatus.CREATED


@cors_preflight("GET, OPTIONS, PATCH, DELETE")
@API.route("/<int:case_file_id>", methods=["PATCH", "GET", "OPTIONS", "DELETE"])
@API.doc(params={"case_file_id": "The unique identifier for the case file"})
class CaseFile(Resource):
    """Resource for managing a single CaseFile."""

    @staticmethod
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch a CaseFile by id")
    @API.response(code=200, model=case_file_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(case_file_id):
        """Fetch a CaseFile by id."""
        case_file = CaseFileService.get_by_id(case_file_id)
        if not case_file:
            raise ResourceNotFoundError(f"CaseFile with {case_file_id} not found")
        return CaseFileSchema().dump(case_file), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Update a CaseFile by id")
    @API.expect(case_file_update_model)
    @API.response(code=200, model=case_file_list_model, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def patch(case_file_id):
        """Update a CaseFile by id."""
        case_file_data = CaseFileUpdateSchema().load(API.payload)
        updated_case_file = CaseFileService.update(case_file_id, case_file_data)
        if not updated_case_file:
            raise ResourceNotFoundError(f"CaseFile with {case_file_id} not found")
        return CaseFileSchema().dump(updated_case_file), HTTPStatus.OK

    @staticmethod
    @auth.require
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER, PermissionEnum.USER])
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete a CaseFile by id")
    @API.response(code=204, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def delete(case_file_id):
        """Delete case file."""
        CaseFileAggregateService.delete_case_file(case_file_id)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS")
@API.route("/case-file-numbers/<string:case_file_number>", methods=["GET", "OPTIONS"])
@API.doc(params={"case_file_number": "The unique file number for the case file"})
class CaseFileNumber(Resource):
    """Resource for managing a single CaseFile."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch a CaseFile by id")
    @API.response(code=200, model=case_file_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(case_file_number):
        """Fetch a CaseFile by number."""
        case_file = CaseFileService.get_by_file_number(case_file_number)
        if not case_file:
            raise ResourceNotFoundError(
                f"CaseFile with case file number {case_file_number} not found"
            )
        return CaseFileSchema().dump(case_file), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/<int:case_file_id>/officers", methods=["GET", "OPTIONS"])
@API.doc(params={"case_file_id": "The unique identifier for the case file"})
class CaseFileOtherOfficers(Resource):
    """Other officers resource for a case file."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Get other officers for a given case file"
    )
    @API.response(code=200, model=staff_list_model, description="Success")
    def get(case_file_id):
        """Update a CaseFile by id."""
        officers = CaseFileService.get_other_officers(case_file_id)
        return StaffUserSchema().dump(officers, many=True), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<string:case_file_number>/status", methods=["PATCH", "OPTIONS"])
@API.doc(params={"case_file_number": "The unique file number for the case file"})
class CaseFileNumberStatus(Resource):
    """Update the case file status."""

    @staticmethod
    @auth.require
    @API.expect(case_file_status_model)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Close the case file")
    @API.response(code=204, description="Case file closed")
    def patch(case_file_number):
        """Close case file."""
        status = CaseFileStatusSchema().load(API.payload)
        case_file = CaseFileService.get_by_file_number(case_file_number)
        CaseFileService.change_case_file_status(case_file, status)
        return {}, HTTPStatus.NO_CONTENT
