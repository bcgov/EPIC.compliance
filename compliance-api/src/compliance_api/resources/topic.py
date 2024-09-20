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
"""API endpoints for managing topic resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource
from flask import current_app, g

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.schemas import TopicCreateSchema, TopicSchema
from compliance_api.services import TopicService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("topics", description="Endpoints for Topic Management")

topic_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, TopicCreateSchema(), "Topic"
)
topic_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, TopicSchema(), "TopicList"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class Topics(Resource):
    """Resource for managing topics."""

    @staticmethod
    @API.response(code=200, description="Success", model=[topic_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all topics")
    def get():
        """Fetch all topics."""
        app_name = current_app.config["APP_NAME"]
        print('----app_name--', app_name)

        topics = TopicService.get_all()
        topic_list_schema = TopicSchema(many=True)
        return topic_list_schema.dump(topics), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an topic")
    @API.expect(topic_request_model)
    @API.response(code=201, model=topic_list_model, description="topicCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create a topic."""
        topic_data = TopicCreateSchema().load(API.payload)
        created_topic = TopicService.create(topic_data)
        return TopicSchema().dump(created_topic), HTTPStatus.CREATED


@cors_preflight("GET, OPTIONS, PATCH, DELETE")
@API.route("/<int:topic_id>", methods=["PATCH", "GET", "OPTIONS", "DELETE"])
@API.doc(params={"topic_id": "The unique identifier of topic"})
class Topic(Resource):
    """Resource for managing a single topic."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch an topic by id")
    @API.response(code=200, model=topic_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(topic_id):
        """Fetch an topic by id."""
        topic = TopicService.get_by_id(topic_id)
        if not topic:
            raise ResourceNotFoundError(f"topic with {topic_id} not found")
        return TopicSchema().dump(topic), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Update an topic by id")
    @API.expect(topic_request_model)
    @API.response(code=200, model=topic_list_model, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def patch(topic_id):
        """Update an topic by id."""
        topic_data = TopicCreateSchema().load(API.payload)
        updated_topic = TopicService.update(topic_id, topic_data)
        if not updated_topic:
            raise ResourceNotFoundError(f"topic with {topic_id} not found")
        return TopicSchema().dump(updated_topic), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete an topic by id")
    @API.response(code=200, model=topic_list_model, description="Deleted")
    @API.response(404, "Not Found")
    def delete(topic_id):
        """Delete an topic by id."""
        deleted_topic = TopicService.delete(topic_id)
        if not deleted_topic:
            raise ResourceNotFoundError(f"topic with {topic_id} not found")
        return TopicSchema().dump(deleted_topic), HTTPStatus.OK
