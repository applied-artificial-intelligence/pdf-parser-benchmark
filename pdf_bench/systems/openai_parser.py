"""OpenAI GPT PDF parser - OpenAI's frontier multimodal models for PDF parsing.

This module implements PDF-to-Markdown parsing using OpenAI's GPT models,
which support native PDF input via the Files API.

Supported Models:
- gpt-5: Latest flagship model (~$1.25/1M input, $10/1M output)
- gpt-5-mini: Cost-effective (~$0.25/1M input, $2/1M output)
- gpt-4.1: Previous flagship (~$2/1M input, $8/1M output)
- gpt-4o: Multimodal model (~$2.50/1M input, $10/1M output)

Features:
- Native PDF vision understanding (since March 2025)
- Text and image extraction from PDFs
- Structured output support
- 128K-1M token context windows

Cost Model (per 1M tokens):
    - gpt-5: $1.25 input, $10.00 output
    - gpt-5-mini: $0.25 input, $2.00 output
    - gpt-4.1: $2.00 input, $8.00 output
    - gpt-4o: $2.50 input, $10.00 output

Token Estimation:
    - ~1500 tokens per PDF page (vision)
    - ~800 tokens output per page (markdown)

Examples:
    >>> from pathlib import Path
    >>> parser = OpenAIParser(model="gpt-5-mini")
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")

Environment Variables:
    OPENAI_API_KEY: API key for OpenAI (required)
        Get your key from: https://platform.openai.com/api-keys
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore

try:
    import fitz  # PyMuPDF for page counting

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


# Pricing per 1M tokens (November 2025)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-5": {"input": 1.25, "output": 10.00},
    "gpt-5-mini": {"input": 0.25, "output": 2.00},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

# Token estimates per page
TOKENS_PER_PAGE_INPUT = 1500  # Vision model estimate
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


class OpenAIParser:
    """Parser using OpenAI's GPT multimodal models for PDF understanding."""

    def __init__(
        self,
        model: str = "gpt-5-mini",
        **kwargs: Any,
    ):
        """Initialize OpenAI parser.

        Args:
            model: GPT model to use. Options:
                - "gpt-5": Latest flagship (most accurate, moderate cost)
                - "gpt-5-mini": Fast and cheap (recommended for benchmarking)
                - "gpt-4.1": Previous flagship
                - "gpt-4o": Multimodal model
                - "gpt-4o-mini": Cheapest option
            **kwargs: Additional options (ignored for compatibility)

        Raises:
            ImportError: If openai is not installed
            ValueError: If API key not set or invalid model
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai is required for OpenAI parser. "
                "Install with: pip install openai"
            )

        # Get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable must be set. "
                "Get your API key from https://platform.openai.com/api-keys"
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
        self.client = OpenAI(api_key=self.api_key)

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Parser identification
        self._name = f"openai_{model.replace('-', '_').replace('.', '_')}"
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
        """Parse a PDF file using OpenAI GPT.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            RuntimeError: If OpenAI API call fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"

        # Get page count for cost tracking
        page_count = self._get_page_count(pdf_path)

        start_time = time.time()

        try:
            # Upload PDF file
            with open(pdf_path, "rb") as f:
                file = self.client.files.create(file=f, purpose="user_data")

            # Call API with PDF file reference
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "file",
                                "file": {"file_id": file.id},
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
            markdown = response.choices[0].message.content or ""

            # Get token usage
            input_tokens = page_count * TOKENS_PER_PAGE_INPUT
            output_tokens = len(markdown) // 4

            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            # Clean up uploaded file
            try:
                self.client.files.delete(file.id)
            except Exception:
                pass  # Best effort cleanup

        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}") from e

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
    def validate_credentials(model: str = "gpt-5-mini") -> tuple[bool, str]:
        """Validate OpenAI API credentials.

        Args:
            model: Model to test with

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not OPENAI_AVAILABLE:
            return False, "openai package not installed"

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "OPENAI_API_KEY not set"

        # Try to initialize client and list models
        try:
            client = OpenAI(api_key=api_key)
            # Quick test - list files (minimal API call)
            _ = client.files.list(limit=1)
            return True, "Client initialized successfully"
        except Exception as e:
            return False, f"Failed to connect: {e}"


# Convenience factory functions for specific models
def create_gpt_5(**kwargs: Any) -> OpenAIParser:
    """Create GPT-5 parser (flagship model)."""
    return OpenAIParser(model="gpt-5", **kwargs)


def create_gpt_5_mini(**kwargs: Any) -> OpenAIParser:
    """Create GPT-5-mini parser (fast and cheap)."""
    return OpenAIParser(model="gpt-5-mini", **kwargs)
