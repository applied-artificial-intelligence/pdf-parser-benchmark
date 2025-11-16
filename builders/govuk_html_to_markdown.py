"""GOV.UK HTML to Markdown converter.

This module provides functions to convert cleaned GOV.UK HTML content to Markdown format.
It handles headings, paragraphs, lists, tables, and figures while applying normalization rules.

The converter is designed to work with HTML that has been cleaned by the scrape_govuk module,
which removes navigation, headers, footers, and other non-content elements.

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import logging
import re

from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

# Configure logging
logger = logging.getLogger(__name__)


class MarkdownConversionError(Exception):
    """Exception raised when HTML to Markdown conversion fails."""

    pass


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    - Converts multiple spaces to single space
    - Converts multiple newlines to maximum of 2 (paragraph break)
    - Strips leading/trailing whitespace from each line
    - Removes trailing whitespace at end of text

    Args:
        text: Input text with potentially irregular whitespace

    Returns:
        Text with normalized whitespace
    """
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]

    # Join lines and normalize spaces within lines
    text = "\n".join(lines)

    # Replace multiple spaces with single space (within lines)
    text = re.sub(r" +", " ", text)

    # Replace 3+ newlines with exactly 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Final strip
    return text.strip()


def _is_simple_table(table: Tag) -> bool:
    """Determine if a table is simple enough for GFM conversion.

    A simple table has:
    - Uniform columns (all rows have same number of cells)
    - No merged cells (rowspan/colspan)
    - No nested tables
    - Single header row (optional)

    Args:
        table: BeautifulSoup table element

    Returns:
        True if table is simple, False if complex
    """
    rows = table.find_all("tr")
    if not rows:
        return False

    # Check for nested tables
    if table.find("table"):
        return False

    # Check for merged cells
    for row in rows:
        cells = row.find_all(["td", "th"])
        for cell in cells:
            if cell.get("rowspan") or cell.get("colspan"):
                return False

    # Check for uniform column count
    column_counts = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        column_counts.append(len(cells))

    # All rows should have same number of columns
    if len(set(column_counts)) > 1:
        return False

    return True


def _table_to_gfm(table: Tag) -> str:
    """Convert simple table to GitHub Flavored Markdown.

    Args:
        table: BeautifulSoup table element (must be simple table)

    Returns:
        GFM table as string
    """
    rows = table.find_all("tr")
    if not rows:
        return ""

    markdown_rows = []

    # Process first row (may be header)
    first_row = rows[0]
    first_cells = first_row.find_all(["td", "th"])
    has_header = any(cell.name == "th" for cell in first_cells)

    # Extract cell text
    header_row = [cell.get_text(strip=True) for cell in first_cells]
    markdown_rows.append("| " + " | ".join(header_row) + " |")

    # Add separator row
    separator = ["---"] * len(header_row)
    markdown_rows.append("| " + " | ".join(separator) + " |")

    # Process data rows
    start_idx = 1 if has_header else 0
    for row in rows[start_idx:]:
        cells = row.find_all(["td", "th"])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        markdown_rows.append("| " + " | ".join(cell_texts) + " |")

    return "\n".join(markdown_rows)


def _table_to_html(table: Tag) -> str:
    """Preserve complex table as HTML.

    Args:
        table: BeautifulSoup table element

    Returns:
        HTML table as string
    """
    return str(table)


def _convert_table(table: Tag) -> str:
    """Convert table to Markdown or HTML.

    Simple tables are converted to GFM, complex tables are preserved as HTML.

    Args:
        table: BeautifulSoup table element

    Returns:
        Markdown or HTML representation of table
    """
    if _is_simple_table(table):
        logger.debug("Converting simple table to GFM")
        return _table_to_gfm(table)
    else:
        logger.debug("Preserving complex table as HTML")
        return _table_to_html(table)


def _convert_list(list_element: Tag, indent_level: int = 0) -> str:
    """Convert list (ul/ol) to Markdown.

    Handles nested lists recursively.

    Args:
        list_element: BeautifulSoup ul or ol element
        indent_level: Current nesting level (0 = top level)

    Returns:
        Markdown list as string
    """
    is_ordered = list_element.name == "ol"
    items = []
    indent = "  " * indent_level

    list_items = list_element.find_all("li", recursive=False)

    for idx, li in enumerate(list_items, 1):
        # Get direct text content (not from nested lists)
        text_parts = []
        for child in li.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    text_parts.append(text)
            elif isinstance(child, Tag) and child.name not in ["ul", "ol"]:
                text = child.get_text(strip=True)
                if text:
                    text_parts.append(text)

        item_text = " ".join(text_parts)

        # Create list marker
        if is_ordered:
            marker = f"{idx}."
        else:
            marker = "-"

        items.append(f"{indent}{marker} {item_text}")

        # Handle nested lists
        nested_lists = li.find_all(["ul", "ol"], recursive=False)
        for nested in nested_lists:
            nested_md = _convert_list(nested, indent_level + 1)
            items.append(nested_md)

    return "\n".join(items)


