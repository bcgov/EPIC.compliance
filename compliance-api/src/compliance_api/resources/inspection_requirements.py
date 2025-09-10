"""Resource to return all inspection requirements for the grid view."""

from datetime import datetime
from http import HTTPStatus
from io import BytesIO

from flask import request, send_file
from flask_restx import Namespace, Resource

from compliance_api.auth import auth
from compliance_api.schemas.inspection_requirement_grid import (
    InspectionRequirementFilterSchema, InspectionRequirementGridItemSchema)
from compliance_api.services import InspectionRequirementService
from compliance_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace(
    "inspection-requirements", description="Endpoints for Inspection Requirements Grid"
)
inspection_requirement_list_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRequirementGridItemSchema(), "InspectionRequirementList"
)
inspection_requirement_filter_model = ApiHelper.convert_ma_schema_to_restx_model(
    API, InspectionRequirementFilterSchema(), "InspectionRequirementFilter"
)


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["GET", "POST", "OPTIONS"])
class InspectionRequirements(Resource):
    """InspectionRequirements."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Fetch all inspection requirements"
    )
    @API.doc(
        params={
            "tpc_ids": {
                "description": "The comma separated list of topic ids",
                "type": "string",
                "required": False,
            },
            "summary": {
                "description": "The summary of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "cmd_fnd_ids": {
                "description": "The comma separated list of compliance finding ids",
                "type": "string",
                "required": False,
            },
            "enf_actn_ids": {
                "description": "The comma separated list of enforcement action ids",
                "type": "string",
                "required": False,
            },
            "enf_stats": {
                "description": (
                    "The comma separated list of enforcement statuses "
                    "(status, progress, or approval status) of the inspection requirement"
                ),
                "type": "string",
                "required": False,
            },
            "enf_number": {
                "description": "The enforcement number of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "req_src_ids": {
                "description": "The comma separated list of requirement source ids of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "req_src_num": {
                "description": "The requirement source number of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "ir_no": {
                "description": "The inspection record number",
                "type": "string",
                "required": False,
            },
            "date_issued": {
                "description": "The comma separated list of date issued of the inspection requirement",
                "type": "date",
                "required": False,
            },
            "prm_offc_ids": {
                "description": "The comma separated list of primary officer ids of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "insp_sts": {
                "description": "The comma separated list of inspection status of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "project_ids": {
                "description": "The comma separated list of project ids of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "reviewer_ids": {
                "description": "The comma separated list of reviewer ids of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "sort_by": {
                "description": "The sort by field of the inspection requirement",
                "type": "string",
                "required": False,
            },
            "sort_order": {
                "description": "The sort order of the inspection requirement",
                "type": "string",
                "enum": ["asc", "desc"],
                "required": False,
            },
            "page_no": {
                "description": "The page number of the inspection requirement",
                "type": "integer",
                "required": False,
            },
            "page_size": {
                "description": "The number of items per page of the inspection requirement",
                "type": "integer",
                "required": False,
            },
        }
    )
    @API.response(
        code=200, description="Success", model=[inspection_requirement_list_model]
    )
    @auth.require
    def get():
        """Return all inspection requirements for the grid."""
        response, total = InspectionRequirementService.get_all_inspection_requirements(
            request.args
        )
        return {
            "items": InspectionRequirementGridItemSchema(many=True).dump(response),
            "total": total,
        }, HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/export", methods=["POST", "OPTIONS"])
class InspectionRequirementsExport(Resource):
    """Export all inspection requirements as Excel."""

    @staticmethod
    @ApiHelper.swagger_decorators(
        API, endpoint_description="Export all inspection requirements as Excel"
    )
    @API.expect(
        ApiHelper.convert_ma_schema_to_restx_model(
            API, InspectionRequirementFilterSchema(), "InspectionRequirementFilter"
        )
    )
    @API.doc()
    @API.response(code=200, description="Success - Excel file download")
    @auth.require
    def post():
        """Export all inspection requirements as Excel."""
        # Get filter parameters from request body instead of query parameters
        schema = InspectionRequirementFilterSchema()
        filter_data = schema.load(request.json or {})
        output = InspectionRequirementService.generate_inspection_requirements_excel(
            filter_data
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inspection_requirements_{timestamp}.xlsx"

        # Return the Excel file as a downloadable attachment
        return send_file(BytesIO(output), as_attachment=True, download_name=filename)
