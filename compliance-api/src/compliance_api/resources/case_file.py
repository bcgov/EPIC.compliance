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

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import KeyValueSchema
from compliance_api.services import CaseFileService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("case-files", description="Endpoints for CaseFile Resource Management")

key_value_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
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
        """Fetch all users."""
        initiation_options = CaseFileService.get_initiation_options()
        key_val_schema = KeyValueSchema(many=True)
        return key_val_schema.dump(initiation_options), HTTPStatus.OK
