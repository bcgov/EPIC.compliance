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
"""API endpoints for managing staff user resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import KeyValueSchema, StaffUserCreateSchema, StaffUserSchema, StaffUserUpdateSchema
from compliance_api.services import StaffUserService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("staff-users", description="Endpoints for Staff User Management")

user_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, StaffUserCreateSchema(), "StaffUserCreate"
)
user_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, StaffUserUpdateSchema(), "StaffUserUpdate"
)
user_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, StaffUserSchema(), "StaffUserList"
)
key_value_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class StaffUsers(Resource):
    """Resource for managing users."""

    @staticmethod
    @API.response(code=200, description="Success", model=[user_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all users")
    @auth.require
    def get():
        """Fetch all users."""
        users = StaffUserService.get_all_staff_users()
        user_list_schema = StaffUserSchema(many=True)
        return user_list_schema.dump(users), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create a user")
    @API.expect(user_request_model)
    @API.response(code=201, model=user_list_model, description="UserCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create a user."""
        user_data = StaffUserCreateSchema().load(API.payload)
        created_user = StaffUserService.create_user(user_data)
        setattr(created_user, "permission", user_data.get("permission", None))
        return StaffUserSchema().dump(created_user), HTTPStatus.CREATED


@cors_preflight("GET, OPTIONS, PATCH, DELETE")
@API.route("/<int:user_id>", methods=["PATCH", "GET", "OPTIONS", "DELETE"])
@API.doc(params={"user_id": "The user identifier"})
class StaffUser(Resource):
    """Resource for managing a single user."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch a user by id")
    @API.response(code=200, model=user_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(user_id):
        """Fetch a user by id."""
        user = StaffUserService.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundError(f"User with {user_id} not found")
        return StaffUserSchema().dump(user), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Update a user by id")
    @API.expect(user_update_model)
    @API.response(code=200, model=user_list_model, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def patch(user_id):
        """Update a user by id."""
        user_data = StaffUserUpdateSchema().load(API.payload)
        updated_user = StaffUserService.update_user(user_id, user_data)
        if not updated_user:
            raise ResourceNotFoundError(f"User with {user_id} not found")
        return StaffUserSchema().dump(updated_user), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete a user by id")
    @API.response(code=200, model=user_list_model, description="Deleted")
    @API.response(404, "Not Found")
    def delete(user_id):
        """Delete a user by id."""
        deleted_user = StaffUserService.delete_user(user_id)
        if not deleted_user:
            raise ResourceNotFoundError(f"User with {user_id} not found")
        return StaffUserSchema().dump(deleted_user), HTTPStatus.OK


@cors_preflight("GET")
@API.route("/permissions", methods=["GET"])
class StaffUserPermissions(Resource):
    """Resources to manage permission level of staff user."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Get the permission levels")
    @API.response(code=200, model=key_value_list_model, description="Success")
    def get():
        """Fetch the permission levels."""
        permissions = StaffUserService.get_permission_levels()
        return KeyValueSchema(many=True).dump(permissions), HTTPStatus.OK
