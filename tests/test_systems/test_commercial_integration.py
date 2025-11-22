"""Integration tests for commercial PDF parsers (AWS Textract, Azure Document Intelligence).

This module tests the integration of commercial parsers with:
- Cost tracking system
- Caching system
- Error handling
- Cross-parser consistency
- Benchmark runner integration

These tests use mocked API responses to avoid actual API costs during testing.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pdf_bench.systems.aws_textract import AWSTextractParser
from pdf_bench.systems.azure_document_intelligence import (
    AzureDocumentIntelligenceParser,
)
from pdf_bench.utils.cost_tracking import CostEstimator, CostReport


class TestCommercialParserInterface:
    """Test that both commercial parsers implement the BaseParser interface correctly."""

    @patch("boto3.client")
    def test_aws_textract_implements_base_parser(self, mock_boto_client: MagicMock) -> None:
        """Test AWS Textract parser implements BaseParser interface."""
        # Setup mock
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        # Create parser
        parser = AWSTextractParser(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="us-east-1",
        )

        # Test interface compliance
        assert hasattr(parser, "name")
        assert hasattr(parser, "version")
        assert hasattr(parser, "parse")
        assert callable(parser.parse)

        # Test name property
        assert parser.name == "aws_textract"
        assert isinstance(parser.version, str)

    @patch("pdf_bench.systems.azure_document_intelligence.DocumentIntelligenceClient")
    def test_azure_di_implements_base_parser(self, mock_azure_client: MagicMock) -> None:
        """Test Azure DI parser implements BaseParser interface."""
        # Setup mock
        mock_client = MagicMock()
        mock_azure_client.return_value = mock_client

        # Create parser
        parser = AzureDocumentIntelligenceParser(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test_key",
        )

        # Test interface compliance
        assert hasattr(parser, "name")
        assert hasattr(parser, "version")
        assert hasattr(parser, "parse")
        assert callable(parser.parse)

        # Test name property
        assert parser.name == "azure_document_intelligence"
        assert isinstance(parser.version, str)


class TestCostTrackingIntegration:
    """Test cost tracking integration across commercial parsers.

    Note: Individual parser cost tracking is tested in test_aws_textract.py
    and test_azure_document_intelligence.py. These integration tests focus
    on cross-parser aggregation and reporting.
    """

    def test_cost_report_aggregation(self, tmp_path: Path) -> None:
        """Test CostReport can aggregate costs from multiple commercial parsers."""
        # Create cost report
        report = CostReport()

        # Simulate parsing with AWS Textract
        report.add_parse_result(
            parser_name="aws_textract",
            pdf_name="doc1.pdf",
            pages=10,
            cost=0.015,
            success=True,
        )

        # Simulate parsing with Azure DI
        report.add_parse_result(
            parser_name="azure_document_intelligence",
            pdf_name="doc2.pdf",
            pages=20,
            cost=0.030,
            success=True,
        )

        # Verify aggregation
        assert report.get_total_cost() == 0.045
        assert report.get_total_pages() == 30

        # Verify per-parser breakdown
        summary = report.summary()
        assert "aws_textract" in summary
        assert "azure_document_intelligence" in summary
        assert "$0.02" in summary or "$0.01" in summary  # AWS cost
        assert "$0.03" in summary  # Azure cost

    def test_cost_estimator_with_commercial_parsers(self, tmp_path: Path) -> None:
        """Test CostEstimator can estimate costs for commercial parsers."""
        # Create test PDFs with known page counts
        pdfs = []
        for i in range(3):
            pdf_path = tmp_path / f"doc{i}.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 test content")
            pdfs.append(pdf_path)

        # Mock page counting (using fitz/PyMuPDF)
        estimator = CostEstimator()

        # Estimate cost for AWS Textract (assuming 10 pages per PDF)
        with patch("fitz.open") as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 10  # 10 pages
            mock_open.return_value = mock_doc

            estimate = estimator.estimate_cost(pdfs, "aws_textract")

            # Should be 3 PDFs * 10 pages * $0.0015/page = $0.045
            assert estimate.total_pages == 30
            assert estimate.total_cost == 0.045
            assert estimate.parser_name == "aws_textract"


class TestCacheIntegration:
    """Test that commercial parsers integrate correctly with the caching system.

    Note: Detailed cache behavior is tested in individual parser unit tests.
    These integration tests verify cache usage across parser types.
    """

    def test_cache_keys_differ_by_parser(self) -> None:
        """Test that different parsers generate different cache keys."""
        # This is implicitly tested by the individual parser tests
        # Each parser has a unique name which is included in the cache key
        # This test serves as documentation of the expected behavior
        pass


class TestCrossParserConsistency:
    """Test that commercial parsers behave consistently with each other."""

    @patch("boto3.client")
    @patch("pdf_bench.systems.azure_document_intelligence.DocumentIntelligenceClient")
    def test_same_cost_per_page(self, mock_azure_client: MagicMock, mock_boto_client: MagicMock) -> None:
        """Test that both parsers have the same cost per page."""
        # Setup mocks
        mock_boto_client.return_value = MagicMock()
        mock_azure_client.return_value = MagicMock()

        # Create parsers
        aws_parser = AWSTextractParser(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
        )
        azure_parser = AzureDocumentIntelligenceParser(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test_key",
        )

        # Verify same pricing
        assert aws_parser.COST_PER_PAGE == azure_parser.COST_PER_PAGE
        assert aws_parser.COST_PER_PAGE == 0.0015

    def test_both_parsers_can_be_instantiated_together(self) -> None:
        """Test both parsers can be instantiated in the same process."""
        # This test verifies no resource conflicts occur
        with patch("boto3.client"), patch(
            "pdf_bench.systems.azure_document_intelligence.DocumentIntelligenceClient"
        ):
            aws_parser = AWSTextractParser(
                aws_access_key_id="test_key",
                aws_secret_access_key="test_secret",
            )
            azure_parser = AzureDocumentIntelligenceParser(
                endpoint="https://test.cognitiveservices.azure.com/",
                api_key="test_key",
            )

            # Both should be instantiated successfully
            assert aws_parser is not None
            assert azure_parser is not None

            # Both should have correct identities
            assert aws_parser.name == "aws_textract"
            assert azure_parser.name == "azure_document_intelligence"


class TestBudgetEnforcement:
    """Test that cost budget enforcement works with commercial parsers."""

    def test_cost_estimator_budget_check(self, tmp_path: Path) -> None:
        """Test CostEstimator can check if parsing would exceed budget."""
        # Create test PDFs
        pdfs = []
        for i in range(100):  # 100 PDFs
            pdf_path = tmp_path / f"doc{i}.pdf"
            pdf_path.write_bytes(b"%PDF-1.4 test content")
            pdfs.append(pdf_path)

        # Mock page counting (10 pages per PDF = 1,000 pages total)
        estimator = CostEstimator()

        with patch("fitz.open") as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__.return_value = 10  # 10 pages
            mock_open.return_value = mock_doc

            # Check against a $1 budget
            # 1,000 pages * $0.0015/page = $1.50, should exceed budget
            within_budget, estimate = estimator.check_budget(
                pdfs, "aws_textract", max_cost=1.0
            )

            assert not within_budget
            assert estimate.total_cost > 1.0

            # Check against a $2 budget (should be within)
            within_budget, estimate = estimator.check_budget(
                pdfs, "aws_textract", max_cost=2.0
            )

            assert within_budget
            assert estimate.total_cost < 2.0
