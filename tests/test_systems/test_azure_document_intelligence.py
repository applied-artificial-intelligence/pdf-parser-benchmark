"""Tests for Azure Document Intelligence parser implementation with mocked API calls."""

import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from pdf_bench.systems.azure_document_intelligence import (
    AzureDocumentIntelligenceParser,
)
from pdf_bench.utils.caching import clear_cache, get_cache_stats


@pytest.fixture
def mock_azure_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Azure credentials for testing."""
    monkeypatch.setenv(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
        "https://test-resource.cognitiveservices.azure.com/",
    )
    monkeypatch.setenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "test_api_key")


@pytest.fixture
def mock_analyze_result() -> Mock:
    """Create a mock AnalyzeResult with typical response."""
    result = Mock()
    result.pages = [
        Mock(
            lines=[
                Mock(content="PDF Bench Sample Document"),
                Mock(content="This is a test document for PDF benchmarking."),
            ]
        )
    ]
    return result


@pytest.fixture
def mock_doc_intelligence_client(mock_analyze_result: Mock) -> Mock:
    """Create a mock Document Intelligence client with typical responses."""
    client = Mock()

    # Create mock poller
    poller = Mock()
    poller.result.return_value = mock_analyze_result

    client.begin_analyze_document.return_value = poller

    return client


@pytest.fixture
def parser(
    mock_azure_credentials: None, mock_doc_intelligence_client: Mock
) -> AzureDocumentIntelligenceParser:
    """Create an AzureDocumentIntelligenceParser instance with mocked client."""
    with patch(
        "pdf_bench.systems.azure_document_intelligence.DocumentIntelligenceClient",
        return_value=mock_doc_intelligence_client,
    ):
        parser = AzureDocumentIntelligenceParser()
        parser._client = mock_doc_intelligence_client
        return parser


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
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture(autouse=True)
def clear_test_cache() -> None:
    """Clear cache before each test to ensure clean state."""
    cache_dir = Path(".cache")
    clear_cache(cache_dir, parser_name="azure_document_intelligence")


class TestAzureDocumentIntelligenceParserInitialization:
    """Test parser initialization and configuration."""

    def test_parser_requires_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that parser raises error without Azure credentials."""
        # Remove environment variables
        monkeypatch.delenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", raising=False)
        monkeypatch.delenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", raising=False)

        with pytest.raises(RuntimeError, match="credentials not found"):
            AzureDocumentIntelligenceParser()

    def test_parser_uses_env_credentials(
        self, mock_azure_credentials: None, mock_doc_intelligence_client: Mock
    ) -> None:
        """Test that parser loads credentials from environment variables."""
        with patch(
            "pdf_bench.systems.azure_document_intelligence.DocumentIntelligenceClient",
            return_value=mock_doc_intelligence_client,
        ) as mock_client:
            parser = AzureDocumentIntelligenceParser()

            # Verify client was called with correct endpoint
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert (
                call_kwargs["endpoint"]
                == "https://test-resource.cognitiveservices.azure.com/"
            )

    def test_parser_uses_constructor_credentials(
        self, mock_doc_intelligence_client: Mock
    ) -> None:
        """Test that parser accepts credentials via constructor."""
        with patch(
            "pdf_bench.systems.azure_document_intelligence.DocumentIntelligenceClient",
            return_value=mock_doc_intelligence_client,
        ) as mock_client:
            parser = AzureDocumentIntelligenceParser(
                endpoint="https://custom.cognitiveservices.azure.com/",
                api_key="custom_key",
            )

            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["endpoint"] == "https://custom.cognitiveservices.azure.com/"


class TestAzureDocumentIntelligenceParserProperties:
    """Test parser properties (name, version)."""

    def test_parser_name(self, parser: AzureDocumentIntelligenceParser) -> None:
        """Test that parser name is correct."""
        assert parser.name == "azure_document_intelligence"

    def test_parser_version(self, parser: AzureDocumentIntelligenceParser) -> None:
        """Test that parser version is a non-empty string."""
        assert isinstance(parser.version, str)
        assert len(parser.version) > 0

    def test_parser_repr(self, parser: AzureDocumentIntelligenceParser) -> None:
        """Test parser string representation."""
        repr_str = repr(parser)
        assert "AzureDocumentIntelligenceParser" in repr_str
        assert "azure_document_intelligence" in repr_str
        assert parser.version in repr_str


