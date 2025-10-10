"""Various test data for sentence type options."""

from enum import Enum

from faker import Faker

from compliance_api.models import SentenceTypeOption as SentenceTypeOptionModel


fake = Faker()


class SentenceTypeOptionScenario(Enum):
    """Sentence type option scenario."""

    # Default sentence types matching migration data
    fine_option = {
        "name": "Fine",
        "sort_order": 1,
        "is_active": True,
        "is_deleted": False,
    }

    creative_sentencing_option = {
        "name": "Creative Sentencing",
        "sort_order": 2,
        "is_active": True,
        "is_deleted": False,
    }

    imprisonment_option = {
        "name": "Imprisonment",
        "sort_order": 3,
        "is_active": True,
        "is_deleted": False,
    }

    discharge_option = {
        "name": "Discharge",
        "sort_order": 4,
        "is_active": True,
        "is_deleted": False,
    }

    # Test scenarios
    custom_option = {
        "name": fake.word().title() + " Sentence",
        "sort_order": 5,
        "is_active": True,
        "is_deleted": False,
    }

    inactive_option = {
        "name": "Inactive Sentence Type",
        "sort_order": 6,
        "is_active": False,
        "is_deleted": False,
    }

    deleted_option = {
        "name": "Deleted Sentence Type",
        "sort_order": 7,
        "is_active": True,
        "is_deleted": True,
    }

    # Edge case scenarios
    long_name_option = {
        "name": fake.text(max_nb_chars=255),
        "sort_order": 8,
        "is_active": True,
        "is_deleted": False,
    }

    zero_sort_order_option = {
        "name": "Zero Sort Order",
        "sort_order": 0,
        "is_active": True,
        "is_deleted": False,
    }

    high_sort_order_option = {
        "name": "High Sort Order",
        "sort_order": 999,
        "is_active": True,
        "is_deleted": False,
    }

    # Update scenarios
    update_name_scenario = {"name": "Updated Sentence Type Name"}

    update_sort_order_scenario = {"sort_order": 99}

    update_status_scenario = {"is_active": False}

    @staticmethod
    def create(sentence_type_data: dict):
        """Create sentence type option."""
        sentence_type = SentenceTypeOptionModel(**sentence_type_data)
        sentence_type.save()
        return sentence_type

    @staticmethod
    def create_multiple(scenarios: list):
        """Create multiple sentence type options."""
        created_options = []
        for scenario in scenarios:
            sentence_type_data = (
                scenario.value if hasattr(scenario, "value") else scenario
            )
            created_options.append(
                SentenceTypeOptionScenario.create(sentence_type_data)
            )
        return created_options

    @staticmethod
    def get_all_default_options():
        """Get all default sentence type options from migration."""
        return [
            SentenceTypeOptionScenario.fine_option.value,
            SentenceTypeOptionScenario.creative_sentencing_option.value,
            SentenceTypeOptionScenario.imprisonment_option.value,
            SentenceTypeOptionScenario.discharge_option.value,
        ]

    @staticmethod
    def get_test_options():
        """Get various test sentence type options."""
        return [
            SentenceTypeOptionScenario.custom_option.value,
            SentenceTypeOptionScenario.inactive_option.value,
            SentenceTypeOptionScenario.deleted_option.value,
        ]
