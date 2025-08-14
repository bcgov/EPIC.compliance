"""API endpoints for managing charge recommendation resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import BadRequestError
from compliance_api.schemas.charge_recommendation import (
    ChargeRecommendationCreateSchema, ChargeRecommendationSchema, ChargeRecommendationUpdateSchema)
from compliance_api.services.charge_recommendation import ChargeRecommendationService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace(
    "charge-recommendations",
    description="Endpoints for Charge Recommendation Management",
)

charge_recommendation_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ChargeRecommendationCreateSchema(), "ChargeRecommendationCreate"
)

charge_recommendation_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ChargeRecommendationSchema(), "ChargeRecommendationList"
)

charge_recommendation_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ChargeRecommendationUpdateSchema(), "ChargeRecommendationUpdate"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class ChargeRecommendations(Resource):
    """Resource for managing charge recommendations."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=[charge_recommendation_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all charge recommendations"
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
        """Fetch all charge recommendations."""
        inspection_id = request.args.get("inspection_id")
        if not inspection_id:
            raise BadRequestError("inspection_id is required")
        charge_recommendations = ChargeRecommendationService.get_all(inspection_id)
        charge_recommendation_list_schema = ChargeRecommendationSchema(many=True)
        return (
            charge_recommendation_list_schema.dump(charge_recommendations),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create a charge recommendation"
    )
    @API.expect(charge_recommendation_create_model)
    @API.response(
        code=201,
        model=charge_recommendation_list_model,
        description="ChargeRecommendationCreated",
    )
    @API.response(400, "Bad Request")
    def post():
        """Create a charge recommendation."""
        charge_recommendation_data = ChargeRecommendationCreateSchema().load(
            API.payload
        )
        created_charge_recommendation = (
            ChargeRecommendationService.create_charge_recommendation(
                charge_recommendation_data
            )
        )
        return (
            ChargeRecommendationSchema().dump(created_charge_recommendation),
            HTTPStatus.CREATED,
        )


@cors_preflight("GET, OPTIONS, PATCH, DELETE")
@API.route(
    "/<int:charge_recommendation_id>", methods=["GET", "PATCH", "DELETE", "OPTIONS"]
)
class ChargeRecommendationById(Resource):
    """Resource for managing a single charge recommendation."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=charge_recommendation_list_model
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a charge recommendation by id"
    )
    def get(charge_recommendation_id):
        """Fetch a charge recommendation by id."""
        charge_recommendation = ChargeRecommendationService.get_by_id(
            charge_recommendation_id
        )
        return ChargeRecommendationSchema().dump(charge_recommendation), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update a charge recommendation"
    )
    @API.expect(charge_recommendation_update_model)
    @API.response(
        code=200,
        model=charge_recommendation_list_model,
        description="ChargeRecommendationUpdated",
    )
    @API.response(400, "Bad Request")
    def patch(charge_recommendation_id):
        """Update a charge recommendation."""
        charge_recommendation_data = ChargeRecommendationUpdateSchema().load(
            API.payload
        )
        updated_charge_recommendation = (
            ChargeRecommendationService.update_charge_recommendation(
                charge_recommendation_id, charge_recommendation_data
            )
        )
        return (
            ChargeRecommendationSchema().dump(updated_charge_recommendation),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete a charge recommendation"
    )
    @API.response(code=204, description="NoContent")
    def delete(charge_recommendation_id):
        """Delete a charge recommendation."""
        return ChargeRecommendationService.delete_charge_recommendation(
            charge_recommendation_id
        )


@cors_preflight("GET, OPTIONS")
@API.route(
    "/by-number/<string:charge_recommendation_number>", methods=["GET", "OPTIONS"]
)
class ChargeRecommendationByNumber(Resource):
    """Resource for managing a single charge recommendation by number."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=charge_recommendation_list_model
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a charge recommendation by number"
    )
    def get(charge_recommendation_number):
        """Fetch a charge recommendation by number."""
        charge_recommendation = ChargeRecommendationService.get_by_number(
            charge_recommendation_number
        )
        return ChargeRecommendationSchema().dump(charge_recommendation), HTTPStatus.OK
