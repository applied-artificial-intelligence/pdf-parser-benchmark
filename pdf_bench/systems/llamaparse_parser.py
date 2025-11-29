"""LlamaParse parser - GenAI-native document parsing from LlamaIndex.

This module implements a parser using LlamaIndex's LlamaParse cloud service,
which uses LLMs to parse PDFs into markdown format optimized for RAG pipelines.

LlamaParse features:
- GenAI-native parsing using LLMs for document understanding
- Multiple parsing modes (fast, premium, multimodal)
- Good table extraction for simple/medium complexity tables
- 90+ file format support
- 100+ language support

Cost Model (credits per page):
    - Basic (no AI): 1 credit ($0.001/page NA, $0.0015/page EU)
    - Cost-effective: 3 credits ($0.003/page)
    - Agentic: 10 credits ($0.01/page)
    - Agentic Plus: 90 credits ($0.09/page)

Free Tier:
    - 1,000 pages per day
    - 7,000 pages per week

API Limits:
    - Max file size: 100 MB
    - Concurrent requests vary by plan

Examples:
    >>> from pathlib import Path
    >>> parser = LlamaParseParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")

Environment Variables:
    LLAMA_CLOUD_API_KEY: API key for LlamaCloud (required)
        Get your key from: https://cloud.llamaindex.ai/api-key
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

try:
    from llama_parse import LlamaParse

    LLAMAPARSE_AVAILABLE = True
except ImportError:
    LLAMAPARSE_AVAILABLE = False

try:
    import fitz  # PyMuPDF for page counting

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class LlamaParseParser:
    """Parser using LlamaIndex's LlamaParse cloud service."""

    # Pricing: Cost-effective mode = 3 credits = $0.003/page (NA)
    # Using cost-effective as default
    COST_PER_PAGE = 0.003

    # Parsing mode options
    PARSING_MODES = {
        "fast": {"credits": 1, "cost": 0.001},
        "cost_effective": {"credits": 3, "cost": 0.003},
        "agentic": {"credits": 10, "cost": 0.01},
        "premium": {"credits": 90, "cost": 0.09},
    }

    def __init__(
        self,
        parsing_mode: str = "cost_effective",
        language: str = "en",
        **kwargs: Any,
    ):
        """Initialize LlamaParse parser.

        Args:
            parsing_mode: Parsing mode - one of 'fast', 'cost_effective',
                'agentic', or 'premium'. Default is 'cost_effective'.
            language: Document language (default: 'en')
            **kwargs: Additional options passed to LlamaParse

        Raises:
            ImportError: If llama-parse is not installed
            ValueError: If required environment variables are missing
        """
        if not LLAMAPARSE_AVAILABLE:
            raise ImportError(
                "llama-parse is required for LlamaParse parser. "
                "Install with: pip install llama-parse"
            )

        # Get API key from environment
        self.api_key = os.getenv("LLAMA_CLOUD_API_KEY")

        if not self.api_key:
            raise ValueError(
                "LLAMA_CLOUD_API_KEY environment variable must be set. "
                "Get your API key from https://cloud.llamaindex.ai/api-key"
            )

        # Validate and set parsing mode
        if parsing_mode not in self.PARSING_MODES:
            raise ValueError(
                f"Invalid parsing_mode '{parsing_mode}'. "
                f"Must be one of: {list(self.PARSING_MODES.keys())}"
            )

        self.parsing_mode = parsing_mode
        self.language = language
        self.extra_kwargs = kwargs

        # Set cost based on mode
        self.COST_PER_PAGE = self.PARSING_MODES[parsing_mode]["cost"]

        # Initialize client
        self.client = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",
            language=language,
            verbose=False,
        )

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0

        # Parser identification
        self._name = "llamaparse"
        self._version = self._get_version()

    def _get_version(self) -> str:
        """Get llama-parse package version."""
        try:
            import llama_parse

            return getattr(llama_parse, "__version__", "0.6.x")
        except Exception:
            return "0.6.x"

    @property
    def name(self) -> str:
        """Return parser name."""
        return self._name

    @property
    def version(self) -> str:
        """Return parser version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using LlamaParse.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If LlamaParse API call fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"

        # Get page count for cost tracking
        page_count = self._get_page_count(pdf_path)

        start_time = time.time()

        try:
            # Call LlamaParse - load_data returns list of Document objects
            documents = self.client.load_data(str(pdf_path))

            # Combine all document texts into markdown
            markdown = self._documents_to_markdown(documents)

        except Exception as e:
            raise RuntimeError(f"LlamaParse processing failed: {e}") from e

        _ = time.time() - start_time  # Available for future logging

        # Write markdown
        output_path.write_text(markdown, encoding="utf-8")

        # Track costs
        cost = page_count * self.COST_PER_PAGE
        self.last_parsing_cost = cost
        self.total_cost += cost
        self.pages_processed += page_count

        return output_path

    def _get_page_count(self, pdf_path: Path) -> int:
        """Get page count from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages
        """
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                count = len(doc)
                doc.close()
                return count
            except Exception:
                pass

        # Fallback: estimate from file size (~75KB per page)
        return max(1, pdf_path.stat().st_size // 75000)

    def _documents_to_markdown(self, documents: list) -> str:
        """Convert LlamaParse documents to markdown.

        Args:
            documents: List of Document objects from LlamaParse

        Returns:
            Combined markdown text
        """
        if not documents:
            return "# Empty Document\n\nNo content extracted."

        parts = []
        for doc in documents:
            # LlamaParse Document has .text attribute with markdown content
            if hasattr(doc, "text") and doc.text:
                parts.append(doc.text.strip())
            elif hasattr(doc, "content") and doc.content:
                parts.append(doc.content.strip())
            elif isinstance(doc, str):
                parts.append(doc.strip())

        if not parts:
            return "# Empty Document\n\nNo content extracted."

        return "\n\n".join(parts)

    def get_cost_info(self) -> dict[str, Any]:
        """Get cost information for this parser.

        Returns:
            Dictionary with cost information
        """
        return {
            "parser": "llamaparse",
            "parsing_mode": self.parsing_mode,
            "cost_per_page": self.COST_PER_PAGE,
            "last_parsing_cost": self.last_parsing_cost,
            "total_cost": self.total_cost,
            "pages_processed": self.pages_processed,
        }

    @staticmethod
    def validate_credentials() -> tuple[bool, str]:
        """Validate LlamaParse credentials.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not LLAMAPARSE_AVAILABLE:
            return False, "llama-parse package not installed"

        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not api_key:
            return False, "LLAMA_CLOUD_API_KEY not set"

        # Try to initialize client
        try:
            LlamaParse(api_key=api_key, result_type="markdown")
            return True, "Client initialized successfully"
        except Exception as e:
            return False, f"Failed to initialize client: {e}"
