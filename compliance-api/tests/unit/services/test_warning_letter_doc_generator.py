"""Tests for the Warning Letter DOCX generator."""

import copy
from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from compliance_api.services.inspection_record.docx_utils import _add_continuation_marker
from compliance_api.services.warning_letter.warning_letter_doc_generator import generate_warning_letter_docx
from compliance_api.services.warning_letter.warning_letter_template_constant import WARNING_LETTER_CONTENT


WL_DATA = {
    "warning_letter": {
        "warning_letter_number": "WL-2026-007",
        "issue_date": "2026-11-17",
        "content": (
            '<p class="editor-paragraph" style="text-align: left;">Dear holder,</p>'
            "<ul><li>Point one</li></ul>"
            "<table><tr><td><p>T1</p></td></tr></table>"
        ),
    },
    "officer_details": {
        "officer_name": "Pat Officer",
        "officer_position": "Compliance Officer",
    },
    "department_details": {
        "office_name": "Environmental Assessment Office",
        "office_branch": "Compliance and Enforcement Branch",
        "signature_branch": "Compliance and Enforcement",
        "address_line1": "PO Box 9426 Stn Prov Govt",
        "address_line2": "Victoria BC V8W 9V1",
    },
}


def build(data=None):
    """Generate the warning letter and reopen it from bytes, as a downloader would."""
    stream = BytesIO()
    generate_warning_letter_docx(data or WL_DATA).save(stream)
    stream.seek(0)
    return Document(stream)


def test_page_setup():
    """Page size, margins and font mirror the warning letter template."""
    doc = build()
    section = doc.sections[0]
    assert (section.page_width, section.page_height) == (Inches(8.5), Inches(11))
    assert section.left_margin == Inches(1)
    assert section.right_margin == Inches(1)
    assert section.top_margin == Inches(0.5)
    assert section.bottom_margin == Inches(1.25)
    assert section.different_first_page_header_footer is True
    assert doc.styles["Normal"].font.name == "Calibri"
    assert doc.styles["Normal"].font.size == Pt(13.5)
    assert doc.styles["Normal"].paragraph_format.line_spacing == Pt(15)


def test_logo_is_first_and_centred():
    """The BC logo opens the letter, centred."""
    doc = build()
    first = doc.paragraphs[0]
    assert first.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert "pic:pic" in first._p.xml
    assert len(doc.inline_shapes) == 1


def test_reference_line():
    """The reference is right-aligned, italic and small."""
    para = next(p for p in build().paragraphs if p.text == "Ref: WL-2026-007")
    assert para.alignment == WD_ALIGN_PARAGRAPH.RIGHT
    assert para.runs[0].italic
    assert para.runs[0].font.size == Pt(8.5)


def test_body_order():
    """Body sections follow the same order as the HTML template."""
    text = "\n".join(p.text for p in build().paragraphs)
    expected = [
        "Ref: WL-2026-007",
        "2026-11-17",
        "Dear holder,",
        "Point one",
        "Sincerely,",
        "Pat Officer",
        "Compliance Officer",
        "Compliance and Enforcement",
        "Environmental Assessment Office",
    ]
    positions = [text.index(s) for s in expected]
    assert positions == sorted(positions)


def test_three_blank_lines_between_sincerely_and_name():
    """Room is left for the signature this change exists to allow."""
    paras = [p.text for p in build().paragraphs]
    i = paras.index("Sincerely,")
    assert paras[i + 1:i + 5] == ["", "", "", "Pat Officer"]


def test_content_table_rendered():
    """Tables inside the letter content are kept."""
    assert build().tables[0].cell(0, 0).text == "T1"


def test_first_page_footer():
    """Page one carries the office footer and a continuation marker."""
    footer = build().sections[0].first_page_footer
    cells = footer.tables[0].rows[0].cells
    assert cells[0].text == "Environmental Assessment Office"
    assert cells[0].paragraphs[0].runs[0].bold
    assert cells[1].text == "Compliance and Enforcement Branch"
    assert cells[2].text == "Mailing Address:\nPO Box 9426 Stn Prov Govt\nVictoria BC V8W 9V1"
    assert cells[2].paragraphs[0].runs[0].font.size == Pt(8.5)
    assert 'w:top w:val="single"' in cells[0]._tc.xml
    assert "NUMPAGES" in footer._element.xml


def test_later_pages_header_and_footer():
    """Pages after the first get a centred page number and a continuation marker."""
    section = build().sections[0]
    assert section.first_page_header.paragraphs[0].text == ""
    header = section.header.paragraphs[0]
    assert header.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert "PAGE" in header._p.xml
    assert header.text.replace(" ", "") == "--"
    assert header.runs[0].font.size == Pt(10)
    assert "NUMPAGES" in section.footer._element.xml
    assert section.footer.paragraphs[0].alignment == WD_ALIGN_PARAGRAPH.RIGHT
    assert not section.footer.tables


