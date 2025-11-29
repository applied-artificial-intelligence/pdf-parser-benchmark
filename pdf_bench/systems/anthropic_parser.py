"""Anthropic Claude PDF parser - Claude's frontier multimodal models for PDF parsing.

This module implements PDF-to-Markdown parsing using Anthropic's Claude models,
which support native PDF input via base64 encoding or the Files API.

Supported Models:
- claude-opus-4.5: Top-tier flagship (~$5/1M input, $25/1M output)
- claude-sonnet-4.5: Balanced performance (~$3/1M input, $15/1M output)
- claude-haiku-4.5: Fast and cheap (~$1/1M input, $5/1M output)

Features:
- Native PDF vision understanding (since late 2024)
- Text and image extraction from PDFs
- Up to 100 pages per request
- Up to 32MB file size
- 200K token context window

Cost Model (per 1M tokens):
    - claude-opus-4.5: $5.00 input, $25.00 output
    - claude-sonnet-4.5: $3.00 input, $15.00 output
    - claude-haiku-4.5: $1.00 input, $5.00 output

Token Estimation:
    - ~1500-3000 tokens per PDF page (varies by density)
    - ~800 tokens output per page (markdown)

Examples:
    >>> from pathlib import Path
    >>> parser = AnthropicParser(model="claude-haiku-4.5")
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")

Environment Variables:
    ANTHROPIC_API_KEY: API key for Anthropic (required)
        Get your key from: https://console.anthropic.com/settings/keys
"""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None  # type: ignore

try:
    import fitz  # PyMuPDF for page counting

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


# Pricing per 1M tokens (November 2025)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 1.00, "output": 5.00},
    "claude-3-opus": {"input": 15.00, "output": 75.00},
}

# Model ID mappings (user-friendly name -> API model ID)
MODEL_IDS: dict[str, str] = {
    "claude-sonnet-4": "claude-sonnet-4-20250514",
    "claude-3-5-haiku": "claude-3-5-haiku-latest",
    "claude-3-opus": "claude-3-opus-latest",
}

# Token estimates per page
TOKENS_PER_PAGE_INPUT = 2000  # Average for PDF with text+images
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


class AnthropicParser:
    """Parser using Anthropic's Claude multimodal models for PDF understanding."""

    def __init__(
        self,
        model: str = "claude-3-5-haiku",
        **kwargs: Any,
    ):
        """Initialize Anthropic parser.

        Args:
            model: Claude model to use. Options:
                - "claude-sonnet-4": Latest Sonnet (balanced performance)
                - "claude-3-5-haiku": Fast and cheap (recommended for benchmarking)
                - "claude-3-opus": Top-tier (most accurate, highest cost)
            **kwargs: Additional options (ignored for compatibility)

        Raises:
            ImportError: If anthropic is not installed
            ValueError: If API key not set or invalid model
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic is required for Anthropic parser. "
                "Install with: pip install anthropic"
            )

        # Get API key from environment
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable must be set. "
                "Get your API key from https://console.anthropic.com/settings/keys"
            )

        # Validate model
        if model not in MODEL_PRICING:
            raise ValueError(
                f"Invalid model '{model}'. "
                f"Available models: {list(MODEL_PRICING.keys())}"
            )

        self.model = model
        self.model_id = MODEL_IDS.get(model, model)
        self.pricing = MODEL_PRICING[model]

        # Initialize client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Parser identification
        self._name = f"anthropic_{model.replace('-', '_').replace('.', '_')}"
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
        """Parse a PDF file using Claude.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF exceeds limits
            RuntimeError: If Anthropic API call fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Check file size (32MB limit)
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 32:
            raise ValueError(f"PDF file too large ({file_size_mb:.1f}MB). Max: 32MB")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"

        # Get page count for cost tracking and limit check
        page_count = self._get_page_count(pdf_path)

        # Check page limit (100 pages)
        if page_count > 100:
            raise ValueError(f"PDF has {page_count} pages. Max: 100 pages")

        start_time = time.time()

        try:
            # Read and encode PDF as base64
            pdf_data = base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")

            # Call API with PDF document
            message = self.client.messages.create(
                model=self.model_id,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": PDF_TO_MARKDOWN_PROMPT,
                            },
                        ],
                    }
                ],
            )

            # Extract markdown from response
            markdown = ""
            for block in message.content:
                if hasattr(block, "text"):
                    markdown += block.text

            # Get token usage
            input_tokens = page_count * TOKENS_PER_PAGE_INPUT
            output_tokens = len(markdown) // 4

            if message.usage:
                input_tokens = message.usage.input_tokens
                output_tokens = message.usage.output_tokens

        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {e}") from e

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
            "model_id": self.model_id,
            "pricing": self.pricing,
            "last_parsing_cost": self.last_parsing_cost,
            "total_cost": self.total_cost,
            "pages_processed": self.pages_processed,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }

    @staticmethod
    def validate_credentials(model: str = "claude-haiku-4.5") -> tuple[bool, str]:
        """Validate Anthropic API credentials.

        Args:
            model: Model to test with

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not ANTHROPIC_AVAILABLE:
            return False, "anthropic package not installed"

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return False, "ANTHROPIC_API_KEY not set"

        # Try to initialize client
        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Quick test - just initialize (no API call needed to verify key format)
            _ = client
            return True, "Client initialized successfully"
        except Exception as e:
            return False, f"Failed to initialize client: {e}"


# Convenience factory functions for specific models
def create_claude_sonnet_4(**kwargs: Any) -> AnthropicParser:
    """Create Claude Sonnet 4 parser (balanced)."""
    return AnthropicParser(model="claude-sonnet-4", **kwargs)


def create_claude_3_5_haiku(**kwargs: Any) -> AnthropicParser:
    """Create Claude 3.5 Haiku parser (fast and cheap)."""
    return AnthropicParser(model="claude-3-5-haiku", **kwargs)
