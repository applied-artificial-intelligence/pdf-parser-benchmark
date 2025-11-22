"""Tests for cost tracking and estimation system."""

import shutil
from pathlib import Path

import pytest

from pdf_bench.utils.cost_tracking import (
    CostEstimate,
    CostEstimator,
    CostReport,
    ParseResult,
    ParserPricing,
)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Copy sample PDF to temp directory for testing."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    sample_pdf = fixtures_dir / "sample.pdf"

    if not sample_pdf.exists():
        pytest.skip("Sample PDF not found - run create_sample_pdf.py first")

    # Copy to temp directory
    temp_pdf = tmp_path / "sample.pdf"
    shutil.copy(sample_pdf, temp_pdf)
    return temp_pdf


@pytest.fixture
def estimator() -> CostEstimator:
    """Create a CostEstimator instance."""
    return CostEstimator()


@pytest.fixture
def cost_report() -> CostReport:
    """Create an empty CostReport instance."""
    return CostReport()


class TestParserPricing:
    """Test ParserPricing dataclass."""

    def test_parser_pricing_creation(self) -> None:
        """Test creating ParserPricing instance."""
        pricing = ParserPricing(
            parser_name="aws_textract",
            cost_per_page=0.0015,
            notes="Test pricing",
        )

        assert pricing.parser_name == "aws_textract"
        assert pricing.cost_per_page == 0.0015
        assert pricing.currency == "USD"
        assert pricing.notes == "Test pricing"


class TestCostEstimate:
    """Test CostEstimate dataclass."""

    def test_cost_estimate_creation(self) -> None:
        """Test creating CostEstimate instance."""
        estimate = CostEstimate(
            parser_name="aws_textract",
            total_pages=100,
            cost_per_page=0.0015,
            total_cost=0.15,
            pdf_count=5,
        )

        assert estimate.parser_name == "aws_textract"
        assert estimate.total_pages == 100
        assert estimate.cost_per_page == 0.0015
        assert estimate.total_cost == 0.15
        assert estimate.pdf_count == 5

    def test_cost_estimate_str(self) -> None:
        """Test string representation of CostEstimate."""
        estimate = CostEstimate(
            parser_name="aws_textract",
            total_pages=100,
            cost_per_page=0.0015,
            total_cost=0.15,
            pdf_count=5,
        )

        estimate_str = str(estimate)
        assert "aws_textract" in estimate_str
        assert "100" in estimate_str
        assert "$0.15" in estimate_str


class TestParseResult:
    """Test ParseResult dataclass."""

    def test_parse_result_success(self) -> None:
        """Test creating successful ParseResult."""
        result = ParseResult(
            parser_name="aws_textract",
            pdf_name="test.pdf",
            pages=10,
            cost=0.015,
        )

        assert result.parser_name == "aws_textract"
        assert result.pdf_name == "test.pdf"
        assert result.pages == 10
        assert result.cost == 0.015
        assert result.success is True
        assert result.error is None

    def test_parse_result_failure(self) -> None:
        """Test creating failed ParseResult."""
        result = ParseResult(
            parser_name="aws_textract",
            pdf_name="test.pdf",
            pages=0,
            cost=0.0,
            success=False,
            error="API error",
        )

        assert result.success is False
        assert result.error == "API error"