def test_missing_values_never_print_none():
    """A draft letter with no date, content or address still renders its fixed parts."""
    data = copy.deepcopy(WL_DATA)
    data["warning_letter"].update(issue_date=None, content=None)
    data["department_details"].update(address_line1=None, address_line2=None)
    doc = build(data)
    text = "\n".join(p.text for p in doc.paragraphs)
    footer_text = "\n".join(c.text for c in doc.sections[0].first_page_footer.tables[0].rows[0].cells)
    assert "None" not in text
    assert "None" not in footer_text
    assert "Sincerely," in text
    assert "Mailing Address:" in footer_text


def test_continuation_marker_field_structure():
    """The marker is one IF field wrapping PAGE, NUMPAGES and a PAGE + 1 expression."""
    para = Document().add_paragraph()
    _add_continuation_marker(para)
    xml = para._p.xml
    assert xml.count('w:fldCharType="begin"') == 5
    assert xml.count('w:fldCharType="end"') == 5
    assert xml.count('w:fldCharType="separate"') == 1
    instructions = "".join(t.text for t in para._p.iter() if t.tag.endswith("}instrText"))
    assert instructions.replace(" ", "") == 'IFPAGE<NUMPAGES"...=PAGE+1"""'


def test_wrapped_source_text_does_not_become_line_breaks():
    """The default letter content is wrapped in its source; the letter must not be."""
    data = copy.deepcopy(WL_DATA)
    data["warning_letter"]["content"] = '<p dir="ltr">\n    On a date,\n     the officer inspected.</p>'
    assert any(p.text == "On a date, the officer inspected." for p in build(data).paragraphs)


def test_content_table_fits_between_the_margins():
    """Tables in the letter stay inside the 6.5in text width."""
    tbl_w = build().tables[0]._element.tblPr.findall(qn("w:tblW"))[-1]
    assert int(tbl_w.get(qn("w:w"))) / 1440 <= 6.5


def test_first_page_footer_columns_are_padded_apart():
    """Footer columns keep a gap so neighbouring text does not run together."""
    cells = build().sections[0].first_page_footer.tables[0].rows[0].cells
    for cell in cells[:2]:
        right = cell._tc.tcPr.find(qn("w:tcMar")).find(qn("w:right"))
        assert int(right.get(qn("w:w"))) >= 180


def test_default_letter_content_keeps_the_address_block():
    """The recipient block of the default content sits in a <div> and must survive."""
    data = copy.deepcopy(WL_DATA)
    data["warning_letter"]["content"] = WARNING_LETTER_CONTENT
    paras = [p.text for p in build(data).paragraphs]
    start = paras.index("SENT VIA EMAIL")
    end = paras.index("Dear [NAME],")
    block = [text for text in paras[start + 1:end] if text]
    assert block == ["NAME", "TITLE", "COMPANY", "ADDRESS", "CITY PROVINCE POSTAL CODE"]


def test_struck_text_stays_struck():
    """Struck-through wording must not read as live text in a signed letter."""
    data = copy.deepcopy(WL_DATA)
    data["warning_letter"]["content"] = "<p>keep <s>removed</s> this</p><ul><li><s>gone</s> stays</li></ul>"
    runs = {r.text.strip(): r for p in build(data).paragraphs for r in p.runs if r.text.strip()}
    assert runs["removed"].font.strike is True
    assert runs["gone"].font.strike is True
    assert not runs["keep"].font.strike
    assert not runs["stays"].font.strike


def test_first_page_footer_ends_with_a_paragraph():
    """Word expects a paragraph after a table that closes a footer."""
    footer = build().sections[0].first_page_footer._element
    assert footer[-1].tag == qn("w:p")


def test_logo_is_cropped_to_the_template_header_height():
    """The 1.875in logo shows through a 1.25in band, as the template's 120px container does."""
    doc = build()
    shape = doc.inline_shapes[0]
    assert shape.height == Inches(1.25)
    src_rect = doc.paragraphs[0]._p.find(".//" + qn("a:srcRect"))
    assert src_rect.get("t") == "16667"
    assert src_rect.get("b") == "16667"


def test_later_pages_start_where_the_pdf_does():
    """Header sits high and pushes body text to the template's 0.75in top margin."""
    doc = build()
    section = doc.sections[0]
    header = section.header.paragraphs[0]
    assert abs(section.header_distance - Inches(0.28)) < 635  # stored in twips
    assert header.paragraph_format.space_after == Pt(21)
    assert doc.styles["Header"].font.size == Pt(10)


def test_footers_sit_where_the_pdf_puts_them():
    """Footer distance places the page-one rule and later-page marker as in the PDF."""
    section = build().sections[0]
    assert section.footer_distance == Inches(0.375)
    assert section.footer.paragraphs[0].paragraph_format.space_after == Pt(10.5)


def test_first_page_marker_is_a_fixed_two():
    """Page one always continues onto page two, so its marker needs only a page count check."""
    footer = build().sections[0].first_page_footer
    instructions = "".join(t.text for t in footer._element.iter() if t.tag.endswith("}instrText"))
    assert instructions.replace(" ", "") == 'IFNUMPAGES>1"...2"""'


def test_reference_line_is_pulled_up_like_the_template():
    """.com-ref has a negative top margin; a tighter line stands in for it."""
    para = next(p for p in build().paragraphs if p.text == "Ref: WL-2026-007")
    assert para.paragraph_format.line_spacing == Pt(11)
