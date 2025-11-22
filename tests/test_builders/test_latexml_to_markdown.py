"""
Unit tests for LaTeXML to Markdown converter.

Tests conversion of LaTeXML HTML/XML output to CommonMark Markdown,
including headings, paragraphs, lists, math, and tables.
"""

import pytest

# Add builders to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'builders'))

from latexml_to_markdown import (
    LaTeXMLToMarkdownConverter,
    LaTeXMLConversionError,
    convert_latexml_to_markdown,
)


class TestLaTeXMLToMarkdownConverter:
    """Test LaTeXMLToMarkdownConverter class."""

    def test_convert_simple_paragraph(self):
        """Test conversion of simple paragraph."""
        html = '<div class="ltx_document"><p class="ltx_p">This is a simple paragraph.</p></div>'

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "This is a simple paragraph." in result

    def test_convert_headings(self):
        """Test conversion of section headings."""
        html = '''
        <div class="ltx_document">
            <section class="ltx_section">
                <h2 class="ltx_title">Introduction</h2>
                <p class="ltx_p">Section content.</p>
            </section>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "# Introduction" in result
        assert "Section content." in result

    def test_convert_subsections(self):
        """Test conversion of nested sections."""
        html = '''
        <div class="ltx_document">
            <section class="ltx_section">
                <h2 class="ltx_title">Main Section</h2>
                <section class="ltx_subsection">
                    <h3 class="ltx_title">Subsection</h3>
                    <p class="ltx_p">Subsection content.</p>
                </section>
            </section>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "# Main Section" in result
        assert "## Subsection" in result

    def test_convert_itemize_list(self):
        """Test conversion of bulleted list (itemize)."""
        html = '''
        <div class="ltx_document">
            <ul class="ltx_itemize">
                <li class="ltx_item">First item</li>
                <li class="ltx_item">Second item</li>
                <li class="ltx_item">Third item</li>
            </ul>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "- First item" in result
        assert "- Second item" in result
        assert "- Third item" in result

    def test_convert_enumerate_list(self):
        """Test conversion of numbered list (enumerate)."""
        html = '''
        <div class="ltx_document">
            <ol class="ltx_enumerate">
                <li class="ltx_item">First item</li>
                <li class="ltx_item">Second item</li>
                <li class="ltx_item">Third item</li>
            </ol>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "1. First item" in result
        assert "2. Second item" in result
        assert "3. Third item" in result

    def test_convert_inline_math(self):
        """Test conversion of inline math (preserves LaTeX)."""
        html = '''
        <div class="ltx_document">
            <p class="ltx_p">The equation <math class="ltx_Math"><annotation encoding="application/x-tex">E = mc^2</annotation></math> is famous.</p>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "$E = mc^2$" in result

    def test_convert_display_math(self):
        """Test conversion of display math."""
        html = '''
        <div class="ltx_document">
            <math class="ltx_Math displaystyle">
                <annotation encoding="application/x-tex">\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}</annotation>
            </math>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "$$" in result
        assert "\\int_{-\\infty}^{\\infty}" in result

    def test_convert_simple_table(self):
        """Test conversion of simple table to GFM."""
        html = '''
        <div class="ltx_document">
            <table class="ltx_tabular">
                <tr><th>Header 1</th><th>Header 2</th></tr>
                <tr><td>Cell 1</td><td>Cell 2</td></tr>
                <tr><td>Cell 3</td><td>Cell 4</td></tr>
            </table>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        # Should be GFM table
        assert "| Header 1 | Header 2 |" in result
        assert "|" in result
        assert "---" in result

    def test_convert_complex_table(self):
        """Test conversion of complex table (with rowspan) to HTML."""
        html = '''
        <div class="ltx_document">
            <table class="ltx_tabular">
                <tr><th rowspan="2">Header</th><th>Col 1</th></tr>
                <tr><td>Data 1</td></tr>
            </table>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        # Should preserve as HTML (contains rowspan)
        assert "<table" in result
        assert "rowspan" in result

    def test_convert_strong_and_em(self):
        """Test conversion of bold and italic text."""
        html = '''
        <div class="ltx_document">
            <p class="ltx_p">This is <strong>bold</strong> and <em>italic</em> text.</p>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "**bold**" in result
        assert "*italic*" in result

    def test_convert_link(self):
        """Test conversion of hyperlinks."""
        html = '''
        <div class="ltx_document">
            <p class="ltx_p">Visit <a href="https://example.com">this link</a> for more.</p>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "[this link](https://example.com)" in result

    def test_convert_figure(self):
        """Test conversion of figure with caption."""
        html = '''
        <div class="ltx_document">
            <figure class="ltx_figure">
                <img src="diagram.png" alt="System Diagram"/>
                <figcaption class="ltx_caption">Figure 1: System architecture</figcaption>
            </figure>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "![" in result
        assert "](diagram.png)" in result
        assert "System architecture" in result

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        html = '''
        <div class="ltx_document">
            <p class="ltx_p">Paragraph    with     extra      spaces.</p>



            <p class="ltx_p">Another paragraph.</p>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        # Should normalize multiple spaces to single space
        assert "Paragraph with extra spaces." in result

        # Should not have more than 2 consecutive newlines
        assert "\n\n\n" not in result

    def test_convert_without_ltx_document(self):
        """Test conversion when ltx_document class is missing."""
        html = '<body><p>Simple paragraph.</p></body>'

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "Simple paragraph." in result

    def test_convert_nested_lists(self):
        """Test conversion of nested lists."""
        html = '''
        <div class="ltx_document">
            <ul class="ltx_itemize">
                <li class="ltx_item">
                    Item 1
                    <ul class="ltx_itemize">
                        <li class="ltx_item">Nested item 1.1</li>
                        <li class="ltx_item">Nested item 1.2</li>
                    </ul>
                </li>
                <li class="ltx_item">Item 2</li>
            </ul>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        # Should contain nested items (markdown will flatten them, which is ok)
        assert "Item 1" in result
        assert "Nested item 1.1" in result

    def test_convert_code(self):
        """Test conversion of inline code."""
        html = '''
        <div class="ltx_document">
            <p class="ltx_p">Use the <code>print()</code> function.</p>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        assert "`print()`" in result

    def test_conversion_error_handling(self):
        """Test error handling for invalid HTML."""
        # Malformed HTML should still attempt conversion
        html = '<div class="ltx_document"><p>Unclosed paragraph'

        converter = LaTeXMLToMarkdownConverter()
        # BeautifulSoup is forgiving, so this should still work
        result = converter.convert(html)

        assert "Unclosed paragraph" in result

    def test_convenience_function(self):
        """Test the convenience function convert_latexml_to_markdown."""
        html = '<div class="ltx_document"><p class="ltx_p">Test paragraph.</p></div>'

        result = convert_latexml_to_markdown(html)

        assert "Test paragraph." in result

    def test_complex_document(self):
        """Test conversion of complex document with multiple elements."""
        html = '''
        <div class="ltx_document">
            <section class="ltx_section">
                <h2 class="ltx_title">Introduction</h2>
                <p class="ltx_p">This paper discusses <math class="ltx_Math"><annotation encoding="application/x-tex">E = mc^2</annotation></math>.</p>

                <section class="ltx_subsection">
                    <h3 class="ltx_title">Background</h3>
                    <p class="ltx_p">Key points:</p>
                    <ul class="ltx_itemize">
                        <li class="ltx_item">Point one</li>
                        <li class="ltx_item">Point two</li>
                    </ul>
                </section>
            </section>

            <section class="ltx_section">
                <h2 class="ltx_title">Methods</h2>
                <p class="ltx_p">We used the following equation:</p>
                <math class="ltx_Math displaystyle">
                    <annotation encoding="application/x-tex">\\sum_{i=1}^{n} x_i = \\mu</annotation>
                </math>

                <table class="ltx_tabular">
                    <tr><th>Method</th><th>Result</th></tr>
                    <tr><td>A</td><td>0.95</td></tr>
                    <tr><td>B</td><td>0.87</td></tr>
                </table>
            </section>
        </div>
        '''

        converter = LaTeXMLToMarkdownConverter()
        result = converter.convert(html)

        # Check all major elements are present
        assert "# Introduction" in result
        assert "## Background" in result
        assert "# Methods" in result
        assert "$E = mc^2$" in result
        assert "$$" in result
        assert "\\sum_{i=1}^{n}" in result
        assert "- Point one" in result
        assert "| Method | Result |" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
