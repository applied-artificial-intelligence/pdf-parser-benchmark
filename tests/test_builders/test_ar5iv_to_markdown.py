"""
Tests for ar5iv HTML5 to Markdown converter.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add builders to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "builders"))

from ar5iv_to_markdown import (
    download_ar5iv_html,
    extract_main_content,
    convert_ar5iv_to_markdown,
    download_and_convert_ar5iv,
    Ar5ivDownloadError,
    Ar5ivConversionError,
)


class TestDownloadAr5ivHtml:
    """Test ar5iv HTML download functionality."""

    def test_download_success(self, tmp_path):
        """Test successful ar5iv HTML download."""
        mock_html = "<html><article class='ltx_document'>Test content</article></html>"

        with patch('ar5iv_to_markdown.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'text/html'}
            mock_response.text = mock_html
            mock_get.return_value = mock_response

            output_path = tmp_path / "test.html"
            result = download_ar5iv_html("2303.08774", output_path)

            assert result is True
            assert output_path.exists()
            assert output_path.read_text() == mock_html

    def test_download_404(self, tmp_path):
        """Test 404 error handling."""
        import requests

        with patch('ar5iv_to_markdown.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
            mock_get.return_value = mock_response

            output_path = tmp_path / "test.html"

            with pytest.raises(Ar5ivDownloadError, match="not found"):
                download_ar5iv_html("9999.99999", output_path)

    def test_download_wrong_content_type(self, tmp_path):
        """Test wrong content type error."""
        with patch('ar5iv_to_markdown.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.text = '{"error": "not html"}'
            mock_get.return_value = mock_response

            output_path = tmp_path / "test.html"

            with pytest.raises(Ar5ivDownloadError, match="Expected HTML"):
                download_ar5iv_html("2303.08774", output_path)


class TestExtractMainContent:
    """Test content extraction from ar5iv HTML."""

    def test_extract_article(self, tmp_path):
        """Test extracting article from ar5iv HTML."""
        html = """
        <html>
        <body>
            <article class="ltx_document">
                <h1 class="ltx_title">Test Title</h1>
                <p>Test content</p>
            </article>
        </body>
        </html>
        """

        html_path = tmp_path / "test.html"
        html_path.write_text(html)

        article = extract_main_content(html_path)

        assert article is not None
        assert article.name == 'article'
        assert 'ltx_document' in article.get('class', [])

    def test_extract_fallback_to_body(self, tmp_path):
        """Test fallback to body when article not found."""
        html = """
        <html>
        <body>
            <h1>Test Title</h1>
            <p>Test content</p>
        </body>
        </html>
        """

        html_path = tmp_path / "test.html"
        html_path.write_text(html)

        content = extract_main_content(html_path)

        assert content is not None
        assert content.name == 'body'

    def test_extract_missing_content_error(self, tmp_path):
        """Test error when no content can be extracted."""
        html = "<html><head><title>Empty</title></head></html>"

        html_path = tmp_path / "test.html"
        html_path.write_text(html)

        with pytest.raises(Ar5ivConversionError, match="Could not find"):
            extract_main_content(html_path)


class TestConvertAr5ivToMarkdown:
    """Test ar5iv HTML to Markdown conversion."""

    def test_basic_conversion(self, tmp_path):
        """Test basic HTML to Markdown conversion."""
        html = """
        <html>
        <body>
            <article class="ltx_document">
                <h1 class="ltx_title ltx_title_document">Test Paper</h1>
                <div class="ltx_abstract">
                    <h6 class="ltx_title ltx_title_abstract">Abstract</h6>
                    <p>This is a test abstract.</p>
                </div>
                <section class="ltx_section">
                    <h2 class="ltx_title ltx_title_section">1 Introduction</h2>
                    <p>This is the introduction.</p>
                </section>
            </article>
        </body>
        </html>
        """

        html_path = tmp_path / "test.html"
        html_path.write_text(html)

        output_path = tmp_path / "output.md"

        result = convert_ar5iv_to_markdown(html_path, output_path)

        assert result['success'] is True
        assert output_path.exists()

        markdown = output_path.read_text()
        assert '# Test Paper' in markdown
        assert 'Abstract' in markdown
        assert 'Introduction' in markdown

    def test_conversion_with_math(self, tmp_path):
        """Test conversion with mathematical content."""
        html = """
        <html>
        <body>
            <article class="ltx_document">
                <h1>Math Test</h1>
                <p>Here is some math: <math id="m1" class="ltx_Math">
                    <semantics>
                        <annotation encoding="application/x-tex">E = mc^2</annotation>
                    </semantics>
                </math></p>
            </article>
        </body>
        </html>
        """

        html_path = tmp_path / "test.html"
        html_path.write_text(html)

        output_path = tmp_path / "output.md"

        result = convert_ar5iv_to_markdown(html_path, output_path)

        assert result['success'] is True

        markdown = output_path.read_text()
        assert '$E = mc^2$' in markdown or 'E = mc^2' in markdown

    def test_conversion_stats(self, tmp_path):
        """Test that conversion returns correct statistics."""
        html = """
        <html>
        <body>
            <article class="ltx_document">
                <h1>Stats Test</h1>
                <section class="ltx_section">
                    <h2>Section 1</h2>
                    <p>Content</p>
                </section>
                <section class="ltx_section">
                    <h2>Section 2</h2>
                    <p>More content</p>
                </section>
            </article>
        </body>
        </html>
        """

        html_path = tmp_path / "test.html"
        html_path.write_text(html)

        output_path = tmp_path / "output.md"

        result = convert_ar5iv_to_markdown(html_path, output_path)

        assert result['success'] is True
        assert 'stats' in result
        assert result['stats']['sections'] >= 2
        assert result['stats']['size_bytes'] > 0


class TestDownloadAndConvertAr5iv:
    """Test complete pipeline."""

    def test_complete_pipeline_success(self, tmp_path):
        """Test successful complete pipeline."""
        mock_html = """
        <html>
        <body>
            <article class="ltx_document">
                <h1>Complete Pipeline Test</h1>
                <p>Test content</p>
            </article>
        </body>
        </html>
        """

        with patch('ar5iv_to_markdown.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'text/html'}
            mock_response.text = mock_html
            mock_get.return_value = mock_response

            result = download_and_convert_ar5iv("2303.08774", tmp_path)

            assert result['success'] is True
            assert result['arxiv_id'] == "2303.08774"
            assert result['html_path'] is not None
            assert result['markdown_path'] is not None
            assert result['error'] is None
            assert result['stats'] is not None

    def test_complete_pipeline_download_failure(self, tmp_path):
        """Test pipeline with download failure."""
        import requests

        with patch('ar5iv_to_markdown.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
            mock_get.return_value = mock_response

            result = download_and_convert_ar5iv("9999.99999", tmp_path)

            assert result['success'] is False
            assert result['error'] is not None
            assert "not found" in result['error'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
