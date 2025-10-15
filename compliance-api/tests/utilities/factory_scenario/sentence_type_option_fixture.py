"""Sentence type option fixtures for testing."""

import pytest

from compliance_api.models import SentenceTypeOption as SentenceTypeOptionModel
from tests.utilities.factory_scenario.sentence_type_option_scenario import SentenceTypeOptionScenario


@pytest.fixture
def created_sentence_type_fine():
    """Create sentence type option for Fine."""
    sentence_type_data = SentenceTypeOptionScenario.fine_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_sentence_type_creative_sentencing():
    """Create sentence type option for Creative Sentencing."""
    sentence_type_data = SentenceTypeOptionScenario.creative_sentencing_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_sentence_type_imprisonment():
    """Create sentence type option for Imprisonment."""
    sentence_type_data = SentenceTypeOptionScenario.imprisonment_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_sentence_type_discharge():
    """Create sentence type option for Discharge."""
    sentence_type_data = SentenceTypeOptionScenario.discharge_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_all_default_sentence_types():
    """Create all default sentence type options."""
    sentence_types = []
    for scenario in [
        SentenceTypeOptionScenario.fine_option,
        SentenceTypeOptionScenario.creative_sentencing_option,
        SentenceTypeOptionScenario.imprisonment_option,
        SentenceTypeOptionScenario.discharge_option,
    ]:
        sentence_type_data = scenario.value
        sentence_type = SentenceTypeOptionModel(**sentence_type_data)
        sentence_type.save()
        sentence_types.append(sentence_type)

    yield sentence_types

    # Cleanup
    for sentence_type in sentence_types:
        sentence_type.delete()


@pytest.fixture
def created_custom_sentence_type():
    """Create custom sentence type option for testing."""
    sentence_type_data = SentenceTypeOptionScenario.custom_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_inactive_sentence_type():
    """Create inactive sentence type option for testing."""
    sentence_type_data = SentenceTypeOptionScenario.inactive_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_deleted_sentence_type():
    """Create deleted sentence type option for testing."""
    sentence_type_data = SentenceTypeOptionScenario.deleted_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_mixed_sentence_types():
    """Create a mix of active, inactive, and deleted sentence types."""
    sentence_types = []
    scenarios = [
        SentenceTypeOptionScenario.fine_option,
        SentenceTypeOptionScenario.custom_option,
        SentenceTypeOptionScenario.inactive_option,
        SentenceTypeOptionScenario.deleted_option,
    ]

    for scenario in scenarios:
        sentence_type_data = scenario.value
        sentence_type = SentenceTypeOptionModel(**sentence_type_data)
        sentence_type.save()
        sentence_types.append(sentence_type)

    yield sentence_types

    # Cleanup
    for sentence_type in sentence_types:
        sentence_type.delete()


@pytest.fixture
def created_sentence_type_with_long_name():
    """Create sentence type option with long name for edge case testing."""
    sentence_type_data = SentenceTypeOptionScenario.long_name_option.value
    sentence_type = SentenceTypeOptionModel(**sentence_type_data)
    sentence_type.save()
    yield sentence_type
    sentence_type.delete()


@pytest.fixture
def created_sentence_types_various_sort_orders():
    """Create sentence types with various sort orders for sorting tests."""
    sentence_types = []
    scenarios = [
        SentenceTypeOptionScenario.zero_sort_order_option,
        SentenceTypeOptionScenario.fine_option,
        SentenceTypeOptionScenario.high_sort_order_option,
        SentenceTypeOptionScenario.creative_sentencing_option,
    ]

    for scenario in scenarios:
        sentence_type_data = scenario.value
        sentence_type = SentenceTypeOptionModel(**sentence_type_data)
        sentence_type.save()
        sentence_types.append(sentence_type)

    yield sentence_types

    # Cleanup
    for sentence_type in sentence_types:
        sentence_type.delete()
