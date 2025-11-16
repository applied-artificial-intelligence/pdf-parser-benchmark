"""Tests for GOV.UK HTML scraper."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from builders.scrape_govuk import (
    ContentExtractionError,
    GovUKScraperError,
    NetworkError,
    download_html,
    extract_main_content,
    save_html_content,
    scrape_and_save,
    scrape_govuk_content,
)

# Sample HTML templates for testing
SAMPLE_GOVUK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test GOV.UK Page</title>
    <style>body { color: black; }</style>
</head>
<body>
    <header>
        <div class="govuk-header">Header content</div>
    </header>
    <nav class="gem-c-breadcrumbs">
        <a href="/">Home</a> > <a href="/test">Test</a>
    </nav>
    <main id="content">
        <h1>Test Publication</h1>
        <div class="publication-content">
            <h2>Section 1</h2>
            <p>This is the main content that should be extracted.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <table>
                <tr><th>Header</th><td>Data</td></tr>
            </table>
        </div>
        <nav class="gem-c-related-navigation">Related links</nav>
    </main>
    <footer>
        <div class="govuk-footer">Footer content</div>
    </footer>
    <script>console.log("tracking");</script>
</body>
</html>
"""

SAMPLE_ARTICLE_HTML = """
<!DOCTYPE html>
<html>
<body>
    <header>Header</header>
    <article class="publication">
        <h1>Article Title</h1>
        <p>Article content here.</p>
    </article>
    <footer>Footer</footer>
</body>
</html>
"""

SAMPLE_MINIMAL_HTML = """
<!DOCTYPE html>
<html>
<body>
    <main>
        <h1>Simple Page</h1>
        <p>Simple content.</p>
    </main>
</body>
</html>
"""

SAMPLE_NO_MAIN_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="wrapper">
        <p>No main content tag</p>
    </div>
