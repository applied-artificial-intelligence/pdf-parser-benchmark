"""Tests for GOV.UK HTML to Markdown converter."""

import pytest
from bs4 import BeautifulSoup

from builders.govuk_html_to_markdown import (
    MarkdownConversionError,
    _convert_figure,
    _convert_heading,
    _convert_image,
    _convert_list,
    _convert_paragraph,
    _convert_table,
    _is_simple_table,
    _normalize_whitespace,
    _table_to_gfm,
    _table_to_html,
    html_to_markdown,
)


class TestNormalizeWhitespace:
    """Tests for _normalize_whitespace function."""

    def test_removes_multiple_spaces(self):
        """Test that multiple spaces are reduced to single space."""
        text = "Hello    world    test"
        result = _normalize_whitespace(text)
        assert result == "Hello world test"

    def test_removes_excessive_newlines(self):
        """Test that 3+ newlines are reduced to 2."""
        text = "Paragraph 1\n\n\n\nParagraph 2"
        result = _normalize_whitespace(text)
        assert result == "Paragraph 1\n\nParagraph 2"

    def test_strips_line_whitespace(self):
        """Test that leading/trailing whitespace is removed from lines."""
        text = "  Line 1  \n  Line 2  "
        result = _normalize_whitespace(text)
        assert result == "Line 1\nLine 2"

    def test_preserves_single_newlines(self):
        """Test that single newlines are preserved."""
        text = "Line 1\nLine 2\nLine 3"
        result = _normalize_whitespace(text)
        assert result == "Line 1\nLine 2\nLine 3"

    def test_preserves_double_newlines(self):
        """Test that double newlines (paragraph breaks) are preserved."""
        text = "Paragraph 1\n\nParagraph 2"
        result = _normalize_whitespace(text)
        assert result == "Paragraph 1\n\nParagraph 2"

    def test_handles_empty_string(self):
        """Test handling of empty string."""
        result = _normalize_whitespace("")
        assert result == ""

    def test_handles_whitespace_only(self):
        """Test handling of whitespace-only string."""
        result = _normalize_whitespace("   \n\n   ")
        assert result == ""


class TestIsSimpleTable:
    """Tests for _is_simple_table function."""

    def test_simple_table_returns_true(self):
        """Test that simple table is identified."""
        html = """
        <table>
            <tr><th>Header 1</th><th>Header 2</th></tr>
            <tr><td>Data 1</td><td>Data 2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is True

    def test_table_with_rowspan_returns_false(self):
        """Test that table with rowspan is marked as complex."""
        html = """
        <table>
            <tr><th rowspan="2">Header</th><td>Data 1</td></tr>
            <tr><td>Data 2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is False

    def test_table_with_colspan_returns_false(self):
        """Test that table with colspan is marked as complex."""
        html = """
        <table>
            <tr><th colspan="2">Header</th></tr>
            <tr><td>Data 1</td><td>Data 2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is False

    def test_nested_table_returns_false(self):
        """Test that table with nested table is marked as complex."""
        html = """
        <table>
            <tr><td>Outer</td><td><table><tr><td>Inner</td></tr></table></td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is False

    def test_uneven_columns_returns_false(self):
        """Test that table with uneven columns is marked as complex."""
        html = """
        <table>
            <tr><td>A</td><td>B</td><td>C</td></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is False

    def test_empty_table_returns_false(self):
        """Test that empty table returns False."""
        html = "<table></table>"
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is False

    def test_table_without_header_returns_true(self):
        """Test that table without header but uniform columns returns True."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        assert _is_simple_table(table) is True


