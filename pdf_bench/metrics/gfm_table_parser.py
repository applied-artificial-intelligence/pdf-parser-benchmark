"""GitHub-Flavored Markdown (GFM) table parser for table extraction and analysis.

This module provides utilities for parsing GFM-style tables from Markdown text
and converting them to 2D arrays for comparison and metrics computation. It leverages
the mistune AST parser to extract table structure and handles alignment markers.

GFM tables use pipe (|) characters and hyphens (-) to define tables:

    | Header 1 | Header 2 |
    |----------|----------|
    | Cell 1   | Cell 2   |
    | Cell 3   | Cell 4   |

Alignment markers in the separator row define column alignment:
    - Left:   |:---------|
    - Center: |:--------:|
    - Right:  |---------:|

Key Features:
- GFM table extraction from Markdown AST
- Conversion to 2D array representation
- Alignment marker detection
- Malformed table handling (graceful degradation)
- Whitespace normalization in cells

Example:
    >>> from pdf_bench.metrics.gfm_table_parser import GFMTableParser
    >>> parser = GFMTableParser()
    >>> markdown = "| A | B |\\n|---|---|\\n| 1 | 2 |"
    >>> tables = parser.extract_tables(markdown)
    >>> tables[0]['cells']
    [['A', 'B'], ['1', '2']]
    >>> tables[0]['alignment']
    ['left', 'left']
"""

from dataclasses import dataclass
from typing import Any

from pdf_bench.metrics.ast_parser import MarkdownASTParser


@dataclass
class GFMTable:
    """Structured representation of a GFM table.

    Attributes:
        cells: 2D list of cell contents (includes header row)
        alignment: List of alignment values for each column ('left', 'center', 'right')
        num_rows: Total number of rows (header + body)
        num_cols: Number of columns
    """

    cells: list[list[str]]
    alignment: list[str]
    num_rows: int
    num_cols: int


