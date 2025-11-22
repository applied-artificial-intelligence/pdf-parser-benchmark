"""HTML table normalization for canonical comparison.

This module provides utilities for normalizing HTML tables to enable
fair comparison between ground truth and predicted tables. It handles:
- Tag and attribute normalization
- Colspan and rowspan expansion
- Whitespace normalization
- Extraction to 2D array format

For use with TEDS (Tree Edit Distance-based Similarity) metrics.
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString


class TableCell:
    """Represents a single table cell with its content and span information."""

    def __init__(
        self,
        content: str,
        rowspan: int = 1,
        colspan: int = 1,
        is_header: bool = False,
    ) -> None:
        """Initialize a table cell.

        Args:
            content: Text content of the cell
            rowspan: Number of rows spanned (default 1)
            colspan: Number of columns spanned (default 1)
            is_header: Whether this is a header cell (th vs td)
        """
        self.content = content.strip()
        self.rowspan = rowspan
        self.colspan = colspan
        self.is_header = is_header


def normalize_html_table(html: str) -> str:
    """Normalize HTML table for canonical comparison.

    Applies the following normalization steps:
    1. Parse HTML with BeautifulSoup
    2. Lowercase all tag names and attributes
    3. Sort attributes alphabetically
    4. Normalize whitespace inside tags and cell content
    5. Remove empty attributes
    6. Standardize self-closing tags

    Args:
        html: HTML string containing a table element

    Returns:
        Normalized HTML string

    Example:
        >>> html = '<TABLE class="data" id="tbl1"><TR><TD>A</TD></TR></TABLE>'
        >>> normalize_html_table(html)
        '<table class="data" id="tbl1"><tr><td>A</td></tr></table>'
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find the table element
    table = soup.find("table")
    if not table:
        return ""

    # Normalize all tags recursively
    _normalize_tag(table)

    return str(table)


def _normalize_tag(tag: Tag) -> None:
    """Recursively normalize a BeautifulSoup tag.

    Args:
        tag: BeautifulSoup Tag object to normalize
    """
    # Lowercase tag name
    tag.name = tag.name.lower()

    # Normalize attributes
    if tag.attrs:
        # Lowercase attribute names and normalize values
        normalized_attrs: dict[str, str] = {}
        for key, value in sorted(tag.attrs.items()):
            key_lower = key.lower()
            if isinstance(value, list):
                # Join list values (e.g., class="a b")
                value_str = " ".join(str(v).strip() for v in value)
            else:
                value_str = str(value).strip()

            # Only keep non-empty attributes
            if value_str:
                normalized_attrs[key_lower] = value_str

        # Cast needed because BeautifulSoup types are complex
        tag.attrs = normalized_attrs  # type: ignore[assignment]

    # Normalize text content (whitespace)
    if tag.string and isinstance(tag.string, NavigableString):
        tag.string.replace_with(tag.string.strip())

    # Recursively normalize children
    for child in tag.children:
        if isinstance(child, Tag):
            _normalize_tag(child)


def extract_table_array(html: str) -> list[list[str]]:
    """Extract HTML table to 2D array format.

    Handles colspan and rowspan by expanding cells to fill
    the appropriate number of positions in the 2D grid.

    Args:
        html: HTML string containing a table element

    Returns:
        2D list representing the table structure, where each
        inner list is a row, and each element is cell content

    Example:
        >>> html = '<table><tr><td>A</td><td>B</td></tr></table>'
        >>> extract_table_array(html)
        [['A', 'B']]

        >>> html = '<table><tr><td colspan="2">A</td></tr></table>'
        >>> extract_table_array(html)
        [['A', 'A']]
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    # First pass: parse all cells with span information
    rows_data: list[list[TableCell]] = []

    for row in table.find_all("tr"):
        row_cells: list[TableCell] = []

        for cell in row.find_all(["td", "th"]):
            content = cell.get_text(strip=True)
            rowspan_val = cell.get("rowspan", "1")
            colspan_val = cell.get("colspan", "1")
            rowspan = int(rowspan_val) if isinstance(rowspan_val, str | int) else 1
            colspan = int(colspan_val) if isinstance(colspan_val, str | int) else 1
            is_header = cell.name == "th"

            cell_obj = TableCell(
                content=content,
                rowspan=rowspan,
                colspan=colspan,
                is_header=is_header,
            )
            row_cells.append(cell_obj)

        if row_cells:  # Only add non-empty rows
            rows_data.append(row_cells)

    if not rows_data:
        return []

    # Second pass: expand spans to create 2D grid
    return _expand_spans_to_grid(rows_data)


def _expand_spans_to_grid(rows_data: list[list[TableCell]]) -> list[list[str]]:
    """Expand cells with rowspan/colspan into a regular 2D grid.

    Args:
        rows_data: List of rows, each containing TableCell objects

    Returns:
        2D list with cells expanded to fill their span areas
    """
    # Determine grid dimensions
    num_rows = len(rows_data)
    if num_rows == 0:
        return []

    # Calculate max columns needed (considering colspans)
    max_cols = 0
    for row_cells in rows_data:
        cols_in_row = sum(cell.colspan for cell in row_cells)
        max_cols = max(max_cols, cols_in_row)

    # Initialize empty grid
    grid: list[list[str]] = [["" for _ in range(max_cols)] for _ in range(num_rows)]

    # Track which cells are already filled (due to rowspan)
    filled: list[list[bool]] = [[False for _ in range(max_cols)] for _ in range(num_rows)]

    # Fill the grid
    for row_idx, row_cells in enumerate(rows_data):
        col_idx = 0

        for cell in row_cells:
            # Skip already-filled columns (from previous rowspans)
            while col_idx < max_cols and filled[row_idx][col_idx]:
                col_idx += 1

            if col_idx >= max_cols:
                # This shouldn't happen with well-formed tables,
                # but handle gracefully
                break

            # Fill the cell and its span area
            for r in range(cell.rowspan):
                for c in range(cell.colspan):
                    target_row = row_idx + r
                    target_col = col_idx + c

                    # Boundary check
                    if target_row < num_rows and target_col < max_cols:
                        grid[target_row][target_col] = cell.content
                        filled[target_row][target_col] = True

            col_idx += cell.colspan

    return grid


def tables_equal(table1_html: str, table2_html: str) -> bool:
    """Check if two HTML tables are structurally equivalent.

    Compares tables after normalization and extraction to 2D arrays.

    Args:
        table1_html: First HTML table string
        table2_html: Second HTML table string

    Returns:
        True if tables have identical structure and content after
        normalization, False otherwise

    Example:
        >>> t1 = '<table><tr><td>A</td><td>B</td></tr></table>'
        >>> t2 = '<TABLE><TR><TD>A</TD><TD>B</TD></TR></TABLE>'
        >>> tables_equal(t1, t2)
        True
    """
    array1 = extract_table_array(normalize_html_table(table1_html))
    array2 = extract_table_array(normalize_html_table(table2_html))

    return array1 == array2
