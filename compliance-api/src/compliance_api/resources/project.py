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
"""API endpoints for managing project resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import ProjectSchema
from compliance_api.services import ProjectService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("projects", description="Endpoints for Project Management")
project_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ProjectSchema(), "ProjectListSchema"
)


@cors_preflight("GET, OPTIONS")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class Projects(Resource):
    """Resource for managing projects."""

    @staticmethod
    @API.response(code=200, description="Success", model=[project_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all agencies")
    @auth.require
    def get():
        """Fetch all projects."""
        projects = ProjectService.get_all_projects()
        project_list_schema = ProjectSchema(many=True)
        return project_list_schema.dump(projects), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/<int:project_id>", methods=["GET", "OPTIONS"])
@API.doc(params={"project_id": "The unique identifier of project"})
class Project(Resource):
    """Resource for managing a single project."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch a project by id")
    @API.response(code=200, model=project_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(project_id):
        """Fetch an project by id."""
        project = ProjectService.get_project_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"Project with {project_id} not found")
        return ProjectSchema().dump(project), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route("/<int:project_id>/abbreviation", methods=["GET", "OPTIONS"])
@API.doc(params={"project_id": "The unique identifier of project"})
class ProjectAbbreviation(Resource):
    """Resource for fetching a project's abbreviation by id."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch a projects abbreviation by id")
    @API.response(code=200, description="Success")
    @API.response(404, "Not Found")
    def get(project_id):
        """Fetch a project's abbreviation by id."""
        abbreviation = ProjectService.get_project_abbreviation_by_id(project_id)
        if not abbreviation:
            raise ResourceNotFoundError(f"Project with {project_id} not found")
        return abbreviation, HTTPStatus.OK
