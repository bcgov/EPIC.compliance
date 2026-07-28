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
"""API endpoints for managing requirement source resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import RequirementSourceSchema
from compliance_api.services import RequirementSourceService

from .apihelper import Api as ApiHelper


API = Namespace(
    "requirement-sources",
    description="Endpoints for Requirement Source Resource Management",
)

requirement_source_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RequirementSourceSchema(), "List"
)


@API.route("", methods=["GET"])
class RequirementSource(Resource):
    """Resource for managing requirement source."""

    @staticmethod
    @API.response(
        code=200, description="Success", model=[requirement_source_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all requirement sources"
    )
    @auth.require
    def get():
        """Fetch all requirement sources."""
        requirement_sources = RequirementSourceService.get_requirement_sources()
        list_schema = RequirementSourceSchema(many=True)
        return list_schema.dump(requirement_sources), HTTPStatus.OK
