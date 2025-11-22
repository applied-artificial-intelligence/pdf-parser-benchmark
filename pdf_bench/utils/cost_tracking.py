"""Cost tracking and estimation system for commercial PDF parsers.

This module provides utilities for tracking, estimating, and reporting costs
for commercial PDF parsing services (AWS Textract, Azure Document Intelligence, etc.).

Key features:
- Pre-run cost estimation based on PDF page counts
- Post-run cost aggregation and reporting
- Cost limits to prevent budget overruns
- Per-parser cost breakdown
- Cost-performance frontier analysis

Examples:
    >>> from pathlib import Path
    >>> from pdf_bench.utils.cost_tracking import CostEstimator, CostReport
    >>>
    >>> # Estimate cost before parsing
    >>> estimator = CostEstimator()
    >>> pdfs = [Path("doc1.pdf"), Path("doc2.pdf")]
    >>> estimate = estimator.estimate_cost(pdfs, "aws_textract")
    >>> print(f"Estimated cost: ${estimate.total_cost:.2f}")
    >>>
    >>> # Track cost after parsing
    >>> report = CostReport()
    >>> report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
    >>> print(report.summary())

Pricing (as of 2025):
    - AWS Textract: $1.50/1000 pages
    - Azure Document Intelligence (Read): $1.50/1000 pages
    - Open-source parsers: $0.00/page
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz  # type: ignore[import-untyped]  # PyMuPDF for page counting


@dataclass
class ParserPricing:
    """Pricing information for a PDF parser.

    Attributes:
        parser_name: Unique parser identifier (e.g., 'aws_textract')
        cost_per_page: Cost in USD per page
        currency: Currency code (default: 'USD')
        notes: Additional pricing notes (e.g., 'First 1M pages')
    """

    parser_name: str
    cost_per_page: float
    currency: str = "USD"
    notes: str = ""


@dataclass
class CostEstimate:
    """Cost estimate for parsing a set of PDFs with a specific parser.

    Attributes:
        parser_name: Parser identifier
        total_pages: Total number of pages across all PDFs
        cost_per_page: Cost in USD per page
        total_cost: Total estimated cost in USD
        pdf_count: Number of PDF files
        breakdown: Per-PDF cost breakdown
    """

    parser_name: str
    total_pages: int
    cost_per_page: float
    total_cost: float
    pdf_count: int
    breakdown: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format cost estimate as readable string."""
        return (
            f"Cost Estimate for {self.parser_name}:\n"
            f"  PDFs: {self.pdf_count}\n"
            f"  Pages: {self.total_pages:,}\n"
            f"  Rate: ${self.cost_per_page:.6f}/page\n"
            f"  Total: ${self.total_cost:.2f}"
        )


@dataclass
class ParseResult:
    """Result of parsing a single PDF with cost information.

    Attributes:
        parser_name: Parser identifier
        pdf_name: PDF filename
        pages: Number of pages processed
        cost: Actual cost incurred in USD
        success: Whether parsing succeeded
        error: Error message if parsing failed
    """

    parser_name: str
    pdf_name: str
    pages: int
    cost: float
    success: bool = True
    error: str | None = None


