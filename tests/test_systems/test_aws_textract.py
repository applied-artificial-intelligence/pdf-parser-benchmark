"""Tests for AWS Textract parser implementation with mocked API calls."""

import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import boto3
import pytest
from botocore.exceptions import ClientError

from pdf_bench.systems.aws_textract import AWSTextractParser
from pdf_bench.utils.caching import clear_cache, get_cache_stats


@pytest.fixture
def mock_aws_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock AWS credentials for testing."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key")
    monkeypatch.setenv("AWS_REGION", "us-east-1")


@pytest.fixture
def mock_textract_client() -> Mock:
    """Create a mock Textract client with typical responses."""
    client = Mock()

    # Default successful response
    client.detect_document_text.return_value = {
        "DocumentMetadata": {"Pages": 1},
        "Blocks": [
            {
                "BlockType": "PAGE",
                "Id": "page-1",
            },
            {
                "BlockType": "LINE",
                "Id": "line-1",
                "Text": "PDF Bench Sample Document",
            },
            {
                "BlockType": "LINE",
                "Id": "line-2",
                "Text": "This is a test document for PDF benchmarking.",
            },
            {
                "BlockType": "WORD",
                "Id": "word-1",
                "Text": "PDF",
            },
        ],
    }

    return client


@pytest.fixture
def parser(mock_aws_credentials: None, mock_textract_client: Mock) -> AWSTextractParser:
    """Create an AWSTextractParser instance with mocked client."""
    with patch("boto3.client", return_value=mock_textract_client):
        parser = AWSTextractParser()
        parser._client = mock_textract_client
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
    clear_cache(cache_dir, parser_name="aws_textract")


