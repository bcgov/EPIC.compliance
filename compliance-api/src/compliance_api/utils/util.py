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

"""Utility helpers shared across the API."""

import os
import re

from compliance_api.exceptions import UnprocessableEntityError

from compliance_api.utils.constant import DEFAULT_PAGE_SIZE, MAX_EXPORT_ROWS, MAX_PAGE_SIZE


def allowedorigins():
    """Return allowed origin."""
    _allowedcors = os.getenv("CORS_ORIGIN")
    allowedcors = []
    if _allowedcors and "," in _allowedcors:
        for entry in re.split(",", _allowedcors):
            allowedcors.append(entry)
    return allowedcors


class Singleton(type):
    """Singleton meta."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call for meta."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_sorted_numbers_from_generated_code(codes: list[str], replace):
    """Return sorted numbers from the generated codes."""
    existing = sorted([int(r[0].split("_")[-1].replace(replace, "")) for r in codes])
    expected = 1
    for num in existing:
        if num != expected:
            return expected
        expected += 1

    return expected


def _parse_positive_int(args, key, default):
    """Return args[key] as a positive integer, or raise if it is not one."""
    raw = args.get(key, default)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise UnprocessableEntityError(  # pylint: disable=raise-missing-from
            f"{key} must be a number"
        )
    if value < 1:
        raise UnprocessableEntityError(f"{key} must be greater than 0")
    return value


def parse_pagination(args):
    """Return validated (page_no, page_size) from raw request arguments.

    The list endpoints hand the service ``request.args`` unvalidated, so this is
    where the bounds are enforced rather than in a schema.
    """
    page_no = _parse_positive_int(args, "page_no", 1)
    page_size = _parse_positive_int(args, "page_size", DEFAULT_PAGE_SIZE)
    if page_size > MAX_PAGE_SIZE:
        raise UnprocessableEntityError(
            f"page_size cannot exceed {MAX_PAGE_SIZE}"
        )
    return page_no, page_size


def check_export_size(total_count):
    """Reject an export whose result set is too large to build in memory."""
    if total_count > MAX_EXPORT_ROWS:
        raise UnprocessableEntityError(
            f"The export matches {total_count} rows, which exceeds the limit of "
            f"{MAX_EXPORT_ROWS}. Narrow the filters and try again."
        )
