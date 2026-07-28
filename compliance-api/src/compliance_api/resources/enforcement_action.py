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
"""API endpoints for managing enforcement action resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import KeyValueSchema
from compliance_api.services import EnforcementActionService

from .apihelper import Api as ApiHelper


API = Namespace(
    "enforcement-actions",
    description="Endpoints for Enforcement Action Management",
)

key_value_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)


@API.route("", methods=["GET"])
class EnforcementActions(Resource):
    """Resource for managing enforcement actions."""

    @staticmethod
    @API.response(code=200, description="Success", model=[key_value_list_model])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all enforcement actions"
    )
    @auth.require
    def get():
        """Fetch all enforcement actions."""
        enforcement_actions = EnforcementActionService.get_enforcement_actions()
        list_schema = KeyValueSchema(many=True)
        return list_schema.dump(enforcement_actions), HTTPStatus.OK
