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
"""API endpoints for managing sentence type option resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas.sentence_type_option import SentenceTypeOptionSchema
from compliance_api.services.sentence_type_option import SentenceTypeOptionService
from compliance_api.utils.cache import cache

from .apihelper import Api as ApiHelper


API = Namespace(
    "sentence-type-options",
    description="Endpoints for Sentence Type Option Management",
)

sentence_type_option_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, SentenceTypeOptionSchema(), "List"
)


@API.route("", methods=["GET"])
class SentenceTypeOptions(Resource):
    """Resource for managing sentence type options."""

    @staticmethod
    @API.response(
        code=200, description="Success", model=[sentence_type_option_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all active sentence type options"
    )
    @auth.require
    @cache.cached(timeout=86400)  # Cache for 1 day (86400 seconds)
    def get():
        """Fetch all active sentence type options."""
        sentence_type_options = SentenceTypeOptionService.get_all_active()
        list_schema = SentenceTypeOptionSchema(many=True)
        return list_schema.dump(sentence_type_options), HTTPStatus.OK
