"""Financial table extraction from SEC EDGAR HTML/XBRL filings.

This module provides specialized extraction of financial tables from SEC filings,
handling complex structures like multi-level headers, merged cells, nested tables,
and XBRL tags.

Financial tables from SEC 10-K/10-Q filings often contain:
- Multi-level column headers spanning multiple rows
- Merged cells with rowspan/colspan attributes
- Currency formatting ($, commas, parentheses for negatives)
- Footnote references (superscript numbers/letters)
- XBRL semantic tags embedded in HTML
- Nested tables for complex statements

This module classifies tables by complexity and applies appropriate conversion:
- Simple tables → GitHub Flavored Markdown
- Medium tables → HTML preservation with normalization
- Complex tables → HTML with XBRL metadata preserved
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class TableComplexity(Enum):
    """Classification of table complexity."""

    SIMPLE = "simple"  # Single header row, no merged cells, uniform columns
    MEDIUM = "medium"  # Multi-level headers OR some merged cells
    COMPLEX = "complex"  # Nested tables OR heavy merging OR XBRL tags


@dataclass
class TableMetadata:
    """Metadata about an extracted table.

    Attributes:
        index: Position of table in document (0-based)
        complexity: Classification of table complexity
        row_count: Number of rows in table
        column_count: Number of columns in table (max across rows)
        has_xbrl: Whether table contains XBRL tags
        has_nested_tables: Whether table contains nested tables
        has_merged_cells: Whether table has rowspan/colspan
        header_rows: Number of header rows detected
    """

    index: int
    complexity: TableComplexity
    row_count: int
    column_count: int
    has_xbrl: bool
    has_nested_tables: bool
    has_merged_cells: bool
    header_rows: int


@dataclass
class ExtractedTable:
    """Result of table extraction.

    Attributes:
        content: Extracted table content (Markdown or HTML)
        format: Format of content ("markdown" or "html")
        metadata: Table metadata
        original_html: Original HTML of table (for reference)
    """

    content: str
    format: str
    metadata: TableMetadata
    original_html: str


def _normalize_currency(text: str) -> str:
    """Normalize currency formatting in text.

    Removes $ symbols, commas, and converts parentheses to negative sign.

    Examples:
        "$1,234,567" → "1234567"
        "(123)" → "-123"
        "$1,234.56" → "1234.56"

    Args:
        text: Input text with currency formatting

    Returns:
        Normalized text
    """
    # Remove $ symbols
    text = text.replace("$", "")

    # Remove commas from numbers
    text = re.sub(r"(\d),(\d)", r"\1\2", text)

    # Convert parentheses to negative (accounting notation)
    # Match (number) and replace with -number
    text = re.sub(r"\((\d+(?:\.\d+)?)\)", r"-\1", text)

    return text


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    Collapses multiple spaces, trims lines, normalizes line breaks.

    Args:
        text: Input text with potentially irregular whitespace

    Returns:
        Text with normalized whitespace
    """
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]

    # Join lines
    text = "\n".join(lines)

    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)

    # Replace 3+ newlines with exactly 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _normalize_cell_text(text: str, normalize_currency: bool = True) -> str:
    """Normalize text within a table cell.

    Args:
        text: Cell text to normalize
        normalize_currency: Whether to apply currency normalization

    Returns:
        Normalized cell text
    """
    # Basic whitespace normalization
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    # Apply currency normalization if requested
    if normalize_currency:
        text = _normalize_currency(text)

    return text


def _has_xbrl_tags(table: Tag) -> bool:
    """Check if table contains XBRL tags.

    XBRL tags typically have namespace prefixes like ix:, xbrl:, us-gaap:

    Args:
        table: BeautifulSoup table element

    Returns:
        True if XBRL tags found
    """
    # Look for common XBRL tag patterns
    xbrl_patterns = ["ix:", "xbrl:", "us-gaap:", "dei:", "srt:"]

    # Check all tags in table
    for tag in table.find_all(True):
        tag_name = tag.name.lower()
        for pattern in xbrl_patterns:
            if pattern in tag_name:
                return True

        # Check attributes for XBRL
        for attr in tag.attrs:
            attr_lower = attr.lower()
            if any(pattern in attr_lower for pattern in xbrl_patterns):
                return True

            # Also check attribute values
            attr_value = tag.attrs[attr]
            if isinstance(attr_value, str) and any(
                pattern in attr_value.lower() for pattern in xbrl_patterns
            ):
                return True

    return False


def _has_merged_cells(table: Tag) -> bool:
    """Check if table has merged cells (rowspan/colspan).

    Args:
        table: BeautifulSoup table element

    Returns:
        True if merged cells found
    """
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        for cell in cells:
            if cell.get("rowspan") or cell.get("colspan"):
                return True
    return False


