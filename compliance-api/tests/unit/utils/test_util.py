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

"""Tests to assure the CORS utilities.

Test-Suite to ensure that the CORS decorator is working as expected.
"""
import base64
import os
from unittest.mock import patch
from urllib.parse import unquote

import pytest

from compliance_api.utils.util import (
    Singleton, allowedorigins, camelback2snake, cors_preflight, digitify, escape_wam_friendly_url, snake2camelback)


TEST_CAMEL_DATA = {
    "loginSource": "PASSCODE",
    "userName": "test name",
    "realmAccess": {"roles": ["basic"]},
}

TEST_SNAKE_DATA = {
    "login_source": "PASSCODE",
    "user_name": "test name",
    "realm_access": {"roles": ["basic"]},
}


def test_camelback2snake():
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    snake = camelback2snake(TEST_CAMEL_DATA)

    assert snake["login_source"] == TEST_SNAKE_DATA["login_source"]


def test_snake2camelback():
    """Assert that the options methos is added to the class and that the correct access controls are set."""
    camel = snake2camelback(TEST_SNAKE_DATA)

    assert camel["loginSource"] == TEST_CAMEL_DATA["loginSource"]


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("foo", "Zm9v"),
        ("foo-bar", "Zm9vLWJhcg%3D%3D"),
        ("foo bar.....", "Zm9vIGJhci4uLi4u"),
    ],
)
def test_escape_wam_friendly_url_multiple(test_input, expected):
    """Assert manually calculated url encodings."""
    assert escape_wam_friendly_url(test_input) == expected


def test_escape_wam_friendly_url():
    """Assert conversion back yields same string."""
    org_name = "foo-bar helo .."
    org_name_encoded = escape_wam_friendly_url(org_name)
    param1 = unquote(org_name_encoded)
    org_name_actual = base64.b64decode(bytes(param1, encoding="utf-8")).decode("utf-8")
    assert org_name_actual == org_name


class TestCorsPreflight:
    """Test cors_preflight decorator."""

    def test_cors_preflight_decorator_adds_options_method(self):
        """Test that cors_preflight decorator adds options method to class."""

        # Arrange
        @cors_preflight("GET, POST, PUT, DELETE")
        class TestResource:
            """Test resource with cors_preflight decorator."""

            def get(self):
                return "get method"

        # Act
        resource = TestResource()

        # Assert
        assert hasattr(resource, "options")
        assert callable(getattr(resource, "options"))

    def test_cors_preflight_options_method_returns_correct_headers(self):
        """Test that options method returns correct CORS headers."""
        # Arrange
        methods = "GET, POST, PUT, DELETE"

        @cors_preflight(methods)
        class TestResource:
            def get(self):
                return "get method"

        resource = TestResource()

        # Act
        response, status_code, headers = resource.options()

        # Assert
        assert status_code == 200
        assert response == {"Allow": "GET, DELETE, PUT, POST"}
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert headers["Access-Control-Allow-Methods"] == methods
        assert "Authorization" in headers["Access-Control-Allow-Headers"]
        assert "Content-Type" in headers["Access-Control-Allow-Headers"]

    def test_cors_preflight_with_different_methods(self):
        """Test cors_preflight with different HTTP methods."""
        # Arrange
        methods = "GET, POST"

        @cors_preflight(methods)
        class TestResource:
            def get(self):
                return "get method"

        resource = TestResource()

        # Act
        response, status_code, headers = resource.options()

        # Assert
        assert headers["Access-Control-Allow-Methods"] == methods

    def test_cors_preflight_preserves_original_class(self):
        """Test that cors_preflight preserves original class functionality."""

        # Arrange
        @cors_preflight("GET, POST")
        class TestResource:
            """Test resource with cors_preflight decorator."""

            def get(self):
                return "original get method"

        resource = TestResource()

        # Act & Assert
        assert resource.get() == "original get method"
        assert hasattr(resource, "options")


