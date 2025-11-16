"""Tests for SEC EDGAR HTML to Markdown converter."""

import pytest

from builders.sec_html_to_markdown import (
    SECHTMLToMarkdown,
    SECMarkdownConversionError,
    convert_sec_html_to_markdown,
)


class TestSECHTMLToMarkdown:
    """Test SECHTMLToMarkdown class."""

    def test_init_default_settings(self) -> None:
        """Test initialization with default settings."""
        converter = SECHTMLToMarkdown()
        assert converter.use_financial_tables is True
        assert converter.normalize_currency is True
        assert converter.strip_xbrl is True
        assert converter.extract_metadata is True

    def test_init_custom_settings(self) -> None:
        """Test initialization with custom settings."""
        converter = SECHTMLToMarkdown(
            use_financial_tables=False,
            normalize_currency=False,
            strip_xbrl=False,
            extract_metadata=False,
        )
        assert converter.use_financial_tables is False
        assert converter.normalize_currency is False
        assert converter.strip_xbrl is False
        assert converter.extract_metadata is False


class TestNormalization:
    """Test whitespace normalization."""

    def test_normalize_whitespace_collapses_spaces(self) -> None:
        """Test that multiple spaces collapse to one."""
        converter = SECHTMLToMarkdown()
        result = converter._normalize_whitespace("hello  world")
        assert result == "hello world"

    def test_normalize_whitespace_limits_newlines(self) -> None:
        """Test that 3+ newlines become 2."""
        converter = SECHTMLToMarkdown()
        result = converter._normalize_whitespace("a\n\n\nb")
        assert result == "a\n\nb"

    def test_normalize_whitespace_strips_lines(self) -> None:
        """Test that lines are stripped."""
        converter = SECHTMLToMarkdown()
        result = converter._normalize_whitespace("  line1  \n  line2  ")
        assert result == "line1\nline2"


class TestMetadataExtraction:
    """Test filing metadata extraction."""

    def test_extract_metadata_from_title(self) -> None:
        """Test extraction of metadata from title tag."""
        converter = SECHTMLToMarkdown()
        html = """
        <html>
            <head>
                <title>APPLE INC - Form 10-K</title>
            </head>
            <body></body>
        </html>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        metadata = converter._extract_filing_metadata(soup)

        assert "company_name" in metadata
        assert metadata["company_name"] == "APPLE INC"
        assert "form_type" in metadata
        assert metadata["form_type"] == "Form 10-K"

    def test_extract_metadata_from_meta_tags(self) -> None:
        """Test extraction from meta tags."""
        converter = SECHTMLToMarkdown()
        html = """
        <html>
            <head>
                <meta name="company" content="Tesla, Inc.">
                <meta name="form-type" content="10-Q">
                <meta name="filing-date" content="2024-01-15">
                <meta name="cik" content="0001318605">
            </head>
        </html>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        metadata = converter._extract_filing_metadata(soup)

        assert metadata.get("company_name") == "Tesla, Inc."
        assert metadata.get("form_type") == "10-Q"
        assert metadata.get("filing_date") == "2024-01-15"
        assert metadata.get("cik") == "0001318605"

    def test_extract_metadata_from_document_text(self) -> None:
        """Test extraction from document text patterns."""
        converter = SECHTMLToMarkdown()
        html = """
        <html>
            <body>
                <p>CIK: 0001234567</p>
                <p>Filed as of date: 2024-03-20</p>
            </body>
        </html>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        metadata = converter._extract_filing_metadata(soup)

        assert metadata.get("cik") == "0001234567"
        assert metadata.get("filing_date") == "2024-03-20"

    def test_format_metadata_header_complete(self) -> None:
        """Test formatting complete metadata as header."""
        converter = SECHTMLToMarkdown()
        metadata = {
            "company_name": "Microsoft Corporation",
            "form_type": "10-K",
            "filing_date": "2024-07-31",
            "cik": "0000789019",
        }

        header = converter._format_metadata_header(metadata)

        assert "# Microsoft Corporation - 10-K" in header
        assert "**Filing Date**: 2024-07-31" in header
        assert "**CIK**: 0000789019" in header
        assert "---" in header

    def test_format_metadata_header_minimal(self) -> None:
        """Test formatting minimal metadata."""
        converter = SECHTMLToMarkdown()
        metadata = {"company_name": "Test Company"}

        header = converter._format_metadata_header(metadata)

        assert "# Test Company" in header

    def test_format_metadata_header_empty(self) -> None:
        """Test formatting empty metadata."""
        converter = SECHTMLToMarkdown()
        metadata = {}

        header = converter._format_metadata_header(metadata)

        assert header == ""


class TestHTMLCleaning:
    """Test HTML cleaning functionality."""

    def test_clean_html_removes_scripts(self) -> None:
        """Test that script tags are removed."""
        converter = SECHTMLToMarkdown()
        html = """
        <html>
            <body>
                <p>Content</p>
                <script>alert('test');</script>
            </body>
        </html>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        converter._clean_html(soup)

        assert soup.find("script") is None
        assert soup.find("p") is not None

    def test_clean_html_removes_styles(self) -> None:
        """Test that style tags are removed."""
        converter = SECHTMLToMarkdown()
        html = """
        <html>
            <style>body { color: red; }</style>
            <body><p>Content</p></body>
        </html>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        converter._clean_html(soup)

        assert soup.find("style") is None

    def test_clean_html_removes_navigation(self) -> None:
        """Test that navigation elements are removed."""
        converter = SECHTMLToMarkdown()
        html = """
        <html>
            <nav>Navigation</nav>
            <header>Header</header>
            <footer>Footer</footer>
            <body><p>Content</p></body>
        </html>
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        converter._clean_html(soup)

        assert soup.find("nav") is None
        assert soup.find("header") is None
        assert soup.find("footer") is None
        assert soup.find("p") is not None


