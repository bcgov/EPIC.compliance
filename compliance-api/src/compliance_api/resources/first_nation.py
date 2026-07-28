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
"""API endpoints for managing First Nations resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.services.epic_track_service.track_service import TrackService

from .apihelper import Api as ApiHelper


API = Namespace(
    "first-nations",
    description="Endpoints for First Nations Management",
)


@API.route("", methods=["GET"])
class FirstNations(Resource):
    """Resource for fetching First Nations."""

    @staticmethod
    @API.response(code=200, description="Success")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all First Nations from EPIC.track"
    )
    @auth.require
    def get():
        """Fetch all First Nations."""
        first_nations = TrackService.get_first_nations()
        return first_nations, HTTPStatus.OK


@API.route("/<int:first_nation_id>", methods=["GET"])
class FirstNation(Resource):
    """Resource for fetching a single First Nation."""

    @staticmethod
    @API.response(code=200, description="Success")
    @API.response(code=404, description="First Nation not found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a First Nation by ID from EPIC.track"
    )
    @auth.require
    def get(first_nation_id: int):
        """Fetch a First Nation by ID."""
        first_nation = TrackService.get_first_nation_by_id(first_nation_id)
        return first_nation, HTTPStatus.OK
