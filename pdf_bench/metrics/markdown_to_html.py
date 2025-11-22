"""Convert GitHub-Flavored Markdown tables to HTML table structures.

This module provides utilities for converting GFM (GitHub-Flavored Markdown) tables
to HTML <table> elements for use with TEDS (Tree Edit Distance based Similarity)
metric computation.

The conversion preserves table structure including:
- Header rows (converted to <thead> with <th> elements)
- Body rows (converted to <tbody> with <td> elements)
- Column alignment (converted to align attributes)

Example:
    >>> from pdf_bench.metrics.markdown_to_html import markdown_table_to_html
    >>> markdown = "| A | B |\\n|---|---|\\n| 1 | 2 |"
    >>> html = markdown_table_to_html(markdown)
    >>> print(html)
    <table><thead><tr><th>A</th><th>B</th></tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table>
"""

from __future__ import annotations

from pdf_bench.metrics.gfm_table_parser import GFMTable, GFMTableParser


def gfm_table_to_html(table: GFMTable) -> str:
    """Convert a GFMTable object to HTML table string.

    Args:
        table: GFMTable object with cells and alignment

    Returns:
        HTML string representing the table structure

    Example:
        >>> from pdf_bench.metrics.gfm_table_parser import GFMTable
        >>> table = GFMTable(
        ...     cells=[['A', 'B'], ['1', '2']],
        ...     alignment=['left', 'right'],
        ...     num_rows=2,
        ...     num_cols=2
        ... )
        >>> html = gfm_table_to_html(table)
        >>> '<table>' in html and '<th>A</th>' in html
        True
    """
    if not table.cells or table.num_rows == 0:
        return "<table></table>"

    # Start table
    html_parts = ["<table>"]

    # Header row (first row in GFM tables)
    html_parts.append("<thead><tr>")
    for i, cell in enumerate(table.cells[0]):
        # Add alignment if not default (left)
        align_attr = ""
        if i < len(table.alignment) and table.alignment[i] != "left":
            align_attr = f' align="{table.alignment[i]}"'
        html_parts.append(f"<th{align_attr}>{cell}</th>")
    html_parts.append("</tr></thead>")

    # Body rows (remaining rows)
    if table.num_rows > 1:
        html_parts.append("<tbody>")
        for row in table.cells[1:]:
            html_parts.append("<tr>")
            for i, cell in enumerate(row):
                # Add alignment if not default (left)
                align_attr = ""
                if i < len(table.alignment) and table.alignment[i] != "left":
                    align_attr = f' align="{table.alignment[i]}"'
                html_parts.append(f"<td{align_attr}>{cell}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody>")

    html_parts.append("</table>")
    return "".join(html_parts)


def markdown_table_to_html(markdown: str) -> str | None:
    """Convert first GFM table in markdown text to HTML.

    Args:
        markdown: Markdown text containing a GFM table

    Returns:
        HTML string of first table, or None if no table found

    Example:
        >>> markdown = "| Header |\\n|--------|\\n| Cell   |"
        >>> html = markdown_table_to_html(markdown)
        >>> html is not None and '<table>' in html
        True
    """
    parser = GFMTableParser()
    tables = parser.extract_tables(markdown)

    if not tables:
        return None

    return gfm_table_to_html(tables[0])


def extract_all_tables_as_html(markdown: str) -> list[str]:
    """Extract all GFM tables from markdown and convert to HTML.

    Args:
        markdown: Markdown text potentially containing multiple tables

    Returns:
        List of HTML strings, one per table found

    Example:
        >>> markdown = "| A |\\n|---|\\n| 1 |\\n\\nText\\n\\n| B |\\n|---|\\n| 2 |"
        >>> tables = extract_all_tables_as_html(markdown)
        >>> len(tables)
        2
    """
    parser = GFMTableParser()
    tables = parser.extract_tables(markdown)
    return [gfm_table_to_html(table) for table in tables]