class TestHeadingConversion:
    """Test heading conversion."""

    def test_convert_heading_h1(self) -> None:
        """Test conversion of h1 to Markdown."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<h1>Business Overview</h1>"
        soup = BeautifulSoup(html, "html.parser")
        h1 = soup.find("h1")

        result = converter._convert_heading(h1)
        assert result == "# Business Overview"

    def test_convert_heading_h2(self) -> None:
        """Test conversion of h2 to Markdown."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<h2>Risk Factors</h2>"
        soup = BeautifulSoup(html, "html.parser")
        h2 = soup.find("h2")

        result = converter._convert_heading(h2)
        assert result == "## Risk Factors"

    def test_convert_heading_with_whitespace(self) -> None:
        """Test heading with excessive whitespace."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<h1>  Financial   Statements  </h1>"
        soup = BeautifulSoup(html, "html.parser")
        h1 = soup.find("h1")

        result = converter._convert_heading(h1)
        assert result == "# Financial Statements"


class TestParagraphConversion:
    """Test paragraph conversion."""

    def test_convert_paragraph_simple(self) -> None:
        """Test simple paragraph conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<p>This is a simple paragraph.</p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        result = converter._convert_paragraph(p)
        assert result == "This is a simple paragraph."

    def test_convert_paragraph_with_link(self) -> None:
        """Test paragraph with link."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = '<p>Visit <a href="https://example.com">our website</a>.</p>'
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        result = converter._convert_paragraph(p)
        assert "[our website](https://example.com)" in result

    def test_convert_paragraph_with_bold(self) -> None:
        """Test paragraph with bold text."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<p>This is <strong>important</strong> text.</p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        result = converter._convert_paragraph(p)
        assert "**important**" in result

    def test_convert_paragraph_with_italic(self) -> None:
        """Test paragraph with italic text."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<p>This is <em>emphasized</em> text.</p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        result = converter._convert_paragraph(p)
        assert "*emphasized*" in result

    def test_convert_paragraph_with_superscript(self) -> None:
        """Test paragraph with superscript (footnote)."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<p>See note<sup>1</sup> for details.</p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        result = converter._convert_paragraph(p)
        assert "^1" in result

    def test_convert_paragraph_with_line_break(self) -> None:
        """Test paragraph with line break."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<p>Line 1<br>Line 2</p>"
        soup = BeautifulSoup(html, "html.parser")
        p = soup.find("p")

        result = converter._convert_paragraph(p)
        assert "Line 1" in result
        assert "Line 2" in result


class TestListConversion:
    """Test list conversion."""

    def test_convert_unordered_list(self) -> None:
        """Test unordered list conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        """
        soup = BeautifulSoup(html, "html.parser")
        ul = soup.find("ul")

        result = converter._convert_list(ul)
        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

    def test_convert_ordered_list(self) -> None:
        """Test ordered list conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = """
        <ol>
            <li>First</li>
            <li>Second</li>
        </ol>
        """
        soup = BeautifulSoup(html, "html.parser")
        ol = soup.find("ol")

        result = converter._convert_list(ol)
        assert "1. First" in result
        assert "2. Second" in result

    def test_convert_nested_list(self) -> None:
        """Test nested list conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = """
        <ul>
            <li>Item 1
                <ul>
                    <li>Nested 1</li>
                    <li>Nested 2</li>
                </ul>
            </li>
            <li>Item 2</li>
        </ul>
        """
        soup = BeautifulSoup(html, "html.parser")
        ul = soup.find("ul")

        result = converter._convert_list(ul)
        assert "- Item 1" in result
        assert "  - Nested 1" in result
        assert "  - Nested 2" in result
        assert "- Item 2" in result


class TestTableConversion:
    """Test table conversion."""

    def test_convert_table_with_financial_extractor(self) -> None:
        """Test table conversion using financial extractor."""
        converter = SECHTMLToMarkdown(use_financial_tables=True)
        from bs4 import BeautifulSoup

        html = """
        <table>
            <tr><th>Item</th><th>Amount</th></tr>
            <tr><td>Revenue</td><td>$1,000</td></tr>
            <tr><td>Expenses</td><td>$500</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")

        result = converter._convert_table(table)

        # Financial extractor should produce markdown for simple tables
        assert "Item" in result
        assert "Amount" in result
        assert "Revenue" in result

    def test_convert_table_without_financial_extractor(self) -> None:
        """Test table conversion without financial extractor."""
        converter = SECHTMLToMarkdown(use_financial_tables=False)
        from bs4 import BeautifulSoup

        html = """
        <table>
            <tr><th>Col1</th><th>Col2</th></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")

        result = converter._convert_table(table)

        # Should preserve as HTML
        assert "<table>" in result
        assert "<th>" in result or "th" in result


class TestFigureAndImageConversion:
    """Test figure and image conversion."""

    def test_convert_image(self) -> None:
        """Test standalone image conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = '<img src="chart.png" alt="Revenue Chart">'
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img")

        result = converter._convert_image(img)
        assert result == "![Revenue Chart](chart.png)"

    def test_convert_figure_with_caption(self) -> None:
        """Test figure with caption."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = """
        <figure>
            <img src="graph.png" alt="Sales Graph">
            <figcaption>Sales trends over 5 years</figcaption>
        </figure>
        """
        soup = BeautifulSoup(html, "html.parser")
        figure = soup.find("figure")

        result = converter._convert_figure(figure)
        assert "![Sales Graph](graph.png)" in result
        assert "*Sales trends over 5 years*" in result


class TestBlockquoteConversion:
    """Test blockquote conversion."""

    def test_convert_blockquote(self) -> None:
        """Test blockquote conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<blockquote>This is a quoted text.</blockquote>"
        soup = BeautifulSoup(html, "html.parser")
        blockquote = soup.find("blockquote")

        result = converter._convert_blockquote(blockquote)
        assert result == "> This is a quoted text."

    def test_convert_blockquote_multiline(self) -> None:
        """Test multiline blockquote."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<blockquote>Line 1\nLine 2</blockquote>"
        soup = BeautifulSoup(html, "html.parser")
        blockquote = soup.find("blockquote")

        result = converter._convert_blockquote(blockquote)
        assert "> Line 1" in result
        assert "> Line 2" in result


class TestHorizontalRule:
    """Test horizontal rule conversion."""

    def test_convert_hr(self) -> None:
        """Test HR conversion."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = "<hr>"
        soup = BeautifulSoup(html, "html.parser")
        hr = soup.find("hr")

        result = converter._convert_hr(hr)
        assert result == "---"


