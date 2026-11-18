"""DOCX generator for Warning Letters.

Mirrors the layout of templates/warning_letter_template.html, which stays the
source for the on-screen preview. Keep the two in step when either changes.
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from compliance_api.services.enforcement_docx import add_rich_text
from compliance_api.services.inspection_record.docx_utils import (
    _add_continuation_marker, _add_first_page_continuation_marker, _add_page_number, _apply_letter_base_style,
    _remove_compatibility_mode, set_cell_border)
from compliance_api.services.inspection_record.html_to_docx import init_list_numbering


FONT_SIZE = Pt(13.5)
LINE_SPACING = Pt(15)
REF_FONT_SIZE = Pt(8.5)
HEADER_FONT_SIZE = Pt(10)
FOOTER_FONT_SIZE = Pt(8.5)
FOOTER_LINE_SPACING = Pt(10)
FOOTER_COLUMN_GAP_TWIPS = 200  # about 1em at the footer size (td { padding-right: 1em })
# The template shows a 180px-high logo through a 120px-high band; the overflow is transparent padding
LOGO_IMAGE_HEIGHT = Inches(1.875)
LOGO_BAND_HEIGHT = Inches(1.25)
LOGO_CROP = "16667"  # (180 - 120) / 2 / 180, in 1/1000ths of a percent
# Later pages: "- N -" sits high in the margin and body text starts at the template's 0.75in
HEADER_DISTANCE = Inches(0.28)
HEADER_GAP = Pt(21)
# Page one's footer rule lands 0.875in above the page bottom; the later-page marker sits a little higher
FOOTER_DISTANCE = Inches(0.375)
LATER_MARKER_LIFT = Pt(10.5)
# Text width is 6.5in; the template splits the footer 28% / 44% / 28%
FOOTER_COLUMN_WIDTHS = (Inches(1.82), Inches(2.86), Inches(1.82))
LOGO_PATH = (
    Path(__file__).resolve().parent.parent / "inspection_record" / "assets" / "BCID_V_RGB_pos.png"
)


def generate_warning_letter_docx(warning_letter_data):
    """Generate a Warning Letter DOCX from the same data the letter template is rendered with."""
    warning_letter = warning_letter_data.get("warning_letter") or {}
    officer_details = warning_letter_data.get("officer_details") or {}
    department_details = warning_letter_data.get("department_details") or {}

    doc = Document()
    _remove_compatibility_mode(doc)
    init_list_numbering(doc)
    _apply_letter_base_style(doc, FONT_SIZE, LINE_SPACING)

    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1.25)
    section.left_margin = Inches(1)
    # Page one starts at the 0.5in margin; the later-page header pushes text to about 0.75in
    section.header_distance = HEADER_DISTANCE
    section.footer_distance = FOOTER_DISTANCE
    doc.styles["Header"].font.size = HEADER_FONT_SIZE
    section.different_first_page_header_footer = True

    _add_logo(doc)

    reference = doc.add_paragraph()
    reference.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    reference.paragraph_format.line_spacing = Pt(11)  # stands in for .com-ref { margin-top: -0.25em }
    ref_run = reference.add_run(f"Ref: {warning_letter.get('warning_letter_number') or ''}")
    ref_run.italic = True
    ref_run.font.size = REF_FONT_SIZE

    issue_date = doc.add_paragraph(warning_letter.get("issue_date") or "")
    issue_date.paragraph_format.space_before = FONT_SIZE
    issue_date.paragraph_format.space_after = FONT_SIZE

    add_rich_text(doc, warning_letter.get("content"))

    _add_signature(doc, officer_details, department_details)

    _add_first_page_header_footer(section, department_details)
    _add_later_pages_header_footer(section)
    return doc


def _add_logo(doc):
    """Put the BC logo, centred, in the document's opening paragraph."""
    para = doc.paragraphs[0] if doc.paragraphs else doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Exact line spacing would clip the picture to one text line
    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    shape = para.add_run().add_picture(str(LOGO_PATH), height=LOGO_IMAGE_HEIGHT)
    shape.height = LOGO_BAND_HEIGHT
    blip_fill = shape._inline.graphic.graphicData.pic.blipFill
    src_rect = OxmlElement('a:srcRect')
    src_rect.set('t', LOGO_CROP)
    src_rect.set('b', LOGO_CROP)
    blip_fill.find(qn('a:blip')).addnext(src_rect)


