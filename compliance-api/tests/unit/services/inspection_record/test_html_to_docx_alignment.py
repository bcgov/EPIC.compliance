"""Tests for alignment, underline and paragraph-level bold in html_to_docx."""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches

from compliance_api.services.inspection_record.html_to_docx import _add_html_to_container, collapse_html_newlines


def _render(html):
    """Render html into a fresh document and return its non-empty paragraphs."""
    doc = Document()
    _add_html_to_container(doc, html, clear_first=False)
    return [p for p in doc.paragraphs if p.text]


def test_center_alignment_is_applied():
    """A centred paragraph is centred in the document."""
    paras = _render('<p style="text-align: center;">Title</p>')
    assert paras[0].alignment == WD_ALIGN_PARAGRAPH.CENTER


def test_right_and_justify_alignment_are_applied():
    """Right and justify alignments map to their Word equivalents."""
    paras = _render('<p style="text-align: right;">R</p><p style="text-align: justify;">J</p>')
    assert paras[0].alignment == WD_ALIGN_PARAGRAPH.RIGHT
    assert paras[1].alignment == WD_ALIGN_PARAGRAPH.JUSTIFY


def test_left_alignment_leaves_paragraph_untouched():
    """Left alignment is the default and must not be written explicitly."""
    paras = _render('<p style="text-align: left;">Body</p><p>Plain</p>')
    assert paras[0].alignment is None
    assert paras[1].alignment is None


def test_alignment_applies_to_formatted_paragraph_and_its_br_continuations():
    """Paragraphs created for a <br> keep the alignment of their source paragraph."""
    paras = _render('<p style="text-align: center;"><strong>One</strong><br>Two</p>')
    assert [p.alignment for p in paras] == [WD_ALIGN_PARAGRAPH.CENTER] * 2


def test_underline_run():
    """Only the text inside <u> is underlined."""
    paras = _render('<p>a <u>under</u> b</p>')
    under = [r for r in paras[0].runs if r.text.strip() == "under"][0]
    assert under.underline is True
    assert all(not r.underline for r in paras[0].runs if r.text.strip() != "under")


def test_underline_inside_list_item():
    """Underline is honoured inside list items."""
    doc = Document()
    _add_html_to_container(doc, '<ul><li><u>item</u></li></ul>', clear_first=False)
    runs = [r for p in doc.paragraphs for r in p.runs if r.text.strip() == "item"]
    assert runs and runs[0].underline is True


def test_paragraph_level_bold_style():
    """font-weight: bold on the paragraph makes every run bold."""
    paras = _render('<p style="text-align: center;font-weight: bold">ORDER<br><u>UNDER SECTION 53</u></p>')
    assert len(paras) == 2
    assert all(r.bold for p in paras for r in p.runs if r.text.strip())
    assert paras[1].runs[0].underline is True


def test_paragraph_level_bold_on_plain_text():
    """Paragraph-level bold applies when the paragraph has no inline tags."""
    paras = _render('<p style="font-weight: 700">Heavy</p><p style="font-weight: 400">Light</p>')
    assert paras[0].runs[0].bold is True
    assert not paras[1].runs[0].bold


def test_first_empty_paragraph_path_honours_alignment():
    """The reuse-first-paragraph path applies alignment too."""
    doc = Document()
    doc.add_paragraph()
    _add_html_to_container(doc, '<p style="text-align: center;">Title</p>', clear_first=True)
    assert doc.paragraphs[0].text == "Title"
    assert doc.paragraphs[0].alignment == WD_ALIGN_PARAGRAPH.CENTER


TABLE_HTML = "<table><tr><td><p>A</p></td><td><p>B</p></td></tr></table>"


def _table_width_inches(doc):
    """Return the width the converter set on the first table, in inches (it appends its own tblW)."""
    tbl_w = doc.tables[0]._element.tblPr.findall(qn("w:tblW"))[-1]
    return int(tbl_w.get(qn("w:w"))) / 1440


