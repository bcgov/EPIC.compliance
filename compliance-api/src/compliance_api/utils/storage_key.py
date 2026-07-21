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
"""Validation for user-supplied cloud storage keys (relative_url).

Guards against path traversal: relative_url is forwarded to the document
service to mint presigned GET/PUT/DELETE URLs, so an unvalidated value could
be used to read, overwrite, or delete objects outside the caller's own prefix.
"""
import re

# Prefixes under which this API ever writes objects: "compliance/" for
# client-uploaded images, "inspection_records/" for server-generated reports.
ALLOWED_RELATIVE_URL_PREFIXES = ("compliance/", "inspection_records/")

# Restrict to a safe character set in addition to the prefix/traversal checks
# below, so encoded traversal sequences or backslashes can't sneak through.
_SAFE_RELATIVE_URL_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")


def is_valid_relative_url(relative_url: str) -> bool:
    """Return True if relative_url is a safe, expected storage key."""
    if not relative_url or not isinstance(relative_url, str):
        return False
    if ".." in relative_url or "\\" in relative_url:
        return False
    if relative_url.startswith("/"):
        return False
    if not _SAFE_RELATIVE_URL_PATTERN.match(relative_url):
        return False
    return relative_url.startswith(ALLOWED_RELATIVE_URL_PREFIXES)
