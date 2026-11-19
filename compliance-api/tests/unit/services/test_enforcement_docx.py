"""Tests for the rich-text styling shared by the Order and Warning Letter DOCX generators."""

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from compliance_api.services.enforcement_docx import add_rich_text
from compliance_api.services.inspection_record.html_to_docx import _add_html_to_container, init_list_numbering


def _doc():
    """Return a letter document with 1in side margins and list numbering ready."""
    doc = Document()
    init_list_numbering(doc)
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    return doc


def _twips(element, tag, attr="w:w"):
    return int(element.find(qn(tag)).get(qn(attr)))


def _col_widths_inches(table):
    return [round(_twips(cell._tc.tcPr, "w:tcW") / 1440, 2) for cell in table.rows[0].cells]


def test_link_becomes_a_real_hyperlink_without_stray_spaces():
    """An <a> renders as a clickable link and its inner padding is not doubled."""
    doc = _doc()
    add_rich_text(doc, '<p>email at <a href="mailto:a@b.ca"> a@b.ca </a> if needed</p>')
    para = next(p for p in doc.paragraphs if p.text)
    assert para.text == "email at a@b.ca if needed"
    link = para._p.find(qn("w:hyperlink"))
    assert link is not None
    rel = para.part.rels[link.get(qn("r:id"))]
    assert rel.target_ref == "mailto:a@b.ca"


def test_link_inside_list_item_is_a_hyperlink():
    """Links in list items are links too."""
    doc = _doc()
    add_rich_text(doc, '<ul><li>see <a href="https://example.com">the site</a> now</li></ul>')
    para = next(p for p in doc.paragraphs if p.text)
    assert para.text == "see the site now"
    assert para._p.find(qn("w:hyperlink")) is not None


def test_plain_converter_still_renders_links_as_text():
    """Without the styling layer (the Inspection Record path) links stay plain text."""
    doc = _doc()
    _add_html_to_container(doc, '<p>at <a href="mailto:a@b.ca">a@b.ca</a> ok</p>', clear_first=False)
    para = next(p for p in doc.paragraphs if p.text)
    assert para._p.find(qn("w:hyperlink")) is None


def test_table_uses_source_column_widths():
    """Column widths set by the editor carry over (96px = 1in)."""
    doc = _doc()
    add_rich_text(doc, (
        '<table style="width: 288px"><colgroup><col style="width: 96px"><col style="width: 192px"></colgroup>'
        "<tr><td><p>A</p></td><td><p>B</p></td></tr></table>"
    ))
    assert _col_widths_inches(doc.tables[0]) == [1.0, 2.0]


def test_table_without_widths_shrinks_to_its_content():
    """A table with no widths is sized to its text, like the PDF, not stretched to the page."""
    doc = _doc()
    add_rich_text(doc, (
        "<table><tr><th><p>Item</p></th><th><p>Due</p></th></tr>"
        "<tr><td><p>Report</p></td><td><p>2026-12-01</p></td></tr></table>"
    ))
    widths = _col_widths_inches(doc.tables[0])
    assert 0.4 <= widths[0] <= 0.6
    assert 0.6 <= widths[1] <= 0.85
    assert widths[0] < widths[1]


def test_wide_table_is_capped_at_the_template_maximum():
    """The template caps editor tables at 5.5in in print."""
    doc = _doc()
    add_rich_text(doc, (
        '<table><colgroup><col style="width: 400px"><col style="width: 400px"></colgroup>'
        "<tr><td><p>A</p></td><td><p>B</p></td></tr></table>"
    ))
    assert _col_widths_inches(doc.tables[0]) == [2.75, 2.75]


def test_table_cells_match_the_template_cell_style():
    """Cells are 9pt (12px) on a 12pt line with 4px/6px padding; header cells are shaded."""
    doc = _doc()
    add_rich_text(doc, (
        "<table><tr><th><p>Item</p></th></tr><tr><td><p>Report</p></td></tr></table>"
    ))
    table = doc.tables[0]
    header, body = table.cell(0, 0), table.cell(1, 0)
    for cell in (header, body):
        para = cell.paragraphs[0]
        assert para.runs[0].font.size == Pt(9)
        assert para.paragraph_format.line_spacing == Pt(12)
        margins = cell._tc.tcPr.find(qn("w:tcMar"))
        assert _twips(margins, "w:top") == 60
        assert _twips(margins, "w:left") == 90
    assert header._tc.tcPr.find(qn("w:shd")).get(qn("w:fill")) == "F2F3F5"
    assert body._tc.tcPr.find(qn("w:shd")) is None
    assert header.paragraphs[0].runs[0].bold


def test_table_keeps_a_gap_from_the_text_around_it():
    """The template gives tables a 10px (7.5pt) margin above and below."""
    doc = _doc()
    add_rich_text(doc, "<p>Before</p><table><tr><td><p>A</p></td></tr></table><p>After</p>")
    before = next(p for p in doc.paragraphs if p.text == "Before")
    after = next(p for p in doc.paragraphs if p.text == "After")
    assert before.paragraph_format.space_after == Pt(7.5)
    assert after.paragraph_format.space_before == Pt(7.5)


