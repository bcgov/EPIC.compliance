# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Exposes all of the Services used in the compliance_api."""
from .agency import AgencyService
from .case_file import CaseFileService
from .inspection import InspectionService
from .position import PositionService
from .project import ProjectService
from .project_status import ProjectStatusService
from .staff_user import StaffUserService
