"""Tests for the Order DOCX generator."""

import copy
from io import BytesIO

from bs4 import BeautifulSoup
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from compliance_api.services.order.order_doc_generator import generate_order_docx
from compliance_api.services.order.order_template_constant import NOW_THEREFORE, WHERE_AS


ORDER_DATA = {
    "order_details": {
        "order_number": "EAO-2026-001",
        "where_as": (
            '<p style="text-align: center;font-weight: bold">ORDER<br><u>ORDER UNDER SECTION 53</u></p>'
            '<p class="editor-paragraph">WHEREAS the holder did a thing.</p>'
        ),
        "now_therefore": (
            "<ol><li>Stop the thing.<ol><li>Nested step.</li></ol></li></ol>"
            "<table><tr><td><p>Cell A</p></td><td><p>Cell B</p></td></tr></table>"
        ),
        "issued_date": "2026-11-17",
    },
    "officer_details": {
        "officer_name": "Pat Officer",
        "officer_position": "Compliance Officer",
    },
    "department_details": {
        "signature_branch": "Compliance and Enforcement Branch",
        "office_name": "Environmental Assessment Office",
    },
}


def build(data=None):
    """Generate the order and reopen it from bytes, as a downloader would."""
    stream = BytesIO()
    generate_order_docx(data or ORDER_DATA).save(stream)
    stream.seek(0)
    return Document(stream)


def test_page_setup():
    """Page size, margins, font and line spacing mirror the order template."""
    doc = build()
    section = doc.sections[0]
    assert (section.page_width, section.page_height) == (Inches(8.5), Inches(11))
    assert section.top_margin == Inches(0.75)
    assert section.bottom_margin == Inches(0.875)
    assert section.left_margin == Inches(0.95)
    assert section.right_margin == Inches(0.95)
    normal = doc.styles["Normal"]
    assert normal.font.name == "Calibri"
    assert normal.font.size == Pt(13.5)
    assert normal.paragraph_format.line_spacing == Pt(15)
    assert normal.paragraph_format.line_spacing_rule == WD_LINE_SPACING.EXACTLY


def test_sections_appear_in_template_order():
    """Body sections follow the same order as the HTML template."""
    text = "\n".join(p.text for p in build().paragraphs)
    expected = [
        "ORDER UNDER SECTION 53",
        "WHEREAS the holder did a thing.",
        "NOW THEREFORE:",
        "Stop the thing.",
        "Pat Officer",
        "Compliance Officer",
        "Compliance and Enforcement Branch",
        "Environmental Assessment Office",
        "Dated 2026-11-17",
        "Order Ref: EAO-2026-001",
    ]
    positions = [text.index(s) for s in expected]
    assert positions == sorted(positions)


def test_now_therefore_heading_is_bold():
    """The fixed NOW THEREFORE heading is bold."""
    para = next(p for p in build().paragraphs if p.text.startswith("NOW THEREFORE:"))
    assert all(r.bold for r in para.runs if r.text.strip())


def test_title_is_centred_bold_and_underlined():
    """Title formatting from the rich text survives into the document."""
    para = next(p for p in build().paragraphs if "ORDER UNDER SECTION 53" in p.text)
    assert para.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert para.runs[0].bold
    assert para.runs[0].underline


def test_table_and_nested_list_are_rendered():
    """Tables and nested lists inside the rich text are kept."""
    doc = build()
    assert doc.tables[0].cell(0, 1).text == "Cell B"
    assert any("Nested step." in p.text for p in doc.paragraphs)


def test_rich_text_uses_document_font_size():
    """Rich text is rendered at the template's 13.5pt, not the converter default."""
    para = next(p for p in build().paragraphs if "WHEREAS the holder" in p.text)
    assert para.runs[0].font.size in (None, Pt(13.5))


def test_footer_has_right_aligned_page_number_field():
    """The footer carries a right-aligned 11pt page number."""
    para = build().sections[0].footer.paragraphs[0]
    assert para.alignment == WD_ALIGN_PARAGRAPH.RIGHT
    assert "PAGE" in para._p.xml
    assert para.runs[0].font.size == Pt(11)


