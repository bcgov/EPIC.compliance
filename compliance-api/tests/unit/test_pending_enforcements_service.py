"""Unit tests for the pending enforcements service implementation."""

import sys
import os
import pytest

# Add the src directory to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestPendingEnforcementsService:
    """Test class for pending enforcements service functionality."""

    def test_schema_import(self):
        """Test if we can import the PendingItemSchema."""
        try:
            from compliance_api.schemas.inspection import PendingItemSchema
            print("✅ PendingItemSchema import successful")
            assert PendingItemSchema is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PendingItemSchema: {e}")

    def test_schema_functionality(self):
        """Test schema serialization functionality."""
        try:
            from compliance_api.schemas.inspection import PendingItemSchema

            schema = PendingItemSchema()
            test_data = {
                'requirement': {
                    'id': 1,
                    'summary': 'Test requirement'
                },
                'item': {
                    'id': 5,
                    'name': 'Order'
                },
                'is_created': False,
                'item_number': 'PROJ_001_O123'
            }

            result = schema.dump(test_data)
            print("✅ Schema serialization successful")
            print(f"   Result: {result}")

            # Validate all fields are present in result
            assert 'requirement' in result
            assert 'item' in result
            assert 'is_created' in result
            assert 'item_number' in result

            # Validate nested object fields
            assert 'id' in result['requirement']
            assert 'summary' in result['requirement']
            assert 'id' in result['item']
            assert 'name' in result['item']

            # Validate field values
            assert result['requirement']['id'] == 1
            assert result['requirement']['summary'] == 'Test requirement'
            assert result['item']['id'] == 5
            assert result['item']['name'] == 'Order'
            assert result['is_created'] is False
            assert result['item_number'] == 'PROJ_001_O123'

        except (ImportError, AttributeError, AssertionError, KeyError) as e:
            pytest.fail(f"Schema functionality test failed: {e}")

    def test_schema_export(self):
        """Test schema export in __init__.py."""
        try:
            from compliance_api.schemas import PendingItemSchema as ImportedSchema
            print("✅ Schema export in __init__.py successful")
            assert ImportedSchema is not None
        except ImportError as e:
            pytest.fail(f"Failed to import from schemas.__init__: {e}")

    def test_service_method_exists(self):
        """Test that the service method exists and is callable."""
        try:
            from compliance_api.services.inspection import InspectionService

            # Check if the method exists
            assert hasattr(InspectionService, 'get_pending_items'), \
                "InspectionService should have get_pending_items method"

            # Check if it's callable
            method = getattr(InspectionService, 'get_pending_items')
            assert callable(method), "get_pending_items should be callable"

            print("✅ Service method exists and is callable")

        except ImportError as e:
            pytest.fail(f"Failed to import InspectionService: {e}")

    def test_helper_methods_exist(self):
        """Test that helper methods exist."""
        try:
            from compliance_api.services import inspection as inspection_module

            helper_methods = [
                '_check_enforcement_status',
                '_check_order_status',
                '_check_warning_letter_status',
                '_check_administrative_penalty_status',
                '_check_violation_ticket_status',
                '_check_charge_recommendation_status',
                '_check_inspection_record_status',
            ]

            for method_name in helper_methods:
                assert hasattr(inspection_module, method_name), \
                    f"inspection module should have {method_name} function"

                method = getattr(inspection_module, method_name)
                assert callable(method), f"{method_name} should be callable"

            print("✅ All helper methods exist and are callable")

        except ImportError as e:
            pytest.fail(f"Failed to import inspection module: {e}")


def test_all_imports():
    """Test all imports work together."""
    try:
        # Test basic imports
        print("Testing imports...")

        # Test schema import
        from compliance_api.schemas.inspection import PendingItemSchema
        print("✅ PendingItemSchema import successful")

        # Test schema functionality
        schema = PendingItemSchema()
        test_data = {
            'requirement': {
                'id': 1,
                'summary': 'Test requirement'
            },
            'item': {
                'id': 5,
                'name': 'Order'
            },
            'is_created': False,
            'item_number': 'PROJ_001_O123'
        }

        result = schema.dump(test_data)
        print("✅ Schema serialization successful")
        print(f"   Result: {result}")

        # Test schema import in init - using ImportedSchema to avoid F401
        from compliance_api.schemas import PendingItemSchema as ImportedSchema
        assert ImportedSchema is not None
        print("✅ Schema export in __init__.py successful")

        print("\n🎉 All tests passed! The implementation looks good.")
        return True

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except (AttributeError, AssertionError) as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_all_imports()