def _marker_and_text_position(para):
    """Return where a list item's marker and its text start, in inches from the margin."""
    fmt = para.paragraph_format
    return (
        round((fmt.left_indent + fmt.first_line_indent) / 914400, 2),
        round(fmt.left_indent / 914400, 2),
    )


def _para(doc, text):
    return next(p for p in doc.paragraphs if p.text == text)


EDITOR_LIST = (
    '<ol class="editor-list-ol editor-list-ol1"><li class="editor-listitem">One</li>'
    '<li class="editor-listitem editor-nested-listitem"><ol class="editor-list-ol editor-list-ol2">'
    '<li class="editor-listitem">Nested</li></ol></li>'
    '<li class="editor-listitem">Two</li></ol><p>After</p>'
)


def test_editor_numbered_list_matches_the_template_counters():
    """Editor lists number inline: 1/4in in, a further 1/4in per level, text right after."""
    doc = _doc()
    add_rich_text(doc, EDITOR_LIST)
    assert _marker_and_text_position(_para(doc, "One")) == (0.25, 0.44)
    assert _marker_and_text_position(_para(doc, "Nested")) == (0.5, 0.69)


def test_default_content_numbered_list_hangs_its_numbers():
    """A list without the editor depth class keeps native markers: text 1/3in in, number hanging."""
    doc = _doc()
    add_rich_text(doc, '<ol class="editor-list-ol"><li class="editor-listitem">One</li></ol>')
    assert _marker_and_text_position(_para(doc, "One")) == (0.14, 0.33)


def test_mixed_lists_each_keep_their_own_style():
    """Consecutive lists are styled by their own markup, not their neighbour's."""
    doc = _doc()
    add_rich_text(doc, (
        '<ol class="editor-list-ol"><li>Plain</li></ol>' + EDITOR_LIST
        + '<ul class="editor-list-ul"><li class="editor-listitem">Dot</li></ul>'
    ))
    assert _marker_and_text_position(_para(doc, "Plain")) == (0.14, 0.33)
    assert _marker_and_text_position(_para(doc, "One")) == (0.25, 0.44)
    assert _marker_and_text_position(_para(doc, "Dot")) == (0.19, 0.33)


def test_list_items_are_three_points_apart():
    """.editor-listitem has a 0.25rem margin above and below."""
    doc = _doc()
    add_rich_text(doc, EDITOR_LIST)
    assert _para(doc, "One").paragraph_format.space_before == Pt(3)
    assert not _para(doc, "One").paragraph_format.space_after
    assert _para(doc, "Two").paragraph_format.space_after == Pt(3)


def test_table_after_a_list_keeps_its_gap():
    """The table margin wins over the list item's smaller one."""
    doc = _doc()
    add_rich_text(doc, "<ul><li>Dot</li></ul><table><tr><td><p>A</p></td></tr></table>")
    assert _para(doc, "Dot").paragraph_format.space_after == Pt(7.5)


def test_empty_rich_text_adds_nothing():
    """Missing content is skipped."""
    doc = _doc()
    before = len(doc.paragraphs)
    add_rich_text(doc, None)
    add_rich_text(doc, "")
    assert len(doc.paragraphs) == before


def test_link_inside_table_cell_is_a_hyperlink_at_the_cell_font_size():
    """A link in a table cell is clickable and sized like the rest of the cell."""
    doc = _doc()
    add_rich_text(doc, '<table><tr><td><p>see <a href="https://x.y"><span>LINK</span></a> now</p></td></tr></table>')
    para = doc.tables[0].cell(0, 0).paragraphs[0]
    link = para._p.find(qn("w:hyperlink"))
    assert link is not None
    assert "".join(t.text for t in para._p.iter(qn("w:t"))) == "see LINK now"
    size = link.find(qn("w:r")).find(qn("w:rPr")).find(qn("w:sz"))
    assert size is not None and size.get(qn("w:val")) == "18"


def test_formatted_words_do_not_narrow_a_content_sized_column():
    """Inline formatting inside a cell must not change the width worked out for its column."""
    plain, formatted = _doc(), _doc()
    add_rich_text(plain, "<table><tr><td><p>UNDER plain STRUCK words here</p></td></tr></table>")
    add_rich_text(
        formatted,
        "<table><tr><td><p><u><span>UNDER</span></u> plain <s><span>STRUCK</span></s> "
        "<strong>words</strong> here</p></td></tr></table>",
    )
    assert _col_widths_inches(formatted.tables[0]) == _col_widths_inches(plain.tables[0])


def test_line_breaks_still_bound_the_content_sized_column():
    """A <br> splits a cell into lines, and the column fits the longest one."""
    one_line, two_lines = _doc(), _doc()
    add_rich_text(one_line, "<table><tr><td><p>a much longer second line</p></td></tr></table>")
    add_rich_text(two_lines, "<table><tr><td><p>short<br>a much longer second line</p></td></tr></table>")
    assert _col_widths_inches(two_lines.tables[0]) == _col_widths_inches(one_line.tables[0])
