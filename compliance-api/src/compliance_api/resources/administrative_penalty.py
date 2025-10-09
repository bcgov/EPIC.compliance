"""API endpoints for managing administrative penalty resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import BadRequestError
from compliance_api.schemas.administrative_penalty import (
    AdministrativePenaltyCreateSchema, AdministrativePenaltyLinkCreateSchema, AdministrativePenaltyLinksResponseSchema,
    AdministrativePenaltySchema, AdministrativePenaltyUpdateSchema)
from compliance_api.services.administrative_penalty import AdministrativePenaltyService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace(
    "administrative-penalties",
    description="Endpoints for Administrative Penalty Management",
)

administrative_penalty_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AdministrativePenaltyCreateSchema(), "AdministrativePenaltyCreate"
)

administrative_penalty_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AdministrativePenaltySchema(), "AdministrativePenaltyList"
)

administrative_penalty_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AdministrativePenaltyUpdateSchema(), "AdministrativePenaltyUpdate"
)

administrative_penalty_link_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, AdministrativePenaltyLinkCreateSchema(), "AdministrativePenaltyLinkCreate"
)

administrative_penalty_links_response_model = (
    ApiHelper.convert_ma_schema_to_restx_model(
        API,
        AdministrativePenaltyLinksResponseSchema(),
        "AdministrativePenaltyLinksResponse",
    )
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class AdministrativePenalties(Resource):
    """Resource for managing administrative penalties."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=[administrative_penalty_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all administrative penalties"
    )
    @API.doc(
        params={
            "inspection_id": {
                "description": "The unique identifier of the inspection",
                "type": "integer",
                "required": True,
            }
        }
    )
    def get():
        """Fetch all administrative penalties."""
        inspection_id = request.args.get("inspection_id")
        if not inspection_id:
            raise BadRequestError("inspection_id is required")
        administrative_penalties = AdministrativePenaltyService.get_all(inspection_id)
        administrative_penalty_list_schema = AdministrativePenaltySchema(many=True)
        return (
            administrative_penalty_list_schema.dump(administrative_penalties),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create an administrative penalty"
    )
    @API.expect(administrative_penalty_create_model)
    @API.response(
        code=201,
        model=administrative_penalty_list_model,
        description="AdministrativePenaltyCreated",
    )
    @API.response(400, "Bad Request")
    def post():
        """Create an administrative penalty."""
        administrative_penalty_data = AdministrativePenaltyCreateSchema().load(
            API.payload
        )
        created_administrative_penalty = (
            AdministrativePenaltyService.create_administrative_penalty(
                administrative_penalty_data
            )
        )
        return (
            AdministrativePenaltySchema().dump(created_administrative_penalty),
            HTTPStatus.CREATED,
        )


