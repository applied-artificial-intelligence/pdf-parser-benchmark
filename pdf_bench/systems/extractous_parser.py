"""Extractous-based parser for PDF-to-text conversion.

Extractous is a Rust-based universal document extractor supporting 50+ file formats
with fast, memory-efficient text extraction.
"""

from pathlib import Path

try:
    import extractous  # type: ignore[import-untyped]

    EXTRACTOUS_AVAILABLE = True
except ImportError:
    EXTRACTOUS_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class ExtractousParser(BaseParser):
    """PDF parser using Extractous for text extraction.

    Extractous is a Rust-based universal document extractor with support
    for 50+ file formats including PDF.
    """

    def __init__(self) -> None:
        """Initialize the ExtractousParser.

        Raises:
            ImportError: If extractous is not installed
        """
        if not EXTRACTOUS_AVAILABLE:
            raise ImportError(
                "extractous is required for ExtractousParser. Install with: pip install extractous"
            )

        try:
            self._version = str(extractous.__version__)
        except AttributeError:
            self._version = "0.3.0"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "extractous"

    @property
    def version(self) -> str:
        """Return the extractous library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using Extractous.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from extractous import Extractor  # type: ignore[import-untyped]

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

        # Parse the PDF
        try:
            extractor = Extractor()
            # extract_file_to_string returns (text, metadata) tuple
            text, metadata = extractor.extract_file_to_string(str(pdf_path))

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with Extractous: {e}") from e
