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
"""API endpoints for managing compliance finding resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas import KeyValueSchema
from compliance_api.services import ComplianceFindingService

from .apihelper import Api as ApiHelper


API = Namespace(
    "compliance-findings",
    description="Endpoints for compliance finding Management",
)

key_value_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, KeyValueSchema(), "List"
)


@API.route("", methods=["GET"])
class ComplianceFindings(Resource):
    """Resource for managing compliance findings."""

    @staticmethod
    @API.response(code=200, description="Success", model=[key_value_list_model])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all compliance findings"
    )
    @auth.require
    def get():
        """Fetch all compliance findings."""
        compliance_findings = ComplianceFindingService.get_compliance_findings()
        list_schema = KeyValueSchema(many=True)
        return list_schema.dump(compliance_findings), HTTPStatus.OK