class TestFullConversion:
    """Test complete HTML to Markdown conversion."""

    def test_convert_empty_html(self) -> None:
        """Test conversion of empty HTML."""
        converter = SECHTMLToMarkdown()

        with pytest.raises(SECMarkdownConversionError, match="HTML content is empty"):
            converter.convert("")

    def test_convert_simple_document(self) -> None:
        """Test conversion of simple document."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h1>Document Title</h1>
                <p>This is a paragraph.</p>
                <h2>Section 1</h2>
                <p>Section content.</p>
            </body>
        </html>
        """

        result = converter.convert(html)

        assert "# Document Title" in result
        assert "This is a paragraph." in result
        assert "## Section 1" in result
        assert "Section content." in result

    def test_convert_with_metadata(self) -> None:
        """Test conversion with metadata extraction."""
        converter = SECHTMLToMarkdown(extract_metadata=True)
        html = """
        <html>
            <head>
                <title>NVIDIA CORPORATION - Form 10-K</title>
            </head>
            <body>
                <p>CIK: 0001045810</p>
                <h1>Business</h1>
                <p>Company description.</p>
            </body>
        </html>
        """

        result = converter.convert(html)

        # Should have metadata header
        assert "NVIDIA CORPORATION" in result
        assert "10-K" in result
        assert "CIK" in result
        assert "0001045810" in result
        assert "---" in result

        # Should also have content
        assert "# Business" in result
        assert "Company description." in result

    def test_convert_with_tables(self) -> None:
        """Test conversion with tables."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h1>Financial Data</h1>
                <table>
                    <tr><th>Year</th><th>Revenue</th></tr>
                    <tr><td>2023</td><td>$100M</td></tr>
                    <tr><td>2024</td><td>$150M</td></tr>
                </table>
            </body>
        </html>
        """

        result = converter.convert(html)

        assert "# Financial Data" in result
        assert "Year" in result
        assert "Revenue" in result

    def test_convert_with_lists(self) -> None:
        """Test conversion with lists."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h1>Risk Factors</h1>
                <ul>
                    <li>Market risk</li>
                    <li>Operational risk</li>
                    <li>Financial risk</li>
                </ul>
            </body>
        </html>
        """

        result = converter.convert(html)

        assert "# Risk Factors" in result
        assert "- Market risk" in result
        assert "- Operational risk" in result
        assert "- Financial risk" in result

    def test_convert_complex_document(self) -> None:
        """Test conversion of complex document with mixed elements."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h1>Annual Report</h1>
                <p>Welcome to our annual report.</p>

                <h2>Business Overview</h2>
                <p>We operate in <strong>technology</strong> sector.</p>

                <h3>Products</h3>
                <ul>
                    <li>Product A</li>
                    <li>Product B</li>
                </ul>

                <h2>Financial Results</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Revenue</td><td>$1B</td></tr>
                </table>

                <hr>

                <p>For more info, visit <a href="https://example.com">our site</a>.</p>
            </body>
        </html>
        """

        result = converter.convert(html)

        # Check all elements are present
        assert "# Annual Report" in result
        assert "## Business Overview" in result
        assert "### Products" in result
        assert "**technology**" in result
        assert "- Product A" in result
        assert "- Product B" in result
        assert "Revenue" in result
        assert "---" in result
        assert "[our site](https://example.com)" in result