class TestAzureDocumentIntelligenceParserBasicParsing:
    """Test basic parsing functionality with mocked API."""

    def test_parse_sample_pdf(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test parsing a PDF with mocked Azure response."""
        result = parser.parse(sample_pdf, output_dir)

        # Check that result path is returned
        assert result is not None
        assert isinstance(result, Path)

        # Check that file was created
        assert result.exists()
        assert result.is_file()
        assert result.suffix == ".md"

        # Check that file has content
        content = result.read_text(encoding="utf-8")
        assert len(content) > 0

        # Verify Azure API was called
        mock_doc_intelligence_client.begin_analyze_document.assert_called_once()

    def test_parse_calls_azure_api(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test that parse calls Azure Document Intelligence API."""
        parser.parse(sample_pdf, output_dir)

        # Verify API was called with prebuilt-read model
        mock_doc_intelligence_client.begin_analyze_document.assert_called_once()
        call_args = mock_doc_intelligence_client.begin_analyze_document.call_args
        assert call_args[1]["model_id"] == "prebuilt-read"
        assert call_args[1]["content_type"] == "application/pdf"

    def test_parse_extracts_text_from_response(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test that parser extracts text from Azure response."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should contain text from mock lines
        assert "PDF Bench Sample Document" in content
        assert "This is a test document for PDF benchmarking." in content

        # Should have two paragraphs (from two lines)
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        assert len(paragraphs) == 2


class TestAzureDocumentIntelligenceParserCostTracking:
    """Test cost tracking functionality."""

    def test_parse_tracks_cost(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
        mock_analyze_result: Mock,
    ) -> None:
        """Test that parser tracks parsing cost."""
        # Clear cache to ensure parsing occurs
        clear_cache(Path(".cache"), parser_name="azure_document_intelligence")

        # Mock response with 1 page
        mock_analyze_result.pages = [Mock(lines=[Mock(content="Test")])]

        parser.parse(sample_pdf, output_dir)

        # Cost should be $0.0015 for 1 page
        assert parser.last_parsing_cost == 0.0015

    def test_parse_tracks_multi_page_cost(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
        mock_analyze_result: Mock,
    ) -> None:
        """Test cost tracking for multi-page documents."""
        # Mock response with 10 pages
        mock_analyze_result.pages = [Mock(lines=[Mock(content="Test")]) for _ in range(10)]

        parser.parse(sample_pdf, output_dir)

        # Cost should be $0.015 for 10 pages
        assert parser.last_parsing_cost == 0.015

    def test_cached_parse_has_zero_cost(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test that cached results don't incur costs."""
        # First parse
        parser.parse(sample_pdf, output_dir)
        first_cost = parser.last_parsing_cost

        # Second parse (should be cached)
        parser.parse(sample_pdf, output_dir)
        second_cost = parser.last_parsing_cost

        # Second parse should have zero cost
        assert first_cost > 0
        assert second_cost == 0.0

    def test_get_total_cost(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test total cost tracking across multiple parses."""
        # Clear cache
        clear_cache(Path(".cache"), parser_name="azure_document_intelligence")

        # Parse same document twice (both should be cached after first)
        parser.parse(sample_pdf, output_dir)
        parser.parse(sample_pdf, output_dir)

        # Total cost should only reflect first parse
        assert parser.get_total_cost() == 0.0015

    def test_get_total_pages(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
        mock_analyze_result: Mock,
    ) -> None:
        """Test total page tracking."""
        # Clear cache
        clear_cache(Path(".cache"), parser_name="azure_document_intelligence")

        # Mock 5-page response
        mock_analyze_result.pages = [Mock(lines=[Mock(content="Test")]) for _ in range(5)]

        parser.parse(sample_pdf, output_dir)

        assert parser.get_total_pages() == 5


class TestAzureDocumentIntelligenceParserCaching:
    """Test cache integration."""

    def test_cache_miss_on_first_parse(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test that first parse is a cache miss."""
        clear_cache(Path(".cache"), parser_name="azure_document_intelligence")

        parser.parse(sample_pdf, output_dir)

        # Check cache stats
        stats = get_cache_stats(Path(".cache"))
        assert "azure_document_intelligence" in stats["parsers"]
        parser_stats = stats["parsers"]["azure_document_intelligence"]
        assert parser_stats["misses"] >= 1

    def test_cache_hit_on_second_parse(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test that second parse is a cache hit."""
        clear_cache(Path(".cache"), parser_name="azure_document_intelligence")

        # First parse
        parser.parse(sample_pdf, output_dir)

        # Second parse
        parser.parse(sample_pdf, output_dir)

        # Check cache stats
        stats = get_cache_stats(Path(".cache"))
        parser_stats = stats["parsers"]["azure_document_intelligence"]
        assert parser_stats["hits"] >= 1

    def test_cached_result_not_reparsed(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test that cached results don't trigger API calls."""
        # First parse
        parser.parse(sample_pdf, output_dir)

        # Reset mock call count
        mock_doc_intelligence_client.begin_analyze_document.reset_mock()

        # Second parse (should be cached)
        parser.parse(sample_pdf, output_dir)

        # API should not be called again
        mock_doc_intelligence_client.begin_analyze_document.assert_not_called()


class TestAzureDocumentIntelligenceParserErrorHandling:
    """Test error handling and edge cases."""

    def test_parse_missing_file(
        self, parser: AzureDocumentIntelligenceParser, output_dir: Path
    ) -> None:
        """Test that parser raises error for missing PDF file."""
        missing_pdf = Path("nonexistent.pdf")

        with pytest.raises(FileNotFoundError):
            parser.parse(missing_pdf, output_dir)

    def test_parse_not_a_file(
        self, parser: AzureDocumentIntelligenceParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser raises error for directory path."""
        directory = tmp_path / "not_a_file"
        directory.mkdir()

        with pytest.raises(ValueError, match="not a file"):
            parser.parse(directory, output_dir)

    def test_parse_file_too_large(
        self, parser: AzureDocumentIntelligenceParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser raises error for files > 500 MB."""
        # Create a large dummy file (501 MB)
        large_pdf = tmp_path / "large.pdf"
        large_pdf.write_bytes(b"x" * (501 * 1024 * 1024))

        with pytest.raises(ValueError, match="too large"):
            parser.parse(large_pdf, output_dir)

    def test_parse_rate_limit_error(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test handling of Azure rate limit errors."""
        # Mock rate limit error
        mock_error = HttpResponseError()
        mock_error.status_code = 429
        mock_doc_intelligence_client.begin_analyze_document.side_effect = mock_error

        with pytest.raises(RuntimeError, match="rate limit exceeded"):
            parser.parse(sample_pdf, output_dir)

    def test_parse_invalid_parameter_error(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test handling of invalid parameter errors."""
        mock_error = HttpResponseError()
        mock_error.status_code = 400
        mock_doc_intelligence_client.begin_analyze_document.side_effect = mock_error

        with pytest.raises(ValueError, match="Invalid PDF file"):
            parser.parse(sample_pdf, output_dir)

    def test_parse_resource_not_found_error(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
    ) -> None:
        """Test handling of resource not found errors."""
        mock_doc_intelligence_client.begin_analyze_document.side_effect = (
            ResourceNotFoundError()
        )

        with pytest.raises(RuntimeError, match="Azure Document Intelligence"):
            parser.parse(sample_pdf, output_dir)


class TestAzureDocumentIntelligenceParserTextExtraction:
    """Test text extraction from Azure responses."""

    def test_extract_text_joins_lines_with_newlines(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
        mock_analyze_result: Mock,
    ) -> None:
        """Test that text lines are joined with paragraph breaks."""
        mock_analyze_result.pages = [
            Mock(
                lines=[
                    Mock(content="Paragraph 1"),
                    Mock(content="Paragraph 2"),
                    Mock(content="Paragraph 3"),
                ]
            )
        ]

        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have double newlines between paragraphs
        assert "Paragraph 1\n\nParagraph 2\n\nParagraph 3" in content

    def test_extract_text_handles_multiple_pages(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
        mock_analyze_result: Mock,
    ) -> None:
        """Test that text from multiple pages is combined."""
        mock_analyze_result.pages = [
            Mock(lines=[Mock(content="Page 1 Line 1"), Mock(content="Page 1 Line 2")]),
            Mock(lines=[Mock(content="Page 2 Line 1"), Mock(content="Page 2 Line 2")]),
        ]

        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # All lines should be present
        assert "Page 1 Line 1" in content
        assert "Page 1 Line 2" in content
        assert "Page 2 Line 1" in content
        assert "Page 2 Line 2" in content

    def test_extract_text_handles_empty_pages(
        self,
        parser: AzureDocumentIntelligenceParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_doc_intelligence_client: Mock,
        mock_analyze_result: Mock,
    ) -> None:
        """Test that empty pages are handled gracefully."""
        mock_analyze_result.pages = [
            Mock(lines=[Mock(content="Page 1 Content")]),
            Mock(lines=[]),  # Empty page
            Mock(lines=[Mock(content="Page 3 Content")]),
        ]

        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Non-empty pages should be present
        assert "Page 1 Content" in content
        assert "Page 3 Content" in content
