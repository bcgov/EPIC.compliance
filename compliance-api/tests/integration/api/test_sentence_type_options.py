"""Test suite for sentence type options."""

from http import HTTPStatus
from urllib.parse import urljoin

import pytest


API_BASE_URL = "/api/"


class TestSentenceTypeOptions:
    """Test cases for sentence type options endpoints."""

    def test_get_sentence_type_options_success(self, client, auth_header):
        """Test successful retrieval of all active sentence type options."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url, headers=auth_header)

        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json, list)

        # Verify expected sentence types are present
        expected_sentence_types = [
            "Fine",
            "Creative Sentencing",
            "Imprisonment",
            "Discharge",
        ]
        response_names = [option["name"] for option in response.json]

        for expected_type in expected_sentence_types:
            assert expected_type in response_names

        # Verify each option has required fields
        for option in response.json:
            assert "id" in option
            assert "name" in option
            assert "sort_order" in option
            assert option["is_active"] is True
            assert option["is_deleted"] is False

    def test_get_sentence_type_options_returns_sorted_results(
        self, client, auth_header
    ):
        """Test that sentence type options are returned in sort_order."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url, headers=auth_header)

        assert response.status_code == HTTPStatus.OK

        # Verify options are sorted by sort_order
        sort_orders = [option["sort_order"] for option in response.json]
        assert sort_orders == sorted(sort_orders)

        # Verify specific order based on migration data
        expected_order = ["Fine", "Creative Sentencing", "Imprisonment", "Discharge"]
        actual_order = [option["name"] for option in response.json]
        assert actual_order == expected_order

    def test_get_sentence_type_options_only_returns_active(self, client, auth_header):
        """Test that only active sentence type options are returned."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url, headers=auth_header)

        assert response.status_code == HTTPStatus.OK

        # All returned options should be active and not deleted
        for option in response.json:
            assert option["is_active"] is True
            assert option["is_deleted"] is False

    def test_get_sentence_type_options_unauthorized(self, client):
        """Test unauthorized access to sentence type options."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_sentence_type_options_invalid_method(self, client, auth_header):
        """Test invalid HTTP methods on sentence type options endpoint."""
        url = urljoin(API_BASE_URL, "sentence-type-options")

        # POST should not be allowed
        response = client.post(url, headers=auth_header, json={})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # PUT should not be allowed
        response = client.put(url, headers=auth_header, json={})
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

        # DELETE should not be allowed
        response = client.delete(url, headers=auth_header)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_get_sentence_type_options_cors_headers(self, client, auth_header):
        """Test CORS preflight headers for sentence type options."""
        url = urljoin(API_BASE_URL, "sentence-type-options")

        # Test OPTIONS request
        response = client.options(url, headers=auth_header)

        # Should allow OPTIONS method
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NO_CONTENT]

    def test_get_sentence_type_options_response_structure(self, client, auth_header):
        """Test the structure of sentence type options response."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url, headers=auth_header)

        assert response.status_code == HTTPStatus.OK
        assert len(response.json) >= 4  # At least the 4 default types

        # Test response structure for first option
        first_option = response.json[0]
        expected_fields = [
            "id",
            "name",
            "sort_order",
            "is_active",
            "is_deleted",
            "created_date",
            "updated_date",
            "created_by",
            "updated_by",
        ]

        for field in expected_fields:
            assert field in first_option, f"Field '{field}' missing from response"

        # Test data types
        assert isinstance(first_option["id"], int)
        assert isinstance(first_option["name"], str)
        assert isinstance(first_option["sort_order"], int)
        assert isinstance(first_option["is_active"], bool)
        assert isinstance(first_option["is_deleted"], bool)

    def test_get_sentence_type_options_caching(self, client, auth_header):
        """Test that sentence type options endpoint supports caching."""
        url = urljoin(API_BASE_URL, "sentence-type-options")

        # First request
        response1 = client.get(url, headers=auth_header)

        # Second request (should be cached)
        response2 = client.get(url, headers=auth_header)

        assert response1.status_code == HTTPStatus.OK
        assert response2.status_code == HTTPStatus.OK
        assert response1.json == response2.json

    def test_get_sentence_type_options_content_type(self, client, auth_header):
        """Test that sentence type options returns correct content type."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url, headers=auth_header)

        assert response.status_code == HTTPStatus.OK
        assert "application/json" in response.content_type

    @pytest.mark.parametrize(
        "expected_name,expected_sort_order",
        [
            ("Fine", 1),
            ("Creative Sentencing", 2),
            ("Imprisonment", 3),
            ("Discharge", 4),
        ],
    )
    def test_get_sentence_type_options_specific_types(
        self, client, auth_header, expected_name, expected_sort_order
    ):
        """Test that specific sentence types exist with correct sort order."""
        url = urljoin(API_BASE_URL, "sentence-type-options")
        response = client.get(url, headers=auth_header)

        assert response.status_code == HTTPStatus.OK

        # Find the specific sentence type
        found_option = None
        for option in response.json:
            if option["name"] == expected_name:
                found_option = option
                break

        assert found_option is not None, f"Sentence type '{expected_name}' not found"
        assert found_option["sort_order"] == expected_sort_order
        assert found_option["is_active"] is True
        assert found_option["is_deleted"] is False

    def test_get_sentence_type_options_performance(self, client, auth_header):
        """Test performance of sentence type options endpoint."""
        import time

        url = urljoin(API_BASE_URL, "sentence-type-options")

        start_time = time.time()
        response = client.get(url, headers=auth_header)
        end_time = time.time()

        assert response.status_code == HTTPStatus.OK

        # Response should be fast (less than 1 second for this simple query)
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response took {response_time:.2f} seconds"