class GFMTableParser:
    """Parser for extracting GFM tables from Markdown text.

    Uses mistune with GFM table plugin to parse Markdown into AST, then extracts
    table structures and converts them to 2D arrays for analysis and comparison.

    Attributes:
        _ast_parser: MarkdownASTParser instance with table plugin enabled
    """

    def __init__(self) -> None:
        """Initialize the GFM table parser with AST parser."""
        # Ensure table plugin is enabled
        self._ast_parser = MarkdownASTParser(plugins=["table", "strikethrough", "task_lists"])

    def extract_tables(self, markdown: str) -> list[GFMTable]:
        """Extract all GFM tables from Markdown text.

        Args:
            markdown: Markdown text containing zero or more GFM tables

        Returns:
            List of GFMTable objects representing tables found in the document.
            Empty list if no tables found.

        Example:
            >>> parser = GFMTableParser()
            >>> md = "| Name | Age |\\n|------|-----|\\n| Alice | 30 |"
            >>> tables = parser.extract_tables(md)
            >>> len(tables)
            1
            >>> tables[0].cells
            [['Name', 'Age'], ['Alice', '30']]
        """
        ast = self._ast_parser.parse(markdown)
        tables: list[GFMTable] = []

        # Recursively search for table tokens
        self._extract_tables_recursive(ast, tables)

        return tables

    def _extract_tables_recursive(
        self, tokens: list[dict[str, Any]], tables: list[GFMTable]
    ) -> None:
        """Recursively extract tables from AST tokens.

        Args:
            tokens: List of AST tokens to search
            tables: Accumulator list for extracted tables
        """
        for token in tokens:
            if token.get("type") == "table":
                table = self._parse_table_token(token)
                if table:
                    tables.append(table)

            # Recurse into children
            if "children" in token and isinstance(token["children"], list):
                self._extract_tables_recursive(token["children"], tables)

    def _parse_table_token(self, table_token: dict[str, Any]) -> GFMTable | None:
        """Parse a table token into a GFMTable object.

        Args:
            table_token: AST token of type 'table'

        Returns:
            GFMTable object or None if table is malformed

        Table Structure in mistune AST:
            {
                "type": "table",
                "children": [
                    {"type": "table_head", "children": [...]},  # Header cells
                    {"type": "table_body", "children": [...]}   # Body rows
                ]
            }
        """
        try:
            children = table_token.get("children", [])
            if not children:
                return None

            # Extract header and body
            table_head = next((c for c in children if c["type"] == "table_head"), None)
            table_body = next((c for c in children if c["type"] == "table_body"), None)

            if not table_head:
                # Tables must have headers in GFM
                return None

            # Parse header row
            header_cells = self._parse_table_row(table_head.get("children", []))
            if not header_cells:
                return None

            num_cols = len(header_cells)

            # Extract alignment from table_head attrs (if available)
            alignment = self._extract_alignment(table_head, num_cols)

            # Parse body rows
            cells: list[list[str]] = [header_cells]
            if table_body:
                body_rows = table_body.get("children", [])
                for row_token in body_rows:
                    if row_token.get("type") == "table_row":
                        row_cells = self._parse_table_row(row_token.get("children", []))
                        # Pad or truncate to match num_cols
                        row_cells = self._normalize_row(row_cells, num_cols)
                        cells.append(row_cells)

            num_rows = len(cells)

            return GFMTable(cells=cells, alignment=alignment, num_rows=num_rows, num_cols=num_cols)

        except (KeyError, StopIteration, TypeError, ValueError):
            # Malformed table - return None for graceful degradation
            return None

    def _parse_table_row(self, cell_tokens: list[dict[str, Any]]) -> list[str]:
        """Parse a row of table cells.

        Args:
            cell_tokens: List of table_cell tokens

        Returns:
            List of cell text contents (whitespace normalized)
        """
        cells: list[str] = []

        for cell_token in cell_tokens:
            if cell_token.get("type") == "table_cell":
                # Extract text from cell children
                cell_text = self._extract_cell_text(cell_token.get("children", []))
                cells.append(cell_text)

        return cells

    def _extract_cell_text(self, cell_children: list[dict[str, Any]]) -> str:
        """Extract and normalize text from table cell children.

        Args:
            cell_children: List of inline tokens in the cell

        Returns:
            Concatenated and normalized text content
        """
        text_parts: list[str] = []

        for child in cell_children:
            child_type = child.get("type")

            if child_type == "text":
                text_parts.append(child.get("raw", ""))
            elif child_type == "codespan":
                # Inline code - has raw text, not children
                text_parts.append(child.get("raw", ""))
            elif child_type in ("strong", "emphasis"):
                # Recurse into inline formatting (has children)
                text_parts.append(self._extract_cell_text(child.get("children", [])))
            elif child_type == "link":
                # Extract link text (has children)
                text_parts.append(self._extract_cell_text(child.get("children", [])))

        # Join parts and normalize whitespace
        text = "".join(text_parts).strip()
        # Collapse multiple spaces to single space
        text = " ".join(text.split())

        return text

    def _extract_alignment(self, table_head: dict[str, Any], num_cols: int) -> list[str]:
        """Extract column alignment from table header.

        GFM alignment is encoded in the separator row:
            |:---  = left
            |:---: = center
            | ---: = right
            |---   = left (default)

        mistune may store this in table_head attrs or in individual cell attrs.

        Args:
            table_head: table_head token
            num_cols: Number of columns

        Returns:
            List of alignment strings ('left', 'center', 'right')
        """
        # Try to get alignment from table_head attrs
        attrs = table_head.get("attrs", {})
        align = attrs.get("align")

        if align and isinstance(align, list) and len(align) == num_cols:
            # mistune provides align list: [None, 'left', 'center', 'right']
            # None means default (left)
            return [a if a in ("left", "center", "right") else "left" for a in align]

        # Fallback: try to extract from individual cells
        header_cells = table_head.get("children", [])
        alignment: list[str] = []

        for cell in header_cells:
            cell_align = cell.get("attrs", {}).get("align")
            if cell_align in ("left", "center", "right"):
                alignment.append(cell_align)
            else:
                alignment.append("left")

        # Ensure we have exactly num_cols alignment values
        while len(alignment) < num_cols:
            alignment.append("left")

        return alignment[:num_cols]

    def _normalize_row(self, row_cells: list[str], expected_cols: int) -> list[str]:
        """Normalize row to have exactly expected_cols columns.

        Pads short rows with empty strings, truncates long rows.

        Args:
            row_cells: List of cell contents
            expected_cols: Expected number of columns

        Returns:
            Normalized row with exactly expected_cols cells
        """
        if len(row_cells) < expected_cols:
            # Pad with empty cells
            row_cells = row_cells + [""] * (expected_cols - len(row_cells))
        elif len(row_cells) > expected_cols:
            # Truncate extra cells
            row_cells = row_cells[:expected_cols]

        return row_cells

    def table_to_dict(self, table: GFMTable) -> dict[str, Any]:
        """Convert GFMTable to dictionary representation.

        Args:
            table: GFMTable object

        Returns:
            Dictionary with keys: cells, alignment, num_rows, num_cols

        Example:
            >>> parser = GFMTableParser()
            >>> table = GFMTable(
            ...     cells=[['A', 'B'], ['1', '2']],
            ...     alignment=['left', 'right'],
            ...     num_rows=2,
            ...     num_cols=2
            ... )
            >>> parser.table_to_dict(table)
            {'cells': [['A', 'B'], ['1', '2']], 'alignment': ['left', 'right'], ...}
        """
        return {
            "cells": table.cells,
            "alignment": table.alignment,
            "num_rows": table.num_rows,
            "num_cols": table.num_cols,
        }
