"""Orders Resource."""

from http import HTTPStatus
from io import BytesIO

from flask import request, send_file
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.exceptions import ResourceNotFoundError
from compliance_api.services.order.order import OrderService
from compliance_api.services.order.order_approval import OrderApprovalService

from ..schemas import (
    CreateOrderApprovalSchema, OrderApprovalSchema, OrderCreateSchema, OrderIssueSchema, OrderLinkCreateSchema,
    OrderLinksResponseSchema, OrderReplaceSchema, OrderSchema, OrderStatusSchema, OrderUpdateSchema,
    RenderRequestSchema, ResetOrderFieldSchema, UpdateOrderApprovalStatusSchema)
from ..utils.util import cors_preflight
from .apihelper import Api as ApiHelper


API = Namespace("orders", description="Endpoints for Orders")

order_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderCreateSchema(), "OrderCreate"
)

order_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderSchema(), "OrderList"
)
order_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderUpdateSchema(), "OrderUpdate"
)
order_status_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderStatusSchema(), "OrderStatus"
)
order_issue_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderIssueSchema(), "OrderIssue"
)
order_approval_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderApprovalSchema(), "OrderApproval"
)
order_approval_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, CreateOrderApprovalSchema(), "OrderApprovalCreate"
)
order_approval_status_update_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, UpdateOrderApprovalStatusSchema(), "OrderApprovalStatusUpdate"
)

reset_order_field_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, ResetOrderFieldSchema(), "ResetOrderField"
)
order_render_request_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, RenderRequestSchema(), "OrderRenderRequest"
)

order_replace_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderReplaceSchema(), "OrderReplace"
)

order_links_create_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderLinkCreateSchema(), "OrderLinkCreate"
)

