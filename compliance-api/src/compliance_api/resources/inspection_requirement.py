"""InspectionRequirementResource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import BadRequestError
from compliance_api.models.inspection import ImageTypeEnum
from compliance_api.schemas.inspection_requirement import (
    InspectionReqDetailDocImageSchema, InspectionReqDetailImageSchema, InspectionReqImageSchema,
    InspectionRequirementCreateSchema, InspectionRequirementSchema, InspectionRequirementUpdateSchema,
    InspectionSortOrderSchema)
from compliance_api.services import InspectionRequirementService
from compliance_api.utils.enum import PermissionEnum
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("requirements", description="Endpoints for Inspection Requirement")
inspection_requirement_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRequirementCreateSchema(), "InspectionRequirement"
)

inspection_requirement_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRequirementSchema(), "InspectionRequirementList"
)

inspection_requirement_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRequirementUpdateSchema(), "InspectionRequirementUpdate"
)

inspection_sort_order_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionSortOrderSchema(), "InspectionSortOrder"
)
inspesction_req_image_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionReqImageSchema(), "InspectionReqImageSchema"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class InspectionRequirements(Resource):
    """InspectionRequirements."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Get all requirements by inspection"
    )
    @auth.require
    @API.response(
        code=200, description="Success", model=[inspection_requirement_list_model]
    )
    def get(inspection_id):
        """Get requirements by inspection id."""
        requirements = InspectionRequirementService.get_all(inspection_id)
        return InspectionRequirementSchema(many=True).dump(requirements), HTTPStatus.OK

    @staticmethod
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an inspection")
    @API.expect(inspection_requirement_create_model)
    @API.response(
        code=201,
        model=inspection_requirement_list_model,
        description="InspectionCreated",
    )
    @API.response(400, "Bad Request")
    @auth.require
    def post(inspection_id):
        """Create an inspection."""
        requirement_data = InspectionRequirementCreateSchema().load(API.payload)
        created_requirement = InspectionRequirementService.create(
            inspection_id, requirement_data
        )
        return (
            InspectionRequirementSchema().dump(created_requirement),
            HTTPStatus.CREATED,
        )


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route("/<int:requirement_id>", methods=["GET", "PATCH", "OPTIONS", "DELETE"])
class InspectionRequirement(Resource):
    """InspectionRequirement resource."""

    @staticmethod
    @API.response(
        code=200, description="Success", model=[inspection_requirement_list_model]
    )
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch inspection requirement by id"
    )
    @API.response(404, "Not Found")
    @auth.require
    def get(inspection_id, requirement_id):
        """Fetch all inspection requirement."""
        requirement = InspectionRequirementService.get_by_id(
            inspection_id, requirement_id
        )
        return InspectionRequirementSchema().dump(requirement), HTTPStatus.OK

    @staticmethod
    @API.response(
        code=200, description="Sucess", model=[inspection_requirement_list_model]
    )
    @API.expect(inspection_requirement_update_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update inspection requirement"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(inspection_id, requirement_id):
        """Update inspection inspection requirement."""
        requirement_data = InspectionRequirementUpdateSchema().load(API.payload)
        updated_requirement = InspectionRequirementService.update(
            inspection_id, requirement_id, requirement_data
        )
        return InspectionRequirementSchema().dump(updated_requirement), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete a Inspection requirement by id"
    )
    @API.response(code=204, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def delete(inspection_id, requirement_id):
        """Delete complaint."""
        InspectionRequirementService.delete(inspection_id, requirement_id)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:requirement_id>/sort-order", methods=["PATCH", "OPTIONS"])
class InspectionRequirementOrder(Resource):
    """Update the sort order of the inspection requirements."""

    @staticmethod
    @API.response(code=204, description="Success")
    @API.expect(inspection_sort_order_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update the sort order of the inspection requirement"
    )
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @auth.require
    def patch(inspection_id, requirement_id):
        """Update inspection inspection requirement."""
        sort_order_data = InspectionSortOrderSchema().load(API.payload)
        InspectionRequirementService.update_sort_order(
            inspection_id, requirement_id, sort_order_data
        )
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS, DELETE")
@API.route("/<int:requirement_id>/photos", methods=["OPTIONS", "GET", "DELETE"])
class InspectionReqPhotos(Resource):
    """Manage the photos uploaded as part of inspection requirements."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Get all photos tagged in the given requirement"
    )
    @auth.require
    @API.response(code=200, description="Success", model=[inspesction_req_image_schema])
    def get(inspection_id, requirement_id):
        """Get all photos by requirement_id."""
        photos = InspectionRequirementService.get_all_images(
            inspection_id, requirement_id, ImageTypeEnum.PHOTO
        )
        return InspectionReqImageSchema(many=True).dump(photos), HTTPStatus.OK

    @staticmethod
    @auth.require
    @auth.has_one_of_roles([PermissionEnum.SUPERUSER])
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Delete an inspection requirement photo"
    )
    @API.response(code=204, description="Success")
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    def delete(inspection_id, requirement_id):
        """Delete complaint."""
        relative_url = request.args.get("relative_url", None)
        if not relative_url:
            raise BadRequestError("No 'relative_url' is passed as query parameter")
        InspectionRequirementService.delete_image(
            inspection_id, requirement_id, relative_url, ImageTypeEnum.PHOTO
        )
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, OPTIONS, DELETE")
@API.route("/<int:requirement_id>/figures", methods=["OPTIONS", "GET", "DELETE"])
class InspectionReqFigures(Resource):
    """Manage the figures uploaded as part of inspection requirements."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Get all figures tagged in the given requirement"
    )
    @auth.require
    @API.response(code=200, description="Success", model=[inspesction_req_image_schema])
    def get(inspection_id, requirement_id):
        """Get all figures by requirement_id."""
        figures = InspectionRequirementService.get_all_images(
            inspection_id, requirement_id, ImageTypeEnum.FIGURE
        )
        return InspectionReqImageSchema(many=True).dump(figures), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route(
    "/<int:requirement_id>/requirement-source-images",
    methods=["OPTIONS", "GET"],
)
class InspectionReqSourceImages(Resource):
    """Manage the images uploaded as part of inspection requirement source details."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Get all images for a requirement source",
    )
    @auth.require
    @API.response(code=200, description="Success", model=[inspesction_req_image_schema])
    @API.response(404, "Not Found")
    def get(inspection_id, requirement_id):
        """Get all images by requirement id."""
        images = InspectionRequirementService.get_all_requirement_detail_images(
            inspection_id, requirement_id
        )
        return InspectionReqDetailImageSchema(many=True).dump(images), HTTPStatus.OK


@cors_preflight("GET, OPTIONS")
@API.route(
    "/<int:requirement_id>/requirement-document-images",
    methods=["OPTIONS", "GET"],
)
class InspectionReqSourceDocImages(Resource):
    """Manage the images uploaded as part of inspection requirement detail documents."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Get all images for requirement detail documents",
    )
    @auth.require
    @API.response(code=200, description="Success", model=[inspesction_req_image_schema])
    @API.response(404, "Not Found")
    def get(inspection_id, requirement_id):
        """Get all document images by requirement id."""
        images = InspectionRequirementService.get_all_requirement_detail_doc_images(
            inspection_id, requirement_id
        )
        return InspectionReqDetailDocImageSchema(many=True).dump(images), HTTPStatus.OK
