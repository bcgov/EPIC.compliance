"""Review Board Resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas.review_board import (
    ReviewBoardAdministrativePenaltySchema, ReviewBoardInspectionRecordSchema, ReviewBoardOrderSchema,
    ReviewBoardWarningLetterSchema)
from compliance_api.services.review_board import ReviewBoardService

from .apihelper import Api as ApiHelper


API = Namespace("review-board", description="Endpoints for Review Board")

# Schema models for API documentation
inspection_record_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ReviewBoardInspectionRecordSchema(), "ReviewBoardInspectionRecord"
)
warning_letter_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ReviewBoardWarningLetterSchema(), "ReviewBoardWarningLetter"
)
order_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ReviewBoardOrderSchema(), "ReviewBoardOrder"
)
administrative_penalty_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ReviewBoardAdministrativePenaltySchema(), "ReviewBoardAdministrativePenalty"
)


@API.route("/inspection-records", methods=["GET"])
class ReviewBoardInspectionRecords(Resource):
    """Resource for managing inspection records in review board."""

    @staticmethod
    @API.response(code=200, description="Success", model=[inspection_record_model])
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch inspection records for review board (OPEN inspections only)",
    )
    @auth.require
    def get():
        """Fetch inspection records for review board with OPEN status only."""
        inspection_records = (
            ReviewBoardService.get_inspection_records_for_open_inspections()
        )
        schema = ReviewBoardInspectionRecordSchema(many=True)
        return schema.dump(inspection_records), HTTPStatus.OK


@API.route("/warning-letters", methods=["GET"])
class ReviewBoardWarningLetters(Resource):
    """Resource for managing warning letters in review board."""

    @staticmethod
    @API.response(code=200, description="Success", model=[warning_letter_model])
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch warning letters for review board (OPEN inspections only)",
    )
    @auth.require
    def get():
        """Fetch warning letters for review board with OPEN status only."""
        warning_letters = ReviewBoardService.get_warning_letters_for_open_inspections()
        schema = ReviewBoardWarningLetterSchema(many=True)
        return schema.dump(warning_letters), HTTPStatus.OK


@API.route("/orders", methods=["GET"])
class ReviewBoardOrders(Resource):
    """Resource for managing orders in review board."""

    @staticmethod
    @API.response(code=200, description="Success", model=[order_model])
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch orders for review board (OPEN inspections only)",
    )
    @auth.require
    def get():
        """Fetch orders for review board with OPEN status only."""
        orders = ReviewBoardService.get_orders_for_open_inspections()
        schema = ReviewBoardOrderSchema(many=True)
        return schema.dump(orders), HTTPStatus.OK


@API.route("/administrative-penalties", methods=["GET"])
class ReviewBoardAdministrativePenalties(Resource):
    """Resource for managing administrative penalties in review board."""

    @staticmethod
    @API.response(code=200, description="Success", model=[administrative_penalty_model])
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Fetch all administrative penalties for the review board",
    )
    @auth.require
    def get():
        """Fetch administrative penalties for the review board that are not closed."""
        administrative_penalties = (
            ReviewBoardService.get_open_administrative_penalties()
        )
        schema = ReviewBoardAdministrativePenaltySchema(many=True)
        return schema.dump(administrative_penalties), HTTPStatus.OK