order_links_response_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, OrderLinksResponseSchema(), "OrderLinksResponse"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class Orders(Resource):
    """Resource for managing orders."""

    @staticmethod
    @auth.require
    @API.doc(
        params={
            "inspection_id": {
                "description": "The unique identifier of the inspection",
                "type": "integer",
                "required": True,
            }
        }
    )
    @API.response(code=200, description="Success", model=[order_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all orders")
    def get():
        """Fetch all orders."""
        inspection_id = request.args.get("inspection_id")
        orders = OrderService.get_all(inspection_id, sort_by="order_number")
        order_list_schema = OrderSchema(many=True)
        return order_list_schema.dump(orders), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an order")
    @API.expect(order_create_model)
    @API.response(code=201, model=order_list_model, description="OrderCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create an order."""
        order_data = OrderCreateSchema().load(API.payload)
        created_order = OrderService.create_order(order_data)
        return OrderSchema().dump(created_order), HTTPStatus.CREATED


@cors_preflight("GET, OPTIONS")
@API.route("/projectwise", methods=["GET", "OPTIONS"])
class ProjectwiseOrders(Resource):
    """Resource for managing projectwise orders."""

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=[order_list_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all orders")
    @API.doc(
        params={
            "case_file_id": {
                "description": "The unique identifier of the case file",
                "type": "integer",
                "required": True,
            }
        }
    )
    def get():
        """Fetch all OPEN orders."""
        case_file_id = request.args.get("case_file_id")
        orders = OrderService.get_projectwise_orders(case_file_id)
        order_list_schema = OrderSchema(many=True)
        return order_list_schema.dump(orders), HTTPStatus.OK


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route("/<int:order_id>", methods=["OPTIONS", "GET", "PATCH", "DELETE"])
@API.doc(params={"order_id": "The unique identifier for the order"})
class Order(Resource):
    """Resource for managing a single Order."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch an order by id")
    @API.response(code=200, model=order_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(order_id):
        """Fetch an order by id."""
        order = OrderService.get_order(order_id)
        if not order:
            raise ResourceNotFoundError(f"Order with {order_id} not found")
        return OrderSchema().dump(order), HTTPStatus.OK

    @staticmethod
    @auth.require
    @API.response(code=200, description="Success", model=[order_list_model])
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.expect(order_update_model)
    @ApiHelper.swagger_decorators(API, endpoint_description="Update order")
    def patch(order_id):
        """Update order."""
        order_data = OrderUpdateSchema().load(API.payload)
        updated_order = OrderService.update_order(order_id, order_data)
        return OrderSchema().dump(updated_order), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete an Order by id")
    @API.response(code=204, description="Success")
    @API.response(404, "Not Found")
    def delete(order_id):
        """Delete order."""
        OrderService.delete_order(order_id)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("GET, PATCH, DELETE, OPTIONS")
@API.route("/order-numbers/<string:order_number>", methods=["GET", "OPTIONS"])
@API.doc(params={"order_number": "The unique identifier for the order"})
class OrderByOrderNumber(Resource):
    """Resource for managing a single Order."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch an order by id")
    @API.response(code=200, model=order_list_model, description="Success")
    @API.response(404, "Not Found")
    def get(order_number):
        """Fetch an order by id."""
        order = OrderService.get_order_by_order_number(order_number)
        if not order:
            raise ResourceNotFoundError(f"Order with {order_number} not found")
        return OrderSchema().dump(order), HTTPStatus.OK


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:order_id>/status", methods=["PATCH", "OPTIONS"])
@API.doc(params={"order_id": "The unique identifier for the order"})
class OrderStatus(Resource):
    """Update the inspection status."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(order_status_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Change order status")
    @API.response(code=204, description="Order status changed")
    def patch(order_id):
        """Change Order Status."""
        status = OrderStatusSchema().load(API.payload)
        OrderService.change_status(order_id, status)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:order_id>/issue", methods=["PATCH", "OPTIONS"])
@API.doc(params={"order_id": "The unique identifier for the order"})
class OrderIssue(Resource):
    """Update the inspection status."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(order_issue_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Issue order")
    @API.response(code=204, description="Order issued")
    def patch(order_id):
        """Issue Order."""
        issue = OrderIssueSchema().load(API.payload)
        OrderService.issue_order(order_id, issue)
        return {}, HTTPStatus.NO_CONTENT


@cors_preflight("PATCH, OPTIONS")
@API.route("/<int:order_id>/reset", methods=["PATCH", "OPTIONS"])
@API.doc(params={"order_id": "The unique identifier for the order"})
class OrderFieldReset(Resource):
    """Reset specific fields in an order."""

    @staticmethod
    @auth.require
    @API.response(400, "Bad Request")
    @API.expect(reset_order_field_model)
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Reset an order field")
    @API.response(code=200, description="Order field reset", model=order_list_model)
    def patch(order_id):
        """Reset a field in the order."""
        reset_data = ResetOrderFieldSchema().load(API.payload)
        field_names = reset_data.get("field_names")
        updated_order = OrderService.reset_field(order_id, field_names)
        return OrderSchema().dump(updated_order), HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/<int:order_id>/render", methods=["POST", "OPTIONS"])
class OrderPreview(Resource):
    """Resource for managing order preview and pdf."""

    @staticmethod
    @API.response(code=200, description="Success")
    @API.response(404, "Not Found")
    @ApiHelper.swagger_decorators(API, endpoint_description="Preview order")
    @API.expect(order_render_request_model)
    @auth.require
    def post(order_id):  # pylint: disable=no-self-use, unused-argument
        """Preview order."""
        render_request = RenderRequestSchema().load(API.payload or {})
        output_format = render_request.get("output_format", "html")
        response, order = OrderService.render(order_id, output_format)
        if output_format == "pdf":
            return send_file(
                BytesIO(response.content),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{order.order_number}.pdf",
            )
        return response.json(), HTTPStatus.OK


@cors_preflight("GET, OPTIONS, POST, PATCH")
@API.route("/<int:order_id>/approvals", methods=["POST", "GET", "OPTIONS"])
class OrderApprovals(Resource):
    """Resource for managing order approvals."""

    @staticmethod
    @API.response(404, "Not Found")
    @API.response(code=200, description="Success", model=[order_approval_model])
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch all order approvals")
    @auth.require
    def get(order_id):  # pylint: disable=no-self-use, unused-argument
        """Fetch all order approvals."""
        approvals = OrderApprovalService.get_all_approvals(order_id)
        approval_schema = OrderApprovalSchema(many=True)
        return approval_schema.dump(approvals), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an order approval")
    @API.expect(order_approval_create_model)
    @API.response(
        code=201, model=order_approval_model, description="OrderApprovalRequestCreated"
    )
    @API.response(400, "Bad Request")
    def post(order_id):
        """Create a agency."""
        order_approval_request = CreateOrderApprovalSchema().load(API.payload)
        created_aproval = OrderApprovalService.create_approval(
            order_approval_request, order_id
        )
        return (
            OrderApprovalSchema().dump(created_aproval),
            HTTPStatus.CREATED,
        )


@cors_preflight("POST, OPTIONS")
@API.route("/<int:order_id>/replace", methods=["POST", "OPTIONS"])
@API.doc(params={"order_id": "The unique identifier for the order to replace"})
class OrderReplace(Resource):
    """Resource for replacing an order."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Create a replacement order"
    )
    @API.expect(order_replace_model)
    @API.response(
        code=201, model=order_list_model, description="Replacement order created"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    def post(order_id):
        """Create a replacement order."""
        replace_data = OrderReplaceSchema().load(API.payload or {})
        replacement_order = OrderService.replace_order(order_id, replace_data)
        return OrderSchema().dump(replacement_order), HTTPStatus.CREATED


@cors_preflight("OPTIONS, PATCH, GET")
@API.route(
    "/<int:order_id>/approvals/<int:approval_id>/status",
    methods=["PATCH", "OPTIONS"],
)
class OrderApprovalStatus(Resource):
    """Resource for managing order approval status."""

    @staticmethod
    @API.response(code=200, description="Sucess", model=order_approval_model)
    @API.expect(order_approval_status_update_model)
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Update order approval status"
    )
    @API.response(404, "Not Found")
    @API.response(400, "Bad Request")
    @auth.require
    def patch(order_id, approval_id):
        """Update order approval."""
        approval_update_data = UpdateOrderApprovalStatusSchema().load(API.payload)
        updated_approval = OrderApprovalService.update_approval_status(
            order_id, approval_id, approval_update_data
        )
        return OrderApprovalSchema().dump(updated_approval), HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/links", methods=["POST", "OPTIONS"])
class OrderLinks(Resource):
    """Link inspection orders."""

    @staticmethod
    @auth.require
    @API.expect(order_links_create_model)
    @API.response(400, "Bad Request")
    @API.response(404, "Not Found")
    @API.response(
        code=201,
        model=order_list_model,
        description="Success",
    )
    @ApiHelper.swagger_decorators(
        API,
        endpoint_description="Link inspection orders",
    )
    def post():
        """Link this Order to inspection requirements."""
        link = OrderLinkCreateSchema().load(API.payload)
        order_id = link.get("order_id")
        created_link = OrderService.link(
            order_id,
            link
        )
        return (
            OrderLinksResponseSchema().dump(created_link),
            HTTPStatus.CREATED,
        )
