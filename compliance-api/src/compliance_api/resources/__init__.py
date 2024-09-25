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

from .agency import API as AGENCY_API
from .apihelper import Api
from .case_file import API as CASE_FILE_API
from .complaint import API as COMPLAINT_API
from .inspection import API as INSPECTION_API
from .ops import API as OPS_API
from .position import API as POSITION_API
from .project import API as PROJECT_API
from .project_status import API as PROJECT_STATUS_API
from .requirement_source import API as REQUIREMENT_SOURCE_API
from .staff_user import API as USER_API
from .topic import API as TOPIC_API


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
