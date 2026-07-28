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
"""API endpoints for managing report resources."""
import traceback
from datetime import datetime
from io import BytesIO

from flask import current_app, request, send_file
from flask_restx import Namespace, Resource

from compliance_api.services.report.report import ReportService
from compliance_api.auth import auth
from compliance_api.schemas.report import ReportGenerationSchema
from compliance_api.utils.limiter import limiter


from .apihelper import Api as ApiHelper


API = Namespace(
    "reports",
    description="Endpoints for Report Management",
)

report_generation_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, ReportGenerationSchema(), "ReportGenerationSchema"
)


@API.route("/export", methods=["POST"])
class Reports(Resource):
    """Resource for managing reports."""

    decorators = [limiter.limit("10 per minute")]

    @staticmethod
    @ApiHelper.swagger_decorators(API, endpoint_description="Fetch report")
    @API.expect(report_generation_schema)
    @API.doc()
    @API.response(code=200, description="Success - Excel file generated")
    @auth.require
    def post():
        """Fetch all reports."""
        schema = ReportGenerationSchema()

        report_data = schema.load(request.json or {})
        report_type = report_data.get("report_type")

        try:
            data, generator = ReportService.generate_report(report_data, report_type)
        except ValueError as value_error:
            current_app.logger.error(f"Error generating report: {value_error}")
            current_app.logger.error(f"Error generating report: {value_error}\n{traceback.format_exc()}")
            return {"message": str(value_error)}, 400

        if hasattr(generator, "get_filename"):
            file_name = f"{generator.get_filename()}.xlsx"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{report_type}_{timestamp}.xlsx"

        return send_file(BytesIO(data), as_attachment=True, download_name=file_name)
