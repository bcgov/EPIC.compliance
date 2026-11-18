"""Tests that html_to_docx keeps the text and spacing a browser would show."""

import pytest
from docx import Document

from compliance_api.services.enforcement_docx import add_rich_text
from compliance_api.services.inspection_record.html_to_docx import (
    _add_html_to_container, init_list_numbering, prepare_html_for_docx)


def _text(paragraph):
    """Return a paragraph's text including text inside hyperlinks."""
    return ''.join(t.text or '' for t in paragraph._p.xpath('.//w:t'))


def _doc():
    doc = Document()
    init_list_numbering(doc)
    return doc


def _rich_text(html):
    """Render html the way Orders and Warning Letters do; return every paragraph's text."""
    doc = _doc()
    add_rich_text(doc, html)
    return [_text(p) for p in doc.paragraphs]


def _cell_text(html):
    """Render a table through the rich text path and return the first cell's paragraph texts."""
    doc = _doc()
    add_rich_text(doc, html)
    return [_text(p) for p in doc.tables[0].cell(0, 0).paragraphs if _text(p)]


WRAPPED_ITALIC = '<span>under the </span><i>\n<em>Environmental Assessment Act</em></i>'


@pytest.mark.parametrize("html, render", [
    (f'<p>{WRAPPED_ITALIC}</p>', _rich_text),
    (f'<ul><li>{WRAPPED_ITALIC}</li></ul>', _rich_text),
    (f'<table><tr><td><p>{WRAPPED_ITALIC}</p></td></tr></table>', _cell_text),
])
def test_wrapped_markup_after_a_trailing_space_gives_one_space(html, render):
    """Whitespace between tags must not stack on the space the previous run ends with."""
    assert render(html) == ['under the Environmental Assessment Act']


def test_adjacent_runs_with_spaces_on_both_sides_give_one_space():
    """A trailing space followed by a leading space collapses like it does in a browser."""
    assert _rich_text('<p><strong>a </strong><em> b</em></p>') == ['a b']


TWO_LINKS = 'See <a href="http://a">A</a> <a href="http://b">B</a> end'


@pytest.mark.parametrize("html, render", [
    (f'<p>{TWO_LINKS}</p>', _rich_text),
    (f'<ul><li>{TWO_LINKS}</li></ul>', _rich_text),
    (f'<table><tr><td><p>{TWO_LINKS}</p></td></tr></table>', _cell_text),
])
def test_space_between_consecutive_links_is_kept(html, render):
    """The space before a link is judged against the previous link, not the last plain run."""
    assert render(html) == ['See A B end']


def test_trailing_br_after_an_earlier_br_adds_no_blank_paragraph():
    """Only a <br> with content after it starts a new paragraph."""
    doc = Document()
    _add_html_to_container(doc, '<p>one<br>two<br></p><p>next</p>', clear_first=False)
    assert [p.text for p in doc.paragraphs] == ['one', 'two', 'next']


def test_every_br_with_content_after_it_starts_a_paragraph():
    """Each <br> is judged from its own position."""
    doc = Document()
    _add_html_to_container(doc, '<p><strong>one</strong><br>two<br>three</p>', clear_first=False)
    assert [p.text for p in doc.paragraphs] == ['one', 'two', 'three']


def test_content_outside_paragraphs_is_kept():
    """Bare text, headings and quotes survive the trip to DOCX."""
    html = '<div>bare text</div><p>x</p><h2>Heading</h2><blockquote>q</blockquote>'
    assert _rich_text(html) == ['bare text', 'x', 'Heading', 'q']


def test_heading_is_rendered_bold():
    """A heading keeps its emphasis once it is rendered as a paragraph."""
    doc = _doc()
    add_rich_text(doc, '<h2>Heading</h2>')
    assert [r.bold for r in doc.paragraphs[0].runs] == [True]


def test_bare_inline_content_stays_in_one_paragraph():
    """Loose text and the inline tags beside it form a single paragraph."""
    assert _rich_text('<div>Dear <strong>Sir</strong>,</div><p>x</p>') == ['Dear Sir,', 'x']


def test_blocks_inside_a_quote_keep_their_own_paragraphs():
    """A quote wrapping paragraphs and lists is unwrapped, not flattened."""
    html = '<blockquote><p>a</p><ul><li>b</li></ul></blockquote>'
    assert _rich_text(html) == ['a', 'b']


def test_prepare_leaves_well_formed_content_alone():
    """Content that is already paragraphs, lists and tables is not rewrapped."""
    html = '<p>a</p><ul><li>b</li></ul><table><tr><td>c</td></tr></table>'
    assert prepare_html_for_docx(html) == html


def test_every_nested_list_in_an_item_is_rendered():
    """A list item holding two nested lists keeps both."""
    html = '<ul><li>a<ul><li>b</li></ul><ol><li>c</li></ol></li></ul>'
    assert _rich_text(html) == ['a', 'b', 'c']


def test_every_nested_list_in_a_table_cell_item_is_rendered():
    """The same holds for lists inside a table cell."""
    html = '<table><tr><td><ul><li>a<ul><li>b</li></ul><ol><li>c</li></ol></li></ul></td></tr></table>'
    assert _cell_text(html) == ['a', 'b', 'c']