class TestConvenienceFunction:
    """Test convenience function."""

    def test_convert_sec_html_to_markdown(self) -> None:
        """Test convenience function."""
        html = """
        <html>
            <body>
                <h1>Test Document</h1>
                <p>Test content.</p>
            </body>
        </html>
        """

        result = convert_sec_html_to_markdown(html, extract_metadata=False)

        assert "# Test Document" in result
        assert "Test content." in result

    def test_convert_sec_html_to_markdown_with_options(self) -> None:
        """Test convenience function with custom options."""
        html = """
        <html>
            <body>
                <table>
                    <tr><th>A</th><th>B</th></tr>
                    <tr><td>1</td><td>2</td></tr>
                </table>
            </body>
        </html>
        """

        result = convert_sec_html_to_markdown(
            html,
            use_financial_tables=True,
            normalize_currency=True,
            extract_metadata=False,
        )

        assert "A" in result
        assert "B" in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_convert_malformed_html(self) -> None:
        """Test conversion of malformed HTML (should handle gracefully)."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h1>Unclosed heading
                <p>Paragraph</p>
            </body>
        """

        # BeautifulSoup should parse this gracefully
        result = converter.convert(html)
        assert "Unclosed heading" in result
        assert "Paragraph" in result

    def test_convert_html_with_only_whitespace(self) -> None:
        """Test conversion of HTML with only whitespace."""
        converter = SECHTMLToMarkdown()

        with pytest.raises(SECMarkdownConversionError, match="HTML content is empty"):
            converter.convert("   \n\n   ")

    def test_convert_nested_tables(self) -> None:
        """Test handling of nested tables."""
        converter = SECHTMLToMarkdown(extract_metadata=False, use_financial_tables=False)
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <td>
                            <table>
                                <tr><td>Nested</td></tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """

        result = converter.convert(html)
        # Should handle nested tables (only outer processed)
        assert "table" in result.lower()

    def test_should_skip_element_nested_list(self) -> None:
        """Test skipping nested list elements."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = """
        <ul>
            <li>Item
                <ul>
                    <li>Nested</li>
                </ul>
            </li>
        </ul>
        """
        soup = BeautifulSoup(html, "html.parser")
        outer_ul = soup.find("ul")
        inner_ul = outer_ul.find("ul")

        # Inner list should be skipped
        assert converter._should_skip_element(inner_ul) is True
        # Outer list should not be skipped
        assert converter._should_skip_element(outer_ul) is False

    def test_should_skip_element_nested_table(self) -> None:
        """Test skipping nested table elements."""
        converter = SECHTMLToMarkdown()
        from bs4 import BeautifulSoup

        html = """
        <table>
            <tr>
                <td>
                    <table><tr><td>Nested</td></tr></table>
                </td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        outer_table = soup.find("table")
        inner_table = outer_table.find("table")

        # Inner table should be skipped
        assert converter._should_skip_element(inner_table) is True
        # Outer table should not be skipped
        assert converter._should_skip_element(outer_table) is False