class TestAllowedOrigins:
    """Test allowedorigins function."""

    @patch.dict(
        os.environ, {"CORS_ORIGIN": "http://localhost:3000,https://example.com"}
    )
    def test_allowedorigins_with_multiple_origins(self):
        """Test allowedorigins with multiple comma-separated origins."""
        # Act
        result = allowedorigins()

        # Assert
        assert result == ["http://localhost:3000", "https://example.com"]

    @patch.dict(os.environ, {"CORS_ORIGIN": "http://localhost:3000"})
    def test_allowedorigins_with_single_origin(self):
        """Test allowedorigins with single origin (no comma)."""
        # Act
        result = allowedorigins()

        # Assert
        assert result == []  # Single origin without comma returns empty list

    @patch.dict(os.environ, {}, clear=True)
    def test_allowedorigins_with_no_env_var(self):
        """Test allowedorigins when CORS_ORIGIN environment variable is not set."""
        # Act
        result = allowedorigins()

        # Assert
        assert result == []

    @patch.dict(os.environ, {"CORS_ORIGIN": ""})
    def test_allowedorigins_with_empty_env_var(self):
        """Test allowedorigins when CORS_ORIGIN environment variable is empty."""
        # Act
        result = allowedorigins()

        # Assert
        assert result == []

    @patch.dict(
        os.environ,
        {"CORS_ORIGIN": "http://localhost:3000,https://example.com,https://test.com"},
    )
    def test_allowedorigins_with_three_origins(self):
        """Test allowedorigins with three comma-separated origins."""
        # Act
        result = allowedorigins()

        # Assert
        assert result == [
            "http://localhost:3000",
            "https://example.com",
            "https://test.com",
        ]

    @patch.dict(
        os.environ, {"CORS_ORIGIN": "http://localhost:3000, https://example.com"}
    )
    def test_allowedorigins_with_spaces_around_comma(self):
        """Test allowedorigins handles spaces around commas."""
        # Act
        result = allowedorigins()

        # Assert
        assert result == ["http://localhost:3000", " https://example.com"]


class TestSingleton:
    """Test Singleton metaclass."""

    def test_singleton_creates_single_instance(self):
        """Test that Singleton metaclass creates only one instance."""

        # Arrange
        class TestClass(metaclass=Singleton):
            """Test class with Singleton metaclass."""

            def __init__(self):
                self.value = "test"

        # Act
        instance1 = TestClass()
        instance2 = TestClass()

        # Assert
        assert instance1 is instance2
        assert id(instance1) == id(instance2)

    def test_singleton_preserves_state(self):
        """Test that Singleton instances preserve state across calls."""

        # Arrange
        class TestClass(metaclass=Singleton):
            """Test class with Singleton metaclass."""

            def __init__(self):
                self.counter = 0

            def increment(self):
                self.counter += 1

        # Act
        instance1 = TestClass()
        instance1.increment()
        instance2 = TestClass()

        # Assert
        assert instance1 is instance2
        assert instance2.counter == 1

    def test_singleton_different_classes_different_instances(self):
        """Test that different classes with Singleton metaclass have different instances."""

        # Arrange
        class TestClass1(metaclass=Singleton):
            """Test class 1 with Singleton metaclass."""

            pass

        class TestClass2(metaclass=Singleton):
            """Test class 2 with Singleton metaclass."""

            pass

        # Act
        instance1 = TestClass1()
        instance2 = TestClass2()

        # Assert
        assert instance1 is not instance2
        assert type(instance1) != type(instance2)

    def test_singleton_with_constructor_args(self):
        """Test that Singleton works with constructor arguments."""

        # Arrange
        class TestClass(metaclass=Singleton):
            """Test class with constructor arguments."""

            def __init__(self, value=None):
                if not hasattr(self, "initialized"):
                    self.value = value
                    self.initialized = True

        # Act
        instance1 = TestClass("first")
        instance2 = TestClass("second")  # This should return the same instance

        # Assert
        assert instance1 is instance2
        assert instance1.value == "first"  # Should keep the first value


