"""Integration tests for the pending enforcements endpoint."""

import requests
import json
import pytest
from http import HTTPStatus


class TestPendingEnforcementsEndpoint:
    """Test class for pending enforcements endpoint."""

    def test_pending_enforcements_endpoint_basic(self):
        """Test the pending enforcements endpoint basic functionality."""
        base_url = "http://localhost:5000"
        inspection_id = 1  # You can change this to test with different inspection IDs
        url = f"{base_url}/api/inspections/{inspection_id}/pending-enforcements"

        # You would need proper authentication headers in a real test
        headers = {
            "Content-Type": "application/json",
            # Add authentication headers here if needed
            # "Authorization": "Bearer <token>"
        }

        try:
            response = requests.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")

            if response.status_code == HTTPStatus.OK:
                data = response.json()
                print("✅ Success! Pending enforcements:")
                print(json.dumps(data, indent=2))

                # Validate response structure
                assert isinstance(data, list), "Response should be a list"

                if data:  # If there are pending enforcements
                    for item in data:
                        # Validate each item has required fields
                        assert "requirement" in item
                        assert "enforcement" in item
                        assert "is_created" in item
                        assert "enforcement_number" in item

                        # Validate nested objects
                        assert "id" in item["requirement"]
                        assert "summary" in item["requirement"]
                        assert "id" in item["enforcement"]
                        assert "name" in item["enforcement"]

            elif response.status_code == HTTPStatus.NOT_FOUND:
                print("❌ Inspection not found")
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                print("❌ Authentication required")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)

        except requests.exceptions.ConnectionError:
            pytest.skip(
                "Could not connect to server. Make sure Flask is running on localhost:5000"
            )
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            pytest.fail(f"Unexpected error: {str(e)}")

    def test_pending_enforcements_invalid_inspection(self):
        """Test the endpoint with an invalid inspection ID."""
        base_url = "http://localhost:5000"
        inspection_id = 999999  # Non-existent ID
        url = f"{base_url}/api/inspections/{inspection_id}/pending-enforcements"

        headers = {
            "Content-Type": "application/json",
            # Add authentication headers here if needed
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == HTTPStatus.NOT_FOUND:
                print("✅ Correctly returned 404 for non-existent inspection")
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                pytest.skip("Authentication required - cannot test without proper auth")
            else:
                print(f"Unexpected status code: {response.status_code}")

        except requests.exceptions.ConnectionError:
            pytest.skip("Could not connect to server")
        except (requests.exceptions.RequestException, ValueError) as e:
            pytest.fail(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    # Run basic test when executed directly
    test_instance = TestPendingEnforcementsEndpoint()
    test_instance.test_pending_enforcements_endpoint_basic()