class TestSECSpecificFormatting:
    """Test SEC-specific formatting scenarios."""

    def test_convert_signature_block(self) -> None:
        """Test conversion of signature block."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h3>Signatures</h3>
                <p>Pursuant to the requirements of Section 13...</p>
                <table>
                    <tr><td>Date: December 31, 2024</td></tr>
                    <tr><td>By: /s/ John Doe</td></tr>
                    <tr><td>John Doe, CEO</td></tr>
                </table>
            </body>
        </html>
        """

        result = converter.convert(html)

        assert "### Signatures" in result
        assert "Pursuant to" in result

    def test_convert_table_of_contents(self) -> None:
        """Test conversion of table of contents."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h2>Table of Contents</h2>
                <ul>
                    <li><a href="#part1">Part I</a>
                        <ul>
                            <li><a href="#item1">Item 1. Business</a></li>
                            <li><a href="#item1a">Item 1A. Risk Factors</a></li>
                        </ul>
                    </li>
                    <li><a href="#part2">Part II</a></li>
                </ul>
            </body>
        </html>
        """

        result = converter.convert(html)

        assert "## Table of Contents" in result
        assert "[Part I](#part1)" in result
        assert "[Item 1. Business](#item1)" in result
        assert "[Item 1A. Risk Factors](#item1a)" in result

    def test_convert_financial_footnotes(self) -> None:
        """Test conversion of financial footnotes."""
        converter = SECHTMLToMarkdown(extract_metadata=False)
        html = """
        <html>
            <body>
                <h3>Notes to Financial Statements</h3>
                <p><strong>Note 1: Summary of Significant Accounting Policies</strong></p>
                <p>We prepare our financial statements<sup>1</sup> in accordance with GAAP.</p>
                <hr>
                <p><sup>1</sup> Subject to certain adjustments as described herein.</p>
            </body>
        </html>
        """

        result = converter.convert(html)

        assert "### Notes to Financial Statements" in result
        assert "**Note 1: Summary of Significant Accounting Policies**" in result
        assert "^1" in result  # Superscript marker

    def test_convert_xbrl_tagged_content(self) -> None:
        """Test handling of XBRL-tagged content."""
        converter = SECHTMLToMarkdown(extract_metadata=False, use_financial_tables=True, strip_xbrl=True)
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <td>Revenue</td>
                        <td><ix:nonFraction contextRef="c1">1000000</ix:nonFraction></td>
                    </tr>
                </table>
            </body>
        </html>
        """

        result = converter.convert(html)

        # XBRL tags should be stripped but content preserved
        assert "Revenue" in result
        assert "1000000" in result or "1,000,000" in result  # Depends on normalization
        assert "ix:nonFraction" not in result  # XBRL tag should be gone