def _add_signature(doc, officer_details, department_details):
    """Add the sign-off, leaving three blank lines for the signature itself."""
    half_line = Pt(6.75)  # .signature p { margin-bottom: 0.5em }
    sincerely = doc.add_paragraph("Sincerely,")
    sincerely.paragraph_format.space_before = Pt(27)  # .signature { margin-top: 2em }
    sincerely.paragraph_format.space_after = half_line
    for _ in range(3):
        doc.add_paragraph().paragraph_format.space_after = half_line

    for line in (
        officer_details.get("officer_name"),
        officer_details.get("officer_position"),
        department_details.get("signature_branch"),
        department_details.get("office_name"),
    ):
        doc.add_paragraph(line or "")


def _add_first_page_header_footer(section, department_details):
    """Page one: no header; footer with a continuation marker above the office details."""
    header_para = section.first_page_header.paragraphs[0]
    header_para.paragraph_format.line_spacing = Pt(1)

    footer = section.first_page_footer
    marker = footer.paragraphs[0]
    marker.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    marker.paragraph_format.space_after = Pt(4)
    _add_first_page_continuation_marker(marker)

    table = footer.add_table(rows=1, cols=3, width=sum(FOOTER_COLUMN_WIDTHS))
    table.autofit = False
    cells = table.rows[0].cells
    contents = (
        ([department_details.get("office_name")], True),
        ([department_details.get("office_branch")], False),
        (
            [
                "Mailing Address:",
                department_details.get("address_line1"),
                department_details.get("address_line2"),
            ],
            False,
        ),
    )
    for cell, width, (lines, bold) in zip(cells, FOOTER_COLUMN_WIDTHS, contents):
        cell.width = width
        _set_footer_cell_margins(cell)
        set_cell_border(cell, top={"val": "single", "sz": 8, "color": "000000", "space": 0})
        para = cell.paragraphs[0]
        para.paragraph_format.line_spacing = FOOTER_LINE_SPACING
        para.paragraph_format.space_before = Pt(4.25)  # padding-top: 0.5em (of 8.5pt) under the rule
        for index, line in enumerate(lines):
            run = para.add_run(line or "")
            run.bold = bold
            run.font.size = FOOTER_FONT_SIZE
            if index < len(lines) - 1:
                run.add_break()

    # Word expects a paragraph after a table that closes a footer; keep it out of the way
    closing = footer.add_paragraph()
    closing.paragraph_format.line_spacing = Pt(1)


def _set_footer_cell_margins(cell):
    """Keep footer text flush left under the rule, with a gap before the next column."""
    tc_margin = OxmlElement('w:tcMar')
    for side, twips in (('top', 0), ('left', 0), ('bottom', 0), ('right', FOOTER_COLUMN_GAP_TWIPS)):
        elem = OxmlElement(f'w:{side}')
        elem.set(qn('w:w'), str(twips))
        elem.set(qn('w:type'), 'dxa')
        tc_margin.append(elem)
    cell._tc.get_or_add_tcPr().append(tc_margin)


def _add_later_pages_header_footer(section):
    """Pages two onward: centred "- N -" header and a bottom-right continuation marker."""
    header_para = section.header.paragraphs[0]
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_para.paragraph_format.space_after = HEADER_GAP
    for text in ("- ", None, " -"):
        run = header_para.add_run(text or "")
        run.font.size = HEADER_FONT_SIZE
        if text is None:
            _add_page_number(run)

    marker = section.footer.paragraphs[0]
    marker.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    marker.paragraph_format.space_after = LATER_MARKER_LIFT
    _add_continuation_marker(marker)
