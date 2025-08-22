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

from datetime import datetime
from http import HTTPStatus
from io import BytesIO

from flask import request, send_file
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import (
    CaseFileCreateSchema, CaseFileFilterSchema, CaseFileLinkCreateSchema, CaseFileLinkSchema, CaseFileOfficerSchema,
    CaseFileOptionSchema, CaseFileSchema, CaseFileStatusSchema, CaseFileUnlinkSchema, CaseFileUpdateSchema,
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
case_file_link_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileLinkCreateSchema(), "CaseFileLinkCreate"
)
case_file_link_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileLinkSchema(), "CaseFileLink"
)
case_file_option_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileOptionSchema(), "CaseFileOptionSchema"
)
case_file_unlink_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileUnlinkSchema(), "CaseFileUnlinkSchema"
)
case_file_filter_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CaseFileFilterSchema(), "CaseFileFilter"
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
            "project_ids": {
                "description": (
                    "The unique identifier(s) of the project. "
                    "Can be a single value or comma-separated list. "
                    "Use 'null' or 'none' to filter for unapproved projects"
                ),
                "type": "string",
                "required": False,
            },
            "case_file_number": {
                "description": "The case file number to filter by",
                "type": "string",
                "required": False,
            },
            "initiation_ids": {
                "description": "The initiation option ID(s) to filter by. "
                "Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "statuses": {
                "description": "The case file status(es) to filter by (OPEN/CLOSE). "
                "Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "primary_officer_ids": {
                "description": "The primary officer ID(s) to filter by. Can be a single value or comma-separated list",
                "type": "string",
                "required": False,
            },
            "date_created": {
                "description": "Filter case files created on this date (YYYY-MM-DD)",
                "type": "string",
                "required": False,
            },
            "page_no": {
                "description": "The page number for pagination",
                "type": "integer",
                "required": False,
            },
            "page_size": {
                "description": "The number of items per page",
                "type": "integer",
                "required": False,
            },
            "sort_by": {
                "description": (
                    "Field to sort by (case_file_number, project, initiation, "
                    "date_created, status, primary_officer)"
                ),
                "type": "string",
                "required": False,
            },
            "sort_order": {
                "description": "Sort order (asc/desc)",
                "type": "string",
                "required": False,
            },
        }
    )
    @API.response(code=200, description="Success", model=[case_file_list_model])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all case files with pagination and filtering"
    )
    @auth.require
    def get():
        """Fetch all casefiles with pagination and filtering."""
        case_files, total = CaseFileService.get_all_with_pagination(request.args)
        case_file_list_schema = CaseFileSchema(many=True)
        return {
            "items": case_file_list_schema.dump(case_files),
            "total": total,
        }, HTTPStatus.OK

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
        deleted_case_file = CaseFileAggregateService.delete_case_file(case_file_id)
        if not deleted_case_file:
            raise ResourceNotFoundError(f"CaseFile with {case_file_id} not found")
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
@API.route("/<int:case_file_id>/status", methods=["PATCH", "OPTIONS"])
@API.doc(params={"case_file_id": "The unique identifier for the case file"})
class CaseFileStatus(Resource):
    """Update the case file status."""

    @staticmethod
    @auth.require
    @API.expect(case_file_status_model)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Close the case file")
    @API.response(code=204, description="Case file closed")
    def patch(case_file_id):
        """Close case file."""
        status = CaseFileStatusSchema().load(API.payload)
        CaseFileService.change_case_file_status(case_file_id, status)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("POST, GET, OPTIONS")
@API.route("/<int:case_file_id>/links", methods=["POST", "GET", "OPTIONS"])
@API.doc(params={"case_file_id": "The unique identifier for the case file"})
class CaseFileLinks(Resource):
    """Link the case file."""

    @staticmethod
    @auth.require
    @API.expect(case_file_link_create_model)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.response(code=201, model=case_file_link_model, description="Success")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Link the case file to another case file"
    )
    @API.response(code=204, description="Case file linked")
    def post(case_file_id):
        """Link the case file."""
        link = CaseFileLinkCreateSchema().load(API.payload)
        created_link = CaseFileService.link(case_file_id, link)
        return CaseFileLinkSchema().dump(created_link), HTTPStatus.CREATED

    @staticmethod
    @ApiHelper.swagger_decorators(API, endpoint_description="Get all linked case files")
    @API.response(code=200, model=[case_file_option_schema], description="Success")
    def get(case_file_id):
        """Get all linked case files."""
        case_files = CaseFileService.get_linked_case_files(case_file_id)
        case_file_list_schema = CaseFileOptionSchema(many=True)
        return case_file_list_schema.dump(case_files), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:case_file_id>/unlink", methods=["PATCH", "OPTIONS"])
@API.doc(params={"case_file_id": "The unique identifier for the case file"})
class CaseFileUnlink(Resource):
    """Unlink the case file."""

    @staticmethod
    @auth.require
    @API.expect(case_file_unlink_schema)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.response(code=204, description="Success")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Unlink the case file from another case file"
    )
    @API.response(code=204, description="Case file is unlined")
    def patch(case_file_id):
        """Unlink the case file."""
        unlink = CaseFileUnlinkSchema().load(API.payload)
        CaseFileService.unlink(case_file_id, unlink)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("POST, OPTIONS")
@API.route("/export", methods=["POST", "OPTIONS"])
class CaseFilesExport(Resource):
    """Export all case files as Excel."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Export all case files as Excel"
    )
    @API.expect(case_file_filter_model)
    @API.doc()
    @API.response(code=200, description="Success - Excel file download")
    @auth.require
    def post():
        """Export all case files as Excel."""
        # Get filter parameters from request body instead of query parameters
        schema = CaseFileFilterSchema()
        filter_data = schema.load(request.json or {})
        output = CaseFileService.generate_case_files_excel(filter_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"case_files_{timestamp}.xlsx"

        # Return the Excel file as a downloadable attachment
        return send_file(BytesIO(output), as_attachment=True, download_name=filename)


@API.route("/options")
class CaseFileOptions(Resource):
    """Resource for getting case file options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[key_value_list_model])
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch active case files as id-name pairs for dropdown options",
    )
    @auth.require
    def get():
        """Fetch active case files as id-name pairs."""
        case_file_options = CaseFileService.get_case_file_options()
        schema = KeyValueSchema(many=True)
        return schema.dump(case_file_options), HTTPStatus.OK