def test_missing_date_and_empty_rich_text():
    """A draft order with no date or content still renders its fixed parts."""
    data = copy.deepcopy(ORDER_DATA)
    data["order_details"].update(issued_date=None, where_as=None, now_therefore="")
    doc = build(data)
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "None" not in text
    assert "NOW THEREFORE:" in text
    assert "Order Ref: EAO-2026-001" in text
    assert any(p.text.strip() == "Dated" for p in doc.paragraphs)


def test_missing_officer_and_department_values_never_print_none():
    """Absent officer or department values render as blanks."""
    data = copy.deepcopy(ORDER_DATA)
    data["officer_details"]["officer_position"] = None
    data["department_details"]["signature_branch"] = None
    text = "\n".join(p.text for p in build(data).paragraphs)
    assert "None" not in text
    assert "Pat Officer" in text


def test_wrapped_source_text_does_not_become_line_breaks():
    """The default order content is wrapped in its source; the order must not be."""
    data = copy.deepcopy(ORDER_DATA)
    data["order_details"]["now_therefore"] = '<p dir="ltr">\n    Pursuant to the Act,\n     I order this.</p>'
    assert any(p.text == "Pursuant to the Act, I order this." for p in build(data).paragraphs)


def test_content_table_fits_between_the_margins():
    """Tables in the order stay inside the 6.6in text width."""
    tbl_w = build().tables[0]._element.tblPr.findall(qn("w:tblW"))[-1]
    assert int(tbl_w.get(qn("w:w"))) / 1440 <= 6.6


def test_content_wrapped_in_divs_is_kept():
    """Block wrappers around rich text must not swallow the paragraphs inside."""
    data = copy.deepcopy(ORDER_DATA)
    data["order_details"]["where_as"] = "<p>Before</p><div><p>Inside</p></div><p>After</p>"
    paras = [p.text for p in build(data).paragraphs if p.text]
    assert paras[:3] == ["Before", "Inside", "After"]


def test_default_order_content_renders_every_paragraph():
    """Every text paragraph of the default order content reaches the document."""
    data = copy.deepcopy(ORDER_DATA)
    data["order_details"].update(where_as=WHERE_AS, now_therefore=NOW_THEREFORE)
    text = " ".join(p.text for p in build(data).paragraphs)
    for html in (WHERE_AS, NOW_THEREFORE):
        for tag in BeautifulSoup(html, "html.parser").find_all(["p", "li"]):
            if tag.find(["p", "li"]):
                continue
            for line in tag.get_text("\n").split("\n"):
                wanted = " ".join(line.split())
                if wanted:
                    assert wanted in " ".join(text.split()), wanted


def test_signature_gap_matches_the_template():
    """The template leaves 6em (5em padding + 1em paragraph margin) above the signature."""
    data = copy.deepcopy(ORDER_DATA)
    data["order_details"]["now_therefore"] = "<p>Do the thing.</p>"
    para = next(p for p in build(data).paragraphs if p.text == "Pat Officer")
    assert para.paragraph_format.space_before == Pt(81)


def test_page_number_sits_in_the_bottom_margin_inset_from_the_edge():
    """The page number is inset 1/3in and centred in the bottom margin, as in the PDF."""
    doc = build()
    section = doc.sections[0]
    para = section.footer.paragraphs[0]
    assert abs(section.footer_distance - Inches(0.33)) < 635  # stored in twips
    assert abs(para.paragraph_format.right_indent - Inches(0.33)) < 635
    assert doc.styles["Footer"].font.size == Pt(11)


def test_signature_gap_grows_by_the_table_margin_when_content_ends_in_a_table():
    """A closing table's 10px bottom margin adds to the signature padding in the template."""
    para = next(p for p in build().paragraphs if p.text == "Pat Officer")
    assert para.paragraph_format.space_before == Pt(88.5)
