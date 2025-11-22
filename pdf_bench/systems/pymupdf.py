"""PyMuPDF-based baseline parser for PDF-to-Markdown conversion.

This module implements a simple baseline parser using PyMuPDF (fitz) that extracts
plain text from PDFs without attempting to preserve structure, tables, or formatting.
It serves as a reference implementation and the simplest parser in the benchmark suite.

The parser focuses on:
- Simple text extraction using PyMuPDF's get_text() method
- Preserving paragraph breaks (double newlines)
- Cache integration for performance
- Basic error handling

This is intentionally a baseline parser - more sophisticated parsers (Marker, Nougat)
will attempt to preserve document structure and formatting.

Examples:
    >>> from pathlib import Path
    >>> parser = PyMuPDFParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(result)
    PosixPath('output/document.md')
"""

from pathlib import Path
from typing import cast

try:
    import fitz  # type: ignore[import-untyped]  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class PyMuPDFParser(BaseParser):
    """Baseline PDF parser using PyMuPDF for simple text extraction.

    This parser extracts plain text from PDFs without attempting to preserve
    document structure, tables, or formatting. It's the simplest parser in
    the benchmark suite and serves as a baseline for comparison.

    The parser integrates with the caching system to avoid redundant parsing
    and provides basic error handling for common PDF issues.

    Attributes:
        name: Parser identifier ('pymupdf')
        version: PyMuPDF library version string

    Examples:
        >>> parser = PyMuPDFParser()
        >>> parser.name
        'pymupdf'
        >>> pdf = Path("document.pdf")
        >>> output = Path("output")
        >>> result = parser.parse(pdf, output)
    """

    def __init__(self) -> None:
        """Initialize PyMuPDF parser.

        Raises:
            ImportError: If PyMuPDF is not installed
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for PyMuPDFParser. Install with: pip install pymupdf"
            )

    @property
    def name(self) -> str:
        """Return the parser's unique identifier.

        Returns:
            str: Always returns 'pymupdf'.
        """
        return "pymupdf"

    @property
    def version(self) -> str:
        """Return the PyMuPDF library version.

        Returns:
            str: PyMuPDF version string (e.g., '1.23.5').
        """
        return cast(str, fitz.version[0])

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output.

        This method extracts plain text from the PDF and saves it as a Markdown file.
        The implementation:
        1. Checks cache for existing result
        2. If cache miss, extracts text using PyMuPDF
        3. Writes text to Markdown file
        4. Stores result in cache
        5. Returns path to generated file

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
            >>> parser = PyMuPDFParser()
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
            # Extract text from PDF
            text = self._extract_text(pdf_path)

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write markdown file
            markdown_path = output_dir / f"{pdf_path.stem}.md"
            markdown_path.write_text(text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, markdown_path, cache_dir)

            return cached_path

        except fitz.FileDataError as e:
            raise RuntimeError(f"Failed to open PDF (corrupted or invalid): {e}") from e
        except fitz.FileNotFoundError as e:
            # This shouldn't happen since we check above, but handle it anyway
            raise FileNotFoundError(f"PDF file not found: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF: {e}") from e

    def _extract_text(self, pdf_path: Path) -> str:
        """Extract plain text from PDF using PyMuPDF.

        This method opens the PDF and extracts text page by page, preserving
        paragraph breaks where appropriate. No attempt is made to preserve
        tables, images, or complex formatting.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            str: Extracted text with basic paragraph breaks preserved.

        Raises:
            fitz.FileDataError: If PDF is corrupted or invalid.
            fitz.FileNotFoundError: If PDF file cannot be found.
        """
        # Open PDF
        doc = fitz.open(pdf_path)

        try:
            # Check if PDF is encrypted/password-protected
            if doc.is_encrypted:
                raise RuntimeError(f"PDF is password-protected: {pdf_path}")

            # Extract text from all pages
            pages_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()

                # Only add non-empty pages
                if page_text.strip():
                    pages_text.append(page_text.strip())

            # Combine pages with double newline separator
            text = "\n\n".join(pages_text)

            # Clean up excessive whitespace while preserving paragraph breaks
            # Replace multiple spaces with single space
            lines = text.split("\n")
            cleaned_lines = [" ".join(line.split()) for line in lines]
            text = "\n".join(cleaned_lines)

            # Normalize paragraph breaks (reduce 3+ newlines to 2)
            while "\n\n\n" in text:
                text = text.replace("\n\n\n", "\n\n")

            return text.strip()

        finally:
            # Always close the document
            doc.close()
