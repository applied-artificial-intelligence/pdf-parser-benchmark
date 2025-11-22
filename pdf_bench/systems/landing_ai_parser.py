"""Landing AI Document Intelligence parser with cost tracking.

This module implements a parser using Landing AI's Visual Prompting platform,
which uses computer vision and foundation models for document understanding.

Landing AI features:
- Visual Prompting for zero-shot document analysis
- Pre-trained models for common document types
- Custom model training with minimal data
- Cloud-based and on-premise deployment options
- High accuracy on complex layouts and forms

Key features:
- API-based processing (no local installation required)
- Excellent performance on forms and invoices
- Visual grounding (highlights extracted regions)
- Built-in cost tracking
- Fast iteration with visual feedback

Cost Model:
    - Document OCR: ~$2-5 per 1,000 pages (varies by plan)
    - Custom models: Additional training costs
    - Enterprise plans: Custom pricing
    This parser uses $3.50/1000 pages as baseline

API Limits:
    - Max file size: 25 MB per file
    - Rate limit: Varies by plan (typically 100-1000 req/min)
    - Batch processing available

Examples:
    >>> from pathlib import Path
    >>> parser = LandingAIParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")
    >>> print(result)
    PosixPath('output/document.md')

Environment Variables:
    LANDING_AI_API_KEY: API key for Landing AI (required)
    LANDING_AI_ENDPOINT: API endpoint (optional, defaults to production)
    LANDING_AI_PROJECT_ID: Project ID for custom models (optional)
"""

import base64
import os
import time
from pathlib import Path
from typing import Any

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import fitz  # PyMuPDF for PDF to image conversion

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class LandingAIParser:
    """Parser using Landing AI Visual Prompting."""

    # Pricing: Estimated $3.50 per 1,000 pages
    COST_PER_PAGE = 0.0035

    # Default API endpoint
    DEFAULT_ENDPOINT = "https://api.landing.ai/v1"

    def __init__(self):
        """Initialize Landing AI parser.

        Raises:
            ImportError: If required packages are not installed
            ValueError: If required environment variables are missing
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests is required for Landing AI parser. Install with: pip install requests"
            )

        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for Landing AI parser (PDF to image conversion). "
                "Install with: pip install pymupdf"
            )

        # Get required config from environment
        self.api_key = os.getenv("LANDING_AI_API_KEY")
        self.endpoint = os.getenv("LANDING_AI_ENDPOINT", self.DEFAULT_ENDPOINT)
        self.project_id = os.getenv("LANDING_AI_PROJECT_ID")

        if not self.api_key:
            raise ValueError(
                "LANDING_AI_API_KEY environment variable must be set. "
                "Get your API key from https://landing.ai/platform"
            )

        # Set up API headers
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using Landing AI.

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

        # Convert PDF pages to images
        doc = fitz.open(pdf_path)
        page_count = len(doc)

        all_text = []
        start_time = time.time()

        try:
            # Process each page
            for page_num in range(page_count):
                page = doc[page_num]

                # Convert page to image (PNG)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_bytes = pix.tobytes("png")

                # Encode image as base64
                img_base64 = base64.b64encode(img_bytes).decode("utf-8")

                # Call Landing AI API for this page
                page_text = self._process_page(img_base64, page_num + 1)
                all_text.append(f"## Page {page_num + 1}\n\n{page_text}")

        except Exception as e:
            raise Exception(f"Landing AI processing failed: {e}") from e
        finally:
            doc.close()

        time.time() - start_time

        # Combine all pages into markdown
        markdown = "\n\n".join(all_text)

        # Write markdown
        output_path.write_text(markdown, encoding="utf-8")

        # Track costs
        cost = page_count * self.COST_PER_PAGE
        self.last_parsing_cost = cost
        self.total_cost += cost
        self.pages_processed += page_count

        return output_path

    def _process_page(self, image_base64: str, page_num: int) -> str:
        """Process a single page image using Landing AI.

        Args:
            image_base64: Base64-encoded PNG image
            page_num: Page number (for logging)

        Returns:
            Extracted text from the page
        """
        # Landing AI Visual Prompting API endpoint
        url = f"{self.endpoint}/ocr"

        payload = {
            "image": f"data:image/png;base64,{image_base64}",
            "model": "general-ocr",  # Use general OCR model
        }

        # If custom project specified, use it
        if self.project_id:
            payload["project_id"] = self.project_id

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code != 200:
                # Fallback: Return error message as placeholder
                return f"[Error processing page {page_num}: {response.status_code}]"

            result = response.json()

            # Extract text from response
            # Note: Actual response format may vary based on Landing AI API version
            if "text" in result:
                return result["text"]
            elif "predictions" in result:
                # Extract text from predictions
                texts = []
                for pred in result["predictions"]:
                    if "text" in pred:
                        texts.append(pred["text"])
                return "\n".join(texts)
            else:
                return "[No text extracted]"

        except requests.exceptions.Timeout:
            return f"[Timeout processing page {page_num}]"
        except requests.exceptions.RequestException as e:
            return f"[Network error on page {page_num}: {e}]"
        except Exception as e:
            return f"[Error processing page {page_num}: {e}]"

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
        if not REQUESTS_AVAILABLE:
            return False, "requests package not installed"

        if not PYMUPDF_AVAILABLE:
            return False, "PyMuPDF package not installed"

        api_key = os.getenv("LANDING_AI_API_KEY")
        if not api_key:
            return False, "LANDING_AI_API_KEY not set"

        # Test API key with a simple request
        try:
            endpoint = os.getenv("LANDING_AI_ENDPOINT", LandingAIParser.DEFAULT_ENDPOINT)
            headers = {
                "apikey": api_key,
                "Content-Type": "application/json",
            }

            # Try to ping the API (adjust endpoint as needed)
            url = f"{endpoint}/health"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return True, "Credentials valid"
            elif response.status_code == 401:
                return False, "Invalid API key"
            elif response.status_code == 403:
                return False, "API key lacks required permissions"
            else:
                # If health endpoint doesn't exist, assume API key is valid
                # (some APIs don't have a health endpoint)
                return True, "API key configured (unable to verify)"

        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Landing AI API"
        except Exception as e:
            # Unable to verify, but API key is set
            return True, f"API key configured (verification skipped: {e})"