class CostEstimator:
    """Estimate costs for commercial PDF parsing before execution.

    This class provides pre-run cost estimation based on PDF page counts
    and parser pricing. It helps users understand costs before committing
    to expensive API operations.

    Examples:
        >>> estimator = CostEstimator()
        >>> pdfs = [Path("doc1.pdf"), Path("doc2.pdf")]
        >>> estimate = estimator.estimate_cost(pdfs, "aws_textract")
        >>> if estimate.total_cost > 10.0:
        ...     print("Cost exceeds budget!")
    """

    # Pricing configuration for commercial parsers
    PARSER_PRICING: dict[str, ParserPricing] = {
        "aws_textract": ParserPricing(
            parser_name="aws_textract",
            cost_per_page=0.0015,  # $1.50 per 1000 pages
            notes="DetectDocumentText API, first 1M pages",
        ),
        "azure_document_intelligence": ParserPricing(
            parser_name="azure_document_intelligence",
            cost_per_page=0.0015,  # $1.50 per 1000 pages
            notes="Read model, first 1M pages",
        ),
        "google_document_ai": ParserPricing(
            parser_name="google_document_ai",
            cost_per_page=0.0015,  # $1.50 per 1000 pages
            notes="Document OCR, first 1M pages/month",
        ),
        "databricks": ParserPricing(
            parser_name="databricks",
            cost_per_page=0.003,  # $3.00 per 1000 pages
            notes="DBU-based pricing, ~0.15 DBU per 100 pages",
        ),
        "landing_ai": ParserPricing(
            parser_name="landing_ai",
            cost_per_page=0.0035,  # $3.50 per 1000 pages
            notes="Visual Prompting OCR",
        ),
        # Open-source parsers have zero cost
        "pymupdf": ParserPricing(
            parser_name="pymupdf", cost_per_page=0.0, notes="Open-source, free"
        ),
        "pdfplumber": ParserPricing(
            parser_name="pdfplumber", cost_per_page=0.0, notes="Open-source, free"
        ),
        "marker": ParserPricing(parser_name="marker", cost_per_page=0.0, notes="Open-source, free"),
        "unstructured": ParserPricing(
            parser_name="unstructured", cost_per_page=0.0, notes="Open-source, free"
        ),
    }

    def estimate_cost(self, pdf_paths: list[Path], parser_name: str) -> CostEstimate:
        """Estimate cost for parsing a list of PDFs with a specific parser.

        This method counts pages in each PDF and calculates total cost
        based on parser pricing. It provides both aggregate and per-PDF
        cost estimates.

        Args:
            pdf_paths: List of paths to PDF files to parse
            parser_name: Parser identifier (e.g., 'aws_textract')

        Returns:
            CostEstimate with total and per-PDF cost breakdown

        Raises:
            ValueError: If parser_name is not recognized
            FileNotFoundError: If any PDF file does not exist

        Examples:
            >>> estimator = CostEstimator()
            >>> pdfs = [Path("doc1.pdf"), Path("doc2.pdf")]
            >>> estimate = estimator.estimate_cost(pdfs, "aws_textract")
            >>> print(f"Total: ${estimate.total_cost:.2f}")
        """
        if parser_name not in self.PARSER_PRICING:
            raise ValueError(
                f"Unknown parser: {parser_name}. Supported: {list(self.PARSER_PRICING.keys())}"
            )

        pricing = self.PARSER_PRICING[parser_name]
        total_pages = 0
        breakdown: dict[str, dict[str, Any]] = {}

        for pdf_path in pdf_paths:
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")

            # Count pages
            page_count = self._count_pages(pdf_path)
            pdf_cost = page_count * pricing.cost_per_page

            total_pages += page_count
            breakdown[str(pdf_path)] = {
                "pages": page_count,
                "cost": pdf_cost,
            }

        total_cost = total_pages * pricing.cost_per_page

        return CostEstimate(
            parser_name=parser_name,
            total_pages=total_pages,
            cost_per_page=pricing.cost_per_page,
            total_cost=total_cost,
            pdf_count=len(pdf_paths),
            breakdown=breakdown,
        )

    def _count_pages(self, pdf_path: Path) -> int:
        """Count number of pages in a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            int: Number of pages in the PDF

        Raises:
            RuntimeError: If PDF cannot be opened
        """
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            raise RuntimeError(f"Failed to count pages in {pdf_path}: {e}") from e

    def check_budget(
        self, pdf_paths: list[Path], parser_name: str, max_cost: float
    ) -> tuple[bool, CostEstimate]:
        """Check if parsing PDFs would exceed budget limit.

        This method estimates cost and compares it against a maximum
        budget threshold. It helps prevent accidental overruns.

        Args:
            pdf_paths: List of paths to PDF files
            parser_name: Parser identifier
            max_cost: Maximum allowed cost in USD

        Returns:
            Tuple of (within_budget: bool, estimate: CostEstimate)

        Examples:
            >>> estimator = CostEstimator()
            >>> pdfs = [Path("doc1.pdf"), Path("doc2.pdf")]
            >>> within_budget, estimate = estimator.check_budget(pdfs, "aws_textract", 10.0)
            >>> if not within_budget:
            ...     print(f"Would exceed budget! Estimated: ${estimate.total_cost:.2f}")
        """
        estimate = self.estimate_cost(pdf_paths, parser_name)
        within_budget = estimate.total_cost <= max_cost
        return within_budget, estimate