def _count_header_rows(table: Tag) -> int:
    """Count number of header rows in table.

    Header rows can be:
    - Rows in <thead>
    - <tr> elements containing mostly <th> cells

    Args:
        table: BeautifulSoup table element

    Returns:
        Number of header rows
    """
    header_count = 0

    # Check for explicit thead
    thead = table.find("thead")
    if thead:
        header_count = len(thead.find_all("tr", recursive=False))
        return header_count

    # Otherwise, count rows with majority th cells
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        th_count = len(row.find_all("th"))
        # If more than half are th, consider it a header row
        if th_count > len(cells) / 2:
            header_count += 1
        else:
            # Stop at first non-header row
            break

    return header_count


def _get_column_count(table: Tag) -> int:
    """Get maximum column count across all rows.

    Takes into account colspan attributes.

    Args:
        table: BeautifulSoup table element

    Returns:
        Maximum number of columns
    """
    max_cols = 0

    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        col_count = 0
        for cell in cells:
            colspan = cell.get("colspan")
            if colspan:
                try:
                    # Handle both str and list values from BeautifulSoup
                    colspan_val = colspan if isinstance(colspan, str) else str(colspan)
                    col_count += int(colspan_val)
                except (ValueError, TypeError):
                    col_count += 1
            else:
                col_count += 1
        max_cols = max(max_cols, col_count)

    return max_cols


def classify_table(table: Tag) -> TableComplexity:
    """Classify table complexity.

    Classification rules:
    - SIMPLE: Single header row, no merged cells, uniform columns, no XBRL
    - MEDIUM: Multi-level headers OR some merged cells
    - COMPLEX: Nested tables OR XBRL tags OR heavy cell merging

    Args:
        table: BeautifulSoup table element

    Returns:
        TableComplexity classification
    """
    # Check for nested tables
    if table.find("table"):
        return TableComplexity.COMPLEX

    # Check for XBRL tags
    if _has_xbrl_tags(table):
        return TableComplexity.COMPLEX

    # Check for merged cells
    has_merged = _has_merged_cells(table)

    # Count header rows
    header_rows = _count_header_rows(table)

    # Check column uniformity
    rows = table.find_all("tr")
    if not rows:
        return TableComplexity.SIMPLE

    column_counts = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        column_counts.append(len(cells))

    uniform_columns = len(set(column_counts)) == 1

    # Classification logic
    if has_merged:
        # Count how many cells are merged
        merge_count = 0
        total_cells = 0
        for row in rows:
            cells = row.find_all(["td", "th"])
            total_cells += len(cells)
            for cell in cells:
                if cell.get("rowspan") or cell.get("colspan"):
                    merge_count += 1

        # If more than 20% of cells are merged, it's complex
        if total_cells > 0 and merge_count / total_cells > 0.2:
            return TableComplexity.COMPLEX
        else:
            return TableComplexity.MEDIUM

    if header_rows > 1:
        return TableComplexity.MEDIUM

    if not uniform_columns:
        return TableComplexity.MEDIUM

    return TableComplexity.SIMPLE


def _table_to_markdown(table: Tag, normalize: bool = True) -> str:
    """Convert simple table to GitHub Flavored Markdown.

    Only suitable for simple tables with uniform structure.

    Args:
        table: BeautifulSoup table element (must be SIMPLE)
        normalize: Whether to apply currency/whitespace normalization

    Returns:
        GFM table as string
    """
    rows = table.find_all("tr")
    if not rows:
        return ""

    markdown_rows = []

    # Detect header rows
    header_row_count = _count_header_rows(table)

    # Process header row(s)
    if header_row_count > 0:
        # For multiple header rows, concatenate them
        header_cells = []
        for i in range(header_row_count):
            row = rows[i]
            cells = row.find_all(["td", "th"])
            if i == 0:
                header_cells = [
                    _normalize_cell_text(cell.get_text(), normalize) for cell in cells
                ]
            else:
                # Append to existing headers
                for j, cell in enumerate(cells):
                    if j < len(header_cells):
                        additional = _normalize_cell_text(cell.get_text(), normalize)
                        if additional:
                            header_cells[j] = f"{header_cells[j]} {additional}"

        markdown_rows.append("| " + " | ".join(header_cells) + " |")

        # Add separator row
        separator = ["---"] * len(header_cells)
        markdown_rows.append("| " + " | ".join(separator) + " |")
    else:
        # No header, create one from first row
        first_row = rows[0]
        cells = first_row.find_all(["td", "th"])
        header_cells = [_normalize_cell_text(cell.get_text(), normalize) for cell in cells]
        markdown_rows.append("| " + " | ".join(header_cells) + " |")

        # Add separator
        separator = ["---"] * len(header_cells)
        markdown_rows.append("| " + " | ".join(separator) + " |")

        # Adjust starting row index
        header_row_count = 1

    # Process data rows
    for row in rows[header_row_count:]:
        cells = row.find_all(["td", "th"])
        cell_texts = [_normalize_cell_text(cell.get_text(), normalize) for cell in cells]
        markdown_rows.append("| " + " | ".join(cell_texts) + " |")

    return "\n".join(markdown_rows)


