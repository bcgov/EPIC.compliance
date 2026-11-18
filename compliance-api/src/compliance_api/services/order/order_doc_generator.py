"""DOCX generator for Orders.

Mirrors the layout of templates/order_template.html, which stays the source
for the on-screen preview. Keep the two in step when either changes.
"""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from compliance_api.services.enforcement_docx import TABLE_GAP, add_rich_text
from compliance_api.services.inspection_record.docx_utils import (
    _add_page_number, _apply_letter_base_style, _remove_compatibility_mode)
from compliance_api.services.inspection_record.html_to_docx import init_list_numbering


FONT_SIZE = Pt(13.5)
LINE_SPACING = Pt(15)
# Template spacing, converted from em at the 13.5pt body size
SECTION_GAP = Pt(20.25)  # .section { padding-top: 1.5em }
SIGNATURE_GAP = Pt(81)  # .signature { padding-top: 5em } plus its first paragraph's 1em margin
# The template centres the number in the 0.875in bottom margin, inset by 32px of padding
FOOTER_DISTANCE = Inches(0.33)
FOOTER_RIGHT_INSET = Inches(0.33)
FOOTER_FONT_SIZE = Pt(11)


def generate_order_docx(order_data):
    """Generate an Order DOCX from the same data the order template is rendered with."""
    order_details = order_data.get("order_details") or {}
    officer_details = order_data.get("officer_details") or {}
    department_details = order_data.get("department_details") or {}

    doc = Document()
    _remove_compatibility_mode(doc)
    init_list_numbering(doc)
    _apply_letter_base_style(doc, FONT_SIZE, LINE_SPACING)

    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.right_margin = Inches(0.95)
    section.bottom_margin = Inches(0.875)
    section.left_margin = Inches(0.95)

    # The default document starts with one empty paragraph: the template's leading <br>
    if not doc.paragraphs:
        doc.add_paragraph()

    # Where as
    _add_section_gap(doc)
    add_rich_text(doc, order_details.get("where_as"))

    # Now therefore
    _add_section_gap(doc)
    heading = doc.add_paragraph()
    heading.add_run("NOW THEREFORE: ").bold = True
    doc.add_paragraph()
    add_rich_text(doc, order_details.get("now_therefore"))

    # Signature
    signature_lines = [
        officer_details.get("officer_name"),
        officer_details.get("officer_position"),
        department_details.get("signature_branch"),
        department_details.get("office_name"),
    ]
    # A table closing the content keeps its bottom margin on top of the signature padding
    body = doc.element.body
    ends_with_table = len(body) > 1 and body[-2].tag == qn("w:tbl")
    signature_gap = SIGNATURE_GAP + TABLE_GAP if ends_with_table else SIGNATURE_GAP
    for index, line in enumerate(signature_lines):
        para = doc.add_paragraph(line or "")
        if index == 0:
            para.paragraph_format.space_before = signature_gap

    dated = doc.add_paragraph(f"Dated {order_details.get('issued_date') or ''}")
    dated.paragraph_format.space_before = FONT_SIZE  # gap between the template's two <p> blocks
    doc.add_paragraph(f"Order Ref: {order_details.get('order_number') or ''}")

    section.footer_distance = FOOTER_DISTANCE
    doc.styles["Footer"].font.size = FOOTER_FONT_SIZE
    _add_page_number_footer(section)
    return doc


def _add_section_gap(doc):
    """Add the empty spacer that stands in for the template's section padding."""
    spacer = doc.add_paragraph()
    spacer.paragraph_format.line_spacing = SECTION_GAP
    return spacer


def _add_page_number_footer(section):
    """Add the page number at the bottom right of every page."""
    para = section.footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    para.paragraph_format.right_indent = FOOTER_RIGHT_INSET
    run = para.add_run()
    run.font.size = FOOTER_FONT_SIZE
    _add_page_number(run)