class CostReport:
    """Track and report actual costs from parsing operations.

    This class aggregates costs from multiple parsing operations and
    provides summary statistics and formatted reports.

    Examples:
        >>> report = CostReport()
        >>> report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        >>> report.add_parse_result("aws_textract", "doc2.pdf", 15, 0.0225)
        >>> print(report.summary())
    """

    def __init__(self) -> None:
        """Initialize empty cost report."""
        self.results: list[ParseResult] = []

    def add_parse_result(
        self,
        parser_name: str,
        pdf_name: str,
        pages: int,
        cost: float,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Add a parsing result to the cost report.

        Args:
            parser_name: Parser identifier
            pdf_name: PDF filename
            pages: Number of pages processed
            cost: Actual cost incurred in USD
            success: Whether parsing succeeded
            error: Error message if parsing failed
        """
        result = ParseResult(
            parser_name=parser_name,
            pdf_name=pdf_name,
            pages=pages,
            cost=cost,
            success=success,
            error=error,
        )
        self.results.append(result)

    def get_total_cost(self, parser_name: str | None = None) -> float:
        """Get total cost across all results or for a specific parser.

        Args:
            parser_name: Optional parser to filter by. If None, returns total across all parsers.

        Returns:
            float: Total cost in USD

        Examples:
            >>> report = CostReport()
            >>> report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
            >>> report.get_total_cost()
            0.015
            >>> report.get_total_cost("aws_textract")
            0.015
        """
        results = self.results
        if parser_name:
            results = [r for r in results if r.parser_name == parser_name]
        return sum(r.cost for r in results)

    def get_total_pages(self, parser_name: str | None = None) -> int:
        """Get total pages processed across all results or for a specific parser.

        Args:
            parser_name: Optional parser to filter by

        Returns:
            int: Total page count
        """
        results = self.results
        if parser_name:
            results = [r for r in results if r.parser_name == parser_name]
        return sum(r.pages for r in results)

    def get_parser_breakdown(self) -> dict[str, dict[str, Any]]:
        """Get cost breakdown by parser.

        Returns:
            dict: Per-parser statistics including cost, pages, success rate

        Examples:
            >>> report = CostReport()
            >>> report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
            >>> breakdown = report.get_parser_breakdown()
            >>> breakdown["aws_textract"]["total_cost"]
            0.015
        """
        breakdown: dict[str, dict[str, Any]] = {}

        for result in self.results:
            parser = result.parser_name
            if parser not in breakdown:
                breakdown[parser] = {
                    "total_cost": 0.0,
                    "total_pages": 0,
                    "pdf_count": 0,
                    "successes": 0,
                    "failures": 0,
                }

            breakdown[parser]["total_cost"] += result.cost
            breakdown[parser]["total_pages"] += result.pages
            breakdown[parser]["pdf_count"] += 1

            if result.success:
                breakdown[parser]["successes"] += 1
            else:
                breakdown[parser]["failures"] += 1

        # Calculate average cost per page
        for parser in breakdown:
            total_pages = breakdown[parser]["total_pages"]
            if total_pages > 0:
                avg_cost = breakdown[parser]["total_cost"] / total_pages
                breakdown[parser]["cost_per_page"] = avg_cost

        return breakdown

    def summary(self) -> str:
        """Generate formatted summary of cost report.

        Returns:
            str: Multi-line formatted summary

        Examples:
            >>> report = CostReport()
            >>> report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
            >>> print(report.summary())
        """
        if not self.results:
            return "No parsing results recorded."

        breakdown = self.get_parser_breakdown()
        lines = ["Cost Report Summary", "=" * 50, ""]

        # Overall statistics
        total_cost = self.get_total_cost()
        total_pages = self.get_total_pages()
        total_pdfs = len(self.results)

        lines.append(f"Total PDFs Processed: {total_pdfs}")
        lines.append(f"Total Pages Processed: {total_pages:,}")
        lines.append(f"Total Cost: ${total_cost:.2f}")
        lines.append("")

        # Per-parser breakdown
        lines.append("Per-Parser Breakdown:")
        lines.append("-" * 50)

        for parser, stats in sorted(breakdown.items()):
            lines.append(f"\n{parser}:")
            lines.append(f"  PDFs: {stats['pdf_count']}")
            lines.append(f"  Pages: {stats['total_pages']:,}")
            lines.append(f"  Cost: ${stats['total_cost']:.2f}")
            if "cost_per_page" in stats:
                lines.append(f"  Avg Cost/Page: ${stats['cost_per_page']:.6f}")
            lines.append(f"  Successes: {stats['successes']}")
            lines.append(f"  Failures: {stats['failures']}")

        return "\n".join(lines)
