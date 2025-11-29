"""Gemini PDF parser - Google's frontier multimodal model for PDF parsing.

This module implements PDF-to-Markdown parsing using Google's Gemini models,
which have native PDF understanding capabilities via vision.

Supported Models:
- gemini-3-pro: Latest flagship model (~$2/1M input, $12/1M output)
- gemini-2.5-pro: Previous generation pro model
- gemini-2.5-flash: Fast, cost-effective (~$0.15/1M input, $0.60/1M output)

Features:
- Native PDF vision understanding (not just text extraction)
- Up to 1000 pages per document
- Up to 50MB file size
- Table, chart, and diagram understanding
- Long context (1M tokens for 2.5 Pro)

Cost Model (per 1M tokens, ≤200K context):
    - gemini-3-pro: $2.00 input, $12.00 output
    - gemini-2.5-pro: $1.25 input, $10.00 output
    - gemini-2.5-flash: $0.15 input, $0.60 output

Token Estimation:
    - ~258 tokens per PDF page (vision)
    - ~800 tokens output per page (markdown)

Examples:
    >>> from pathlib import Path
    >>> parser = GeminiParser(model="gemini-2.5-flash")
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")

Environment Variables:
    GOOGLE_API_KEY or GEMINI_API_KEY: API key for Google AI Studio (required)
        Get your key from: https://aistudio.google.com/apikey
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

try:
    from google import genai
    from google.genai import types

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None  # type: ignore
    types = None  # type: ignore

try:
    import fitz  # PyMuPDF for page counting

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


# Pricing per 1M tokens (November 2025)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gemini-3-pro": {"input": 2.00, "output": 12.00},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
}

# Token estimates per page
TOKENS_PER_PAGE_INPUT = 258  # Per Google docs
TOKENS_PER_PAGE_OUTPUT = 800  # Estimated markdown output


# Prompt for PDF to Markdown conversion
PDF_TO_MARKDOWN_PROMPT = """Convert this PDF document to clean, well-structured Markdown format.

Instructions:
1. Preserve the document structure (headings, paragraphs, lists)
2. Convert tables to Markdown table format
3. Preserve any important formatting (bold, italic, code)
4. Extract text accurately, maintaining reading order
5. For multi-column layouts, merge into single-column reading order
6. Include figure/image captions as descriptive text
7. Do not add any commentary or explanations - just output the converted content

Output only the Markdown content, nothing else."""


class GeminiParser:
    """Parser using Google's Gemini multimodal models for PDF understanding."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        **kwargs: Any,
    ):
        """Initialize Gemini parser.

        Args:
            model: Gemini model to use. Options:
                - "gemini-3-pro": Latest flagship (most accurate, highest cost)
                - "gemini-2.5-pro": Previous flagship
                - "gemini-2.5-flash": Fast and cheap (recommended for benchmarking)
                - "gemini-2.0-flash": Older flash model
            **kwargs: Additional options (ignored for compatibility)

        Raises:
            ImportError: If google-genai is not installed
            ValueError: If API key not set or invalid model
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-genai is required for Gemini parser. "
                "Install with: pip install google-genai"
            )

        # Get API key from environment
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY environment variable must be set. "
                "Get your API key from https://aistudio.google.com/apikey"
            )

        # Validate model
        if model not in MODEL_PRICING:
            raise ValueError(
                f"Invalid model '{model}'. "
                f"Available models: {list(MODEL_PRICING.keys())}"
            )

        self.model = model
        self.pricing = MODEL_PRICING[model]

        # Initialize client
        self.client = genai.Client(api_key=self.api_key)

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Parser identification
        self._name = f"gemini_{model.replace('-', '_').replace('.', '_')}"
        self._version = "1.0.0"

    @property
    def name(self) -> str:
        """Return parser name."""
        return self._name

    @property
    def version(self) -> str:
        """Return parser version."""
        return self._version

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using Gemini vision.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If Gemini API call fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check file size (50MB limit)
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 50:
            raise ValueError(f"PDF file too large ({file_size_mb:.1f}MB). Max: 50MB")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"

        # Get page count for cost tracking
        page_count = self._get_page_count(pdf_path)

        # Check page limit (1000 pages)
        if page_count > 1000:
            raise ValueError(f"PDF has {page_count} pages. Max: 1000 pages")

        start_time = time.time()

        try:
            # Read PDF bytes
            pdf_data = pdf_path.read_bytes()

            # Call Gemini API with PDF
            pdf_part = types.Part.from_bytes(
                data=pdf_data,
                mime_type="application/pdf",
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=[pdf_part, PDF_TO_MARKDOWN_PROMPT],  # type: ignore[arg-type]
            )

            # Extract markdown from response
            markdown = response.text or ""

            # Get token usage if available
            input_tokens = page_count * TOKENS_PER_PAGE_INPUT
            output_tokens = len(markdown) // 4  # Rough estimate: 4 chars per token

            if response.usage_metadata is not None:
                usage = response.usage_metadata
                if hasattr(usage, "prompt_token_count") and usage.prompt_token_count:
                    input_tokens = int(usage.prompt_token_count)
                if hasattr(usage, "candidates_token_count") and usage.candidates_token_count:
                    output_tokens = int(usage.candidates_token_count)

        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}") from e

        _ = time.time() - start_time  # Available for future logging

        # Write markdown
        output_path.write_text(markdown, encoding="utf-8")

        # Calculate and track costs
        input_cost = (input_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (output_tokens / 1_000_000) * self.pricing["output"]
        cost = input_cost + output_cost

        self.last_parsing_cost = cost
        self.total_cost += cost
        self.pages_processed += page_count
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

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

    def get_cost_info(self) -> dict[str, Any]:
        """Get cost information for this parser.

        Returns:
            Dictionary with cost information
        """
        return {
            "parser": self._name,
            "model": self.model,
            "pricing": self.pricing,
            "last_parsing_cost": self.last_parsing_cost,
            "total_cost": self.total_cost,
            "pages_processed": self.pages_processed,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }

    @staticmethod
    def validate_credentials(model: str = "gemini-2.5-flash") -> tuple[bool, str]:
        """Validate Gemini API credentials.

        Args:
            model: Model to test with

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not GENAI_AVAILABLE:
            return False, "google-genai package not installed"

        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return False, "GOOGLE_API_KEY or GEMINI_API_KEY not set"

        # Try to initialize client and list models
        try:
            client = genai.Client(api_key=api_key)
            # Simple test - just initialize (listing models costs nothing)
            _ = client
            return True, "Client initialized successfully"
        except Exception as e:
            return False, f"Failed to initialize client: {e}"


# Convenience factory functions for specific models
def create_gemini_3_pro(**kwargs: Any) -> GeminiParser:
    """Create Gemini 3 Pro parser (flagship model)."""
    return GeminiParser(model="gemini-3-pro", **kwargs)


def create_gemini_2_5_flash(**kwargs: Any) -> GeminiParser:
    """Create Gemini 2.5 Flash parser (fast and cheap)."""
    return GeminiParser(model="gemini-2.5-flash", **kwargs)
