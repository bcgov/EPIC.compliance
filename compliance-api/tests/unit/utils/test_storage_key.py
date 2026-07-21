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

"""Tests for the relative_url storage key validator.

Test-Suite to ensure path traversal and other malicious storage keys are
rejected before being forwarded to the document service.
"""
import pytest

from compliance_api.utils.storage_key import is_valid_relative_url


class TestIsValidRelativeUrl:
    """Test is_valid_relative_url function."""

    @pytest.mark.parametrize(
        "relative_url",
        [
            "compliance/1/inspection/1/requirement_images/filename1.jpg",
            "compliance/inspections/42/requirements-images/photo.png",
            "inspection_records/abcdef1234567890.pdf",
        ],
    )
    def test_accepts_expected_keys(self, relative_url):
        """Test that well-formed keys under an allowed prefix are accepted."""
        assert is_valid_relative_url(relative_url) is True

    @pytest.mark.parametrize(
        "relative_url",
        [
            "../../other_prefix/secret.pdf",
            "compliance/../../../etc/passwd",
            "compliance/1/../../secret.pdf",
            "/compliance/1/requirement_images/filename1.jpg",
            "compliance\\1\\requirement_images\\filename1.jpg",
            "documents/not_allowed_prefix.pdf",
            "",
            None,
        ],
    )
    def test_rejects_malicious_or_unexpected_keys(self, relative_url):
        """Test that traversal, backslashes, leading slashes, and unknown prefixes are rejected."""
        assert is_valid_relative_url(relative_url) is False
