"""Rich-text rendering shared by the Order and Warning Letter DOCX generators.

Wraps the Inspection Record HTML converter and then restyles what it produced
so lists, tables and links match the Order and Warning Letter HTML templates.
The Inspection Record path does not come through here and is left as it was.
"""
# python-docx exposes no public API for the OOXML this module has to set
# pylint: disable=protected-access

import re

from bs4 import BeautifulSoup
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from compliance_api.services.inspection_record.docx_utils import _set_cell_background
from compliance_api.services.inspection_record.html_to_docx import _add_html_to_container, prepare_html_for_docx


PX_PER_INCH = 96
# .editor-table: max-width 5.5in in print, 12px text on a 16px line, margin 10px 0
TABLE_MAX_WIDTH_PX = 5.5 * PX_PER_INCH
TABLE_FONT_SIZE = Pt(9)
TABLE_LINE_SPACING = Pt(12)
TABLE_GAP = Pt(7.5)
# .editor-tableCell: padding 4px 6px, in twips
CELL_PADDING_VERTICAL = 60
CELL_PADDING_HORIZONTAL = 90
HEADER_CELL_FILL = "F2F3F5"
# Rough glyph advance for 12px Calibri, used only when a table carries no widths
CELL_CHAR_PX = 5.6
HEADER_CELL_CHAR_PX = 6.1
CELL_EXTRA_PX = 14  # padding plus borders

# Bullets and native numbers: list margin-left 8px + .editor-listitem margin 1.5rem puts text 32px in,
# with the marker hanging to its left. Lists carrying an editor depth class (editor-list-ol1..5)
# number through CSS counters instead: the number starts 24px in and the text follows it.
LIST_TEXT_INDENT = Inches(1 / 3)
LIST_COUNTER_INDENT = Inches(0.25)
LIST_LEVEL_STEP = Inches(0.25)
COUNTER_LIST_CLASS = re.compile(r"^editor-list-ol\d$")
LIST_NUMBER_WIDTH = Inches(0.19)
LIST_BULLET_WIDTH = Inches(0.14)
LIST_ITEM_GAP = Pt(3)


def add_rich_text(doc, html):
    """Append editor HTML to the document body, styled as the PDF templates style it."""
    if not html:
        return

    soup = BeautifulSoup(prepare_html_for_docx(html), "html.parser")
    for link in soup.find_all("a", href=True):
        # Opt in to real hyperlinks; the converter leaves unmarked links as plain text
        link["data-docx-link"] = "1"
    source_tables = [el for el in soup.children if getattr(el, "name", None) == "table"]
    source_lists = [el for el in soup.children if getattr(el, "name", None) in ("ol", "ul")]

    body = doc.element.body
    existing = list(body)
    _add_html_to_container(doc, str(soup), clear_first=False)
    added = [el for el in body if not any(el is old for old in existing)]

    # Lists first: a table's gap then wins over a neighbouring list item's smaller one
    _style_lists(doc, [el for el in added if el.tag == qn("w:p")], source_lists)

    tables = [el for el in added if el.tag == qn("w:tbl")]
    for element, source in zip(tables, source_tables):
        _style_table(Table(element, doc), source)
        _space_around_table(element, doc)


def _style_lists(doc, paragraph_elements, source_lists):
    """Indent and space list items the way the template's list CSS does."""
    numbering = doc.part.numbering_part.numbering_definitions._numbering
    bullet_num_id = str(getattr(numbering, "_html_numbering_ids", {}).get("bullet_num_id"))

    items = [el for el in paragraph_elements if _num_pr(el) is not None]
    # One flag per rendered item, in order: does its list number through CSS counters?
    counter_flags = []
    for source in source_lists:
        uses_counters = any(COUNTER_LIST_CLASS.match(cls) for cls in source.get("class", []) or [])
        counter_flags.extend([uses_counters] * _rendered_item_count(source))
    if len(counter_flags) != len(items):
        # Source and output disagree; fall back to the editor's own style for every item
        counter_flags = [True] * len(items)

    for element, uses_counters in zip(items, counter_flags):
        num_pr = _num_pr(element)
        level = int(num_pr.find(qn("w:ilvl")).get(qn("w:val")))
        is_bullet = num_pr.find(qn("w:numId")).get(qn("w:val")) == bullet_num_id
        marker_width = LIST_BULLET_WIDTH if is_bullet else LIST_NUMBER_WIDTH
        if is_bullet or not uses_counters:
            text_start = LIST_TEXT_INDENT + LIST_LEVEL_STEP * level
        else:
            text_start = LIST_COUNTER_INDENT + LIST_LEVEL_STEP * level + marker_width

        fmt = Paragraph(element, doc).paragraph_format
        fmt.left_indent = text_start
        fmt.first_line_indent = -marker_width
        fmt.space_before = LIST_ITEM_GAP
        following = element.getnext()
        if following is None or following.tag != qn("w:p") or _num_pr(following) is None:
            fmt.space_after = LIST_ITEM_GAP