def _strip_xbrl_tags(html: str) -> str:
    """Strip XBRL tags from HTML while preserving content.

    Args:
        html: HTML string with XBRL tags

    Returns:
        HTML with XBRL tags removed but content preserved
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find all XBRL tags (ix:, xbrl:, etc.)
    xbrl_prefixes = ["ix:", "xbrl:", "us-gaap:", "dei:", "srt:"]

    for prefix in xbrl_prefixes:
        # Find all tags with this prefix
        for tag in soup.find_all(True):
            if tag.name.startswith(prefix.replace(":", "")):
                # Replace tag with its contents
                tag.unwrap()

    return str(soup)


def _table_to_html(table: Tag, strip_xbrl: bool = False) -> str:
    """Convert table to HTML (for medium/complex tables).

    Args:
        table: BeautifulSoup table element
        strip_xbrl: Whether to strip XBRL tags

    Returns:
        HTML table as string
    """
    html = str(table)

    if strip_xbrl:
        html = _strip_xbrl_tags(html)

    return html


def extract_table(
    table: Tag, index: int = 0, normalize: bool = True, strip_xbrl: bool = False
) -> ExtractedTable:
    """Extract a single table with metadata.

    Args:
        table: BeautifulSoup table element
        index: Position of table in document (0-based)
        normalize: Whether to apply normalization to cell content
        strip_xbrl: Whether to strip XBRL tags from HTML output

    Returns:
        ExtractedTable with content, format, and metadata
    """
    # Classify table
    complexity = classify_table(table)

    # Gather metadata
    rows = table.find_all("tr")
    row_count = len(rows)
    column_count = _get_column_count(table)
    has_xbrl = _has_xbrl_tags(table)
    has_nested = table.find("table") is not None
    has_merged = _has_merged_cells(table)
    header_rows = _count_header_rows(table)

    metadata = TableMetadata(
        index=index,
        complexity=complexity,
        row_count=row_count,
        column_count=column_count,
        has_xbrl=has_xbrl,
        has_nested_tables=has_nested,
        has_merged_cells=has_merged,
        header_rows=header_rows,
    )

    # Convert based on complexity
    if complexity == TableComplexity.SIMPLE:
        content = _table_to_markdown(table, normalize=normalize)
        format_type = "markdown"
    else:
        content = _table_to_html(table, strip_xbrl=strip_xbrl)
        format_type = "html"

    return ExtractedTable(
        content=content, format=format_type, metadata=metadata, original_html=str(table)
    )


def extract_tables_from_html(
    html: str, normalize: bool = True, strip_xbrl: bool = False
) -> list[ExtractedTable]:
    """Extract all tables from SEC filing HTML.

    Args:
        html: HTML content of SEC filing
        normalize: Whether to apply normalization to cell content
        strip_xbrl: Whether to strip XBRL tags from HTML output

    Returns:
        List of ExtractedTable objects

    Raises:
        ValueError: If HTML is empty or invalid
    """
    if not html or not html.strip():
        raise ValueError("HTML content is empty")

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        raise ValueError(f"Failed to parse HTML: {e}") from e

    # Find all tables
    tables = soup.find_all("table")

    if not tables:
        logger.warning("No tables found in HTML")
        return []

    logger.info(f"Found {len(tables)} tables in HTML")

    # Extract each table
    extracted_tables = []
    for idx, table in enumerate(tables):
        try:
            extracted = extract_table(table, index=idx, normalize=normalize, strip_xbrl=strip_xbrl)
            extracted_tables.append(extracted)
            logger.debug(
                f"Extracted table {idx}: {extracted.metadata.complexity.value}, "
                f"{extracted.metadata.row_count}x{extracted.metadata.column_count}"
            )
        except Exception as e:
            logger.warning(f"Failed to extract table {idx}: {e}")
            continue

    logger.info(
        f"Successfully extracted {len(extracted_tables)}/{len(tables)} tables "
        f"({len([t for t in extracted_tables if t.format == 'markdown'])} markdown, "
        f"{len([t for t in extracted_tables if t.format == 'html'])} html)"
    )

    return extracted_tables


def extract_tables_from_file(
    file_path: str, normalize: bool = True, strip_xbrl: bool = False
) -> list[ExtractedTable]:
    """Extract tables from SEC filing HTML file.

    Args:
        file_path: Path to HTML file
        normalize: Whether to apply normalization to cell content
        strip_xbrl: Whether to strip XBRL tags from HTML output

    Returns:
        List of ExtractedTable objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file content is invalid
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file_path}") from e
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}") from e

    return extract_tables_from_html(html, normalize=normalize, strip_xbrl=strip_xbrl)
