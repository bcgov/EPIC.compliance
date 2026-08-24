"""Tests for the inspection summary spacing applied before rendering an inspection record."""
from compliance_api.services.inspection_record.inspection_record import (
    BLANK_PARAGRAPH, _add_gap_before_finding_statement)


FINDING_STATEMENT = (
    '<p class="editor-paragraph" dir="ltr">'
    "<span>Additional detail regarding these findings may be found in the sections below.</span></p>"
)
SCOPE_WITH_BLANK = (
    '<p class="editor-paragraph" dir="ltr"><span>The Officer inspected the site.</span></p>'
    f"{BLANK_PARAGRAPH}"
)
SCOPE_WITHOUT_BLANK = (
    '<p class="editor-paragraph" dir="ltr"><span>The Officer inspected the site.</span></p>'
)
PRELIMINARY_WITHOUT_BLANK = (
    '<div><p class="editor-paragraph" dir="ltr"><span>On August 21, 2026, Officer Chapman provided the '
    "preliminary inspection record to the Regulated Party.</span></p></div>"
)


class TestAddGapBeforeFindingStatement:
    """Tests for _add_gap_before_finding_statement function."""

    def test_gap_added_when_preceding_block_ends_with_text(self):
        """Test that a blank paragraph is added when the block above ends with text."""
        preview_data = {
            "inspection_scope": SCOPE_WITHOUT_BLANK,
            "finding_statement": FINDING_STATEMENT,
        }

        _add_gap_before_finding_statement(preview_data)

        assert preview_data["finding_statement"] == BLANK_PARAGRAPH + FINDING_STATEMENT

    def test_gap_added_when_edited_preliminary_review_details_ends_with_text(self):
        """Test that an edited preliminary review details block gets a gap after it."""
        preview_data = {
            "inspection_scope": SCOPE_WITH_BLANK,
            "preliminary_review_details": PRELIMINARY_WITHOUT_BLANK,
            "finding_statement": FINDING_STATEMENT,
        }

        _add_gap_before_finding_statement(preview_data)

        assert preview_data["finding_statement"] == BLANK_PARAGRAPH + FINDING_STATEMENT

    def test_no_gap_added_when_preceding_block_ends_blank(self):
        """Test that no gap is added when the block above already ends with a blank paragraph."""
        preview_data = {
            "inspection_scope": SCOPE_WITH_BLANK,
            "finding_statement": FINDING_STATEMENT,
        }

        _add_gap_before_finding_statement(preview_data)

        assert preview_data["finding_statement"] == FINDING_STATEMENT

    def test_preliminary_review_details_takes_precedence_over_scope(self):
        """Test that the block directly above the finding statement is the one inspected."""
        preview_data = {
            "inspection_scope": SCOPE_WITHOUT_BLANK,
            "preliminary_review_details": f"{PRELIMINARY_WITHOUT_BLANK}{BLANK_PARAGRAPH}",
            "finding_statement": FINDING_STATEMENT,
        }

        _add_gap_before_finding_statement(preview_data)

        assert preview_data["finding_statement"] == FINDING_STATEMENT

    def test_no_gap_added_when_finding_statement_already_starts_blank(self):
        """Test that an edited finding statement providing its own gap is left alone."""
        finding_statement = BLANK_PARAGRAPH + FINDING_STATEMENT
        preview_data = {
            "inspection_scope": SCOPE_WITHOUT_BLANK,
            "finding_statement": finding_statement,
        }

        _add_gap_before_finding_statement(preview_data)

        assert preview_data["finding_statement"] == finding_statement

    def test_no_finding_statement_is_a_no_op(self):
        """Test that preview data without a finding statement is left untouched."""
        preview_data = {"inspection_scope": SCOPE_WITHOUT_BLANK}

        _add_gap_before_finding_statement(preview_data)

        assert preview_data == {"inspection_scope": SCOPE_WITHOUT_BLANK}

    def test_no_preceding_block_is_a_no_op(self):
        """Test that a finding statement with nothing above it is left untouched."""
        preview_data = {"finding_statement": FINDING_STATEMENT}

        _add_gap_before_finding_statement(preview_data)

        assert preview_data["finding_statement"] == FINDING_STATEMENT
