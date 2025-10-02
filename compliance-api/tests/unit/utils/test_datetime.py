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

"""Tests for datetime utility functions.

Test-Suite to ensure that the datetime utility functions are working as expected.
"""
from datetime import datetime
from unittest.mock import patch

import pytest
import pytz

from compliance_api.utils.datetime import (
    convert_and_format_to_utc_str, convert_to_full_month_format, local_datetime, utc_datetime)


class TestLocalDatetime:
    """Test local_datetime function."""

    @patch("compliance_api.utils.datetime.datetime")
    def test_local_datetime_returns_pacific_time(self, mock_datetime):
        """Test that local_datetime returns Pacific timezone datetime."""
        # Arrange
        mock_utc_time = datetime(2024, 6, 15, 20, 30, 45)  # 8:30 PM UTC
        mock_datetime.utcnow.return_value = mock_utc_time

        # Act
        result = local_datetime()

        # Assert
        assert result.tzinfo.zone == "US/Pacific"
        # In June, Pacific time is PDT (UTC-7), so 20:30 UTC = 13:30 PDT
        assert result.hour == 13
        assert result.minute == 30
        assert result.second == 45

    @patch("compliance_api.utils.datetime.datetime")
    def test_local_datetime_winter_time(self, mock_datetime):
        """Test that local_datetime handles PST (winter time) correctly."""
        # Arrange
        mock_utc_time = datetime(2024, 1, 15, 20, 30, 45)  # 8:30 PM UTC in January
        mock_datetime.utcnow.return_value = mock_utc_time

        # Act
        result = local_datetime()

        # Assert
        assert result.tzinfo.zone == "US/Pacific"
        # In January, Pacific time is PST (UTC-8), so 20:30 UTC = 12:30 PST
        assert result.hour == 12
        assert result.minute == 30
        assert result.second == 45

    @patch("compliance_api.utils.datetime.datetime")
    def test_local_datetime_has_timezone_info(self, mock_datetime):
        """Test that local_datetime returns timezone-aware datetime."""
        # Arrange
        mock_utc_time = datetime(2024, 6, 15, 20, 30, 45)
        mock_datetime.utcnow.return_value = mock_utc_time

        # Act
        result = local_datetime()

        # Assert
        assert result.tzinfo is not None
        assert isinstance(result.tzinfo, pytz.tzinfo.DstTzInfo)


class TestUtcDatetime:
    """Test utc_datetime function."""

    @patch("compliance_api.utils.datetime.datetime")
    def test_utc_datetime_returns_utc_time(self, mock_datetime):
        """Test that utc_datetime returns UTC timezone datetime."""
        # Arrange
        mock_utc_time = datetime(2024, 6, 15, 20, 30, 45)
        mock_datetime.utcnow.return_value = mock_utc_time

        # Act
        result = utc_datetime()

        # Assert
        assert result.tzinfo.zone == "UTC"
        assert result.hour == 20
        assert result.minute == 30
        assert result.second == 45

    @patch("compliance_api.utils.datetime.datetime")
    def test_utc_datetime_has_timezone_info(self, mock_datetime):
        """Test that utc_datetime returns timezone-aware datetime."""
        # Arrange
        mock_utc_time = datetime(2024, 6, 15, 20, 30, 45)
        mock_datetime.utcnow.return_value = mock_utc_time

        # Act
        result = utc_datetime()

        # Assert
        assert result.tzinfo is not None
        assert result.tzinfo == pytz.UTC


class TestConvertAndFormatToUtcStr:
    """Test convert_and_format_to_utc_str function."""

    def test_convert_and_format_to_utc_str_default_format(self, app):
        """Test conversion with default format."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"
            local_time = datetime(2024, 6, 15, 13, 30, 45)  # 1:30 PM PDT

            # Act
            result = convert_and_format_to_utc_str(local_time)

            # Assert
            # PDT is UTC-7, so 13:30 PDT = 20:30 UTC
            assert result == "2024-06-15 20:30:45"

    def test_convert_and_format_to_utc_str_custom_format(self, app):
        """Test conversion with custom format."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"
            local_time = datetime(2024, 6, 15, 13, 30, 45)
            custom_format = "%Y-%m-%d %H:%M"

            # Act
            result = convert_and_format_to_utc_str(local_time, custom_format)

            # Assert
            assert result == "2024-06-15 20:30"

    def test_convert_and_format_to_utc_str_timezone_override(self, app):
        """Test conversion with timezone override."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"
            local_time = datetime(2024, 6, 15, 13, 30, 45)
            timezone_override = "US/Eastern"

            # Act
            result = convert_and_format_to_utc_str(
                local_time, timezone_override=timezone_override
            )

            # Assert
            # EDT is UTC-4, so 13:30 EDT = 17:30 UTC
            assert result == "2024-06-15 17:30:45"

    def test_convert_and_format_to_utc_str_winter_time(self, app):
        """Test conversion during winter time (PST)."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"
            local_time = datetime(2024, 1, 15, 13, 30, 45)  # 1:30 PM PST

            # Act
            result = convert_and_format_to_utc_str(local_time)

            # Assert
            # PST is UTC-8, so 13:30 PST = 21:30 UTC
            assert result == "2024-01-15 21:30:45"

    def test_convert_and_format_to_utc_str_different_timezone(self, app):
        """Test conversion with different timezone."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Mountain"
            local_time = datetime(2024, 6, 15, 14, 30, 45)  # 2:30 PM MDT

            # Act
            result = convert_and_format_to_utc_str(local_time)

            # Assert
            # MDT is UTC-6, so 14:30 MDT = 20:30 UTC
            assert result == "2024-06-15 20:30:45"

    @pytest.mark.parametrize(
        "input_time,expected_utc",
        [
            (datetime(2024, 6, 15, 0, 0, 0), "2024-06-15 07:00:00"),  # Midnight PDT
            (datetime(2024, 6, 15, 12, 0, 0), "2024-06-15 19:00:00"),  # Noon PDT
            (
                datetime(2024, 6, 15, 23, 59, 59),
                "2024-06-16 06:59:59",
            ),  # End of day PDT
        ],
    )
    def test_convert_and_format_to_utc_str_various_times(
        self, app, input_time, expected_utc
    ):
        """Test conversion with various times of day."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"

            # Act
            result = convert_and_format_to_utc_str(input_time)

            # Assert
            assert result == expected_utc


