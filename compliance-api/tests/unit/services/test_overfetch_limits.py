"""Tests for the pagination and export bounds added for COMP-932."""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from compliance_api.exceptions import UnprocessableEntityError
from compliance_api.services.inspection import _set_first_nation_names
from compliance_api.utils.constant import DEFAULT_PAGE_SIZE, MAX_EXPORT_ROWS, MAX_PAGE_SIZE
from compliance_api.utils.util import check_export_size, parse_pagination


class TestParsePagination:
    """parse_pagination is the only thing standing between request.args and the query."""

    def test_defaults_when_absent(self):
        """Missing parameters fall back to page 1 and the default page size."""
        assert parse_pagination({}) == (1, DEFAULT_PAGE_SIZE)

    def test_parses_strings(self):
        """Values arrive from request.args as strings."""
        assert parse_pagination({"page_no": "3", "page_size": "20"}) == (3, 20)

    def test_allows_the_maximum(self):
        """The cap itself is a valid request."""
        assert parse_pagination({"page_size": str(MAX_PAGE_SIZE)}) == (1, MAX_PAGE_SIZE)

    def test_rejects_above_the_maximum(self):
        """This is the defect the ticket reports: an unbounded page_size."""
        with pytest.raises(UnprocessableEntityError):
            parse_pagination({"page_size": str(MAX_PAGE_SIZE + 1)})

    @pytest.mark.parametrize("bad", ["abc", "", None, "1.5"])
    def test_rejects_non_numeric(self, bad):
        """Non-numeric input used to raise an uncaught ValueError (a 500)."""
        if bad in ("", None):
            # Empty means "not supplied" rather than invalid.
            assert parse_pagination({"page_size": bad}) == (1, DEFAULT_PAGE_SIZE)
        else:
            with pytest.raises(UnprocessableEntityError):
                parse_pagination({"page_size": bad})

    @pytest.mark.parametrize("bad", ["0", "-5"])
    def test_rejects_non_positive(self, bad):
        """Zero and negatives used to reach .limit() and .offset() directly."""
        with pytest.raises(UnprocessableEntityError):
            parse_pagination({"page_size": bad})
        with pytest.raises(UnprocessableEntityError):
            parse_pagination({"page_no": bad})


class TestCheckExportSize:
    """Exports build the whole workbook in memory, so the row count is bounded."""

    def test_allows_up_to_the_limit(self):
        """At the limit the export proceeds."""
        check_export_size(MAX_EXPORT_ROWS)

    def test_rejects_above_the_limit(self):
        """Above the limit nothing is built."""
        with pytest.raises(UnprocessableEntityError) as excinfo:
            check_export_size(MAX_EXPORT_ROWS + 1)
        assert str(MAX_EXPORT_ROWS) in str(excinfo.value)
        assert str(MAX_EXPORT_ROWS + 1) in str(excinfo.value)


class TestSetFirstNationNames:
    """One EPIC.track request per API request, not one per first nation."""

    @staticmethod
    def _nations(count):
        return [SimpleNamespace(firstnation_id=i) for i in range(1, count + 1)]

    @patch("compliance_api.services.inspection.TrackService")
    def test_resolves_all_names_in_one_request(self, track_service):
        """Five first nations used to mean five HTTP calls, each retried up to three times."""
        track_service.get_first_nations.return_value = [
            {"id": i, "name": f"Nation {i}"} for i in range(1, 6)
        ]

        result = _set_first_nation_names(self._nations(5))

        assert track_service.get_first_nations.call_count == 1
        assert track_service.get_first_nation_by_id.call_count == 0
        assert result == [{"id": i, "name": f"Nation {i}"} for i in range(1, 6)]

    @patch("compliance_api.services.inspection.TrackService")
    def test_makes_no_request_for_an_empty_list(self, track_service):
        """An inspection with no first nations should not call EPIC.track at all."""
        assert _set_first_nation_names([]) == []
        assert track_service.get_first_nations.call_count == 0

    @patch("compliance_api.services.inspection.TrackService")
    def test_unknown_id_yields_the_same_shape(self, track_service):
        """get_first_nations cannot 404 the way get_first_nation_by_id did."""
        track_service.get_first_nations.return_value = [{"id": 1, "name": "Nation 1"}]

        result = _set_first_nation_names(self._nations(2))

        assert result == [
            {"id": 1, "name": "Nation 1"},
            {"id": 2, "name": None},
        ]


class _FakeQuery:
    """Stands in for a query so the guard can be exercised without seeding rows."""

    def __init__(self, count):
        self._count = count
        self.all_called = False

    def count(self):
        return self._count

    def all(self):
        self.all_called = True
        return []


class TestExportsAreGuarded:
    """Every Excel export must check the row count before materializing it."""

    def test_inspections_export_rejects_oversized_result(self):
        """The guard runs before query.all(), so no workbook is built."""
        from compliance_api.services import inspection as inspection_service

        query = _FakeQuery(MAX_EXPORT_ROWS + 1)
        with patch.object(
            inspection_service, "_build_inspections_paginated_query", return_value=query
        ):
            with pytest.raises(UnprocessableEntityError):
                inspection_service.InspectionService.generate_inspections_excel({})
        assert query.all_called is False

    def test_complaints_export_rejects_oversized_result(self):
        """Same guard on the complaints export."""
        from compliance_api.services import complaint as complaint_service

        query = _FakeQuery(MAX_EXPORT_ROWS + 1)
        with patch.object(
            complaint_service, "_build_complaints_paginated_query", return_value=query
        ):
            with pytest.raises(UnprocessableEntityError):
                complaint_service.ComplaintService.generate_complaints_excel({})
        assert query.all_called is False

    def test_case_files_export_rejects_oversized_result(self):
        """The case file export was not named in the ticket but shares the defect."""
        from compliance_api.services import case_file as case_file_service

        query = _FakeQuery(MAX_EXPORT_ROWS + 1)
        with patch.object(
            case_file_service, "_build_base_query", return_value=query
        ), patch.object(
            case_file_service, "_apply_case_file_filters", return_value=query
        ), patch.object(
            case_file_service, "_apply_case_file_sorting", return_value=query
        ):
            with pytest.raises(UnprocessableEntityError):
                case_file_service.CaseFileService.generate_case_files_excel({})
        assert query.all_called is False

    def test_inspection_requirements_export_rejects_oversized_result(self):
        """The requirement grid fans out over enforcement documents, so it counts distinctly."""
        from compliance_api.services import inspection_requirement as requirement_service

        query = _FakeQuery(0)
        with patch.object(
            requirement_service,
            "_build_inspection_requirements_query",
            return_value=(query, MAX_EXPORT_ROWS + 1),
        ):
            with pytest.raises(UnprocessableEntityError):
                requirement_service.InspectionRequirementService.generate_inspection_requirements_excel({})
        assert query.all_called is False