@cors_preflight("GET, OPTIONS")
@API.route("/projectwise", methods=["GET", "OPTIONS"])
class ProjectwiseAdministrativePenalties(Resource):
    """Resource for managing projectwise administrative penalties."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=[administrative_penalty_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all administrative penalties for a project"
    )
    @API.doc(
        params={
            "case_file_id": {
                "description": "The unique identifier of the case file",
                "type": "integer",
                "required": True,
            },
            "include_open_aps": {
                "description": "Include open administrative penalties",
                "type": "boolean",
                "required": False,
            },
        }
    )
    def get():
        """Fetch all administrative penalties for the project associated to the case file."""
        case_file_id = request.args.get("case_file_id")
        if not case_file_id:
            raise BadRequestError("case_file_id is required")
        include_open_aps = request.args.get("include_open_aps")
        administrative_penalties = (
            AdministrativePenaltyService.get_projectwise_administrative_penalties(
                case_file_id, include_open_aps
            )
        )
        administrative_penalty_list_schema = AdministrativePenaltySchema(many=True)
        return (
            administrative_penalty_list_schema.dump(administrative_penalties),
            HTTPStatus.OK,
        )


@cors_preflight("GET, OPTIONS, PATCH, DELETE")
@API.route(
    "/<int:administrative_penalty_id>", methods=["GET", "PATCH", "DELETE", "OPTIONS"]
)
class AdministrativePenaltyById(Resource):
    """Resource for managing a single administrative penalty."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=administrative_penalty_list_model
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch an administrative penalty by id"
    )
    def get(administrative_penalty_id):
        """Fetch an administrative penalty by id."""
        administrative_penalty = AdministrativePenaltyService.get_by_id(
            administrative_penalty_id
        )
        return AdministrativePenaltySchema().dump(administrative_penalty), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update an administrative penalty"
    )
    @API.expect(administrative_penalty_update_model)
    @API.response(
        code=200,
        model=administrative_penalty_list_model,
        description="AdministrativePenaltyUpdated",
    )
    @API.response(400, "Bad Request")
    def patch(administrative_penalty_id):
        """Update an administrative penalty."""
        administrative_penalty_data = AdministrativePenaltyUpdateSchema().load(
            API.payload
        )
        updated_administrative_penalty = (
            AdministrativePenaltyService.update_administrative_penalty(
                administrative_penalty_id, administrative_penalty_data
            )
        )
        return (
            AdministrativePenaltySchema().dump(updated_administrative_penalty),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete an administrative penalty"
    )
    @API.response(code=204, description="NoContent")
    @API.doc(
        params={
            "inspection_id": {
                "description": "Optional inspection ID to validate deletion scope",
                "type": "integer",
                "required": True,
            }
        }
    )
    def delete(administrative_penalty_id):
        """Delete an administrative penalty."""
        #  This should be the inspection id under the scope of deletion
        inspection_id = request.args.get("inspection_id")
        if not inspection_id:
            raise BadRequestError("inspection_id is required")

        AdministrativePenaltyService.delete_administrative_penalty(
            administrative_penalty_id, int(inspection_id)
        )
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS")
@API.route(
    "/by-number/<string:administrative_penalty_number>", methods=["GET", "OPTIONS"]
)
class AdministrativePenaltyByNumber(Resource):
    """Resource for managing a single administrative penalty by number."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=administrative_penalty_list_model
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch an administrative penalty by number"
    )
    def get(administrative_penalty_number):
        """Fetch an administrative penalty by number."""
        administrative_penalty = AdministrativePenaltyService.get_by_number(
            administrative_penalty_number
        )
        return AdministrativePenaltySchema().dump(administrative_penalty), HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/links", methods=["POST", "OPTIONS"])
class AdministrativePenaltyLinks(Resource):
    """Link the administrative penalty."""

    @staticmethod
    @auth.require
    @API.expect(administrative_penalty_link_create_model)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.response(
        code=201, model=administrative_penalty_list_model, description="Success"
    )
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Link an administrative penalty to inspection requirements",
    )
    def post():
        """Link the administrative penalty to inspection requirements."""
        link = AdministrativePenaltyLinkCreateSchema().load(API.payload)
        administrative_penalty_id = link.get("administrative_penalty_id")
        created_link = AdministrativePenaltyService.link(
            administrative_penalty_id, link
        )
        return AdministrativePenaltySchema().dump(created_link), HTTPStatus.CREATED


@cors_preflight("GET, OPTIONS")
@API.route("/<int:administrative_penalty_id>/links", methods=["GET", "OPTIONS"])
class AdministrativePenaltyLinksById(Resource):
    """Get inspection and requirements linked to an administrative penalty."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.response(
        code=200,
        model=[administrative_penalty_links_response_model],
        description="Success",
    )
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Get inspection and requirements linked to an administrative penalty",
    )
    def get(administrative_penalty_id):
        """Get inspection and requirements linked to an administrative penalty."""
        linked_data = (
            AdministrativePenaltyService.get_linked_inspections_and_requirements(
                administrative_penalty_id
            )
        )
        return (
            AdministrativePenaltyLinksResponseSchema(many=True).dump(linked_data),
            HTTPStatus.OK,
        )
