"""ViolationTicket Resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.services.violation_ticket import ViolationTicketService

from ..schemas import (
    ViolationTicketCreateSchema, ViolationTicketSchema, ViolationTicketStatusSchema, ViolationTicketUpdateSchema)
from ..utils.util import cors_preflight
from .apihelper import Api as ApiHelper


API = Namespace("violation-tickets", description="Endpoints for Violation Tickets")

violation_ticket_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ViolationTicketCreateSchema(), "ViolationTicketCreate"
)

violation_ticket_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ViolationTicketSchema(), "ViolationTicketList"
)
violation_ticket_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ViolationTicketUpdateSchema(), "ViolationTicketUpdate"
)
violation_ticket_status_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ViolationTicketStatusSchema(), "ViolationTicketStatus"
)


@cors_preflight("GET,POST,OPTIONS")
@API.route("", methods=["GET", "POST", "OPTIONS"])
class ViolationTickets(Resource):
    """Resource for managing violation tickets."""

    @staticmethod
    @auth.require
    @API.doc(
        "get_violation_tickets",
        description="Fetch all violation tickets.",
        responses={200: "Success", 401: "Unauthorized"},
    )
    @API.marshal_with(violation_ticket_list_model, as_list=True, code=200)
    def get():
        """Fetch all violation tickets."""
        inspection_id = request.args.get("inspection_id", type=int)
        violation_tickets = ViolationTicketService.get_all(inspection_id)
        return ViolationTicketSchema(many=True).dump(violation_tickets), HTTPStatus.OK

    @staticmethod
    @auth.require
    @API.doc(
        "create_violation_ticket",
        description="Create a violation ticket.",
        responses={201: "Created", 400: "Bad Request", 401: "Unauthorized"},
    )
    @API.expect(violation_ticket_create_model)
    @API.marshal_with(violation_ticket_list_model, code=201)
    def post():
        """Create a violation ticket."""
        violation_ticket_data = ViolationTicketCreateSchema().load(API.payload)
        violation_ticket = ViolationTicketService.create(violation_ticket_data)
        return ViolationTicketSchema().dump(violation_ticket), HTTPStatus.CREATED


@cors_preflight("GET,PATCH,DELETE,OPTIONS")
@API.route("/<int:violation_ticket_id>", methods=["GET", "PATCH", "DELETE", "OPTIONS"])
class ViolationTicket(Resource):
    """Resource for managing a single ViolationTicket."""

    @staticmethod
    @auth.require
    @API.doc(
        "get_violation_ticket",
        description="Fetch a violation ticket by id.",
        responses={200: "Success", 401: "Unauthorized", 404: "Not Found"},
    )
    @API.marshal_with(violation_ticket_list_model, code=200)
    def get(violation_ticket_id):
        """Fetch a violation ticket by id."""
        violation_ticket = ViolationTicketService.get_by_id(violation_ticket_id)
        return ViolationTicketSchema().dump(violation_ticket), HTTPStatus.OK

    @staticmethod
    @auth.require
    @API.doc(
        "update_violation_ticket",
        description="Update violation ticket.",
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    @API.expect(violation_ticket_update_model)
    @API.marshal_with(violation_ticket_list_model, code=200)
    def patch(violation_ticket_id):
        """Update violation ticket."""
        violation_ticket_data = ViolationTicketUpdateSchema().load(API.payload)
        violation_ticket = ViolationTicketService.update(
            violation_ticket_id, violation_ticket_data
        )
        return ViolationTicketSchema().dump(violation_ticket), HTTPStatus.OK

    @staticmethod
    @auth.require
    @API.doc(
        "delete_violation_ticket",
        description="Delete violation ticket.",
        responses={204: "No Content", 401: "Unauthorized", 404: "Not Found"},
    )
    def delete(violation_ticket_id):
        """Delete violation ticket."""
        ViolationTicketService.delete(violation_ticket_id)
        return "", HTTPStatus.NO_CONTENT


@cors_preflight("GET,OPTIONS")
@API.route("/vt-number/<string:vt_number>", methods=["GET", "OPTIONS"])
class ViolationTicketByVtNumber(Resource):
    """Resource for managing a single ViolationTicket by VT number."""

    @staticmethod
    @auth.require
    @API.doc(
        "get_violation_ticket_by_vt_number",
        description="Fetch a violation ticket by VT number.",
        responses={200: "Success", 401: "Unauthorized", 404: "Not Found"},
    )
    @API.marshal_with(violation_ticket_list_model, code=200)
    def get(vt_number):
        """Fetch a violation ticket by VT number."""
        violation_ticket = ViolationTicketService.get_by_vt_number(vt_number)
        return ViolationTicketSchema().dump(violation_ticket), HTTPStatus.OK
