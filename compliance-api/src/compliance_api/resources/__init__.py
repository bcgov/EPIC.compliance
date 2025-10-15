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
"""Exposes all of the resource endpoints mounted in Flask-Blueprint style.

Uses restplus namespaces to mount individual api endpoints into the service.

All services have 2 defaults sets of endpoints:
 - ops
 - meta
That are used to expose operational health information about the service, and meta information.
"""

from flask import Blueprint

from .administrative_penalty import API as ADMINISTRATIVE_PENALTY_API
from .agency import API as AGENCY_API
from .apihelper import Api
from .appendix import API as APPENDIX_API
from .case_file import API as CASE_FILE_API
from .charge_recommendation import API as CHARGE_RECOMMENDATION_API
from .complaint import API as COMPLAINT_API
from .compliance_finding import API as COMPLIANCE_FINDING_API
from .continuation_report import API as CONTINUATION_REPORT_API
from .document_type import API as DOCUMENT_TYPE_API
from .enforcement_action import API as ENFORCEMENT_ACTION_API
from .inspection import API as INSPECTION_API
from .inspection_record import API as IR_API
from .inspection_requirement import API as INSPECTION_REQUIREMENT_API
from .inspection_requirement_type import API as REQUIREMENT_TYPE_API
from .inspection_requirements import API as INSPECTION_REQUIREMENTS_API
from .ops import API as OPS_API
from .order import API as ORDER_API
from .position import API as POSITION_API
from .project import API as PROJECT_API
from .project_status import API as PROJECT_STATUS_API
from .requirement_source import API as REQUIREMENT_SOURCE_API
from .restorative_justice import API as RESTORATIVE_JUSTICE_API
from .review_board import API as REVIEW_BOARD_API
from .section import API as SECTION_API
from .sentence_type_option import API as SENTENCE_TYPE_OPTION_API
from .staff_user import API as USER_API
from .topic import API as TOPIC_API
from .violation_ticket import API as VIOLATION_TICKET_API
from .warning_letter import API as WARNING_LETTER_API


__all__ = ("API_BLUEPRINT", "OPS_BLUEPRINT")

URL_PREFIX = "/api/"
API_BLUEPRINT = Blueprint("API", __name__, url_prefix=URL_PREFIX)

OPS_BLUEPRINT = Blueprint("API_OPS", __name__, url_prefix="/ops")
API_OPS = Api(
    OPS_BLUEPRINT,
    title="Service OPS API",
    version="1.0",
    description="The Core API for the Reports System",
)

API_OPS.add_namespace(OPS_API, path="/")

authorizations = {
    "Bearer Auth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": 'Add "Bearer " before your token',
    }
}

API = Api(
    API_BLUEPRINT,
    title="COMPLIANCE API",
    version="1.0",
    description="The Core API for COMPLIANCE",
    authorizations=authorizations,
)

API.add_namespace(USER_API)
API.add_namespace(POSITION_API)
API.add_namespace(AGENCY_API)
API.add_namespace(CASE_FILE_API)
API.add_namespace(PROJECT_API)
API.add_namespace(INSPECTION_API)
API.add_namespace(PROJECT_STATUS_API)
API.add_namespace(TOPIC_API)
API.add_namespace(COMPLAINT_API)

API.add_namespace(REQUIREMENT_SOURCE_API)
API.add_namespace(CONTINUATION_REPORT_API)
API.add_namespace(ENFORCEMENT_ACTION_API)
API.add_namespace(COMPLIANCE_FINDING_API)
API.add_namespace(
    INSPECTION_REQUIREMENT_API, path="inspections/<int:inspection_id>/requirements"
)
API.add_namespace(DOCUMENT_TYPE_API)
API.add_namespace(REQUIREMENT_TYPE_API)
API.add_namespace(APPENDIX_API)
API.add_namespace(IR_API, path="inspections/<int:inspection_id>/inspection-records")
API.add_namespace(ORDER_API, path="orders")
API.add_namespace(SECTION_API)
API.add_namespace(VIOLATION_TICKET_API, path="violation-tickets")
API.add_namespace(WARNING_LETTER_API, path="warning-letters")
API.add_namespace(ADMINISTRATIVE_PENALTY_API, path="administrative-penalties")
API.add_namespace(CHARGE_RECOMMENDATION_API, path="charge-recommendations")
API.add_namespace(RESTORATIVE_JUSTICE_API, path="restorative-justices")
API.add_namespace(REVIEW_BOARD_API, path="review-board")
API.add_namespace(INSPECTION_REQUIREMENTS_API, path="inspection-requirements")
API.add_namespace(SENTENCE_TYPE_OPTION_API, path="sentence-type-options")
