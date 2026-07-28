"""API endpoints for managing restorative justice resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import BadRequestError
from compliance_api.schemas.restorative_justice import (
    RestorativeJusticeCreateSchema, RestorativeJusticeSchema, RestorativeJusticeUpdateSchema)
from compliance_api.services.restorative_justice import RestorativeJusticeService

from .apihelper import Api as ApiHelper


API = Namespace(
    "restorative-justices",
    description="Endpoints for Restorative Justice Management",
)

restorative_justice_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RestorativeJusticeCreateSchema(), "RestorativeJusticeCreate"
)

restorative_justice_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RestorativeJusticeSchema(), "RestorativeJusticeList"
)

restorative_justice_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RestorativeJusticeUpdateSchema(), "RestorativeJusticeUpdate"
)


@API.route("", methods=["POST", "GET"])
class RestorativeJustices(Resource):
    """Resource for managing restorative justices."""

    @staticmethod
    @auth.require
    @API.response(
        code=200, description="Success", model=[restorative_justice_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all restorative justices"
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
        """Fetch all restorative justices."""
        inspection_id = request.args.get("inspection_id")
        if not inspection_id:
            raise BadRequestError("inspection_id is required")
        restorative_justices = RestorativeJusticeService.get_all(inspection_id, sort_by="restorative_justice_number")
        restorative_justice_list_schema = RestorativeJusticeSchema(many=True)
        return (
            restorative_justice_list_schema.dump(restorative_justices),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create a restorative justice"
    )
    @API.expect(restorative_justice_create_model)
    @API.response(
        code=201,
        model=restorative_justice_list_model,
        description="RestorativeJusticeCreated",
    )
    @API.response(400, "Bad Request")
    def post():
        """Create a restorative justice."""
        restorative_justice_data = RestorativeJusticeCreateSchema().load(API.payload)
        created_restorative_justice = (
            RestorativeJusticeService.create_restorative_justice(
                restorative_justice_data
            )
        )
        return (
            RestorativeJusticeSchema().dump(created_restorative_justice),
            HTTPStatus.CREATED,
        )


@API.route(
    "/<int:restorative_justice_id>", methods=["GET", "PATCH", "DELETE"]
)
class RestorativeJusticeById(Resource):
    """Resource for managing a single restorative justice."""

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=restorative_justice_list_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a restorative justice by id"
    )
    def get(restorative_justice_id):
        """Fetch a restorative justice by id."""
        restorative_justice = RestorativeJusticeService.get_by_id(
            restorative_justice_id
        )
        return RestorativeJusticeSchema().dump(restorative_justice), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update a restorative justice"
    )
    @API.expect(restorative_justice_update_model)
    @API.response(
        code=200,
        model=restorative_justice_list_model,
        description="RestorativeJusticeUpdated",
    )
    @API.response(400, "Bad Request")
    def patch(restorative_justice_id):
        """Update a restorative justice."""
        restorative_justice_data = RestorativeJusticeUpdateSchema().load(API.payload)
        updated_restorative_justice = (
            RestorativeJusticeService.update_restorative_justice(
                restorative_justice_id, restorative_justice_data
            )
        )
        return (
            RestorativeJusticeSchema().dump(updated_restorative_justice),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete a restorative justice"
    )
    @API.response(code=204, description="NoContent")
    def delete(restorative_justice_id):
        """Delete a restorative justice."""
        RestorativeJusticeService.delete_restorative_justice(restorative_justice_id)
        return {}, HTTPStatus.NO_CONTENT


@API.route("/by-number/<string:restorative_justice_number>", methods=["GET"])
class RestorativeJusticeByNumber(Resource):
    """Resource for managing a single restorative justice by number."""

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=restorative_justice_list_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch a restorative justice by number"
    )
    def get(restorative_justice_number):
        """Fetch a restorative justice by number."""
        restorative_justice = RestorativeJusticeService.get_by_number(
            restorative_justice_number
        )
        return RestorativeJusticeSchema().dump(restorative_justice), HTTPStatus.OK