class TestDigitify:
    """Test digitify function."""

    def test_digitify_with_numbers_only(self):
        """Test digitify with string containing only numbers."""
        # Act
        result = digitify("12345")

        # Assert
        assert result == 12345

    def test_digitify_with_mixed_characters(self):
        """Test digitify with string containing numbers and letters."""
        # Act
        result = digitify("abc123def456")

        # Assert
        assert result == 123456

    def test_digitify_with_special_characters(self):
        """Test digitify with string containing numbers and special characters."""
        # Act
        result = digitify("$1,234.56!")

        # Assert
        assert result == 123456

    def test_digitify_with_phone_number_format(self):
        """Test digitify with phone number format."""
        # Act
        result = digitify("(555) 123-4567")

        # Assert
        assert result == 5551234567

    def test_digitify_with_no_digits(self):
        """Test digitify with string containing no digits raises ValueError."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="invalid literal for int\\(\\) with base 10: ''"
        ):
            digitify("abcdef!@#")

    def test_digitify_with_empty_string(self):
        """Test digitify with empty string raises ValueError."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="invalid literal for int\\(\\) with base 10: ''"
        ):
            digitify("")

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("123", 123),
            ("a1b2c3", 123),
            ("1.2.3", 123),
            ("1-2-3", 123),
            ("1 2 3", 123),
            ("order#123", 123),
            ("ID: 456", 456),
            ("v1.2.3", 123),
        ],
    )
    def test_digitify_various_formats(self, test_input, expected):
        """Test digitify with various input formats."""
        # Act
        result = digitify(test_input)

        # Assert
        assert result == expected

    def test_digitify_with_leading_zeros(self):
        """Test digitify preserves leading zeros as integers."""
        # Act
        result = digitify("00123")

        # Assert
        assert result == 123  # Leading zeros are ignored in integer conversion

    def test_digitify_with_unicode_digits(self):
        """Test digitify with unicode characters and digits."""
        # Act
        result = digitify("test123测试456")

        # Assert
        assert result == 123456


class TestCamelSnakeConversionEdgeCases:
    """Additional edge case tests for camel/snake case conversion."""

    def test_camelback2snake_with_empty_dict(self):
        """Test camelback2snake with empty dictionary."""
        # Act
        result = camelback2snake({})

        # Assert
        assert result == {}

    def test_snake2camelback_with_empty_dict(self):
        """Test snake2camelback with empty dictionary."""
        # Act
        result = snake2camelback({})

        # Assert
        assert result == {}

    def test_camelback2snake_with_nested_dicts(self):
        """Test camelback2snake with nested dictionaries."""
        # Arrange
        nested_camel = {
            "outerKey": {
                "innerKey": "value",
                "anotherInnerKey": {"deepKey": "deepValue"},
            }
        }

        # Act
        result = camelback2snake(nested_camel)

        # Assert
        assert "outer_key" in result
        assert "inner_key" in result["outer_key"]
        assert "another_inner_key" in result["outer_key"]
        assert "deep_key" in result["outer_key"]["another_inner_key"]

    def test_snake2camelback_with_nested_dicts(self):
        """Test snake2camelback with nested dictionaries."""
        # Arrange
        nested_snake = {
            "outer_key": {
                "inner_key": "value",
                "another_inner_key": {"deep_key": "deepValue"},
            }
        }

        # Act
        result = snake2camelback(nested_snake)

        # Assert
        assert "outerKey" in result
        assert "innerKey" in result["outerKey"]
        assert "anotherInnerKey" in result["outerKey"]
        assert "deepKey" in result["outerKey"]["anotherInnerKey"]


class TestEscapeWamFriendlyUrlEdgeCases:
    """Additional edge case tests for escape_wam_friendly_url."""

    def test_escape_wam_friendly_url_with_empty_string(self):
        """Test escape_wam_friendly_url with empty string."""
        # Act
        result = escape_wam_friendly_url("")

        # Assert
        assert result == ""

    def test_escape_wam_friendly_url_with_unicode(self):
        """Test escape_wam_friendly_url with unicode characters."""
        # Arrange
        unicode_string = "测试unicode"

        # Act
        result = escape_wam_friendly_url(unicode_string)

        # Assert
        # Should be able to decode back to original
        param1 = unquote(result)
        original = base64.b64decode(bytes(param1, encoding="utf-8")).decode("utf-8")
        assert original == unicode_string

    def test_escape_wam_friendly_url_with_special_chars(self):
        """Test escape_wam_friendly_url with various special characters."""
        # Arrange
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

        # Act
        result = escape_wam_friendly_url(special_chars)

        # Assert
        # Should be able to decode back to original
        param1 = unquote(result)
        original = base64.b64decode(bytes(param1, encoding="utf-8")).decode("utf-8")
        assert original == special_chars
