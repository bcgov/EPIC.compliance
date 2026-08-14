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
"""API endpoints for async document jobs."""

from http import HTTPStatus

from flask import g, request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.models.document_job import DocumentJob
from compliance_api.schemas.document_job import DocumentJobSchema, DocumentJobUpdateSchema
from compliance_api.services.document_job import DocumentJobService
from compliance_api.services.staff_user import StaffUserService

from .apihelper import Api as ApiHelper


API = Namespace(
    "document-jobs",
    description="Endpoints for async document jobs management",
)


@API.route("/inspections/<int:inspection_record_id>/recent", methods=["GET"])
class DocumentJobRecent(Resource):
    """Resource for managing document jobs per inspection."""

    @staticmethod
    @API.response(code=200, description="Success", model=[DocumentJob])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch most recent document job for user and inspection"
    )
    @auth.require
    def get(inspection_record_id):
        """Fetch most recent document job for user and inspection."""
        auth_user_guid = g.token_info.get("preferred_username")
        output_format = request.args.get("output_format", "pdf")
        current_staff_user = StaffUserService.get_user_by_auth_guid(auth_user_guid)
        document_job = DocumentJobService.get_most_recent_document_job_for_user(
            current_staff_user.id, inspection_record_id, output_format
        )
        schema = DocumentJobSchema(many=False)
        return schema.dump(document_job), HTTPStatus.OK


@API.route("/inspections/<int:inspection_record_id>/last-generated", methods=["GET"])
class DocumentJobLastGenerated(Resource):
    """Resource for managing document jobs per inspection."""

    @staticmethod
    @API.response(code=200, description="Success", model=[DocumentJob])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch most recent document job for user and inspection"
    )
    @auth.require
    def get(inspection_record_id):
        """Fetch the last time a document was generated for user and inspection."""
        auth_user_guid = g.token_info.get("preferred_username")
        output_format = request.args.get("output_format", "pdf")
        current_staff_user = StaffUserService.get_user_by_auth_guid(auth_user_guid)
        last_generated_time = DocumentJobService.get_last_generated_time_for_user(
            current_staff_user.id, inspection_record_id, output_format
        )
        return {"last_generated_time": last_generated_time}, HTTPStatus.OK


@API.route("/<int:job_id>", methods=["DELETE", "PUT"])
class DocumentJobById(Resource):
    """Resource for getting a specific document job by inspection."""

    @staticmethod
    @API.response(code=200, description="Success")
    @API.response(code=404, description="Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Mark document job as delete"
    )
    @auth.require
    def delete(job_id):
        """Mark document job as deleted by inspection."""
        auth_user_guid = g.token_info.get("preferred_username")
        current_staff_user = StaffUserService.get_user_by_auth_guid(auth_user_guid)
        DocumentJobService.delete(job_id, current_staff_user.id)
        return {}, HTTPStatus.NO_CONTENT

    @staticmethod
    @API.response(code=200, description="Success", model=DocumentJob)
    @API.response(code=404, description="Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update a document job with the given data"
    )
    @auth.require
    def put(job_id: int):
        """Update a document job with the given data."""
        auth_user_guid = g.token_info.get("preferred_username")
        data = DocumentJobUpdateSchema().load(request.get_json())
        current_staff_user = StaffUserService.get_user_by_auth_guid(auth_user_guid)
        job = DocumentJobService.update(job_id, current_staff_user.id, data)
        return DocumentJobSchema().dump(job), HTTPStatus.OK


@API.route("/<int:job_id>/cancel", methods=["POST"])
class DocumentJobCancel(Resource):
    """Resource for cancelling an in-progress document job."""

    @staticmethod
    @API.response(code=200, description="Success", model=DocumentJob)
    @API.response(code=404, description="Not Found")
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Cancel an in-progress document job"
    )
    @auth.require
    def post(job_id: int):
        """Cancel an in-progress document job.

        Returns the resulting job so the caller can tell a genuine cancellation
        from a job that finished generating before the request landed - the
        latter comes back COMPLETED and stays downloadable.
        """
        auth_user_guid = g.token_info.get("preferred_username")
        current_staff_user = StaffUserService.get_user_by_auth_guid(auth_user_guid)
        job = DocumentJobService.cancel(job_id, current_staff_user.id)
        return DocumentJobSchema().dump(job), HTTPStatus.OK
