"""PDFMiner-based parser for PDF-to-text conversion.

PDFMiner.six is a community-maintained fork of PDFMiner that provides
detailed PDF analysis and text extraction with layout information.
"""

from pathlib import Path
from io import StringIO

try:
    import pdfminer  # type: ignore[import-untyped]
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class PDFMinerParser(BaseParser):
    """PDF parser using PDFMiner.six for text extraction.

    PDFMiner provides detailed PDF analysis and text extraction with
    layout information preservation.
    """

    def __init__(self) -> None:
        """Initialize the PDFMinerParser.

        Raises:
            ImportError: If pdfminer.six is not installed
        """
        if not PDFMINER_AVAILABLE:
            raise ImportError(
                "pdfminer.six is required for PDFMinerParser. "
                "Install with: pip install pdfminer.six"
            )

        try:
            self._version = str(pdfminer.__version__)
        except AttributeError:
            self._version = "20231228"

    @property
    def name(self) -> str:
        """Return the parser's unique identifier."""
        return "pdfminer"

    @property
    def version(self) -> str:
        """Return the pdfminer library version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file and generate Markdown output using PDFMiner.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where the output Markdown file should be saved

        Returns:
            Path: Path to the generated Markdown file
        """
        from pdfminer.high_level import extract_text  # type: ignore[import-untyped]

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
            # Extract text using PDFMiner
            text = extract_text(str(pdf_path))

            # Write to output file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(text, encoding="utf-8")

            # Store in cache
            cached_path = store_cached(key, output_path, cache_dir)
            return cached_path

        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF with PDFMiner: {e}") from e
