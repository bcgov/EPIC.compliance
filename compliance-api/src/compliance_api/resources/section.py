"""Sections Resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth

from ..schemas import SectionSchema
from ..services.section import SectionService
from .apihelper import Api as ApiHelper


API = Namespace("sections", description="Endpoints for Sections")

section_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, SectionSchema(), "SectionList"
)


@API.route("", methods=["GET"])
class Sections(Resource):
    """Resource for managing sections."""

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=[section_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all active sections")
    def get():
        """Fetch all active sections."""
        sections = SectionService.get_all()
        section_list_schema = SectionSchema(many=True)
        return section_list_schema.dump(sections), HTTPStatus.OK
