"""Unit tests for SentenceTypeOptionService."""

from unittest.mock import Mock, patch

import pytest

from compliance_api.exceptions import BusinessError, ResourceNotFoundError
from compliance_api.models import SentenceTypeOption as SentenceTypeOptionModel
from compliance_api.services.sentence_type_option import SentenceTypeOptionService


class TestSentenceTypeOptionService:
    """Test cases for SentenceTypeOptionService."""

    def test_get_all_active_success(self):
        """Test successful retrieval of all active sentence type options."""
        # Arrange
        mock_sentence_types = [
            Mock(id=1, name="Fine", sort_order=1, is_active=True, is_deleted=False),
            Mock(
                id=2,
                name="Creative Sentencing",
                sort_order=2,
                is_active=True,
                is_deleted=False,
            ),
            Mock(
                id=3,
                name="Imprisonment",
                sort_order=3,
                is_active=True,
                is_deleted=False,
            ),
            Mock(
                id=4, name="Discharge", sort_order=4, is_active=True, is_deleted=False
            ),
        ]

        with patch.object(
            SentenceTypeOptionModel, "get_all_active", return_value=mock_sentence_types
        ) as mock_get_all_active:
            # Act
            result = SentenceTypeOptionService.get_all_active()

            # Assert
            assert result == mock_sentence_types
            mock_get_all_active.assert_called_once()

    def test_get_all_active_empty_result(self):
        """Test retrieval when no active sentence type options exist."""
        # Arrange
        with patch.object(
            SentenceTypeOptionModel, "get_all_active", return_value=[]
        ) as mock_get_all_active:
            # Act
            result = SentenceTypeOptionService.get_all_active()

            # Assert
            assert result == []
            mock_get_all_active.assert_called_once()

    def test_get_all_active_database_error(self):
        """Test handling of database errors during retrieval."""
        # Arrange
        with patch.object(
            SentenceTypeOptionModel,
            "get_all_active",
            side_effect=Exception("Database error"),
        ):
            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                SentenceTypeOptionService.get_all_active()

    def test_get_by_id_success(self):
        """Test successful retrieval of sentence type option by ID."""
        # Arrange
        sentence_type_id = 1
        mock_sentence_type = Mock(
            id=sentence_type_id,
            name="Fine",
            sort_order=1,
            is_active=True,
            is_deleted=False,
        )

        with patch.object(
            SentenceTypeOptionModel, "find_by_id", return_value=mock_sentence_type
        ) as mock_find_by_id:
            # Act
            result = SentenceTypeOptionService.get_by_id(sentence_type_id)

            # Assert
            assert result == mock_sentence_type
            mock_find_by_id.assert_called_once_with(sentence_type_id)

    def test_get_by_id_not_found(self):
        """Test retrieval when sentence type option ID does not exist."""
        # Arrange
        sentence_type_id = 999

        with patch.object(
            SentenceTypeOptionModel, "find_by_id", return_value=None
        ) as mock_find_by_id:
            # Act & Assert
            with pytest.raises(
                ResourceNotFoundError, match="Sentence type option not found"
            ):
                SentenceTypeOptionService.get_by_id(sentence_type_id)

            mock_find_by_id.assert_called_once_with(sentence_type_id)

    def test_get_by_name_success(self):
        """Test successful retrieval of sentence type option by name."""
        # Arrange
        sentence_type_name = "Fine"
        mock_sentence_type = Mock(
            id=1,
            name=sentence_type_name,
            sort_order=1,
            is_active=True,
            is_deleted=False,
        )

        with patch.object(
            SentenceTypeOptionModel, "find_by_name", return_value=mock_sentence_type
        ) as mock_find_by_name:
            # Act
            result = SentenceTypeOptionService.get_by_name(sentence_type_name)

            # Assert
            assert result == mock_sentence_type
            mock_find_by_name.assert_called_once_with(sentence_type_name)

    def test_get_by_name_not_found(self):
        """Test retrieval when sentence type option name does not exist."""
        # Arrange
        sentence_type_name = "NonExistent"

        with patch.object(
            SentenceTypeOptionModel, "find_by_name", return_value=None
        ) as mock_find_by_name:
            # Act & Assert
            with pytest.raises(
                ResourceNotFoundError, match="Sentence type option not found"
            ):
                SentenceTypeOptionService.get_by_name(sentence_type_name)

            mock_find_by_name.assert_called_once_with(sentence_type_name)

    def test_get_by_ids_success(self):
        """Test successful retrieval of multiple sentence type options by IDs."""
        # Arrange
        sentence_type_ids = [1, 2, 3]
        mock_sentence_types = [
            Mock(id=1, name="Fine", sort_order=1),
            Mock(id=2, name="Creative Sentencing", sort_order=2),
            Mock(id=3, name="Imprisonment", sort_order=3),
        ]

        with patch.object(
            SentenceTypeOptionModel, "get_by_ids", return_value=mock_sentence_types
        ) as mock_get_by_ids:
            # Act
            result = SentenceTypeOptionService.get_by_ids(sentence_type_ids)

            # Assert
            assert result == mock_sentence_types
            mock_get_by_ids.assert_called_once_with(sentence_type_ids)

    def test_get_by_ids_empty_list(self):
        """Test retrieval with empty ID list."""
        # Arrange
        sentence_type_ids = []

        with patch.object(
            SentenceTypeOptionModel, "get_by_ids", return_value=[]
        ) as mock_get_by_ids:
            # Act
            result = SentenceTypeOptionService.get_by_ids(sentence_type_ids)

            # Assert
            assert result == []
            mock_get_by_ids.assert_called_once_with(sentence_type_ids)

    def test_get_by_ids_partial_results(self):
        """Test retrieval when some IDs don't exist."""
        # Arrange
        sentence_type_ids = [1, 999, 2]
        mock_sentence_types = [
            Mock(id=1, name="Fine", sort_order=1),
            Mock(id=2, name="Creative Sentencing", sort_order=2),
        ]

        with patch.object(
            SentenceTypeOptionModel, "get_by_ids", return_value=mock_sentence_types
        ) as mock_get_by_ids:
            # Act
            result = SentenceTypeOptionService.get_by_ids(sentence_type_ids)

            # Assert
            assert len(result) == 2
            assert result == mock_sentence_types
            mock_get_by_ids.assert_called_once_with(sentence_type_ids)

    def test_validate_sentence_type_ids_success(self):
        """Test successful validation of sentence type IDs."""
        # Arrange
        sentence_type_ids = [1, 2, 3]
        mock_sentence_types = [
            Mock(id=1, name="Fine"),
            Mock(id=2, name="Creative Sentencing"),
            Mock(id=3, name="Imprisonment"),
        ]

        with patch.object(
            SentenceTypeOptionService, "get_by_ids", return_value=mock_sentence_types
        ):
            # Act & Assert - Should not raise an exception
            SentenceTypeOptionService.validate_sentence_type_ids(sentence_type_ids)

    def test_validate_sentence_type_ids_invalid_ids(self):
        """Test validation failure with invalid sentence type IDs."""
        # Arrange
        sentence_type_ids = [1, 999, 2]
        mock_sentence_types = [
            Mock(id=1, name="Fine"),
            Mock(id=2, name="Creative Sentencing"),
        ]

        with patch.object(
            SentenceTypeOptionService, "get_by_ids", return_value=mock_sentence_types
        ):
            # Act & Assert
            with pytest.raises(
                BusinessError, match="Invalid sentence type option IDs: {999}"
            ):
                SentenceTypeOptionService.validate_sentence_type_ids(sentence_type_ids)

    def test_validate_sentence_type_ids_empty_list(self):
        """Test validation with empty ID list."""
        # Arrange
        sentence_type_ids = []

        with patch.object(SentenceTypeOptionService, "get_by_ids", return_value=[]):
            # Act & Assert - Should not raise an exception
            SentenceTypeOptionService.validate_sentence_type_ids(sentence_type_ids)

    def test_is_valid_sentence_type_id_true(self):
        """Test validation of a valid sentence type ID."""
        # Arrange
        sentence_type_id = 1
        mock_sentence_type = Mock(id=1, name="Fine")

        with patch.object(
            SentenceTypeOptionService, "get_by_id", return_value=mock_sentence_type
        ):
            # Act
            result = SentenceTypeOptionService.is_valid_sentence_type_id(
                sentence_type_id
            )

            # Assert
            assert result is True

    def test_is_valid_sentence_type_id_false(self):
        """Test validation of an invalid sentence type ID."""
        # Arrange
        sentence_type_id = 999

        with patch.object(
            SentenceTypeOptionService,
            "get_by_id",
            side_effect=ResourceNotFoundError("Not found"),
        ):
            # Act
            result = SentenceTypeOptionService.is_valid_sentence_type_id(
                sentence_type_id
            )

            # Assert
            assert result is False

    def test_get_sorted_active_options(self):
        """Test retrieval of active options sorted by sort_order."""
        # Arrange
        mock_sentence_types = [
            Mock(id=1, name="Fine", sort_order=1, is_active=True),
            Mock(id=2, name="Creative Sentencing", sort_order=2, is_active=True),
            Mock(id=3, name="Imprisonment", sort_order=3, is_active=True),
            Mock(id=4, name="Discharge", sort_order=4, is_active=True),
        ]

        with patch.object(
            SentenceTypeOptionService,
            "get_all_active",
            return_value=mock_sentence_types,
        ):
            # Act
            result = SentenceTypeOptionService.get_sorted_active_options()

            # Assert
            assert len(result) == 4
            assert result[0].sort_order == 1
            assert result[1].sort_order == 2
            assert result[2].sort_order == 3
            assert result[3].sort_order == 4
