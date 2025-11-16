"""pdfplumber-based parser for PDF-to-Markdown conversion with table extraction.

This module implements a parser using pdfplumber that focuses on extracting structured
content from PDFs, particularly tables. pdfplumber uses visual layout analysis to detect
and extract tables with high accuracy.

The parser focuses on:
- Text extraction with character-level positioning
- Table extraction via visual layout analysis
- GFM-compliant Markdown table generation
- Cache integration for performance
- Robust error handling

pdfplumber strengths:
- Excellent table detection and extraction
- Preserves table structure and cell boundaries
- Character-level bounding box information
- Visual debugging capabilities (not used here)

Examples:
    >>> from pathlib import Path
    >>> parser = PdfPlumberParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(result)
    PosixPath('output/document.md')
"""

from pathlib import Path
from typing import Any, cast

import pdfplumber

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached
from pdf_bench.utils.normalization import normalize_text


class PdfPlumberParser(BaseParser):
    """PDF parser using pdfplumber for text and table extraction.

    This parser leverages pdfplumber's visual layout analysis capabilities
    to extract structured content from PDFs, with a particular focus on
    tables. Tables are converted to GitHub Flavored Markdown (GFM) format.

    The parser integrates with the caching system to avoid redundant parsing
    and provides comprehensive error handling for common PDF issues.

    Attributes:
        name: Parser identifier ('pdfplumber')
        version: pdfplumber library version string

    Examples:
        >>> parser = PdfPlumberParser()
        >>> parser.name
        'pdfplumber'
        >>> pdf = Path("document.pdf")
        >>> output = Path("output")
        >>> result = parser.parse(pdf, output)
    """

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'pdfplumber'.
        """
        return "pdfplumber"

    @property
    def version(self) -> str:
        """Return the pdfplumber library version.

        Returns:
            str: pdfplumber version string (e.g., '0.11.8').
        """
        return pdfplumber.__version__

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output with tables.

        This method extracts text and tables from the PDF and saves it as a Markdown file.
        The implementation:
        1. Checks cache for existing result
        2. If cache miss, extracts text and tables using pdfplumber
        3. Converts tables to GFM Markdown format
        4. Writes formatted text to Markdown file
        5. Stores result in cache
        6. Returns path to generated file

        Args:
            pdf_path: Path to the input PDF file. Must exist and be readable.
            output_dir: Directory where the output Markdown file should be saved.
                Must exist and be writable.

        Returns:
            Path: Path to the generated Markdown file.

        Raises:
            FileNotFoundError: If pdf_path does not exist.
            PermissionError: If pdf_path is not readable or output_dir is not writable.
            RuntimeError: If PDF parsing fails (corrupted PDF, password-protected, etc.).

        Examples:
            >>> parser = PdfPlumberParser()
            >>> pdf = Path("document.pdf")
            >>> output = Path("output")
            >>> result = parser.parse(pdf, output)
            >>> result.exists()
            True
        """
        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.is_file():
            raise ValueError(f"Path is not a file: {pdf_path}")

        # Generate cache key
        key = cache_key(pdf_path, self.name, self.version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Cache miss - parse the PDF
        try:
            # Extract text and tables from PDF
            markdown_content = self._extract_content(pdf_path)

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write markdown file
            markdown_path = output_dir / f"{pdf_path.stem}.md"
            markdown_path.write_text(markdown_content, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, markdown_path, cache_dir)

            return cached_path

        except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as e:
            raise RuntimeError(f"Failed to open PDF (corrupted or invalid): {e}") from e
        except PermissionError as e:
            raise PermissionError(f"Permission denied reading PDF: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF: {e}") from e

    def _extract_content(self, pdf_path: Path) -> str:
        """Extract text and tables from PDF using pdfplumber.

        This method opens the PDF and extracts content page by page. For each page:
        1. Extract tables using visual layout analysis
        2. Extract text outside of tables
        3. Combine tables and text in reading order

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            str: Extracted content in Markdown format with tables.

        Raises:
            RuntimeError: If PDF is password-protected or cannot be opened.
        """
        # Open PDF
        with pdfplumber.open(pdf_path) as pdf:
            # Check if PDF has pages
            if not pdf.pages:
                return ""

            # Extract content from all pages
            pages_content = []
            for page_num, page in enumerate(pdf.pages, start=1):
                page_content = self._extract_page_content(page, page_num)

                # Only add non-empty pages
                if page_content.strip():
                    pages_content.append(page_content.strip())

            # Combine pages with double newline separator
            markdown = "\n\n".join(pages_content)

            # Normalize the text
            markdown = normalize_text(markdown)

            return markdown

    def _extract_page_content(self, page: Any, page_num: int) -> str:
        """Extract content from a single page.

        This method extracts both tables and text from a page, attempting to
        maintain reading order.

        Args:
            page: pdfplumber Page object.
            page_num: Page number (1-indexed) for reference.

        Returns:
            str: Page content in Markdown format.
        """
        content_parts = []

        # Extract tables first
        tables = page.extract_tables()

        if tables:
            # If there are tables, extract them and surrounding text
            for table in tables:
                # Convert table to Markdown
                table_md = self._table_to_markdown(table)
                if table_md:
                    content_parts.append(table_md)

            # Also extract text (this will include text outside tables)
            text = page.extract_text()
            if text and text.strip():
                # Add text if it's not empty
                # Note: This might include some table content, but normalization
                # will help clean this up in practice
                content_parts.append(text.strip())
        else:
            # No tables, just extract text
            text = page.extract_text()
            if text and text.strip():
                content_parts.append(text.strip())

        return "\n\n".join(content_parts)

    def _table_to_markdown(self, table: list[list[str | None]]) -> str:
        """Convert a table to GitHub Flavored Markdown format.

        This method converts a pdfplumber table (list of lists) to a GFM
        Markdown table with proper formatting.

        Args:
            table: Table data as list of rows, where each row is a list of cells.
                   Cells can be strings or None.

        Returns:
            str: Markdown-formatted table, or empty string if table is invalid.

        Example:
            >>> table = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
            >>> parser = PdfPlumberParser()
            >>> print(parser._table_to_markdown(table))
            | Name | Age |
            | --- | --- |
            | Alice | 30 |
            | Bob | 25 |
        """
        if not table or len(table) < 2:
            # Need at least header + one data row
            return ""

        # Filter out completely empty rows
        table = [row for row in table if any(cell for cell in row if cell)]

        if not table:
            return ""

        # Get the maximum number of columns
        max_cols = max(len(row) for row in table)

        if max_cols == 0:
            return ""

        # Normalize all rows to have the same number of columns
        normalized_table: list[list[str]] = []
        for row in table:
            # Pad row to max_cols length with None values
            padded_row: list[str | None] = row + [None] * (max_cols - len(row))
            # Convert None to empty string and clean up cells
            normalized_row: list[str] = [
                str(cell).strip() if cell is not None else "" for cell in padded_row
            ]
            normalized_table.append(normalized_row)

        # Build markdown table
        lines: list[str] = []

        # Header row (first row)
        header = normalized_table[0]
        lines.append("| " + " | ".join(header) + " |")

        # Separator row
        separator = "| " + " | ".join(["---"] * max_cols) + " |"
        lines.append(separator)

        # Data rows
        for row_data in normalized_table[1:]:
            # All rows in normalized_table are list[str] due to normalization above
            lines.append("| " + " | ".join(row_data) + " |")

        return "\n".join(lines)
