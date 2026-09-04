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
from datetime import datetime, timedelta

import pytest
import pytz

from compliance_api.utils.datetime import BC_TIMEZONE, convert_to_full_month_format


class TestBritishColumbiaTimezone:
    """Test that BC local time is used, not a US Pacific stand-in.

    From 2026-11-01 BC stays on UTC-7 year-round while the US Pacific zones keep
    falling back to UTC-8, so the two are an hour apart from November to March.
    """

    def test_bc_timezone_is_vancouver(self):
        """Test that the shared constant points at the BC zone."""
        assert str(BC_TIMEZONE) == "America/Vancouver"

    @pytest.mark.parametrize(
        "winter_moment",
        [
            datetime(2026, 12, 15, 12, 0, 0),
            datetime(2027, 1, 15, 12, 0, 0),
            datetime(2027, 3, 1, 12, 0, 0),
        ],
    )
    def test_bc_stays_on_utc_minus_7_after_permanent_dst(self, winter_moment):
        """Test that BC winter time is UTC-7 once permanent DST is in effect."""
        offset = winter_moment.replace(tzinfo=BC_TIMEZONE).utcoffset()

        assert offset == timedelta(hours=-7)

    def test_bc_keeps_dst_rules_before_the_change(self):
        """Test that pre-2026 winters are still UTC-8."""
        offset = datetime(2024, 1, 15, 12, 0, 0).replace(tzinfo=BC_TIMEZONE).utcoffset()

        assert offset == timedelta(hours=-8)

    def test_bc_differs_from_us_pacific_in_winter(self):
        """Test that the tz database in use actually carries the BC rule."""
        winter_moment = datetime(2026, 12, 15, 12, 0, 0)

        bc_offset = winter_moment.replace(tzinfo=BC_TIMEZONE).utcoffset()
        us_offset = pytz.timezone("US/Pacific").localize(winter_moment).utcoffset()

        assert bc_offset - us_offset == timedelta(hours=1)

    def test_utc_timestamp_converts_to_bc_local_in_winter(self):
        """Test the conversion the report generators actually perform."""
        # 2026-11-16 03:00Z is 2026-11-15 20:00 BC local under permanent DST
        utc_moment = datetime(2026, 11, 16, 3, 0, 0, tzinfo=pytz.UTC)

        local = utc_moment.astimezone(BC_TIMEZONE)

        assert local.strftime("%Y-%m-%d %H:%M") == "2026-11-15 20:00"


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
