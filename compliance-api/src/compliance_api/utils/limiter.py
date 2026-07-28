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
"""Bring in the common rate limiter."""
from flask import g, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def rate_limit_key():
    """Key rate limits by authenticated user, falling back to the client IP."""
    token_info = getattr(g, "token_info", None)
    if token_info:
        user_id = token_info.get("preferred_username")
        if user_id:
            return user_id
    return get_remote_address()


def exempt_from_default_limits():
    """Skip the default limit for CORS preflight and the ops health checks."""
    return request.method == "OPTIONS" or request.path.startswith("/ops")


# lower case name as used by convention in most Flask apps
# Configuration will be loaded from Flask app config
limiter = Limiter(  # pylint: disable=invalid-name
    key_func=rate_limit_key,
    default_limits=["200 per minute"],
    default_limits_exempt_when=exempt_from_default_limits,
)