class TestConvertToFullMonthFormat:
    """Test convert_to_full_month_format function."""

    def test_convert_to_full_month_format_basic(self):
        """Test basic month format conversion."""
        # Arrange
        test_date = datetime(2024, 6, 15, 13, 30, 45)

        # Act
        result = convert_to_full_month_format(test_date)

        # Assert
        assert result == "June 15, 2024"

    def test_convert_to_full_month_format_january(self):
        """Test month format conversion for January."""
        # Arrange
        test_date = datetime(2024, 1, 1, 0, 0, 0)

        # Act
        result = convert_to_full_month_format(test_date)

        # Assert
        assert result == "January 01, 2024"

    def test_convert_to_full_month_format_december(self):
        """Test month format conversion for December."""
        # Arrange
        test_date = datetime(2024, 12, 31, 23, 59, 59)

        # Act
        result = convert_to_full_month_format(test_date)

        # Assert
        assert result == "December 31, 2024"

    @pytest.mark.parametrize(
        "month,day,expected_month_name",
        [
            (1, 15, "January"),
            (2, 29, "February"),  # Leap year
            (3, 10, "March"),
            (4, 5, "April"),
            (5, 20, "May"),
            (6, 30, "June"),
            (7, 4, "July"),
            (8, 15, "August"),
            (9, 22, "September"),
            (10, 31, "October"),
            (11, 11, "November"),
            (12, 25, "December"),
        ],
    )
    def test_convert_to_full_month_format_all_months(
        self, month, day, expected_month_name
    ):
        """Test month format conversion for all months."""
        # Arrange
        test_date = datetime(2024, month, day, 12, 0, 0)

        # Act
        result = convert_to_full_month_format(test_date)

        # Assert
        assert result.startswith(expected_month_name)
        assert f"{day:02d}, 2024" in result

    def test_convert_to_full_month_format_different_years(self):
        """Test month format conversion for different years."""
        # Arrange
        test_cases = [
            (datetime(2020, 6, 15), "June 15, 2020"),
            (datetime(2023, 6, 15), "June 15, 2023"),
            (datetime(2025, 6, 15), "June 15, 2025"),
        ]

        for test_date, expected in test_cases:
            # Act
            result = convert_to_full_month_format(test_date)

            # Assert
            assert result == expected

    def test_convert_to_full_month_format_ignores_time(self):
        """Test that time components are ignored in month format conversion."""
        # Arrange
        test_cases = [
            datetime(2024, 6, 15, 0, 0, 0),
            datetime(2024, 6, 15, 12, 30, 45),
            datetime(2024, 6, 15, 23, 59, 59),
        ]

        for test_date in test_cases:
            # Act
            result = convert_to_full_month_format(test_date)

            # Assert
            assert result == "June 15, 2024"


class TestDatetimeUtilsIntegration:
    """Integration tests for datetime utilities."""

    def test_local_and_utc_datetime_consistency(self):
        """Test that local_datetime and utc_datetime are consistent."""
        # Act
        local_time = local_datetime()
        utc_time = utc_datetime()

        # Assert
        # Convert both to UTC for comparison
        local_time_utc = local_time.astimezone(pytz.UTC)

        # They should be within a few seconds of each other
        time_diff = abs((local_time_utc - utc_time).total_seconds())
        assert time_diff < 5  # Allow up to 5 seconds difference for execution time

    def test_convert_and_format_round_trip(self, app):
        """Test that conversion and formatting works correctly in round trip."""
        # Arrange
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"
            original_time = datetime(2024, 6, 15, 13, 30, 45)

            # Act
            utc_str = convert_and_format_to_utc_str(original_time)
            # Parse the UTC string back to datetime
            parsed_utc = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S")
            parsed_utc = pytz.UTC.localize(parsed_utc)

            # Convert back to Pacific time
            pacific_tz = pytz.timezone("US/Pacific")
            back_to_pacific = parsed_utc.astimezone(pacific_tz)

            # Assert
            # The time should match (ignoring timezone info for comparison)
            assert back_to_pacific.replace(tzinfo=None) == original_time

    def test_all_functions_with_edge_cases(self, app):
        """Test all functions with edge cases."""
        with app.app_context():
            app.config["LEGISLATIVE_TIMEZONE"] = "US/Pacific"

            # Test with leap year date
            leap_year_date = datetime(2024, 2, 29, 12, 0, 0)

            # All functions should handle leap year correctly
            utc_str = convert_and_format_to_utc_str(leap_year_date)
            full_month = convert_to_full_month_format(leap_year_date)

            assert "2024-02-29" in utc_str
            assert "February 29, 2024" == full_month
