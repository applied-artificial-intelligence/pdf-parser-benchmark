"""Databricks ai_parse_document parser with cost tracking.

This module implements a parser using Databricks' ai_parse_document SQL function,
which provides document parsing capabilities via Databricks SQL warehouses.

Databricks ai_parse_document features:
- Built-in document structure extraction
- Bounding box detection for elements
- Support for PDF, JPG, PNG, DOC, PPT
- Enterprise-grade security via OAuth

Key features:
- SQL API-based (uses Databricks SQL warehouse)
- OAuth M2M authentication (client credentials)
- Built-in cost tracking
- JSON-structured output with element types

Cost Model:
    - Based on serverless SQL warehouse consumption
    - Approximately $0.07 per DBU
    - Document processing: ~0.01-0.05 DBU per page
    - This parser estimates $0.003 per page

API Limits:
    - Max file size: Varies by warehouse configuration
    - Requires Databricks Runtime 17.1+
    - US/EU region only

Examples:
    >>> from pathlib import Path
    >>> parser = DatabricksParser()
    >>> pdf_path = Path("document.pdf")
    >>> output_dir = Path("output")
    >>> result = parser.parse(pdf_path, output_dir)
    >>> print(f"Estimated cost: ${parser.last_parsing_cost:.4f}")

Environment Variables:
    DATABRICKS_HOST: Databricks workspace URL (required)
    DATABRICKS_CLIENT_ID: OAuth client ID (required for M2M auth)
    DATABRICKS_CLIENT_SECRET: OAuth client secret (required for M2M auth)
    DATABRICKS_WAREHOUSE_ID: SQL warehouse ID (optional, auto-detected)
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any

try:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.sql import StatementState

    DATABRICKS_SDK_AVAILABLE = True
except ImportError:
    DATABRICKS_SDK_AVAILABLE = False

from pdf_bench.utils.caching import cache_key, get_cached, store_cached


class DatabricksParser:
    """Parser using Databricks ai_parse_document SQL function."""

    # Pricing: Estimated $3.00 per 1,000 pages
    # Based on serverless SQL warehouse DBU consumption
    COST_PER_PAGE = 0.003

    def __init__(self, **kwargs: Any):
        """Initialize Databricks parser.

        Args:
            **kwargs: Additional options (ignored for compatibility)

        Raises:
            ImportError: If databricks-sdk is not installed
            ValueError: If required environment variables are missing
        """
        if not DATABRICKS_SDK_AVAILABLE:
            raise ImportError(
                "databricks-sdk is required for Databricks parser. "
                "Install with: pip install databricks-sdk"
            )

        # Get required config from environment
        self.host = os.getenv("DATABRICKS_HOST")
        self.client_id = os.getenv("DATABRICKS_CLIENT_ID")
        self.client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
        self.warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

        if not self.host:
            raise ValueError(
                "DATABRICKS_HOST environment variable must be set. "
                "Format: https://<workspace-id>.cloud.databricks.com"
            )

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET must be set. "
                "Create a service principal in your Databricks workspace."
            )

        # Initialize SDK client (uses OAuth M2M automatically)
        self.client = WorkspaceClient()

        # Auto-detect warehouse if not specified
        if not self.warehouse_id:
            self.warehouse_id = self._get_warehouse_id()

        # Track costs
        self.last_parsing_cost = 0.0
        self.total_cost = 0.0
        self.pages_processed = 0

        # Parser identification
        self._name = "databricks"
        self._version = "1.0.0"

    @property
    def name(self) -> str:
        """Return parser name."""
        return self._name

    @property
    def version(self) -> str:
        """Return parser version."""
        return self._version

    def _get_warehouse_id(self) -> str:
        """Get SQL warehouse ID, preferring serverless.

        Returns:
            Warehouse ID

        Raises:
            ValueError: If no warehouse found
        """
        warehouses = list(self.client.warehouses.list())
        if not warehouses:
            raise ValueError(
                "No SQL warehouses found in workspace. "
                "Create a serverless SQL warehouse in Databricks."
            )

        # Prefer serverless, then any available
        for wh in warehouses:
            if wh.name and "serverless" in wh.name.lower():
                if wh.id:
                    return wh.id

        # Return first warehouse with valid ID
        for wh in warehouses:
            if wh.id:
                return wh.id

        raise ValueError("No warehouse with valid ID found")

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Parse a PDF file using Databricks ai_parse_document.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output markdown file

        Returns:
            Path to generated markdown file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If Databricks API call fails
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"

        # Check cache first
        cache_dir = Path(".cache")
        key = cache_key(pdf_path, self._name, self._version)
        cached = get_cached(key, cache_dir)
        if cached is not None:
            return cached

        # Read PDF and encode as base64
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        pdf_b64 = base64.b64encode(pdf_content).decode("utf-8")

        # Execute ai_parse_document via SQL
        start_time = time.time()

        # Ensure warehouse_id is set
        if not self.warehouse_id:
            raise ValueError("No warehouse ID configured")

        try:
            result = self.client.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=f"SELECT ai_parse_document(unbase64('{pdf_b64}')) as result",
                wait_timeout="50s",
            )

            # Poll for completion if needed
            statement_id = result.statement_id
            if not statement_id:
                raise Exception("No statement ID returned")

            while (
                result.status
                and result.status.state in (StatementState.PENDING, StatementState.RUNNING)
            ):
                time.sleep(2)
                result = self.client.statement_execution.get_statement(statement_id)

            if result.status and result.status.state == StatementState.FAILED:
                error_msg = (
                    result.status.error.message
                    if result.status.error
                    else "Unknown error"
                )
                raise Exception(f"SQL execution failed: {error_msg}")

            # Parse JSON result
            if not result.result or not result.result.data_array:
                raise Exception("No result returned from ai_parse_document")

            json_str = result.result.data_array[0][0]
            doc_data = json.loads(json_str)

        except Exception as e:
            raise Exception(f"Databricks processing failed: {e}") from e

        # Convert to markdown
        markdown = self._document_to_markdown(doc_data)

        # Write markdown
        output_path.write_text(markdown, encoding="utf-8")

        # Store in cache for future runs
        store_cached(key, output_path)

        # Track costs (estimate pages from elements or file size)
        page_count = self._estimate_pages(doc_data, pdf_content)
        cost = page_count * self.COST_PER_PAGE
        self.last_parsing_cost = cost
        self.total_cost += cost
        self.pages_processed += page_count

        return output_path

    def _estimate_pages(self, doc_data: dict, pdf_content: bytes) -> int:
        """Estimate page count from document data or file size.

        Args:
            doc_data: Parsed document JSON
            pdf_content: Raw PDF bytes

        Returns:
            Estimated page count
        """
        # Try to get from bounding boxes (page_id)
        if "document" in doc_data and "elements" in doc_data["document"]:
            max_page = 0
            for elem in doc_data["document"]["elements"]:
                if "bbox" in elem:
                    for box in elem["bbox"]:
                        page_id = box.get("page_id", 0)
                        max_page = max(max_page, page_id)
            if max_page > 0:
                return max_page + 1  # page_id is 0-indexed

        # Fallback to file size estimate (~75KB per page)
        return max(1, len(pdf_content) // 75000)

    def _document_to_markdown(self, doc_data: dict) -> str:
        """Convert ai_parse_document JSON to markdown.

        Args:
            doc_data: Parsed document JSON from ai_parse_document

        Returns:
            Markdown text
        """
        lines = []

        if "document" not in doc_data or "elements" not in doc_data["document"]:
            return "# Empty Document\n\nNo content extracted."

        elements = doc_data["document"]["elements"]

        for elem in elements:
            elem_type = elem.get("type", "text")
            content = (elem.get("content") or "").strip()

            if not content:
                continue

            # Format based on element type
            if elem_type == "title":
                lines.append(f"# {content}")
                lines.append("")
            elif elem_type == "section_header" or elem_type == "heading":
                lines.append(f"## {content}")
                lines.append("")
            elif elem_type == "list_item":
                # Detect numbered vs bullet
                if content[0].isdigit():
                    lines.append(content)
                else:
                    lines.append(f"- {content}")
            elif elem_type == "table":
                # Tables may have structured data
                table_md = self._format_table(elem)
                if table_md:
                    lines.append(table_md)
                    lines.append("")
            elif elem_type == "caption":
                lines.append(f"*{content}*")
                lines.append("")
            elif elem_type == "footnote":
                lines.append(f"[^]: {content}")
                lines.append("")
            else:
                # Default: paragraph
                lines.append(content)
                lines.append("")

        return "\n".join(lines).strip()

    def _format_table(self, elem: dict) -> str:
        """Format table element to markdown.

        Args:
            elem: Table element from ai_parse_document

        Returns:
            Markdown table string
        """
        content = elem.get("content", "")

        # If content is just text, try to detect table structure
        if isinstance(content, str):
            # Simple case: content is already text
            return content

        # If content is structured (rows/cells), format as markdown table
        if isinstance(content, dict):
            rows = content.get("rows", [])
            if not rows:
                return ""

            md_lines = []
            for i, row in enumerate(rows):
                cells = row.get("cells", [])
                cell_text = [str(c.get("content", "")).replace("|", "\\|") for c in cells]
                md_lines.append("| " + " | ".join(cell_text) + " |")

                # Add separator after header
                if i == 0:
                    md_lines.append("| " + " | ".join(["---"] * len(cells)) + " |")

            return "\n".join(md_lines)

        return str(content)

    def get_cost_info(self) -> dict[str, Any]:
        """Get cost information for this parser.

        Returns:
            Dictionary with cost information
        """
        return {
            "parser": "databricks",
            "cost_per_page": self.COST_PER_PAGE,
            "last_parsing_cost": self.last_parsing_cost,
            "total_cost": self.total_cost,
            "pages_processed": self.pages_processed,
            "note": "Cost estimate based on serverless SQL warehouse DBU consumption",
        }

    @staticmethod
    def validate_credentials() -> tuple[bool, str]:
        """Validate Databricks credentials.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not DATABRICKS_SDK_AVAILABLE:
            return False, "databricks-sdk package not installed"

        host = os.getenv("DATABRICKS_HOST")
        if not host:
            return False, "DATABRICKS_HOST not set"

        client_id = os.getenv("DATABRICKS_CLIENT_ID")
        client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
        if not client_id or not client_secret:
            return False, "DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET not set"

        # Try to initialize client and verify connection
        try:
            client = WorkspaceClient()
            user = client.current_user.me()
            return True, f"Connected as {user.user_name}"
        except Exception as e:
            return False, f"Connection failed: {e}"
