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

Test-Suite to ensure that the CORS utilities are working as expected.
"""
import os
from unittest.mock import patch

from compliance_api.utils.util import Singleton, allowedorigins


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
        assert type(instance1) is not type(instance2)

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
