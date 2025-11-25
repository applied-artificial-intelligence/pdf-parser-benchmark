"""Landing AI Document Intelligence parser with cost tracking.

This module implements a parser using Landing AI's ADE (Agentic Document Extraction)
SDK, which provides document parsing capabilities via foundation models.

Landing AI ADE features:
- High-accuracy document parsing using DPT-2 model
- Support for PDF, images, and other document formats
- Chunk-based output with structured content
- Cloud-based API processing

Key features:
- Simple SDK-based integration
- Fast processing
- Built-in cost tracking
- Structured output with chunks

Cost Model:
    - Estimated ~$3.50 per 1,000 pages
    - Varies by plan and usage tier

API Limits:
    - Max file size: 25 MB per file
    - Rate limit: Varies by plan

Examples:
    >>> from pathlib import Path
    >>> parser = LandingAIParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")

Environment Variables:
    VISION_AGENT_API_KEY: API key for Landing AI (required)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

try:
    from landingai_ade import LandingAIADE

    LANDINGAI_AVAILABLE = True
except ImportError:
    LANDINGAI_AVAILABLE = False

try:
    import fitz  # PyMuPDF for page counting

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class LandingAIParser:
    """Parser using Landing AI ADE SDK."""

    # Pricing: Estimated $3.50 per 1,000 pages
    COST_PER_PAGE = 0.0035

    def __init__(self, **kwargs: Any):
        """Initialize Landing AI parser.

        Args:
            **kwargs: Additional options (ignored for compatibility)

        Raises:
            ImportError: If landingai-ade is not installed
            ValueError: If required environment variables are missing
        """
        if not LANDINGAI_AVAILABLE:
            raise ImportError(
                "landingai-ade is required for Landing AI parser. "
                "Install with: pip install landingai-ade"
            )

        # Get API key from environment
        self.api_key = os.getenv("VISION_AGENT_API_KEY")

        if not self.api_key:
            raise ValueError(
                "VISION_AGENT_API_KEY environment variable must be set. "
                "Get your API key from https://landing.ai/platform"
            )

        # Initialize client
        self.client = LandingAIADE(apikey=self.api_key)

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0

        # Parser identification
        self._name = "landing_ai"
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
        """Parse a PDF file using Landing AI ADE.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If Landing AI API call fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"

        # Get page count for cost tracking
        page_count = self._get_page_count(pdf_path)

        start_time = time.time()

        try:
            # Call Landing AI ADE
            response = self.client.parse(
                document=pdf_path,
                model="dpt-2-latest",
            )

            # Convert response to markdown
            markdown = self._response_to_markdown(response)

        except Exception as e:
            raise Exception(f"Landing AI processing failed: {e}") from e

        processing_time = time.time() - start_time

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

    def _response_to_markdown(self, response: Any) -> str:
        """Convert Landing AI response to markdown.

        Args:
            response: Response from LandingAIADE.parse()

        Returns:
            Markdown text
        """
        lines = []

        # Response has .chunks attribute with extracted content
        if hasattr(response, "chunks") and response.chunks:
            for i, chunk in enumerate(response.chunks):
                # Each chunk may have different attributes
                if hasattr(chunk, "text"):
                    text = chunk.text.strip()
                    if text:
                        lines.append(text)
                        lines.append("")
                elif hasattr(chunk, "content"):
                    content = chunk.content.strip()
                    if content:
                        lines.append(content)
                        lines.append("")
                elif isinstance(chunk, str):
                    if chunk.strip():
                        lines.append(chunk.strip())
                        lines.append("")
                elif isinstance(chunk, dict):
                    # Handle dict-like chunks
                    text = chunk.get("text", chunk.get("content", ""))
                    if text:
                        lines.append(str(text).strip())
                        lines.append("")

        # Fallback: try to get markdown directly
        if not lines:
            if hasattr(response, "markdown"):
                return response.markdown
            elif hasattr(response, "text"):
                return response.text
            elif hasattr(response, "content"):
                return response.content

        if not lines:
            return "# Empty Document\n\nNo content extracted."

        return "\n".join(lines).strip()

    def get_cost_info(self) -> dict[str, Any]:
        """Get cost information for this parser.

        Returns:
            Dictionary with cost information
        """
        return {
            "parser": "landing_ai",
            "cost_per_page": self.COST_PER_PAGE,
            "last_parsing_cost": self.last_parsing_cost,
            "total_cost": self.total_cost,
            "pages_processed": self.pages_processed,
        }

    @staticmethod
    def validate_credentials() -> tuple[bool, str]:
        """Validate Landing AI credentials.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not LANDINGAI_AVAILABLE:
            return False, "landingai-ade package not installed"

        api_key = os.getenv("VISION_AGENT_API_KEY")
        if not api_key:
            return False, "VISION_AGENT_API_KEY not set"

        # Try to initialize client
        try:
            LandingAIADE(apikey=api_key)
            return True, "Client initialized successfully"
        except Exception as e:
            return False, f"Failed to initialize client: {e}"