class TestTableToGfm:
    """Tests for _table_to_gfm function."""

    def test_converts_table_with_header(self):
        """Test conversion of table with header row."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
            <tr><td>Bob</td><td>25</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_gfm(table)

        assert "| Name | Age |" in result
        assert "| --- | --- |" in result
        assert "| Alice | 30 |" in result
        assert "| Bob | 25 |" in result

    def test_converts_table_without_header(self):
        """Test conversion of table without header (all td)."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_gfm(table)

        # First row becomes header
        assert "| A | B |" in result
        assert "| --- | --- |" in result
        assert "| 1 | 2 |" in result

    def test_handles_empty_cells(self):
        """Test handling of empty cells."""
        html = """
        <table>
            <tr><th>Header</th><th></th></tr>
            <tr><td>Data</td><td></td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_gfm(table)

        assert "| Header |  |" in result

    def test_handles_multiline_cell_content(self):
        """Test that multiline content in cells is normalized."""
        html = """
        <table>
            <tr><th>Header</th></tr>
            <tr><td>Line 1
            Line 2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_gfm(table)

        assert "Line 1 Line 2" in result or "Line 1\n            Line 2" in result

    def test_empty_table_returns_empty_string(self):
        """Test that empty table returns empty string."""
        html = "<table></table>"
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_gfm(table)

        assert result == ""


class TestTableToHtml:
    """Tests for _table_to_html function."""

    def test_preserves_html_structure(self):
        """Test that HTML structure is preserved."""
        html = """<table>
            <tr><th>Header</th></tr>
            <tr><td>Data</td></tr>
        </table>"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_html(table)

        assert "<table>" in result
        assert "<th>Header</th>" in result
        assert "<td>Data</td>" in result

    def test_preserves_complex_attributes(self):
        """Test that attributes like rowspan are preserved."""
        html = """<table>
            <tr><th rowspan="2">Header</th><td>Data</td></tr>
        </table>"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _table_to_html(table)

        assert 'rowspan="2"' in result or "rowspan='2'" in result


class TestConvertTable:
    """Tests for _convert_table function."""

    def test_converts_simple_table_to_gfm(self):
        """Test that simple table is converted to GFM."""
        html = """
        <table>
            <tr><th>Name</th></tr>
            <tr><td>Alice</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _convert_table(table)

        assert "| Name |" in result
        assert "| --- |" in result
        assert "<table>" not in result

    def test_preserves_complex_table_as_html(self):
        """Test that complex table is preserved as HTML."""
        html = """
        <table>
            <tr><th colspan="2">Header</th></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        result = _convert_table(table)

        assert "<table>" in result
        assert "colspan" in result