def test_document_table_fits_between_the_margins():
    """A table added to a document is sized to that document's text width."""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    _add_html_to_container(doc, TABLE_HTML, clear_first=False)
    assert abs(_table_width_inches(doc) - 6.34) < 0.01


def test_inspection_record_table_width_is_unchanged():
    """With the Inspection Record margins the table keeps its 7.09in width."""
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.5)
    _add_html_to_container(doc, TABLE_HTML, clear_first=False)
    assert abs(_table_width_inches(doc) - 7.09) < 0.01


def test_collapse_html_newlines_joins_wrapped_source_text():
    """Source line wrapping inside a paragraph is not a line break."""
    html = '<p class="x"\n   dir="ltr">\n    On a date,\n     the officer</p>\n<p>Next</p>'
    doc = Document()
    _add_html_to_container(doc, collapse_html_newlines(html), clear_first=False)
    assert [p.text for p in doc.paragraphs if p.text] == ["On a date, the officer", "Next"]


def test_collapse_html_newlines_handles_empty_values():
    """Missing rich text passes straight through."""
    assert collapse_html_newlines(None) is None
    assert collapse_html_newlines("") == ""


def _cell_text(cell_html):
    """Render a one-cell table and return the text of that cell."""
    doc = Document()
    _add_html_to_container(doc, f"<table><tr><td>{cell_html}</td></tr></table>", clear_first=False)
    return doc.tables[0].cell(0, 0).text


def test_table_cell_keeps_underlined_struck_and_linked_text():
    """Text the editor wraps in <u>, <s> or <a> inside a table cell must not be dropped."""
    text = _cell_text(
        '<p><u><span>UNDER</span></u> plain <s><span>STRUCK</span></s> '
        '<a href="https://x.y"><span>LINK</span></a> <span>sp</span></p>'
    )
    assert text == "UNDER plain STRUCK LINK sp"


def test_table_cell_keeps_text_in_nested_inline_tags():
    """Unknown inline wrappers around or inside known ones keep their text."""
    assert _cell_text("<p><u><strong>Bold under</strong></u> <strong><s>bold struck</s></strong> <sub>x</sub></p>") == (
        "Bold under bold struck x"
    )


def _cell_runs(cell_html):
    """Render a one-cell table and return the runs of its first paragraph, keyed by stripped text."""
    doc = Document()
    _add_html_to_container(doc, f"<table><tr><td>{cell_html}</td></tr></table>", clear_first=False)
    return {r.text.strip(): r for r in doc.tables[0].cell(0, 0).paragraphs[0].runs}


def test_table_cell_underline_and_strikethrough_are_applied():
    """Underline and strikethrough inside a table cell format only their own text."""
    runs = _cell_runs("<p><u><span>UNDER</span></u> plain <s><span>STRUCK</span></s></p>")
    assert runs["UNDER"].underline is True and not runs["UNDER"].font.strike
    assert runs["STRUCK"].font.strike is True and not runs["STRUCK"].underline
    assert not runs["plain"].underline and not runs["plain"].font.strike


def test_table_cell_combines_underline_and_strike_with_bold():
    """Nested formatting inside a table cell is all kept."""
    runs = _cell_runs("<p><u><strong>Both</strong></u> <strong><s>Struck</s></strong></p>")
    assert runs["Both"].bold and runs["Both"].underline
    assert runs["Struck"].bold and runs["Struck"].font.strike


def test_table_cell_link_stays_plain_text_unless_opted_in():
    """The Inspection Record path keeps links in cells as plain text."""
    doc = Document()
    _add_html_to_container(
        doc, '<table><tr><td><p>see <a href="https://x.y">LINK</a></p></td></tr></table>', clear_first=False
    )
    para = doc.tables[0].cell(0, 0).paragraphs[0]
    assert para.text == "see LINK"
    assert para._p.find(qn("w:hyperlink")) is None
