"""DOCX Generator for Inspection Reports."""

import re
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from requests.exceptions import RequestException


def _add_hyperlink(paragraph, text, url):
    """Add a hyperlink to a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
        is_external=True
    )
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    # Create a new run object (a wrapper around a new w:r element)
    new_run = OxmlElement('w:r')
    # Set the run's text
    rpr = OxmlElement('w:rPr')

    # Add color (blue) and underline for hyperlink style
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '0563C1')  # hyperlink blue
    rpr.append(c)

    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rpr.append(u)

    new_run.append(rpr)
    new_run.text = text

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

    return hyperlink


def _set_cell_background(cell, fill):
    """Set cell background color."""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), fill)
    cell._element.get_or_add_tcPr().append(shading_elm)


def set_cell_border(cell, **kwargs):
    """Set cell borders."""
    tc = cell._tc
    tc_para = tc.get_or_add_tcPr()

    tc_borders = OxmlElement('w:tcBorders')
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        if edge in kwargs:
            edge_data = kwargs[edge]
            edge_el = OxmlElement(f'w:{edge}')
            for key, value in edge_data.items():
                edge_el.set(qn(f'w:{key}'), str(value))
            tc_borders.append(edge_el)
    tc_para.append(tc_borders)


def _add_html_to_container(container, html_text, *, font_size=None, clear_first=True):
    if not html_text:
        return

    soup = BeautifulSoup(html_text, "html.parser")

    # Clear the first paragraph if requested
    if clear_first and hasattr(container, 'paragraphs') and container.paragraphs:
        container.paragraphs[0].text = ""
        first_para_used = False
    else:
        first_para_used = True

    # if div, get its children
    children = soup.children
    if len(list(soup.children)) == 1 and list(soup.children)[0].name == 'div':
        children = list(soup.children)[0].children

    for element in children:
        if element.name == "p":
            # Use the first empty paragraph if available
            if not first_para_used and hasattr(container, 'paragraphs') and container.paragraphs:
                para = container.paragraphs[0]
                text = element.get_text(strip=True)
                # Replace 2+ spaces with single space
                text = re.sub(r' {2,}', ' ', text)
                if text:
                    run = para.add_run(text)
                    if font_size:
                        run.font.size = font_size
                first_para_used = True
            else:
                _add_paragraph(container, element, font_size)

        elif element.name in ("ol", "ul"):
            _add_list(container, element, font_size)
            first_para_used = True  # Mark as used after adding list

        elif element.name == "table":
            add_html_table_to_container(container, element)
            first_para_used = True  # Mark as used after adding table


def _add_paragraph(container, p_tag, font_size):
    text = p_tag.get_text(strip=True)
    # Replace 2+ spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # Blank paragraph (<p><br/></p>)
    para = container.add_paragraph()
    if not text:
        return

    run = para.add_run(text)
    if font_size:
        run.font.size = font_size


def _add_list(container, list_tag, font_size):
    style = "List Number" if list_tag.name == "ol" else "List Bullet"

    for li in list_tag.find_all("li", recursive=False):
        para = container.add_paragraph(style=style)
        text = li.get_text(strip=True)
        # Replace 2+ spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        run = para.add_run(text)
        if font_size:
            run.font.size = font_size


def _add_html_paragraphs_to_cell(cell, html, font_size=Pt(11)):
    soup = BeautifulSoup(html, "html.parser")

    # Clear the first existing paragraph
    if cell.paragraphs:
        cell.paragraphs[0].text = ""
        first_para_used = False
    else:
        first_para_used = True

    # Find only direct child paragraphs, not nested ones
    # First, get the root element(s)
    root_elements = [el for el in soup.children if el.name == 'p']

    # If we have a wrapper <p>, get its children instead
    if len(root_elements) == 1 and root_elements[0].find_all('p', recursive=False):
        paragraphs = root_elements[0].find_all('p', recursive=False)
    else:
        paragraphs = soup.find_all('p', recursive=False)

    for p in paragraphs:
        # Handle empty <p><br/></p>
        text = p.get_text(strip=True)
        # Data has duplicate (sometimes four spaces) in a row
        # Replace 2+ spaces with single space
        text = re.sub(r' {2,}', ' ', text)

        # Use the first empty paragraph if available
        if not first_para_used:
            para = cell.paragraphs[0]
            first_para_used = True
        else:
            para = cell.add_paragraph()

        # Handle text with inline formatting (italic, bold)
        if p.find(['i', 'em', 'strong', 'b']):
            _add_formatted_text_to_para(para, p, font_size)
        else:
            run = para.add_run(text if text else "")
            run.font.size = font_size


def _add_formatted_text_to_para(para, element, font_size):
    """Add text with inline formatting (bold, italic) to a paragraph."""
    for child in element.children:
        if isinstance(child, str):
            # Replace 2+ spaces with single space
            text = re.sub(r' {2,}', ' ', child)
            if text.strip():
                run = para.add_run(text)
                run.font.size = font_size
        elif child.name in ['strong', 'b']:
            text = re.sub(r' {2,}', ' ', child.get_text())
            run = para.add_run(text)
            run.bold = True
            run.font.size = font_size
        elif child.name in ['em', 'i']:
            text = re.sub(r' {2,}', ' ', child.get_text())
            run = para.add_run(text)
            run.italic = True
            run.font.size = font_size
        elif child.name == 'br':
            pass  # Skip <br> tags inside paragraphs
        else:
            text = re.sub(r' {2,}', ' ', child.get_text())
            run = para.add_run(text)
            run.font.size = font_size


def _add_page_number(run):
    fld_char_begin = OxmlElement('w:fldChar')
    fld_char_begin.set(qn('w:fldCharType'), 'begin')

    instr_text = OxmlElement('w:instrText')
    instr_text.text = 'PAGE'

    fld_char_end = OxmlElement('w:fldChar')
    fld_char_end.set(qn('w:fldCharType'), 'end')

    run._r.append(fld_char_begin)
    run._r.append(instr_text)
    run._r.append(fld_char_end)


def _remove_cell_margins(cell):
    table_cell = cell._tc
    table_cell_pr = table_cell.get_or_add_tcPr()

    tc_margin = OxmlElement('w:tcMar')
    for side in ('top', 'left', 'bottom', 'right'):
        elem = OxmlElement(f'w:{side}')
        elem.set(qn('w:w'), '0')
        elem.set(qn('w:type'), 'dxa')
        tc_margin.append(elem)

    table_cell_pr.append(tc_margin)


def add_html_table_to_container(container, table_element):
    """Convert an HTML table to a docx table."""
    rows = table_element.find_all('tr')
    if not rows:
        return

    max_cols = max(len(row.find_all(['th', 'td'])) for row in rows)

    # Create docx table
    docx_table = container.add_table(rows=len(rows), cols=max_cols)
    docx_table.style = 'Table Grid'

    # Populate table
    for row_idx, tr in enumerate(rows):
        docx_row = docx_table.rows[row_idx]

        # Try to extract row height from style attribute
        style = tr.get('style', '')
        if 'height:' in style:
            # Extract height value (e.g., "66px")
            import re as regex
            height_match = regex.search(r'height:\s*(\d+)px', style)
            if height_match:
                height_px = int(height_match.group(1))
                # Convert pixels to inches (roughly 96 DPI)
                height_inches = height_px / 96
                docx_row.height = Inches(height_inches)

        cells = tr.find_all(['th', 'td'])
        for col_idx, cell in enumerate(cells):
            docx_cell = docx_row.cells[col_idx]

            # Clear default paragraph
            docx_cell.paragraphs[0].text = ""

            # Process cell content - handle paragraphs, lists, and formatting
            first_element = True
            for element in cell.children:
                if element.name == 'p':
                    # Use first paragraph or create new one
                    if first_element and docx_cell.paragraphs:
                        para = docx_cell.paragraphs[0]
                        first_element = False
                    else:
                        para = docx_cell.add_paragraph()

                    # Add formatted text to paragraph
                    _add_formatted_text_to_table_para(para, element)

                elif element.name in ('ul', 'ol'):
                    # If list is first element, remove the empty default paragraph
                    if first_element and docx_cell.paragraphs and not docx_cell.paragraphs[0].text.strip():
                        p = docx_cell.paragraphs[0]._element
                        p.getparent().remove(p)
                    # Add list to cell
                    _add_list_to_table_cell(docx_cell, element)
                    first_element = False

            # Make header cells bold
            if cell.name == 'th':
                for para in docx_cell.paragraphs:
                    for run in para.runs:
                        run.bold = True

            # Set borders
            set_cell_border(
                docx_cell,
                top={"sz": 4, "val": "single", "color": "000000"},
                bottom={"sz": 4, "val": "single", "color": "000000"},
                start={"sz": 4, "val": "single", "color": "000000"},
                end={"sz": 4, "val": "single", "color": "000000"}
            )


def _add_formatted_text_to_table_para(para, p_element):
    """Add text with formatting (bold, italic) to a paragraph from a <p> element."""
    for child in p_element.children:
        if isinstance(child, str):
            text = re.sub(r' {2,}', ' ', child)
            if text.strip():
                run = para.add_run(text)
                run.font.size = Pt(11)
        elif child.name in ['strong', 'b']:
            text = re.sub(r' {2,}', ' ', child.get_text())
            run = para.add_run(text)
            run.bold = True
            run.font.size = Pt(11)
        elif child.name in ['em', 'i']:
            text = re.sub(r' {2,}', ' ', child.get_text())
            run = para.add_run(text)
            run.italic = True
            run.font.size = Pt(11)
        elif child.name == 'span':
            text = re.sub(r' {2,}', ' ', child.get_text())
            if text.strip():
                run = para.add_run(text)
                run.font.size = Pt(11)
        elif child.name == 'br':
            para.add_run('\n')


def _add_list_to_table_cell(cell, list_element):
    """Add a list (ordered or unordered) to a table cell."""
    style = "List Number" if list_element.name == "ol" else "List Bullet"

    for li in list_element.find_all('li', recursive=False):
        para = cell.add_paragraph(style=style)
        text = li.get_text(strip=True)
        text = re.sub(r' {2,}', ' ', text)
        run = para.add_run(text)
        run.font.size = Pt(11)


def _add_photo(photo, cell):
    photo_url = photo.get('photo_url')
    caption_text = f"Photo {photo.get('photo_number', '')}. {photo.get('photo_caption', '')}"

    if photo_url:
        try:
            response = requests.get(photo_url)
            response.raise_for_status()
            image_stream = BytesIO(response.content)

            # Insert the image
            para = cell.add_paragraph()
            run = para.add_run()
            run.add_picture(image_stream, width=Inches(4))

            # Insert caption below image
            caption_para = cell.add_paragraph()
            caption_run = caption_para.add_run(caption_text)
            caption_run.font.size = Pt(9)
        except RequestException:
            # If image fails, show placeholder text
            para = cell.add_paragraph()
            para.text = f"[Failed to load image] {caption_text}"
            run.font.size = Pt(9)


def _add_figure(figure, cell):
    figure_url = figure.get('figure_url')
    caption_text = (
        f"Figure {figure.get('figure_number', '')}. "
        f"{figure.get('figure_caption', '')}"
    )

    if not figure_url:
        return

    try:
        response = requests.get(figure_url)
        response.raise_for_status()
        image_stream = BytesIO(response.content)
        para = cell.add_paragraph()
        run = para.add_run()
        run.add_picture(image_stream, width=Inches(4))
        caption_para = cell.add_paragraph()
        caption_run = caption_para.add_run(caption_text)
        caption_run.font.size = Pt(9)

    except RequestException:
        para = cell.add_paragraph()
        run = para.add_run(f"[Failed to load figure] {caption_text}")
        run.font.size = Pt(9)


def _add_requirement_details_table(doc, req):
    req_table = doc.add_table(rows=0, cols=2)
    req_table.style = 'Table Grid'

    # Requirement header and details
    source_details = req.get('requirement_source_details', [])
    last_description_is_table = False
    if source_details:
        row = req_table.add_row()
        cell = row.cells[0].merge(row.cells[1])
        para = cell.paragraphs[0]

        # Set Requirement header spacing
        para.paragraph_format.space_before = Inches(0.04)
        para.paragraph_format.space_after = Inches(0.08)

        ends_with_table = False
        for idx, source in enumerate(source_details):
            # Add requirement header for first source
            if idx == 0:
                run = para.add_run(f"Requirement {req.get('sort_order', '')}: ")
                run.bold = True

            # Add requirement title
            req_title = source.get('requirement_title', '')
            run = para.add_run(req_title)
            run.bold = True

            # Add appendix if present
            if source.get('appendix_no'):
                run = para.add_run(f" (Appendix {source.get('appendix_no')})")

            para.add_run('\n')

            # Add title if present (comes right after requirement title)
            if source.get('title'):
                run = para.add_run(source.get('title'))
                run.bold = True

            # Add description
            if source.get("requirement_source_description"):
                _add_html_to_container(
                    cell,
                    source["requirement_source_description"],
                    clear_first=False,
                )
                ends_with_table = source.get("requirement_source_description", '').strip().endswith('</table>')

            # Add req source images
            for img in source.get('requirement_source_images', []):
                ends_with_table = False
                image_url = img.get('image_url')
                if image_url:
                    try:
                        response = requests.get(image_url)
                        response.raise_for_status()
                        image_stream = BytesIO(response.content)

                        # Insert the image
                        img_para = cell.add_paragraph()
                        run = img_para.add_run()
                        run.add_picture(image_stream, width=Inches(4))

                        # Add filename as caption if available
                        if img.get('original_file_name'):
                            caption_para = cell.add_paragraph()
                            caption_run = caption_para.add_run(img.get('original_file_name'))
                            caption_run.font.size = Pt(9)
                    except RequestException:
                        # If image fails, show placeholder text
                        error_para = cell.add_paragraph()
                        error_para.text = f"[Failed to load image: {img.get('original_file_name', 'unknown')}]"

            # Add document details (come after source description and images)
            for doc_group in source.get('requirement_documents', []):
                para = cell.add_paragraph()  # New paragraph for document group
                para.add_run('\n')
                run = para.add_run(doc_group.get('document_title', ''))
                run.bold = True

                # Check if first document has appendix
                documents = doc_group.get('documents', [])
                if documents and documents[0].get('appendix_no'):
                    ends_with_table = False
                    run = para.add_run(f" (Appendix {documents[0].get('appendix_no')})")
                    para.add_run('\n')

                for document in documents:
                    ends_with_table = False
                    # Add section info
                    if document.get('section_number') or document.get('section_title'):
                        section_para = cell.add_paragraph()
                        section_text = ''
                        if document.get('section_number'):
                            section_text = f"Section {document.get('section_number')} "
                        if document.get('section_title'):
                            section_text += document.get('section_title')
                        run = section_para.add_run(section_text)
                        run.bold = True

                    # Add description
                    if document.get('description'):
                        ends_with_table = document.get("description", '').strip().endswith('</table>')
                        _add_html_to_container(
                            cell,
                            document.get('description'),
                            clear_first=False,
                        )
                    # Add document images
                    for img in document.get('document_images', []):
                        ends_with_table = False
                        image_url = img.get('image_url')
                        if image_url:
                            try:
                                response = requests.get(image_url)
                                response.raise_for_status()
                                image_stream = BytesIO(response.content)

                                img_para = cell.add_paragraph()
                                run = img_para.add_run()
                                run.add_picture(image_stream, width=Inches(4))

                                if img.get('original_file_name'):
                                    caption_para = cell.add_paragraph()
                                    caption_run = caption_para.add_run(img.get('original_file_name'))
                                    caption_run.font.size = Pt(9)
                            except RequestException:
                                error_para = cell.add_paragraph()
                                error_para.text = f"[Failed to load image: {img.get('original_file_name', 'unknown')}]"

            # Add spacing between multiple sources
            if idx < len(source_details) - 1:
                para = cell.add_paragraph()
                para = cell.add_paragraph()  # New paragraph for next source

            # Check if last description ends with a table
            if idx == len(source_details) - 1 and ends_with_table:
                last_description_is_table = True

    if last_description_is_table:
        cell.add_paragraph()

    # Inspection Details/Findings
    row = req_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    para = cell.paragraphs[0]
    # Set Header spacing
    para.paragraph_format.space_before = Inches(0.04)
    para.paragraph_format.space_after = Inches(0.08)
    run = para.add_run("Inspection Details:")
    run.bold = True
    _add_html_to_container(
        cell,
        req.get('requirement_findings', ''),
        clear_first=False
    )

    # Photos
    for photo in req.get('requirement_photos', []):
        _add_photo(photo, cell)

    # Figures
    for figure in req.get('requirement_figures', []):
        _add_figure(figure, cell)

    # Compliance Finding
    row = req_table.add_row()
    row.cells[0].text = "Compliance Finding"
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    _set_cell_background(row.cells[0], 'D9D9D9')
    row.cells[1].text = req.get('compliance_finding', '')

    # Set column width for first column
    row.cells[0].width = Inches(2)

    # Enforcement Action
    row = req_table.add_row()
    row.cells[0].text = "Enforcement Action"
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    _set_cell_background(row.cells[0], 'BFBFBF')
    row.cells[1].text = req.get('enforcement_action', '')


def generate_inspection_report_docx(preview_data):
    """Generate a DOCX file from inspection report preview data."""
    doc = Document()

    # Set document margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.25)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.5)

    # Set font and spacing
    style = doc.styles['Normal']
    style.paragraph_format.space_after = Inches(0.04)
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # List styles spacing
    list_bullet_style = doc.styles['List Bullet']
    list_bullet_style.paragraph_format.space_after = Inches(0.04)
    list_bullet_style.paragraph_format.left_indent = Inches(0.5)

    # Disable contextual spacing at style level
    para_properties = list_bullet_style._element.pPr
    if para_properties is not None:
        contextual_spacing = para_properties.find(qn('w:contextualSpacing'))
        if contextual_spacing is not None:
            para_properties.remove(contextual_spacing)

    list_number_style = doc.styles['List Number']
    list_number_style.paragraph_format.space_after = Inches(0.04)
    list_number_style.paragraph_format.left_indent = Inches(0.5)

    para_properties = list_number_style._element.pPr
    if para_properties is not None:
        contextual_spacing = para_properties.find(qn('w:contextualSpacing'))
        if contextual_spacing is not None:
            para_properties.remove(contextual_spacing)

    rpr = style._element.get_or_add_rPr()

    # Set East Asia font
    rfonts = rpr.rFonts
    rfonts.set(qn('w:eastAsia'), 'Calibri')

    # Add header with logo and title
    header = doc.sections[0].header
    header_table = header.add_table(rows=1, cols=2, width=Inches(7.25))
    header_table.autofit = False
    # Column widths
    header_table.columns[0].width = Inches(4.25)
    header_table.columns[1].width = Inches(3.0)
    for row in header_table.rows:
        row.cells[0].width = Inches(4.25)
        row.cells[1].width = Inches(3.0)
    if len(header.paragraphs) > 0:
        # Remove default paragraph
        p = header.paragraphs[0]
        p._element.getparent().remove(p._element)
    logo_cell = header_table.rows[0].cells[0]
    _remove_cell_margins(logo_cell)
    logo_para = logo_cell.paragraphs[0]
    logo_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    logo_para.paragraph_format.space_before = Pt(0)
    logo_para.paragraph_format.space_after = Pt(0)
    logo_para.paragraph_format.left_indent = Inches(-0.10)

    logo_run = logo_para.add_run()
    logo_path = Path(__file__).parent / "assets" / "EAO_Logo.png"
    logo_run.add_picture(str(logo_path), width=Inches(4))

    # Add footer with page numbers
    footer = doc.sections[0].footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    footer_run = footer_para.add_run()
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(51, 102, 153)  # #336699

    _add_page_number(footer_run)

    title_cell = header_table.rows[0].cells[1]
    title_cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    title_para = title_cell.paragraphs[0]
    title_para.text = "INSPECTION RECORD"
    title_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    title_run = title_para.runs[0]
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(51, 102, 153)  # #336699

    # Extract data
    project_details = preview_data.get('project_details', {})
    inspection_details = preview_data.get('inspection_details', {})
    officer_details = preview_data.get('officer_details', {})
    department_details = preview_data.get('department_details', {})
    approval_info = preview_data.get('approval_info', {})
    version_date_info = preview_data.get('version_date_info', {})

    # Helper function to set header cell
    def set_header_cell(cell, text):
        cell.text = text
        cell.paragraphs[0].runs[0].font.bold = True

    # First page table - Project and Inspection Information
    info_table = doc.add_table(rows=14, cols=4)
    info_table.style = 'Table Grid'

    # Row 1: Project Name and Inspection Status
    set_header_cell(info_table.cell(0, 0), "Project Name")
    info_table.cell(0, 1).text = project_details.get('name', '')
    set_header_cell(info_table.cell(0, 2), "Inspection Status")
    info_table.cell(0, 3).text = preview_data.get('ir_status', '')

    # Row 2: EA Certificate and Inspection No
    set_header_cell(info_table.cell(1, 0), project_details.get('certificate_label', 'EA Certificate #'))
    info_table.cell(1, 1).text = project_details.get('eac_certificate', '')
    set_header_cell(info_table.cell(1, 2), "Inspection No.")
    info_table.cell(1, 3).text = inspection_details.get('ir_number', '')

    # Row 3: Project Status and Inspection Start
    set_header_cell(info_table.cell(2, 0), "Project Status")
    info_table.cell(2, 1).text = project_details.get('project_state', '') or ''
    set_header_cell(info_table.cell(2, 2), "Inspection Start")
    info_table.cell(2, 3).text = inspection_details.get('start_date', '')

    # Row 4: Inspection Type and Initiation
    set_header_cell(info_table.cell(3, 0), "Inspection Type")
    info_table.cell(3, 1).text = inspection_details.get('inspection_type', '')
    set_header_cell(info_table.cell(3, 2), "Initiation")
    info_table.cell(3, 3).text = inspection_details.get('initiation', '')

    # Row 5: UTM
    set_header_cell(info_table.cell(4, 0), "UTM")
    merged_cell = info_table.cell(4, 1).merge(info_table.cell(4, 3))
    merged_cell.text = inspection_details.get('utm', '')

    # Row 6: Project Description
    set_header_cell(info_table.cell(5, 0), "Project Description")
    merged_cell = info_table.cell(5, 1).merge(info_table.cell(5, 3))
    merged_cell.text = inspection_details.get('project_description', '')

    # Row 7: Location Description
    set_header_cell(info_table.cell(6, 0), "Location Description")
    merged_cell = info_table.cell(6, 1).merge(info_table.cell(6, 3))
    merged_cell.text = inspection_details.get('location_description', '')

    # Row 8: Inspection Summary
    set_header_cell(info_table.cell(7, 0), "Inspection Summary")
    merged_cell = info_table.cell(7, 1).merge(info_table.cell(7, 3))

    merged_cell.text = ""

    if preview_data.get("inspection_scope"):
        _add_html_to_container(
            merged_cell,
            preview_data["inspection_scope"],
            clear_first=True,
        )

    if preview_data.get("preliminary_review_details"):
        _add_html_to_container(
            merged_cell,
            preview_data["preliminary_review_details"],
            clear_first=False,
        )

    if preview_data.get("finding_statement"):
        _add_html_to_container(
            merged_cell,
            preview_data["finding_statement"],
            clear_first=False,
        )

    # Row 9: In Attendance
    set_header_cell(info_table.cell(8, 0), "In Attendance")
    merged_cell = info_table.cell(8, 1).merge(info_table.cell(8, 3))
    attendance = officer_details.get('in_attendance', [])
    if attendance:
        merged_cell.text = '\n'.join(attendance) if isinstance(attendance, list) else str(attendance)
    else:
        merged_cell.text = 'N/A'

    # Row 10: Certificate Holder/Proponent
    set_header_cell(info_table.cell(9, 0), project_details.get('proponent_label', 'Certificate Holder'))
    merged_cell = info_table.cell(9, 1).merge(info_table.cell(9, 3))
    merged_cell.text = project_details.get('proponent', '')

    # Row 11: Mailing Address
    set_header_cell(info_table.cell(10, 0), "Mailing Address")
    merged_cell = info_table.cell(10, 1).merge(info_table.cell(10, 3))
    merged_cell.text = preview_data.get('mailing_address', 'None') or 'None'

    # Row 12: Inspecting Officer(s)
    set_header_cell(info_table.cell(11, 0), "Inspecting Officer(s)")
    merged_cell = info_table.cell(11, 1).merge(info_table.cell(11, 3))
    inspecting_officers = officer_details.get('inspecting_officers', [])
    if inspecting_officers:
        officer_text = '\n'.join([f"{officer.get('name', '')}\n{officer.get('position', '')}"
                                  for officer in inspecting_officers])
        merged_cell.text = officer_text

    # Row 13: Record Prepared By
    set_header_cell(info_table.cell(12, 0), "Record Prepared By")
    merged_cell = info_table.cell(12, 1).merge(info_table.cell(12, 3))
    record_prepared = officer_details.get('record_prepared_by', {})
    if record_prepared:
        merged_cell.text = f"{record_prepared.get('name', '')}\n{record_prepared.get('position', '')}"

    # Row 14: Record Approved By
    set_header_cell(info_table.cell(13, 0), "Record Approved By")
    merged_cell = info_table.cell(13, 1).merge(info_table.cell(13, 3))
    if approval_info:
        merged_cell.text = f"{approval_info.get('approved_by', '')}\n{approval_info.get('approved_by_position', '')}"

    # Inspection Details Section
    heading = doc.add_heading('INSPECTION DETAILS', level=1)
    heading.runs[0].font.color.rgb = RGBColor(51, 102, 153)
    heading.runs[0].font.size = Pt(11)

    # Requirement Inspection Details tables
    for req in preview_data.get('requirement_details', []):
        _add_requirement_details_table(doc, req)
        # Add spacing between requirements
        doc.add_paragraph()

    # Actions Required and Enforcement Summary table
    summary_table = doc.add_table(rows=0, cols=2)
    summary_table.style = 'Table Grid'

    # Actions Required by Certificate Holder
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    cell.text = f"Actions Required by {project_details.get('proponent_label', 'Certificate Holder')}"
    cell.paragraphs[0].runs[0].font.bold = True
    _set_cell_background(cell, 'BFBFBF')

    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    cell.text = ""

    if preview_data.get("action_required_by_rp"):
        _add_html_to_container(
            cell,
            preview_data["action_required_by_rp"],
        )
    else:
        para = cell.paragraphs[0]
        para.add_run("None at this time.")

    # Enforcement Summary
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    cell.text = "Enforcement Summary"
    cell.paragraphs[0].runs[0].font.bold = True
    _set_cell_background(cell, 'BFBFBF')

    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])

    if preview_data.get("enforcement_summary"):
        _add_html_paragraphs_to_cell(
            cell,
            preview_data["enforcement_summary"],
        )
    else:
        cell.paragraphs[0].text = "None at this time."

    # Regulatory Considerations
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    cell.text = "Regulatory Considerations"
    cell.paragraphs[0].runs[0].font.bold = True
    _set_cell_background(cell, 'BFBFBF')

    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    regulatory_consideration = preview_data.get('regulatory_consideration')
    cell.text = ""

    if regulatory_consideration and regulatory_consideration.get("findings"):
        _add_html_to_container(
            cell,
            regulatory_consideration["findings"],
        )

        # Add photos for regulatory considerations
        for photo in regulatory_consideration.get('photos', []):
            para = cell.add_paragraph()
            para.add_run(f"[Photo {photo.get('photo_number', '')}] {photo.get('photo_caption', '')}")

        # Add figures for regulatory considerations
        for figure in regulatory_consideration.get('figures', []):
            para = cell.add_paragraph()
            para.add_run(f"[Figure {figure.get('figure_number', '')}] {figure.get('figure_caption', '')}")
    else:
        para = cell.paragraphs[0]
        para.add_run("None at this time.")

    # Inspection Record Version Dates
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    cell.text = "Inspection Record Version Dates"
    cell.paragraphs[0].runs[0].font.bold = True
    _set_cell_background(cell, 'BFBFBF')

    # Date Preliminary
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    para = cell.paragraphs[0]
    run = para.add_run("Date Preliminary")
    run.bold = True
    para.add_run('\n')

    if version_date_info and version_date_info.get('preliminary_dates'):
        for date in version_date_info.get('preliminary_dates'):
            para.add_run(f"{date}\n")
    else:
        para.add_run('n/a')

    # Date Issued
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    para = cell.paragraphs[0]
    run = para.add_run("Date Issued")
    run.bold = True
    para.add_run('\n')

    if version_date_info and version_date_info.get('final_date'):
        para.add_run(version_date_info.get('final_date'))

    # Appendices
    if preview_data.get('appendices'):
        row = summary_table.add_row()
        cell = row.cells[0].merge(row.cells[1])
        cell.text = "Appendices:"
        cell.paragraphs[0].runs[0].font.bold = True
        _set_cell_background(cell, 'BFBFBF')

        row = summary_table.add_row()
        cell = row.cells[0].merge(row.cells[1])
        appendix_text = '\n'.join([f"Appendix {app.get('appendix_no', '')}: {app.get('document_title', '')}"
                                   for app in preview_data.get('appendices', [])])
        cell.text = appendix_text

    # Department details
    row = summary_table.add_row()
    cell = row.cells[0].merge(row.cells[1])
    cell.text = "Environmental Assessment Office - Compliance & Enforcement Branch"
    cell.paragraphs[0].runs[0].font.bold = True
    _set_cell_background(cell, 'BFBFBF')

    row = summary_table.add_row()
    dept = department_details

    # Mailing Address
    para = row.cells[0].paragraphs[0]
    run = para.add_run("Mailing Address:")
    run.bold = True
    para.add_run(f"\n{dept.get('address_line1', '')}\n{dept.get('address_line2', '')}")

    # Contact Info
    para = row.cells[1].paragraphs[0]
    run = para.add_run("Phone: ")
    run.bold = True
    para.add_run(f"{dept.get('phone', '')}\n")

    run = para.add_run("Email: ")
    run.bold = True
    _add_hyperlink(para, dept.get('email', ''), f"mailto:{dept.get('email', '')}")
    para.add_run("\n")

    run = para.add_run("Website: ")
    run.bold = True
    _add_hyperlink(para, dept.get('website', ''), f"https://{dept.get('website', '')}")

    return doc