class TestCostEstimator:
    """Test CostEstimator class."""

    def test_estimator_has_pricing_config(self, estimator: CostEstimator) -> None:
        """Test that estimator has pricing configuration."""
        assert "aws_textract" in estimator.PARSER_PRICING
        assert "azure_document_intelligence" in estimator.PARSER_PRICING
        assert "pymupdf" in estimator.PARSER_PRICING

    def test_commercial_parser_pricing(self, estimator: CostEstimator) -> None:
        """Test commercial parser pricing is configured correctly."""
        aws_pricing = estimator.PARSER_PRICING["aws_textract"]
        assert aws_pricing.cost_per_page == 0.0015

        azure_pricing = estimator.PARSER_PRICING["azure_document_intelligence"]
        assert azure_pricing.cost_per_page == 0.0015

    def test_opensource_parser_pricing(self, estimator: CostEstimator) -> None:
        """Test open-source parsers have zero cost."""
        pymupdf_pricing = estimator.PARSER_PRICING["pymupdf"]
        assert pymupdf_pricing.cost_per_page == 0.0

        marker_pricing = estimator.PARSER_PRICING["marker"]
        assert marker_pricing.cost_per_page == 0.0

    def test_estimate_cost_single_pdf(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test cost estimation for a single PDF."""
        estimate = estimator.estimate_cost([sample_pdf], "aws_textract")

        assert estimate.parser_name == "aws_textract"
        assert estimate.pdf_count == 1
        assert estimate.total_pages > 0
        assert estimate.cost_per_page == 0.0015
        assert estimate.total_cost == estimate.total_pages * 0.0015

    def test_estimate_cost_multiple_pdfs(
        self, estimator: CostEstimator, sample_pdf: Path, tmp_path: Path
    ) -> None:
        """Test cost estimation for multiple PDFs."""
        # Create second PDF by copying
        sample_pdf_2 = tmp_path / "sample2.pdf"
        shutil.copy(sample_pdf, sample_pdf_2)

        pdfs = [sample_pdf, sample_pdf_2]
        estimate = estimator.estimate_cost(pdfs, "aws_textract")

        assert estimate.pdf_count == 2
        assert estimate.total_pages > 0
        assert len(estimate.breakdown) == 2

    def test_estimate_cost_with_breakdown(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test that estimate includes per-PDF breakdown."""
        estimate = estimator.estimate_cost([sample_pdf], "aws_textract")

        assert str(sample_pdf) in estimate.breakdown
        pdf_breakdown = estimate.breakdown[str(sample_pdf)]
        assert "pages" in pdf_breakdown
        assert "cost" in pdf_breakdown
        assert pdf_breakdown["pages"] > 0
        assert pdf_breakdown["cost"] > 0

    def test_estimate_cost_unknown_parser(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test that unknown parser raises ValueError."""
        with pytest.raises(ValueError, match="Unknown parser"):
            estimator.estimate_cost([sample_pdf], "nonexistent_parser")

    def test_estimate_cost_missing_pdf(self, estimator: CostEstimator) -> None:
        """Test that missing PDF raises FileNotFoundError."""
        missing_pdf = Path("nonexistent.pdf")
        with pytest.raises(FileNotFoundError):
            estimator.estimate_cost([missing_pdf], "aws_textract")

    def test_estimate_cost_zero_for_opensource(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test that open-source parsers have zero cost."""
        estimate = estimator.estimate_cost([sample_pdf], "pymupdf")

        assert estimate.cost_per_page == 0.0
        assert estimate.total_cost == 0.0

    def test_check_budget_within_limit(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test budget check when cost is within limit."""
        within_budget, estimate = estimator.check_budget(
            [sample_pdf], "aws_textract", max_cost=10.0
        )

        assert within_budget is True
        assert estimate.total_cost < 10.0

    def test_check_budget_exceeds_limit(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test budget check when cost exceeds limit."""
        within_budget, estimate = estimator.check_budget(
            [sample_pdf], "aws_textract", max_cost=0.001
        )

        # Sample PDF is likely >1 page, so should exceed $0.001
        if estimate.total_pages > 1:
            assert within_budget is False
            assert estimate.total_cost > 0.001


class TestCostReport:
    """Test CostReport class."""

    def test_empty_report(self, cost_report: CostReport) -> None:
        """Test empty cost report."""
        assert len(cost_report.results) == 0
        assert cost_report.get_total_cost() == 0.0
        assert cost_report.get_total_pages() == 0

    def test_add_parse_result(self, cost_report: CostReport) -> None:
        """Test adding a parse result."""
        cost_report.add_parse_result("aws_textract", "test.pdf", 10, 0.015)

        assert len(cost_report.results) == 1
        result = cost_report.results[0]
        assert result.parser_name == "aws_textract"
        assert result.pdf_name == "test.pdf"
        assert result.pages == 10
        assert result.cost == 0.015
        assert result.success is True

    def test_add_failed_result(self, cost_report: CostReport) -> None:
        """Test adding a failed parse result."""
        cost_report.add_parse_result(
            "aws_textract",
            "test.pdf",
            0,
            0.0,
            success=False,
            error="API error",
        )

        result = cost_report.results[0]
        assert result.success is False
        assert result.error == "API error"

    def test_get_total_cost(self, cost_report: CostReport) -> None:
        """Test total cost calculation."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result("aws_textract", "doc2.pdf", 20, 0.030)

        total_cost = cost_report.get_total_cost()
        assert total_cost == 0.045

    def test_get_total_cost_by_parser(self, cost_report: CostReport) -> None:
        """Test total cost calculation filtered by parser."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result("azure_document_intelligence", "doc2.pdf", 20, 0.030)

        aws_cost = cost_report.get_total_cost("aws_textract")
        azure_cost = cost_report.get_total_cost("azure_document_intelligence")

        assert aws_cost == 0.015
        assert azure_cost == 0.030

    def test_get_total_pages(self, cost_report: CostReport) -> None:
        """Test total pages calculation."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result("aws_textract", "doc2.pdf", 20, 0.030)

        total_pages = cost_report.get_total_pages()
        assert total_pages == 30

    def test_get_total_pages_by_parser(self, cost_report: CostReport) -> None:
        """Test total pages calculation filtered by parser."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result("azure_document_intelligence", "doc2.pdf", 20, 0.030)

        aws_pages = cost_report.get_total_pages("aws_textract")
        azure_pages = cost_report.get_total_pages("azure_document_intelligence")

        assert aws_pages == 10
        assert azure_pages == 20

    def test_get_parser_breakdown(self, cost_report: CostReport) -> None:
        """Test per-parser cost breakdown."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result("aws_textract", "doc2.pdf", 20, 0.030)
        cost_report.add_parse_result("azure_document_intelligence", "doc3.pdf", 15, 0.0225)

        breakdown = cost_report.get_parser_breakdown()

        assert "aws_textract" in breakdown
        assert "azure_document_intelligence" in breakdown

        aws_stats = breakdown["aws_textract"]
        assert aws_stats["total_cost"] == 0.045
        assert aws_stats["total_pages"] == 30
        assert aws_stats["pdf_count"] == 2
        assert aws_stats["successes"] == 2
        assert aws_stats["failures"] == 0
        assert aws_stats["cost_per_page"] == 0.0015

    def test_get_parser_breakdown_with_failures(self, cost_report: CostReport) -> None:
        """Test parser breakdown includes failure counts."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result(
            "aws_textract", "doc2.pdf", 0, 0.0, success=False, error="Failed"
        )

        breakdown = cost_report.get_parser_breakdown()
        aws_stats = breakdown["aws_textract"]

        assert aws_stats["successes"] == 1
        assert aws_stats["failures"] == 1

    def test_summary_empty_report(self, cost_report: CostReport) -> None:
        """Test summary for empty report."""
        summary = cost_report.summary()
        assert "No parsing results" in summary

    def test_summary_with_results(self, cost_report: CostReport) -> None:
        """Test summary with results."""
        cost_report.add_parse_result("aws_textract", "doc1.pdf", 10, 0.015)
        cost_report.add_parse_result("azure_document_intelligence", "doc2.pdf", 20, 0.030)

        summary = cost_report.summary()

        assert "Cost Report Summary" in summary
        assert "Total PDFs Processed: 2" in summary
        assert "Total Pages Processed: 30" in summary
        assert "$0.05" in summary or "$0.04" in summary  # Total cost
        assert "aws_textract" in summary
        assert "azure_document_intelligence" in summary


class TestCostEstimatorIntegration:
    """Integration tests for cost estimator with real PDF files."""

    def test_realistic_cost_estimate(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test realistic cost estimate with sample PDF."""
        # Estimate for 100 sample PDFs
        pdfs = [sample_pdf]  # Just one, but we can scale the estimate
        estimate = estimator.estimate_cost(pdfs, "aws_textract")

        # Calculate cost for 100 similar PDFs
        cost_per_pdf = estimate.total_cost
        cost_for_100 = cost_per_pdf * 100

        # Should be reasonable (under $1 for 100 single-page PDFs)
        assert cost_for_100 < 1.0

    def test_compare_commercial_vs_opensource(
        self, estimator: CostEstimator, sample_pdf: Path
    ) -> None:
        """Test cost comparison between commercial and open-source parsers."""
        commercial_estimate = estimator.estimate_cost([sample_pdf], "aws_textract")
        opensource_estimate = estimator.estimate_cost([sample_pdf], "pymupdf")

        # Commercial should have positive cost
        assert commercial_estimate.total_cost > 0

        # Open-source should be free
        assert opensource_estimate.total_cost == 0.0

        # Both should process same number of pages
        assert commercial_estimate.total_pages == opensource_estimate.total_pages