class TestAWSTextractParserInitialization:
    """Test parser initialization and configuration."""

    def test_parser_requires_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that parser raises error without AWS credentials."""
        # Remove environment variables
        monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
        monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

        with pytest.raises(RuntimeError, match="AWS credentials not found"):
            AWSTextractParser()

    def test_parser_uses_env_credentials(
        self, mock_aws_credentials: None, mock_textract_client: Mock
    ) -> None:
        """Test that parser loads credentials from environment variables."""
        with patch("boto3.client", return_value=mock_textract_client) as mock_boto:
            AWSTextractParser()

            # Verify boto3.client was called with correct credentials
            mock_boto.assert_called_once_with(
                "textract",
                aws_access_key_id="test_access_key",
                aws_secret_access_key="test_secret_key",
                region_name="us-east-1",
            )

    def test_parser_uses_constructor_credentials(self, mock_textract_client: Mock) -> None:
        """Test that parser accepts credentials via constructor."""
        with patch("boto3.client", return_value=mock_textract_client) as mock_boto:
            AWSTextractParser(
                aws_access_key_id="custom_key",
                aws_secret_access_key="custom_secret",
                region_name="us-west-2",
            )

            mock_boto.assert_called_once_with(
                "textract",
                aws_access_key_id="custom_key",
                aws_secret_access_key="custom_secret",
                region_name="us-west-2",
            )

    def test_parser_defaults_to_us_east_1(
        self, monkeypatch: pytest.MonkeyPatch, mock_textract_client: Mock
    ) -> None:
        """Test that parser defaults to us-east-1 region."""
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_key")
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret")
        monkeypatch.delenv("AWS_REGION", raising=False)

        with patch("boto3.client", return_value=mock_textract_client) as mock_boto:
            AWSTextractParser()

            call_kwargs = mock_boto.call_args[1]
            assert call_kwargs["region_name"] == "us-east-1"


class TestAWSTextractParserProperties:
    """Test parser properties (name, version)."""

    def test_parser_name(self, parser: AWSTextractParser) -> None:
        """Test that parser name is correct."""
        assert parser.name == "aws_textract"

    def test_parser_version(self, parser: AWSTextractParser) -> None:
        """Test that parser version matches boto3 version."""
        assert parser.version == boto3.__version__
        assert isinstance(parser.version, str)
        assert len(parser.version) > 0

    def test_parser_repr(self, parser: AWSTextractParser) -> None:
        """Test parser string representation."""
        repr_str = repr(parser)
        assert "AWSTextractParser" in repr_str
        assert "aws_textract" in repr_str
        assert parser.version in repr_str


class TestAWSTextractParserBasicParsing:
    """Test basic parsing functionality with mocked API."""

    def test_parse_sample_pdf(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test parsing a PDF with mocked Textract response."""
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

        # Verify Textract API was called
        mock_textract_client.detect_document_text.assert_called_once()

    def test_parse_calls_textract_api(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that parse calls Textract DetectDocumentText API."""
        parser.parse(sample_pdf, output_dir)

        # Verify API was called with document bytes
        mock_textract_client.detect_document_text.assert_called_once()
        call_args = mock_textract_client.detect_document_text.call_args
        assert "Document" in call_args[1]
        assert "Bytes" in call_args[1]["Document"]

    def test_parse_extracts_text_from_response(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that parser extracts text from Textract response."""
        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should contain text from mock LINE blocks
        assert "PDF Bench Sample Document" in content
        assert "This is a test document for PDF benchmarking." in content

        # Should have two paragraphs (from two LINE blocks)
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        assert len(paragraphs) == 2


class TestAWSTextractParserCostTracking:
    """Test cost tracking functionality."""

    def test_parse_tracks_cost(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that parser tracks parsing cost."""
        # Clear cache to ensure parsing occurs
        clear_cache(Path(".cache"), parser_name="aws_textract")

        # Mock response with 1 page
        mock_textract_client.detect_document_text.return_value = {
            "DocumentMetadata": {"Pages": 1},
            "Blocks": [{"BlockType": "LINE", "Text": "Test"}],
        }

        parser.parse(sample_pdf, output_dir)

        # Cost should be $0.0015 for 1 page
        assert parser.last_parsing_cost == 0.0015

    def test_parse_tracks_multi_page_cost(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test cost tracking for multi-page documents."""
        # Mock response with 10 pages
        mock_textract_client.detect_document_text.return_value = {
            "DocumentMetadata": {"Pages": 10},
            "Blocks": [{"BlockType": "LINE", "Text": "Test"}],
        }

        parser.parse(sample_pdf, output_dir)

        # Cost should be $0.015 for 10 pages
        assert parser.last_parsing_cost == 0.015

    def test_cached_parse_has_zero_cost(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
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
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test total cost tracking across multiple parses."""
        # Clear cache
        clear_cache(Path(".cache"), parser_name="aws_textract")

        # Mock 1-page response
        mock_textract_client.detect_document_text.return_value = {
            "DocumentMetadata": {"Pages": 1},
            "Blocks": [{"BlockType": "LINE", "Text": "Test"}],
        }

        # Parse same document twice (both should be cached after first)
        parser.parse(sample_pdf, output_dir)
        parser.parse(sample_pdf, output_dir)

        # Total cost should only reflect first parse
        assert parser.get_total_cost() == 0.0015

    def test_get_total_pages(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test total page tracking."""
        # Clear cache
        clear_cache(Path(".cache"), parser_name="aws_textract")

        # Mock 5-page response
        mock_textract_client.detect_document_text.return_value = {
            "DocumentMetadata": {"Pages": 5},
            "Blocks": [{"BlockType": "LINE", "Text": "Test"}],
        }

        parser.parse(sample_pdf, output_dir)

        assert parser.get_total_pages() == 5


class TestAWSTextractParserCaching:
    """Test cache integration."""

    def test_cache_miss_on_first_parse(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that first parse is a cache miss."""
        clear_cache(Path(".cache"), parser_name="aws_textract")

        parser.parse(sample_pdf, output_dir)

        # Check cache stats
        stats = get_cache_stats(Path(".cache"))
        assert "aws_textract" in stats["parsers"]
        parser_stats = stats["parsers"]["aws_textract"]
        assert parser_stats["misses"] >= 1

    def test_cache_hit_on_second_parse(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that second parse is a cache hit."""
        clear_cache(Path(".cache"), parser_name="aws_textract")

        # First parse
        parser.parse(sample_pdf, output_dir)

        # Second parse
        parser.parse(sample_pdf, output_dir)

        # Check cache stats
        stats = get_cache_stats(Path(".cache"))
        parser_stats = stats["parsers"]["aws_textract"]
        assert parser_stats["hits"] >= 1

    def test_cached_result_not_reparsed(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that cached results don't trigger API calls."""
        # First parse
        parser.parse(sample_pdf, output_dir)

        # Reset mock call count
        mock_textract_client.detect_document_text.reset_mock()

        # Second parse (should be cached)
        parser.parse(sample_pdf, output_dir)

        # API should not be called again
        mock_textract_client.detect_document_text.assert_not_called()


class TestAWSTextractParserErrorHandling:
    """Test error handling and edge cases."""

    def test_parse_missing_file(self, parser: AWSTextractParser, output_dir: Path) -> None:
        """Test that parser raises error for missing PDF file."""
        missing_pdf = Path("nonexistent.pdf")

        with pytest.raises(FileNotFoundError):
            parser.parse(missing_pdf, output_dir)

    def test_parse_not_a_file(
        self, parser: AWSTextractParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser raises error for directory path."""
        directory = tmp_path / "not_a_file"
        directory.mkdir()

        with pytest.raises(ValueError, match="not a file"):
            parser.parse(directory, output_dir)

    def test_parse_file_too_large(
        self, parser: AWSTextractParser, tmp_path: Path, output_dir: Path
    ) -> None:
        """Test that parser raises error for files > 10 MB."""
        # Create a large dummy file (11 MB)
        large_pdf = tmp_path / "large.pdf"
        large_pdf.write_bytes(b"x" * (11 * 1024 * 1024))

        with pytest.raises(ValueError, match="too large"):
            parser.parse(large_pdf, output_dir)

    def test_parse_throttling_error(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test handling of Textract throttling errors."""
        # Mock throttling error
        mock_textract_client.detect_document_text.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ThrottlingException",
                    "Message": "Rate exceeded",
                }
            },
            "DetectDocumentText",
        )

        with pytest.raises(RuntimeError, match="rate limit exceeded"):
            parser.parse(sample_pdf, output_dir)

    def test_parse_invalid_parameter_error(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test handling of invalid parameter errors."""
        mock_textract_client.detect_document_text.side_effect = ClientError(
            {
                "Error": {
                    "Code": "InvalidParameterException",
                    "Message": "Invalid document",
                }
            },
            "DetectDocumentText",
        )

        with pytest.raises(ValueError, match="Invalid PDF file"):
            parser.parse(sample_pdf, output_dir)

    def test_parse_generic_api_error(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test handling of generic API errors."""
        mock_textract_client.detect_document_text.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ServiceUnavailable",
                    "Message": "Service is down",
                }
            },
            "DetectDocumentText",
        )

        with pytest.raises(RuntimeError, match="AWS Textract API error"):
            parser.parse(sample_pdf, output_dir)


class TestAWSTextractParserTextExtraction:
    """Test text extraction from Textract responses."""

    def test_extract_blocks_filters_line_blocks(self, parser: AWSTextractParser) -> None:
        """Test that _extract_blocks only extracts LINE blocks."""
        response = {
            "Blocks": [
                {"BlockType": "PAGE", "Id": "page-1"},
                {"BlockType": "LINE", "Id": "line-1", "Text": "Line 1"},
                {"BlockType": "WORD", "Id": "word-1", "Text": "Word"},
                {"BlockType": "LINE", "Id": "line-2", "Text": "Line 2"},
            ]
        }

        blocks = parser._extract_blocks(response)

        assert len(blocks) == 2
        assert blocks[0] == "Line 1"
        assert blocks[1] == "Line 2"

    def test_extract_blocks_skips_empty_text(self, parser: AWSTextractParser) -> None:
        """Test that _extract_blocks skips empty text."""
        response = {
            "Blocks": [
                {"BlockType": "LINE", "Id": "line-1", "Text": "Line 1"},
                {"BlockType": "LINE", "Id": "line-2", "Text": ""},
                {"BlockType": "LINE", "Id": "line-3", "Text": "   "},
                {"BlockType": "LINE", "Id": "line-4", "Text": "Line 4"},
            ]
        }

        blocks = parser._extract_blocks(response)

        assert len(blocks) == 2
        assert blocks[0] == "Line 1"
        assert blocks[1] == "Line 4"

    def test_extract_text_joins_blocks_with_newlines(
        self,
        parser: AWSTextractParser,
        sample_pdf: Path,
        output_dir: Path,
        mock_textract_client: Mock,
    ) -> None:
        """Test that text blocks are joined with paragraph breaks."""
        mock_textract_client.detect_document_text.return_value = {
            "DocumentMetadata": {"Pages": 1},
            "Blocks": [
                {"BlockType": "LINE", "Text": "Paragraph 1"},
                {"BlockType": "LINE", "Text": "Paragraph 2"},
                {"BlockType": "LINE", "Text": "Paragraph 3"},
            ],
        }

        result = parser.parse(sample_pdf, output_dir)
        content = result.read_text(encoding="utf-8")

        # Should have double newlines between paragraphs
        assert "Paragraph 1\n\nParagraph 2\n\nParagraph 3" in content
