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
"""Datetime object helper."""
from datetime import datetime
from zoneinfo import ZoneInfo

# British Columbia local time. BC stays on UTC-7 year-round from 2026-11-01,
# while the US Pacific zones keep falling back to UTC-8, so US/Pacific and
# America/Los_Angeles are an hour out from November through March.
BC_TIMEZONE = ZoneInfo("America/Vancouver")


def convert_to_full_month_format(date_val: datetime):
    """Convert a datetime object to a full month format."""
    return date_val.strftime("%B %d, %Y")
