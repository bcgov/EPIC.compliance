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
"""API endpoints for managing project status option resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import KeyValueSchema
from compliance_api.services import ProjectStatusService

from .apihelper import Api as ApiHelper


API = Namespace(
    "project-status-options",
    description="Endpoints for Project Status Option Management",
)

keyvalue_list_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)


@API.route("", methods=["GET"])
class ProjectStatusOptions(Resource):
    """Resource for managing project status options."""

    @staticmethod
    @API.response(code=200, description="Success", model=[keyvalue_list_schema])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all project status options"
    )
    @auth.require
    def get():
        """Fetch all project status options."""
        project_status_options = ProjectStatusService.get_all_project_status_options()
        project_status_options_schema = KeyValueSchema(many=True)
        return project_status_options_schema.dump(project_status_options), HTTPStatus.OK