</body>
</html>
"""


class TestDownloadHtml:
    """Tests for download_html function."""

    @patch("builders.scrape_govuk.requests.get")
    def test_successful_download(self, mock_get):
        """Test successful HTML download."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = download_html("https://www.gov.uk/test")

        assert result == "<html><body>Test</body></html>"
        mock_get.assert_called_once()
        assert "User-Agent" in mock_get.call_args[1]["headers"]

    @patch("builders.scrape_govuk.requests.get")
    def test_uses_custom_user_agent(self, mock_get):
        """Test that custom User-Agent header is set."""
        mock_response = Mock()
        mock_response.text = "test"
        mock_get.return_value = mock_response

        download_html("https://www.gov.uk/test")

        user_agent = mock_get.call_args[1]["headers"]["User-Agent"]
        assert "PDF-Bench" in user_agent

    @patch("builders.scrape_govuk.requests.get")
    def test_timeout_parameter(self, mock_get):
        """Test that timeout parameter is passed to requests."""
        mock_response = Mock()
        mock_response.text = "test"
        mock_get.return_value = mock_response

        download_html("https://www.gov.uk/test", timeout=60)

        assert mock_get.call_args[1]["timeout"] == 60

    @patch("builders.scrape_govuk.requests.get")
    @patch("builders.scrape_govuk.time.sleep")
    def test_retry_on_timeout(self, mock_sleep, mock_get):
        """Test retry logic on timeout."""
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            Mock(text="Success", status_code=200),
        ]

        result = download_html("https://www.gov.uk/test", max_retries=3)

        assert result == "Success"
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep between retries

    @patch("builders.scrape_govuk.requests.get")
    @patch("builders.scrape_govuk.time.sleep")
    def test_exponential_backoff(self, mock_sleep, mock_get):
        """Test exponential backoff between retries."""
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            Mock(text="Success", status_code=200),
        ]

        download_html("https://www.gov.uk/test", max_retries=3, backoff_factor=2.0)

        # First retry should wait 2.0^0 = 1.0 second
        mock_sleep.assert_called_once_with(1.0)

    @patch("builders.scrape_govuk.requests.get")
    def test_raises_on_404(self, mock_get):
        """Test that 404 errors are not retried."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        with pytest.raises(NetworkError, match="HTTP 404"):
            download_html("https://www.gov.uk/test")

        # Should not retry on 4xx errors
        mock_get.assert_called_once()

    @patch("builders.scrape_govuk.requests.get")
    @patch("builders.scrape_govuk.time.sleep")
    def test_retries_on_500(self, mock_sleep, mock_get):
        """Test that 500 errors are retried."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        with pytest.raises(NetworkError, match="HTTP error after"):
            download_html("https://www.gov.uk/test", max_retries=3)

        # Should retry on 5xx errors
        assert mock_get.call_count == 3

    @patch("builders.scrape_govuk.requests.get")
    def test_raises_after_max_retries(self, mock_get):
        """Test that NetworkError is raised after max retries."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        with pytest.raises(NetworkError, match="Timeout after 3 attempts"):
            download_html("https://www.gov.uk/test", max_retries=3)

        assert mock_get.call_count == 3

    @patch("builders.scrape_govuk.requests.get")
    @patch("builders.scrape_govuk.time.sleep")
    def test_retries_on_connection_error(self, mock_sleep, mock_get):
        """Test retry on connection errors."""
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            Mock(text="Success", status_code=200),
        ]

        result = download_html("https://www.gov.uk/test", max_retries=3)

        assert result == "Success"
        assert mock_get.call_count == 2


class TestExtractMainContent:
    """Tests for extract_main_content function."""

    def test_extracts_main_tag_with_id(self):
        """Test extraction of <main id='content'> tag."""
        result = extract_main_content(SAMPLE_GOVUK_HTML)

        assert "<h1>Test Publication</h1>" in result
        assert "This is the main content" in result
        assert "<table>" in result
        # Should NOT include header, footer, nav, scripts
        assert "Header content" not in result
        assert "Footer content" not in result
        assert "gem-c-breadcrumbs" not in result
        assert "tracking" not in result
        assert "<script>" not in result

    def test_extracts_article_tag(self):
        """Test extraction of <article> tag."""
        result = extract_main_content(SAMPLE_ARTICLE_HTML)

        assert "<h1>Article Title</h1>" in result
        assert "Article content here" in result
        assert "Header" not in result
        assert "Footer" not in result

    def test_extracts_simple_main_tag(self):
        """Test extraction of simple <main> tag."""
        result = extract_main_content(SAMPLE_MINIMAL_HTML)

        assert "<h1>Simple Page</h1>" in result
        assert "Simple content" in result

    def test_removes_navigation_from_content(self):
        """Test that navigation elements within main are removed."""
        result = extract_main_content(SAMPLE_GOVUK_HTML)

        assert "Related links" not in result
        assert "gem-c-related-navigation" not in result

    def test_removes_breadcrumbs(self):
        """Test that breadcrumbs are removed."""
        result = extract_main_content(SAMPLE_GOVUK_HTML)

        assert "gem-c-breadcrumbs" not in result

    def test_removes_scripts_and_styles(self):
        """Test that script and style tags are removed."""
        html_with_inline = """
        <html>
        <body>
            <main>
                <h1>Content</h1>
                <script>alert("test");</script>
                <style>body { color: red; }</style>
                <p>Text</p>
            </main>
        </body>
        </html>
        """
        result = extract_main_content(html_with_inline)

        assert "<h1>Content</h1>" in result
        assert "<p>Text</p>" in result
        assert "<script>" not in result
        assert "<style>" not in result
        assert "alert" not in result

    def test_preserves_semantic_html(self):
        """Test that semantic HTML structure is preserved."""
        result = extract_main_content(SAMPLE_GOVUK_HTML)

        # Should preserve headings
        assert "<h1>" in result
        assert "<h2>" in result
        # Should preserve lists
        assert "<ul>" in result
        assert "<li>" in result
        # Should preserve tables
        assert "<table>" in result
        assert "<tr>" in result
        assert "<th>" in result
        # Should preserve paragraphs
        assert "<p>" in result

    def test_raises_on_no_main_content(self):
        """Test that ContentExtractionError is raised when no main content found."""
        with pytest.raises(ContentExtractionError, match="Could not find main content"):
            extract_main_content(SAMPLE_NO_MAIN_HTML)

    def test_raises_on_empty_content(self):
        """Test that ContentExtractionError is raised when content is empty."""
        empty_main_html = "<html><body><main></main></body></html>"

        with pytest.raises(ContentExtractionError, match="Extracted content is empty"):
            extract_main_content(empty_main_html)

    def test_handles_govuk_main_wrapper_class(self):
        """Test extraction of .govuk-main-wrapper class."""
        html = """
        <html><body>
        <div class="govuk-main-wrapper">
            <h1>Main Wrapper Content</h1>
        </div>
        </body></html>
        """
        result = extract_main_content(html)

        assert "<h1>Main Wrapper Content</h1>" in result

    def test_url_parameter_for_logging(self):
        """Test that url parameter is accepted (for logging)."""
        # Should not raise even with url parameter
        result = extract_main_content(SAMPLE_MINIMAL_HTML, url="https://www.gov.uk/test")
        assert "<h1>Simple Page</h1>" in result


class TestScrapeGovukContent:
    """Tests for scrape_govuk_content function."""

    @patch("builders.scrape_govuk.download_html")
    @patch("builders.scrape_govuk.time.sleep")
    def test_combines_download_and_extract(self, mock_sleep, mock_download):
        """Test that scrape_govuk_content combines download and extract."""
        mock_download.return_value = SAMPLE_GOVUK_HTML

        result = scrape_govuk_content("https://www.gov.uk/test")

        assert "<h1>Test Publication</h1>" in result
        mock_download.assert_called_once()

    @patch("builders.scrape_govuk.download_html")
    @patch("builders.scrape_govuk.time.sleep")
    def test_applies_rate_limiting(self, mock_sleep, mock_download):
        """Test that rate limiting delay is applied."""
        mock_download.return_value = SAMPLE_MINIMAL_HTML

        scrape_govuk_content("https://www.gov.uk/test", rate_limit_delay=2.0)

        mock_sleep.assert_called_once_with(2.0)

    @patch("builders.scrape_govuk.download_html")
    @patch("builders.scrape_govuk.time.sleep")
    def test_no_rate_limiting_when_zero(self, mock_sleep, mock_download):
        """Test that rate limiting can be disabled."""
        mock_download.return_value = SAMPLE_MINIMAL_HTML

        scrape_govuk_content("https://www.gov.uk/test", rate_limit_delay=0)

        mock_sleep.assert_not_called()

    @patch("builders.scrape_govuk.download_html")
    def test_passes_max_retries(self, mock_download):
        """Test that max_retries parameter is passed to download_html."""
        mock_download.return_value = SAMPLE_MINIMAL_HTML

        scrape_govuk_content("https://www.gov.uk/test", max_retries=5, rate_limit_delay=0)

        mock_download.assert_called_once()
        assert mock_download.call_args[1]["max_retries"] == 5

    @patch("builders.scrape_govuk.download_html")
    def test_raises_network_error(self, mock_download):
        """Test that NetworkError is propagated."""
        mock_download.side_effect = NetworkError("Download failed")

        with pytest.raises(NetworkError, match="Download failed"):
            scrape_govuk_content("https://www.gov.uk/test")

    @patch("builders.scrape_govuk.download_html")
    def test_raises_content_extraction_error(self, mock_download):
        """Test that ContentExtractionError is propagated."""
        mock_download.return_value = SAMPLE_NO_MAIN_HTML

        with pytest.raises(ContentExtractionError):
            scrape_govuk_content("https://www.gov.uk/test")


class TestSaveHtmlContent:
    """Tests for save_html_content function."""

    def test_saves_content_to_file(self, tmp_path):
        """Test that content is saved to specified path."""
        output_path = tmp_path / "test.html"
        content = "<html><body>Test</body></html>"

        save_html_content(content, output_path)

        assert output_path.exists()
        assert output_path.read_text() == content

    def test_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if they don't exist."""
        output_path = tmp_path / "nested" / "dir" / "test.html"
        content = "<html><body>Test</body></html>"

        save_html_content(content, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_overwrites_existing_file(self, tmp_path):
        """Test that existing files are overwritten."""
        output_path = tmp_path / "test.html"
        output_path.write_text("old content")

        new_content = "<html><body>New</body></html>"
        save_html_content(new_content, output_path)

        assert output_path.read_text() == new_content

    def test_handles_unicode_content(self, tmp_path):
        """Test that Unicode content is handled correctly."""
        output_path = tmp_path / "test.html"
        content = "<html><body>Test with émojis: 🎉 and symbols: £€¥</body></html>"

        save_html_content(content, output_path)

        assert output_path.read_text(encoding="utf-8") == content


class TestScrapeAndSave:
    """Tests for scrape_and_save function."""

    @patch("builders.scrape_govuk.scrape_govuk_content")
    def test_successful_scrape_and_save(self, mock_scrape, tmp_path):
        """Test successful scraping and saving."""
        mock_scrape.return_value = "<html><body>Content</body></html>"
        output_path = tmp_path / "test.html"

        result = scrape_and_save("https://www.gov.uk/test", output_path)

        assert result["status"] == "success"
        assert result["url"] == "https://www.gov.uk/test"
        assert result["output_path"] == str(output_path)
        assert result["content_size"] == len("<html><body>Content</body></html>")
        assert "error" not in result
        assert output_path.exists()

    @patch("builders.scrape_govuk.scrape_govuk_content")
    def test_handles_network_error(self, mock_scrape, tmp_path):
        """Test error handling for network errors."""
        mock_scrape.side_effect = NetworkError("Download failed")
        output_path = tmp_path / "test.html"

        result = scrape_and_save("https://www.gov.uk/test", output_path)

        assert result["status"] == "error"
        assert result["url"] == "https://www.gov.uk/test"
        assert result["content_size"] == 0
        assert "Download failed" in result["error"]

    @patch("builders.scrape_govuk.scrape_govuk_content")
    def test_handles_extraction_error(self, mock_scrape, tmp_path):
        """Test error handling for extraction errors."""
        mock_scrape.side_effect = ContentExtractionError("No content found")
        output_path = tmp_path / "test.html"

        result = scrape_and_save("https://www.gov.uk/test", output_path)

        assert result["status"] == "error"
        assert "No content found" in result["error"]

    @patch("builders.scrape_govuk.scrape_govuk_content")
    def test_passes_parameters(self, mock_scrape, tmp_path):
        """Test that parameters are passed correctly."""
        mock_scrape.return_value = "<html><body>Test</body></html>"
        output_path = tmp_path / "test.html"

        scrape_and_save(
            "https://www.gov.uk/test",
            output_path,
            max_retries=5,
            rate_limit_delay=2.0,
        )

        mock_scrape.assert_called_once_with(
            "https://www.gov.uk/test", max_retries=5, rate_limit_delay=2.0
        )


class TestErrorHierarchy:
    """Tests for exception hierarchy."""

    def test_network_error_is_govuk_scraper_error(self):
        """Test that NetworkError is a subclass of GovUKScraperError."""
        error = NetworkError("test")
        assert isinstance(error, GovUKScraperError)

    def test_content_extraction_error_is_govuk_scraper_error(self):
        """Test that ContentExtractionError is a subclass of GovUKScraperError."""
        error = ContentExtractionError("test")
        assert isinstance(error, GovUKScraperError)

    def test_can_catch_all_errors_with_base_exception(self):
        """Test that all scraper errors can be caught with base exception."""
        errors = [
            NetworkError("network"),
            ContentExtractionError("extraction"),
        ]

        for error in errors:
            with pytest.raises(GovUKScraperError):
                raise error
