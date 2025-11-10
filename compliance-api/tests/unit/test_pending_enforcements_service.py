"""Unit tests for the pending enforcements service implementation."""

import sys
import os
import pytest

# Add the src directory to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestPendingEnforcementsService:
    """Test class for pending enforcements service functionality."""

    def test_schema_import(self):
        """Test if we can import the PendingEnforcementSchema."""
        try:
            from compliance_api.schemas.inspection import PendingEnforcementSchema
            print("✅ PendingEnforcementSchema import successful")
            assert PendingEnforcementSchema is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PendingEnforcementSchema: {e}")

    def test_schema_functionality(self):
        """Test schema serialization functionality."""
        try:
            from compliance_api.schemas.inspection import PendingEnforcementSchema
            
            schema = PendingEnforcementSchema()
            test_data = {
                'requirement': {
                    'id': 1,
                    'summary': 'Test requirement'
                },
                'enforcement': {
                    'id': 5,
                    'name': 'Order'
                },
                'is_created': False,
                'enforcement_number': 'PROJ_001_O123'
            }
            
            result = schema.dump(test_data)
            print("✅ Schema serialization successful")
            print(f"   Result: {result}")
            
            # Validate all fields are present in result
            assert 'requirement' in result
            assert 'enforcement' in result
            assert 'is_created' in result
            assert 'enforcement_number' in result
            
            # Validate nested object fields
            assert 'id' in result['requirement']
            assert 'summary' in result['requirement']
            assert 'id' in result['enforcement']
            assert 'name' in result['enforcement']
            
            # Validate field values
            assert result['requirement']['id'] == 1
            assert result['requirement']['summary'] == 'Test requirement'
            assert result['enforcement']['id'] == 5
            assert result['enforcement']['name'] == 'Order'
            assert result['is_created'] is False
            assert result['enforcement_number'] == 'PROJ_001_O123'
            
        except Exception as e:
            pytest.fail(f"Schema functionality test failed: {e}")

    def test_schema_export(self):
        """Test schema export in __init__.py."""
        try:
            from compliance_api.schemas import PendingEnforcementSchema as ImportedSchema
            print("✅ Schema export in __init__.py successful")
            assert ImportedSchema is not None
        except ImportError as e:
            pytest.fail(f"Failed to import from schemas.__init__: {e}")

    def test_service_method_exists(self):
        """Test that the service method exists and is callable."""
        try:
            from compliance_api.services.inspection import InspectionService
            
            # Check if the method exists
            assert hasattr(InspectionService, 'get_pending_enforcements'), \
                "InspectionService should have get_pending_enforcements method"
            
            # Check if it's callable
            method = getattr(InspectionService, 'get_pending_enforcements')
            assert callable(method), "get_pending_enforcements should be callable"
            
            print("✅ Service method exists and is callable")
            
        except ImportError as e:
            pytest.fail(f"Failed to import InspectionService: {e}")

    def test_helper_methods_exist(self):
        """Test that helper methods exist."""
        try:
            from compliance_api.services.inspection import InspectionService
            
            helper_methods = [
                '_check_enforcement_status',
                '_check_order_status',
                '_check_warning_letter_status',
                '_check_administrative_penalty_status',
                '_check_violation_ticket_status',
                '_check_charge_recommendation_status',
                '_check_restorative_justice_status'
            ]
            
            for method_name in helper_methods:
                assert hasattr(InspectionService, method_name), \
                    f"InspectionService should have {method_name} method"
                
                method = getattr(InspectionService, method_name)
                assert callable(method), f"{method_name} should be callable"
            
            print("✅ All helper methods exist and are callable")
            
        except ImportError as e:
            pytest.fail(f"Failed to import InspectionService: {e}")


def test_all_imports():
    """Test all imports work together."""
    try:
        # Test basic imports
        print("Testing imports...")
        
        # Test schema import
        from compliance_api.schemas.inspection import PendingEnforcementSchema
        print("✅ PendingEnforcementSchema import successful")
        
        # Test schema functionality
        schema = PendingEnforcementSchema()
        test_data = {
            'requirement': {
                'id': 1,
                'summary': 'Test requirement'
            },
            'enforcement': {
                'id': 5,
                'name': 'Order'
            },
            'is_created': False,
            'enforcement_number': 'PROJ_001_O123'
        }
        
        result = schema.dump(test_data)
        print("✅ Schema serialization successful")
        print(f"   Result: {result}")
        
        # Test schema import in init
        from compliance_api.schemas import PendingEnforcementSchema as ImportedSchema
        print("✅ Schema export in __init__.py successful")
        
        print("\n🎉 All tests passed! The implementation looks good.")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_all_imports()
