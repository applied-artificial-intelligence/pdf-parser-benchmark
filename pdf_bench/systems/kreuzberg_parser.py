"""Kreuzberg-based parser for PDF-to-text conversion.

Kreuzberg is a Rust-based document intelligence framework supporting 50+ formats
with async processing and built-in OCR capabilities.

NOTE: By default, this parser disables OCR to avoid loading heavy ML models.
For OCR-based extraction, use force_ocr=True in parser_options.
"""

import asyncio
from pathlib import Path

try:
    import kreuzberg
    from kreuzberg import ExtractionConfig

    KREUZBERG_AVAILABLE = True
except ImportError:
    KREUZBERG_AVAILABLE = False
    ExtractionConfig = None  # type: ignore[misc,assignment]

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class KreuzbergParser(BaseParser):
    """PDF parser using Kreuzberg for text extraction.

    Kreuzberg is a Rust-based framework with async support and OCR capabilities.

    By default, OCR is disabled for performance. Enable with force_ocr=True.
    """

    def __init__(self, force_ocr: bool = False) -> None:
        """Initialize the KreuzbergParser.

        Args:
            force_ocr: If True, enable OCR for scanned documents (memory-intensive)

        Raises:
            ImportError: If kreuzberg is not installed
        """
        if not KREUZBERG_AVAILABLE:
            raise ImportError(
                "kreuzberg is required for KreuzbergParser. Install with: pip install kreuzberg"
            )

        self._force_ocr = force_ocr

        try:
            self._version = str(kreuzberg.__version__)
        except AttributeError:
            self._version = "3.21.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "kreuzberg"

    @property
    def version(self) -> str:
        """Return the kreuzberg library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using Kreuzberg.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from kreuzberg import extract_file

        # Validate input
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Generate cache key
        key = cache_key(pdf_path, self.name, self.version)

        # Check cache
        cache_dir = Path(".cache")
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Parse the PDF using async function
        try:
            # Configure extraction - disable OCR by default to avoid loading ML models
            if self._force_ocr:
                config = ExtractionConfig(force_ocr=True)
            else:
                # Text-only mode: no OCR backend, much faster and lighter
                config = ExtractionConfig(ocr_backend=None, force_ocr=False)

            async def extract_async() -> str:
                result = await extract_file(str(pdf_path), config=config)
                return result.content

            # Run async function in sync context
            text = asyncio.run(extract_async())

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Kreuzberg: {e}") from e
