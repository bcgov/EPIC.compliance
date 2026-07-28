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

"""Tests for app-level security behaviour (auth gate, docs gating, headers).

These run under the "testing" config, where the Swagger docs are enabled. In
production/staging the docs routes are not registered at all (doc=False plus
add_specs=False), so the docs exemption below cannot apply there.
"""

from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/api/agencies",
        "/api/case-files",
        "/api/inspections",
        "/api/staff-users",
    ],
)
def test_data_endpoints_require_auth(client, path):
    """No data endpoint may be reachable without a bearer token."""
    assert client.get(path).status_code == HTTPStatus.UNAUTHORIZED


def test_auth_gate_normalizes_trailing_slash(client):
    """The auth gate must treat "/api/x" and "/api/x/" identically.

    The gate compares the request path against the "/api/" prefix, so a path
    that does not already end in a slash has to be normalized first or it
    would fall through the check unauthenticated.
    """
    assert client.get("/api/agencies").status_code == HTTPStatus.UNAUTHORIZED
    assert client.get("/api/agencies/").status_code == HTTPStatus.UNAUTHORIZED


def test_docs_reachable_when_enabled(client):
    """Where the docs are registered (non-production) they stay usable."""
    assert client.get("/api/").status_code != HTTPStatus.UNAUTHORIZED


def test_ops_healthz_does_not_require_auth(client):
    """Health checks under /ops must stay open for OpenShift probes."""
    assert client.get("/ops/healthz").status_code != HTTPStatus.UNAUTHORIZED


def test_security_headers(client):
    """CORP/COOP use valid values and CSP disallows inline scripts."""
    result = client.get("/ops/healthz")
    assert result.headers.get("Cross-Origin-Resource-Policy") == "same-origin"
    assert result.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    csp = result.headers.get("Content-Security-Policy", "")
    script_src = csp.split("script-src")[1].split(";")[0]
    assert "'self'" in script_src
    assert "unsafe-inline" not in script_src


def test_cors_preflight_rejects_unknown_origin(client):
    """Preflight must not hand an allow-origin header to an arbitrary site."""
    result = client.open(
        "/api/agencies",
        method="OPTIONS",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert result.headers.get("Access-Control-Allow-Origin") is None