def _convert_heading(heading: Tag) -> str:
    """Convert heading to Markdown.

    h1 → #, h2 → ##, etc.

    Args:
        heading: BeautifulSoup heading element (h1-h6)

    Returns:
        Markdown heading as string
    """
    level = int(heading.name[1])  # Extract number from h1, h2, etc.
    text = heading.get_text(strip=True)
    return f"{'#' * level} {text}"


def _convert_paragraph(paragraph: Tag) -> str:
    """Convert paragraph to Markdown.

    Args:
        paragraph: BeautifulSoup p element

    Returns:
        Markdown paragraph as string
    """
    # Build markdown by processing children without modifying the tree
    result_parts: list[str] = []

    def process_element(elem: PageElement) -> None:
        """Recursively process element and its children."""
        if isinstance(elem, NavigableString):
            text = str(elem).strip()
            if text:
                result_parts.append(text)
        elif isinstance(elem, Tag):
            if elem.name == "a":
                href = elem.get("href", "")
                text = elem.get_text(strip=True)
                result_parts.append(f"[{text}]({href})")
            elif elem.name in ["em", "i"]:
                text = elem.get_text(strip=True)
                result_parts.append(f"*{text}*")
            elif elem.name in ["strong", "b"]:
                text = elem.get_text(strip=True)
                result_parts.append(f"**{text}**")
            elif elem.name == "code":
                text = elem.get_text(strip=True)
                result_parts.append(f"`{text}`")
            else:
                # For other elements, process children
                for child in elem.children:
                    process_element(child)

    for child in paragraph.children:
        process_element(child)

    return " ".join(result_parts)


def _convert_figure(figure: Tag) -> str:
    """Convert figure element to Markdown.

    Extracts image with alt text and caption.

    Args:
        figure: BeautifulSoup figure element

    Returns:
        Markdown figure as string
    """
    parts = []

    # Find image
    img = figure.find("img")
    if img:
        src = img.get("src", "")
        alt = img.get("alt", "")
        parts.append(f"![{alt}]({src})")

    # Find caption
    caption = figure.find("figcaption")
    if caption:
        caption_text = caption.get_text(strip=True)
        parts.append(f"\n*{caption_text}*")

    return "\n".join(parts)


def _convert_image(img: Tag) -> str:
    """Convert standalone image to Markdown.

    Args:
        img: BeautifulSoup img element

    Returns:
        Markdown image as string
    """
    src = img.get("src", "")
    alt = img.get("alt", "")
    return f"![{alt}]({src})"


def html_to_markdown(html: str) -> str:
    """Convert GOV.UK HTML to Markdown.

    This function converts cleaned GOV.UK HTML (from scrape_govuk) to Markdown format.
    It handles:
    - Headings (h1-h6)
    - Paragraphs with inline formatting (links, em, strong, code)
    - Lists (ul/ol) including nested lists
    - Tables (simple → GFM, complex → HTML)
    - Figures and images

    Args:
        html: Cleaned HTML content (from scrape_govuk.extract_main_content)

    Returns:
        Markdown content as string

    Raises:
        MarkdownConversionError: If conversion fails
    """
    if not html or not html.strip():
        raise MarkdownConversionError("HTML content is empty")

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        raise MarkdownConversionError(f"Failed to parse HTML: {e}") from e

    # Find main content container (should be present from scraper)
    # If not found, use entire soup
    content = soup.find("main") or soup.find("article") or soup

    if not content:
        raise MarkdownConversionError("No content found in HTML")

    markdown_parts = []

    # Process elements in order
    for element in content.descendants:
        # Skip non-Tag elements (NavigableString, etc.) and already processed
        if not isinstance(element, Tag):
            continue

        # Skip if element is nested within another we'll process
        # For lists and tables, check if they're nested within another list/table
        if element.name in ["ul", "ol"]:
            # Skip if this list is nested within another list
            if element.find_parent(["ul", "ol", "th", "td", "figcaption"]):
                continue
        elif element.name == "table":
            # Skip if this table is nested within another table or list item
            if element.find_parent(["table", "li", "figcaption"]):
                continue
        else:
            # For other elements, skip if nested within paragraph, list item, table cell, or caption
            if element.find_parent(["p", "li", "th", "td", "figcaption"]):
                continue

        # Convert based on element type
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            markdown_parts.append(_convert_heading(element))
        elif element.name == "p":
            markdown_parts.append(_convert_paragraph(element))
        elif element.name in ["ul", "ol"]:
            markdown_parts.append(_convert_list(element))
        elif element.name == "table":
            markdown_parts.append(_convert_table(element))
        elif element.name == "figure":
            markdown_parts.append(_convert_figure(element))
        elif element.name == "img" and not element.find_parent("figure"):
            markdown_parts.append(_convert_image(element))

    # Join parts with double newline (paragraph separator)
    markdown = "\n\n".join(part for part in markdown_parts if part)

    # Apply normalization
    markdown = _normalize_whitespace(markdown)

    if not markdown:
        raise MarkdownConversionError("Conversion resulted in empty content")

    logger.info(f"Converted HTML ({len(html)} bytes) to Markdown ({len(markdown)} bytes)")
    return markdown