def _rendered_item_count(list_tag):
    """Count the paragraphs the converter makes for a list: one per item with content of its own."""
    count = 0
    for item in list_tag.find_all("li", recursive=False):
        has_own_content = any(
            (isinstance(child, str) and child.strip())
            or (getattr(child, "name", None) not in (None, "ul", "ol") and child.get_text(strip=True))
            for child in item.children
        )
        if has_own_content:
            count += 1
        nested = item.find(["ul", "ol"], recursive=False)
        if nested:
            count += _rendered_item_count(nested)
    return count


def _num_pr(paragraph_element):
    """Return the paragraph's numbering properties, or None when it is not a list item."""
    p_pr = paragraph_element.find(qn("w:pPr"))
    return None if p_pr is None else p_pr.find(qn("w:numPr"))


def _style_table(table, source):
    """Size and style a converted table like the template's .editor-table."""
    source_rows = [tr.find_all(["th", "td"]) for tr in source.find_all("tr")]
    widths = _column_widths_px(source, source_rows, len(table.columns))
    total_twips = 0

    for index, width_px in enumerate(widths):
        width = Inches(width_px / PX_PER_INCH)
        total_twips += int(width.twips)
        table.columns[index].width = width
        for row in table.rows:
            row.cells[index].width = width

    table_pr = table._element.tblPr
    for old in table_pr.findall(qn("w:tblW")):
        table_pr.remove(old)
    table_width = OxmlElement("w:tblW")
    table_width.set(qn("w:w"), str(total_twips))
    table_width.set(qn("w:type"), "dxa")
    table_pr.append(table_width)

    for row, source_cells in zip(table.rows, source_rows):
        for cell, source_cell in zip(row.cells, source_cells):
            _set_cell_padding(cell)
            if source_cell.name == "th":
                _set_cell_background(cell, HEADER_CELL_FILL)
            for para in cell.paragraphs:
                para.paragraph_format.line_spacing = TABLE_LINE_SPACING
                for run in para.runs:
                    run.font.size = TABLE_FONT_SIZE
                for link_run in para._p.iterfind(f"{qn('w:hyperlink')}/{qn('w:r')}"):
                    Run(link_run, para).font.size = TABLE_FONT_SIZE


def _column_widths_px(source, source_rows, column_count):
    """Work out column widths in CSS pixels: editor widths if present, else fitted to the text."""
    widths = []
    colgroup = source.find("colgroup")
    if colgroup:
        widths = [_style_width_px(col) for col in colgroup.find_all("col")]
    if len(widths) != column_count or not all(widths):
        table_width = _style_width_px(source)
        if table_width:
            widths = [table_width / column_count] * column_count
        else:
            widths = _content_widths_px(source_rows, column_count)

    total = sum(widths)
    if total > TABLE_MAX_WIDTH_PX:
        widths = [width * TABLE_MAX_WIDTH_PX / total for width in widths]
    return widths


def _style_width_px(element):
    """Return the pixel width from an element's style, or None."""
    match = re.search(r"(?:^|;)\s*width:\s*([\d.]+)px", element.get("style", "") or "")
    return float(match.group(1)) if match else None


def _content_widths_px(source_rows, column_count):
    """Estimate shrink-to-fit column widths from the longest line of text in each column."""
    widths = [CELL_EXTRA_PX + CELL_CHAR_PX] * column_count
    for cells in source_rows:
        for index, cell in enumerate(cells[:column_count]):
            char_px = HEADER_CELL_CHAR_PX if cell.name == "th" else CELL_CHAR_PX
            longest = max((len(line) for line in _cell_lines(cell)), default=0)
            widths[index] = max(widths[index], longest * char_px + CELL_EXTRA_PX)
    return widths


def _cell_lines(cell):
    """Return the lines of text a cell lays out: one per paragraph, split again at each <br>."""
    lines = []
    for block in cell.find_all(["p", "li"]) or [cell]:
        parts = ["\n" if getattr(node, "name", None) == "br" else node
                 for node in block.descendants if isinstance(node, str) or node.name == "br"]
        lines.extend(" ".join(line.split()) for line in "".join(parts).split("\n"))
    return lines


def _set_cell_padding(cell):
    """Give a cell the template's 4px/6px padding."""
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:tcMar")):
        tc_pr.remove(old)
    margins = OxmlElement("w:tcMar")
    for side, twips in (
        ("top", CELL_PADDING_VERTICAL),
        ("left", CELL_PADDING_HORIZONTAL),
        ("bottom", CELL_PADDING_VERTICAL),
        ("right", CELL_PADDING_HORIZONTAL),
    ):
        edge = OxmlElement(f"w:{side}")
        edge.set(qn("w:w"), str(twips))
        edge.set(qn("w:type"), "dxa")
        margins.append(edge)
    tc_pr.append(margins)


def _space_around_table(table_element, doc):
    """Word tables have no margin, so put the template's gap on the paragraphs either side."""
    before = table_element.getprevious()
    if before is not None and before.tag == qn("w:p"):
        Paragraph(before, doc).paragraph_format.space_after = TABLE_GAP
    after = table_element.getnext()
    if after is not None and after.tag == qn("w:p"):
        Paragraph(after, doc).paragraph_format.space_before = TABLE_GAP
