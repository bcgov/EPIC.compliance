"""
PDF Style Converter Utility.

This module provides utilities to convert inline CSS styles to PDF-compatible formats.
The PDF rendering engine used by the docgen service may not support all CSS properties,
so this utility converts unsupported properties to equivalent supported ones.
"""

import re
from typing import Dict

from bs4 import BeautifulSoup


class PDFStyleConverter:
    """Converts inline styles in HTML to PDF-compatible format."""

    # Map of unsupported CSS properties to their PDF-compatible equivalents
    PROPERTY_MAP = {
        'padding-inline-start': 'margin-left',
        'padding-inline-end': 'margin-right',
        'padding-block-start': 'margin-top',
        'padding-block-end': 'margin-bottom',
        'margin-inline-start': 'margin-left',
        'margin-inline-end': 'margin-right',
        'margin-block-start': 'margin-top',
        'margin-block-end': 'margin-bottom',
        'border-inline-start': 'border-left',
        'border-inline-end': 'border-right',
        'border-block-start': 'border-top',
        'border-block-end': 'border-bottom',
    }

    # CSS properties that are generally well-supported in PDF
    SUPPORTED_PROPERTIES = {
        'margin', 'margin-left', 'margin-right', 'margin-top', 'margin-bottom',
        'padding', 'padding-left', 'padding-right', 'padding-top', 'padding-bottom',
        'font-family', 'font-size', 'font-weight', 'font-style',
        'color', 'background-color',
        'text-align', 'text-decoration', 'text-transform',
        'line-height', 'letter-spacing', 'word-spacing',
        'border', 'border-left', 'border-right', 'border-top', 'border-bottom',
        'border-color', 'border-style', 'border-width',
        'width', 'height', 'max-width', 'max-height', 'min-width', 'min-height',
        'display', 'position', 'float', 'clear',
        'vertical-align',
    }

    # Properties that should be removed as they cause issues in PDF
    PROBLEMATIC_PROPERTIES = {
        'white-space': ['pre-wrap', 'pre-line'],  # Specific values that cause issues
        'overflow': True,
        'overflow-x': True,
        'overflow-y': True,
        'box-shadow': True,
        'text-shadow': True,
        'transform': True,
        'transition': True,
        'animation': True,
        'filter': True,
        'backdrop-filter': True,
        'resize': True,
        'user-select': True,
        'pointer-events': True,
        'cursor': True,
    }

    @classmethod
    def convert_html_styles(cls, html_content: str) -> str:
        """
        Convert inline styles in HTML to PDF-compatible format.

        Args:
            html_content: HTML string with inline styles

        Returns:
            HTML string with converted styles
        """
        if not html_content:
            return html_content

        # First fix list ordering issues
        html_content = cls._fix_list_ordering(html_content)

        def style_replacer(match):
            """Replace style attribute with PDF-compatible version."""
            style_content = match.group(1)  # Just the content inside quotes

            converted_styles = cls._convert_style_string(style_content)

            if converted_styles:
                return f'style="{converted_styles}"'
            else:
                # Remove empty style attribute completely
                return ''

        # Process all style attributes
        result = re.sub(r'style="([^"]*?)"', style_replacer, html_content)
        return result

    @classmethod
    def _fix_list_ordering(cls, html_content: str) -> str:
        """
        Fix list ordering issues by properly processing nested lists and ensuring correct numbering.

        Args:
            html_content: HTML string with list ordering issues

        Returns:
            HTML string with corrected list ordering
        """
        if not html_content:
            return html_content

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Process all ordered lists
            for ol in soup.find_all('ol', class_='editor-list-ol'):
                cls._fix_ordered_list(ol)

            # Process all unordered lists
            for ul in soup.find_all('ul', class_='editor-list-ul'):
                cls._fix_unordered_list(ul)

            return str(soup)
        except Exception:  # noqa: B902
            # If BeautifulSoup fails, return original content
            return html_content

    @classmethod
    def _fix_ordered_list(cls, ol_element):
        """Fix numbering in an ordered list element."""
        if not ol_element:
            return

        # Get the list level from class names
        for class_name in ol_element.get('class', []):
            if class_name.startswith('editor-list-ol') and len(class_name) > 13:
                try:
                    level_str = class_name[13:]  # Extract number after 'editor-list-ol'
                    int(level_str)  # Validate it's a number
                except ValueError:
                    pass
                break

        # Reset counter for this list
        counter = 1

        # Process list items
        for li in ol_element.find_all('li', recursive=False):
            # Check if this is a nested list item that should not be numbered
            if 'editor-nested-listitem' in li.get('class', []):
                # Remove the value attribute and add a special class for styling
                if li.has_attr('value'):
                    del li['value']
                li['class'] = li.get('class', []) + ['no-numbering']
            else:
                # This is a regular list item that should be numbered
                li['value'] = str(counter)
                counter += 1

            # Recursively process nested lists
            nested_ol = li.find('ol', class_='editor-list-ol')
            if nested_ol:
                cls._fix_ordered_list(nested_ol)

            nested_ul = li.find('ul', class_='editor-list-ul')
            if nested_ul:
                cls._fix_unordered_list(nested_ul)

    @classmethod
    def _fix_unordered_list(cls, ul_element):
        """Fix bullet points in an unordered list element."""
        if not ul_element:
            return

        # Process list items
        for li in ul_element.find_all('li', recursive=False):
            # Remove value attributes from unordered list items
            if li.has_attr('value'):
                del li['value']

            # Recursively process nested lists
            nested_ol = li.find('ol', class_='editor-list-ol')
            if nested_ol:
                cls._fix_ordered_list(nested_ol)

            nested_ul = li.find('ul', class_='editor-list-ul')
            if nested_ul:
                cls._fix_unordered_list(nested_ul)

    @classmethod
    def _convert_style_string(cls, style_string: str) -> str:
        """
        Convert a CSS style string to PDF-compatible format.

        Args:
            style_string: CSS style string (content of style attribute)

        Returns:
            Converted CSS style string
        """
        if not style_string:
            return ""

        # Parse individual CSS declarations
        declarations = cls._parse_css_declarations(style_string)
        converted_declarations = []

        for prop, value in declarations.items():
            # Convert unsupported properties to supported ones
            if prop in cls.PROPERTY_MAP:
                converted_prop = cls.PROPERTY_MAP[prop]
                converted_declarations.append(f"{converted_prop}: {value}")
            # Keep supported properties as-is
            elif cls._is_supported_property(prop):
                # Check if it's a problematic property with specific values
                if cls._is_problematic_property_value(prop, value):
                    continue  # Skip this property
                converted_declarations.append(f"{prop}: {value}")
            # Skip unsupported properties
            else:
                continue

        return "; ".join(converted_declarations)

    @classmethod
    def _parse_css_declarations(cls, style_string: str) -> Dict[str, str]:
        """
        Parse CSS declarations from a style string.

        Args:
            style_string: CSS style string

        Returns:
            Dictionary of property: value pairs
        """
        declarations = {}

        # Split by semicolon and process each declaration
        for declaration in style_string.split(';'):
            declaration = declaration.strip()
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                prop = prop.strip().lower()
                value = value.strip()
                if prop and value:
                    declarations[prop] = value

        return declarations

    @classmethod
    def _is_supported_property(cls, prop: str) -> bool:
        """Check if a CSS property is supported in PDF."""
        # Check exact match
        if prop in cls.SUPPORTED_PROPERTIES:
            return True

        # Check prefixes (e.g., border-left-width matches border-)
        for supported in cls.SUPPORTED_PROPERTIES:
            if prop.startswith(supported + '-'):
                return True

        return False

    @classmethod
    def _is_problematic_property_value(cls, prop: str, value: str) -> bool:
        """Check if a property-value combination is problematic in PDF."""
        if prop in cls.PROBLEMATIC_PROPERTIES:
            problematic_values = cls.PROBLEMATIC_PROPERTIES[prop]
            if isinstance(problematic_values, list):
                return value.lower() in [v.lower() for v in problematic_values]
            else:
                return True  # Property itself is problematic
        return False


def convert_inline_styles_for_pdf(html_content: str) -> str:
    """
    Convert HTML inline styles for PDF compatibility.

    Args:
        html_content: HTML string with inline styles

    Returns:
        HTML string with PDF-compatible styles
    """
    return PDFStyleConverter.convert_html_styles(html_content)