class TestConvertList:
    """Tests for _convert_list function."""

    def test_converts_unordered_list(self):
        """Test conversion of unordered list."""
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        """
        soup = BeautifulSoup(html, "lxml")
        ul = soup.find("ul")
        result = _convert_list(ul)

        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

    def test_converts_ordered_list(self):
        """Test conversion of ordered list."""
        html = """
        <ol>
            <li>First</li>
            <li>Second</li>
            <li>Third</li>
        </ol>
        """
        soup = BeautifulSoup(html, "lxml")
        ol = soup.find("ol")
        result = _convert_list(ol)

        assert "1. First" in result
        assert "2. Second" in result
        assert "3. Third" in result

    def test_converts_nested_lists(self):
        """Test conversion of nested lists."""
        html = """
        <ul>
            <li>Item 1
                <ul>
                    <li>Sub 1</li>
                    <li>Sub 2</li>
                </ul>
            </li>
            <li>Item 2</li>
        </ul>
        """
        soup = BeautifulSoup(html, "lxml")
        ul = soup.find("ul")
        result = _convert_list(ul)

        assert "- Item 1" in result
        assert "  - Sub 1" in result
        assert "  - Sub 2" in result
        assert "- Item 2" in result

    def test_handles_mixed_nested_lists(self):
        """Test conversion of mixed ordered/unordered nested lists."""
        html = """
        <ul>
            <li>Item 1
                <ol>
                    <li>Step 1</li>
                    <li>Step 2</li>
                </ol>
            </li>
        </ul>
        """
        soup = BeautifulSoup(html, "lxml")
        ul = soup.find("ul")
        result = _convert_list(ul)

        assert "- Item 1" in result
        assert "  1. Step 1" in result
        assert "  2. Step 2" in result

    def test_handles_deeply_nested_lists(self):
        """Test conversion of deeply nested lists."""
        html = """
        <ul>
            <li>Level 1
                <ul>
                    <li>Level 2
                        <ul>
                            <li>Level 3</li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>
        """
        soup = BeautifulSoup(html, "lxml")
        ul = soup.find("ul")
        result = _convert_list(ul)

        assert "- Level 1" in result
        assert "  - Level 2" in result
        assert "    - Level 3" in result


class TestConvertHeading:
    """Tests for _convert_heading function."""

    def test_converts_h1(self):
        """Test conversion of h1."""
        html = "<h1>Main Title</h1>"
        soup = BeautifulSoup(html, "lxml")
        h1 = soup.find("h1")
        result = _convert_heading(h1)
        assert result == "# Main Title"

    def test_converts_h2(self):
        """Test conversion of h2."""
        html = "<h2>Section Title</h2>"
        soup = BeautifulSoup(html, "lxml")
        h2 = soup.find("h2")
        result = _convert_heading(h2)
        assert result == "## Section Title"

    def test_converts_h3(self):
        """Test conversion of h3."""
        html = "<h3>Subsection</h3>"
        soup = BeautifulSoup(html, "lxml")
        h3 = soup.find("h3")
        result = _convert_heading(h3)
        assert result == "### Subsection"

    def test_converts_h6(self):
        """Test conversion of h6."""
        html = "<h6>Deep Heading</h6>"
        soup = BeautifulSoup(html, "lxml")
        h6 = soup.find("h6")
        result = _convert_heading(h6)
        assert result == "###### Deep Heading"

    def test_strips_whitespace(self):
        """Test that whitespace is stripped from heading text."""
        html = "<h1>  Spaced Title  </h1>"
        soup = BeautifulSoup(html, "lxml")
        h1 = soup.find("h1")
        result = _convert_heading(h1)
        assert result == "# Spaced Title"


class TestConvertParagraph:
    """Tests for _convert_paragraph function."""

    def test_converts_simple_paragraph(self):
        """Test conversion of simple paragraph."""
        html = "<p>This is a paragraph.</p>"
        soup = BeautifulSoup(html, "lxml")
        p = soup.find("p")
        result = _convert_paragraph(p)
        assert result == "This is a paragraph."

    def test_converts_links(self):
        """Test conversion of links in paragraph."""
        html = '<p>Visit <a href="https://example.com">this site</a> for info.</p>'
        soup = BeautifulSoup(html, "lxml")
        p = soup.find("p")
        result = _convert_paragraph(p)
        assert "[this site](https://example.com)" in result

    def test_converts_emphasis(self):
        """Test conversion of emphasis (em/i) tags."""
        html = "<p>This is <em>emphasized</em> and <i>italic</i>.</p>"
        soup = BeautifulSoup(html, "lxml")
        p = soup.find("p")
        result = _convert_paragraph(p)
        assert "*emphasized*" in result
        assert "*italic*" in result

    def test_converts_strong(self):
        """Test conversion of strong/b tags."""
        html = "<p>This is <strong>bold</strong> and <b>important</b>.</p>"
        soup = BeautifulSoup(html, "lxml")
        p = soup.find("p")
        result = _convert_paragraph(p)
        assert "**bold**" in result
        assert "**important**" in result

    def test_converts_code(self):
        """Test conversion of inline code."""
        html = "<p>Use the <code>print()</code> function.</p>"
        soup = BeautifulSoup(html, "lxml")
        p = soup.find("p")
        result = _convert_paragraph(p)
        assert "`print()`" in result

    def test_converts_mixed_formatting(self):
        """Test conversion of mixed inline formatting."""
        html = (
            '<p>This has <strong>bold</strong>, <em>italic</em>, and <a href="/test">links</a>.</p>'
        )
        soup = BeautifulSoup(html, "lxml")
        p = soup.find("p")
        result = _convert_paragraph(p)
        assert "**bold**" in result
        assert "*italic*" in result
        assert "[links](/test)" in result


class TestConvertFigure:
    """Tests for _convert_figure function."""

    def test_converts_figure_with_image_and_caption(self):
        """Test conversion of figure with image and caption."""
        html = """
        <figure>
            <img src="/image.jpg" alt="Test image">
            <figcaption>Image caption</figcaption>
        </figure>
        """
        soup = BeautifulSoup(html, "lxml")
        figure = soup.find("figure")
        result = _convert_figure(figure)

        assert "![Test image](/image.jpg)" in result
        assert "*Image caption*" in result

    def test_converts_figure_with_only_image(self):
        """Test conversion of figure with only image (no caption)."""
        html = """
        <figure>
            <img src="/image.jpg" alt="Test image">
        </figure>
        """
        soup = BeautifulSoup(html, "lxml")
        figure = soup.find("figure")
        result = _convert_figure(figure)

        assert "![Test image](/image.jpg)" in result
        assert "*" not in result

    def test_converts_figure_with_only_caption(self):
        """Test conversion of figure with only caption (no image)."""
        html = """
        <figure>
            <figcaption>Caption only</figcaption>
        </figure>
        """
        soup = BeautifulSoup(html, "lxml")
        figure = soup.find("figure")
        result = _convert_figure(figure)

        assert "*Caption only*" in result


class TestConvertImage:
    """Tests for _convert_image function."""

    def test_converts_image_with_alt(self):
        """Test conversion of image with alt text."""
        html = '<img src="/test.jpg" alt="Test image">'
        soup = BeautifulSoup(html, "lxml")
        img = soup.find("img")
        result = _convert_image(img)
        assert result == "![Test image](/test.jpg)"

    def test_converts_image_without_alt(self):
        """Test conversion of image without alt text."""
        html = '<img src="/test.jpg">'
        soup = BeautifulSoup(html, "lxml")
        img = soup.find("img")
        result = _convert_image(img)
        assert result == "![](/test.jpg)"

    def test_converts_image_without_src(self):
        """Test conversion of image without src."""
        html = '<img alt="No source">'
        soup = BeautifulSoup(html, "lxml")
        img = soup.find("img")
        result = _convert_image(img)
        assert result == "![No source]()"


class TestHtmlToMarkdown:
    """Tests for html_to_markdown function."""

    def test_converts_simple_document(self):
        """Test conversion of simple document."""
        html = """
        <main>
            <h1>Title</h1>
            <p>Paragraph text.</p>
        </main>
        """
        result = html_to_markdown(html)

        assert "# Title" in result
        assert "Paragraph text." in result

    def test_converts_complex_document(self):
        """Test conversion of complex document with multiple elements."""
        html = """
        <main>
            <h1>Main Title</h1>
            <p>Introduction paragraph.</p>
            <h2>Section 1</h2>
            <p>Section content.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <h2>Section 2</h2>
            <table>
                <tr><th>Header</th></tr>
                <tr><td>Data</td></tr>
            </table>
        </main>
        """
        result = html_to_markdown(html)

        assert "# Main Title" in result
        assert "## Section 1" in result
        assert "## Section 2" in result
        assert "- Item 1" in result
        assert "| Header |" in result

    def test_handles_govuk_structure(self):
        """Test conversion of actual GOV.UK HTML structure."""
        html = """
        <main class="govuk-main-wrapper" id="content">
            <div class="govuk-grid-row">
                <div class="govuk-grid-column-two-thirds">
                    <h1 class="gem-c-heading__text govuk-heading-l">NHS England Report</h1>
                    <p class="gem-c-lead-paragraph">Annual report for NHS England.</p>
                    <div class="gem-c-govspeak govuk-govspeak">
                        <div class="govspeak">
                            <p>This annual report contains information on:</p>
                            <ul>
                                <li>NHS England's work this year</li>
                                <li>achievements and challenges</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </main>
        """
        result = html_to_markdown(html)

        assert "# NHS England Report" in result
        assert "Annual report for NHS England." in result
        assert "- NHS England's work this year" in result
        assert "- achievements and challenges" in result

    def test_raises_on_empty_html(self):
        """Test that error is raised for empty HTML."""
        with pytest.raises(MarkdownConversionError, match="empty"):
            html_to_markdown("")

    def test_raises_on_whitespace_only_html(self):
        """Test that error is raised for whitespace-only HTML."""
        with pytest.raises(MarkdownConversionError, match="empty"):
            html_to_markdown("   \n  ")

    def test_raises_on_invalid_html(self):
        """Test that error is raised for invalid HTML."""
        # Malformed HTML that BeautifulSoup can't parse gracefully
        with pytest.raises(MarkdownConversionError):
            html_to_markdown(None)

    def test_handles_article_tag(self):
        """Test that article tag is recognized as content container."""
        html = """
        <article>
            <h1>Article Title</h1>
            <p>Article content.</p>
        </article>
        """
        result = html_to_markdown(html)

        assert "# Article Title" in result
        assert "Article content." in result

    def test_normalizes_output_whitespace(self):
        """Test that output whitespace is normalized."""
        html = """
        <main>
            <h1>Title</h1>


            <p>Paragraph</p>
        </main>
        """
        result = html_to_markdown(html)

        # Should not have more than 2 consecutive newlines
        assert "\n\n\n" not in result

    def test_handles_mixed_content(self):
        """Test handling of document with all element types."""
        html = """
        <main>
            <h1>Report Title</h1>
            <p>Introduction with <a href="/link">a link</a>.</p>
            <h2>Data Section</h2>
            <table>
                <tr><th>Year</th><th>Value</th></tr>
                <tr><td>2024</td><td>100</td></tr>
            </table>
            <h2>List Section</h2>
            <ul>
                <li>Point 1</li>
                <li>Point 2</li>
            </ul>
            <figure>
                <img src="/chart.png" alt="Chart">
                <figcaption>Data visualization</figcaption>
            </figure>
        </main>
        """
        result = html_to_markdown(html)

        assert "# Report Title" in result
        assert "[a link](/link)" in result
        assert "## Data Section" in result
        assert "| Year | Value |" in result
        assert "- Point 1" in result
        assert "![Chart](/chart.png)" in result
        assert "*Data visualization*" in result

    def test_skips_nested_elements(self):
        """Test that nested elements are not double-processed."""
        html = """
        <main>
            <p>Paragraph with <strong>nested</strong> elements.</p>
        </main>
        """
        result = html_to_markdown(html)

        # Should only appear once
        assert result.count("**nested**") == 1

    def test_handles_empty_elements(self):
        """Test handling of empty elements."""
        html = """
        <main>
            <h1>Title</h1>
            <p></p>
            <p>Content</p>
        </main>
        """
        result = html_to_markdown(html)

        # Empty paragraphs should be filtered out
        assert "# Title" in result
        assert "Content" in result

    def test_preserves_element_order(self):
        """Test that element order is preserved."""
        html = """
        <main>
            <h1>First</h1>
            <p>Second</p>
            <h2>Third</h2>
            <ul><li>Fourth</li></ul>
        </main>
        """
        result = html_to_markdown(html)

        first_pos = result.find("# First")
        second_pos = result.find("Second")
        third_pos = result.find("## Third")
        fourth_pos = result.find("- Fourth")

        assert first_pos < second_pos < third_pos < fourth_pos

    def test_raises_on_conversion_to_empty_result(self):
        """Test that error is raised if conversion results in empty content."""
        # HTML with only elements that produce no markdown (like divs with no text)
        html = "<main><div></div><span></span></main>"
        with pytest.raises(MarkdownConversionError, match="empty content"):
            html_to_markdown(html)
