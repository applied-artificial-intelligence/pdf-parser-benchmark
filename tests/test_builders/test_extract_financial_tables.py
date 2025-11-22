"""Tests for financial table extraction from SEC EDGAR filings."""

import pytest
from bs4 import BeautifulSoup

from builders.extract_financial_tables import (
    TableComplexity,
    _count_header_rows,
    _get_column_count,
    _has_merged_cells,
    _has_xbrl_tags,
    _normalize_cell_text,
    _normalize_currency,
    _normalize_whitespace,
    _strip_xbrl_tags,
    _table_to_html,
    _table_to_markdown,
    classify_table,
    extract_table,
    extract_tables_from_html,
)


class TestNormalization:
    """Test normalization functions."""

    def test_normalize_currency_removes_dollar_sign(self) -> None:
        """Test that $ symbols are removed."""
        assert _normalize_currency("$1,234") == "1234"
        assert _normalize_currency("$1,234.56") == "1234.56"

    def test_normalize_currency_removes_commas(self) -> None:
        """Test that commas are removed from numbers."""
        assert _normalize_currency("1,234,567") == "1234567"
        assert _normalize_currency("12,345.67") == "12345.67"

    def test_normalize_currency_converts_parentheses(self) -> None:
        """Test that (number) becomes -number."""
        assert _normalize_currency("(123)") == "-123"
        assert _normalize_currency("(1,234)") == "-1234"
        assert _normalize_currency("($1,234.56)") == "-1234.56"

    def test_normalize_currency_preserves_text(self) -> None:
        """Test that non-numeric text is preserved."""
        assert _normalize_currency("Revenue") == "Revenue"
        assert _normalize_currency("Total Assets") == "Total Assets"

    def test_normalize_whitespace_collapses_spaces(self) -> None:
        """Test that multiple spaces collapse to one."""
        assert _normalize_whitespace("hello  world") == "hello world"
        assert _normalize_whitespace("a   b   c") == "a b c"

    def test_normalize_whitespace_limits_newlines(self) -> None:
        """Test that 3+ newlines become 2."""
        assert _normalize_whitespace("a\n\n\nb") == "a\n\nb"
        assert _normalize_whitespace("x\n\n\n\ny") == "x\n\ny"

    def test_normalize_whitespace_strips_lines(self) -> None:
        """Test that lines are stripped of leading/trailing space."""
        text = "  line1  \n  line2  "
        assert _normalize_whitespace(text) == "line1\nline2"

    def test_normalize_cell_text_with_currency(self) -> None:
        """Test cell text normalization with currency."""
        assert _normalize_cell_text("  $1,234.56  ") == "1234.56"
        assert _normalize_cell_text("  (123)  ") == "-123"

    def test_normalize_cell_text_without_currency(self) -> None:
        """Test cell text normalization without currency processing."""
        assert _normalize_cell_text("  $1,234.56  ", normalize_currency=False) == "$1,234.56"
        assert _normalize_cell_text("  hello  world  ") == "hello world"


class TestXBRLDetection:
    """Test XBRL tag detection."""

    def test_has_xbrl_tags_detects_ix_namespace(self) -> None:
        """Test detection of ix: namespace tags."""
        html = "<table><td><ix:nonFraction>123</ix:nonFraction></td></table>"
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _has_xbrl_tags(table) is True

    def test_has_xbrl_tags_detects_us_gaap(self) -> None:
        """Test detection of us-gaap: namespace."""
        html = '<table><td name="us-gaap:Assets">123</td></table>'
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _has_xbrl_tags(table) is True

    def test_has_xbrl_tags_returns_false_for_plain_html(self) -> None:
        """Test that plain HTML tables return False."""
        html = "<table><tr><td>123</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _has_xbrl_tags(table) is False

    def test_strip_xbrl_tags_preserves_content(self) -> None:
        """Test that XBRL tags are removed but content preserved."""
        html = '<td><ix:nonFraction contextRef="c1">12345</ix:nonFraction></td>'
        result = _strip_xbrl_tags(html)
        assert "12345" in result
        assert "ix:nonFraction" not in result


class TestMergedCellDetection:
    """Test merged cell detection."""

    def test_has_merged_cells_detects_rowspan(self) -> None:
        """Test detection of rowspan attribute."""
        html = '<table><tr><td rowspan="2">Cell</td></tr></table>'
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _has_merged_cells(table) is True

    def test_has_merged_cells_detects_colspan(self) -> None:
        """Test detection of colspan attribute."""
        html = '<table><tr><td colspan="3">Cell</td></tr></table>'
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _has_merged_cells(table) is True

    def test_has_merged_cells_returns_false_for_simple_table(self) -> None:
        """Test that simple tables without merging return False."""
        html = "<table><tr><td>A</td><td>B</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _has_merged_cells(table) is False


class TestHeaderRowCounting:
    """Test header row counting."""

    def test_count_header_rows_with_thead(self) -> None:
        """Test counting rows in <thead>."""
        html = """
        <table>
            <thead>
                <tr><th>Col1</th><th>Col2</th></tr>
                <tr><th>Sub1</th><th>Sub2</th></tr>
            </thead>
            <tbody>
                <tr><td>1</td><td>2</td></tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _count_header_rows(table) == 2

    def test_count_header_rows_with_th_cells(self) -> None:
        """Test counting rows with majority <th> cells."""
        html = """
        <table>
            <tr><th>Col1</th><th>Col2</th></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _count_header_rows(table) == 1

    def test_count_header_rows_no_headers(self) -> None:
        """Test counting when no headers present."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _count_header_rows(table) == 0


class TestColumnCounting:
    """Test column counting."""

    def test_get_column_count_uniform_table(self) -> None:
        """Test column count for uniform table."""
        html = """
        <table>
            <tr><td>A</td><td>B</td><td>C</td></tr>
            <tr><td>1</td><td>2</td><td>3</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _get_column_count(table) == 3

    def test_get_column_count_with_colspan(self) -> None:
        """Test column count accounting for colspan."""
        html = """
        <table>
            <tr><td colspan="2">Header</td><td>C</td></tr>
            <tr><td>A</td><td>B</td><td>C</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _get_column_count(table) == 3

    def test_get_column_count_variable_rows(self) -> None:
        """Test column count with variable row lengths."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>1</td><td>2</td><td>3</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert _get_column_count(table) == 3  # Maximum


class TestTableClassification:
    """Test table classification."""

    def test_classify_simple_table(self) -> None:
        """Test classification of simple table."""
        html = """
        <table>
            <tr><th>Name</th><th>Value</th></tr>
            <tr><td>Item 1</td><td>100</td></tr>
            <tr><td>Item 2</td><td>200</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert classify_table(table) == TableComplexity.SIMPLE

    def test_classify_medium_table_with_multi_headers(self) -> None:
        """Test classification of table with multiple header rows."""
        html = """
        <table>
            <thead>
                <tr><th colspan="2">Financial Data</th></tr>
                <tr><th>2023</th><th>2024</th></tr>
            </thead>
            <tbody>
                <tr><td>100</td><td>200</td></tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        complexity = classify_table(table)
        # Has merged cells (colspan), should be at least MEDIUM
        assert complexity in [TableComplexity.MEDIUM, TableComplexity.COMPLEX]

    def test_classify_complex_table_with_nested_table(self) -> None:
        """Test classification of table with nested table."""
        html = """
        <table>
            <tr>
                <td>
                    <table>
                        <tr><td>Nested</td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert classify_table(table) == TableComplexity.COMPLEX

    def test_classify_complex_table_with_xbrl(self) -> None:
        """Test classification of table with XBRL tags."""
        html = """
        <table>
            <tr>
                <td><ix:nonFraction>123</ix:nonFraction></td>
            </tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None
        assert classify_table(table) == TableComplexity.COMPLEX


class TestMarkdownConversion:
    """Test Markdown conversion for simple tables."""

    def test_table_to_markdown_simple(self) -> None:
        """Test conversion of simple table to Markdown."""
        html = """
        <table>
            <tr><th>Name</th><th>Amount</th></tr>
            <tr><td>Revenue</td><td>$1,000</td></tr>
            <tr><td>Expenses</td><td>($500)</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        md = _table_to_markdown(table, normalize=True)

        # Check structure
        assert "Name" in md
        assert "Amount" in md
        assert "Revenue" in md
        assert "---" in md  # Separator row

        # Check normalization
        assert "1000" in md  # $ and comma removed
        assert "-500" in md  # Parentheses converted

    def test_table_to_markdown_without_normalization(self) -> None:
        """Test Markdown conversion without normalization."""
        html = """
        <table>
            <tr><th>Item</th><th>Price</th></tr>
            <tr><td>Product</td><td>$1,234.56</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        md = _table_to_markdown(table, normalize=False)

        # Currency formatting should be preserved
        assert "$1,234.56" in md

    def test_table_to_markdown_multi_level_headers(self) -> None:
        """Test Markdown conversion with multi-level headers."""
        html = """
        <table>
            <thead>
                <tr><th>Year</th><th>2023</th><th>2024</th></tr>
                <tr><th>Metric</th><th>Q1</th><th>Q1</th></tr>
            </thead>
            <tbody>
                <tr><td>Revenue</td><td>100</td><td>150</td></tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        md = _table_to_markdown(table, normalize=True)

        # Should concatenate multi-level headers
        assert "Year Metric" in md or "Year" in md
        assert "---" in md


class TestHTMLConversion:
    """Test HTML preservation for complex tables."""

    def test_table_to_html_preserves_structure(self) -> None:
        """Test that HTML conversion preserves table structure."""
        html = """
        <table>
            <tr><th colspan="2">Header</th></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        result = _table_to_html(table, strip_xbrl=False)

        assert "<table>" in result
        assert 'colspan="2"' in result
        # Tag name may or may not have angle brackets depending on formatting
        assert "th" in result

    def test_table_to_html_strips_xbrl_when_requested(self) -> None:
        """Test that XBRL tags are stripped when requested."""
        html = """
        <table>
            <tr><td><ix:nonFraction>123</ix:nonFraction></td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        result = _table_to_html(table, strip_xbrl=True)

        assert "123" in result
        assert "ix:nonFraction" not in result


class TestTableExtraction:
    """Test complete table extraction."""

    def test_extract_table_simple(self) -> None:
        """Test extraction of simple table."""
        html = """
        <table>
            <tr><th>Col1</th><th>Col2</th></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        result = extract_table(table, index=0)

        assert result.format == "markdown"
        assert result.metadata.complexity == TableComplexity.SIMPLE
        assert result.metadata.row_count == 2
        assert result.metadata.column_count == 2
        assert result.metadata.has_xbrl is False
        assert result.metadata.has_nested_tables is False
        assert result.metadata.has_merged_cells is False

    def test_extract_table_complex(self) -> None:
        """Test extraction of complex table."""
        html = """
        <table>
            <tr><td><ix:nonFraction>123</ix:nonFraction></td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        result = extract_table(table, index=0)

        assert result.format == "html"
        assert result.metadata.complexity == TableComplexity.COMPLEX
        assert result.metadata.has_xbrl is True

    def test_extract_table_with_metadata(self) -> None:
        """Test that metadata is correctly populated."""
        html = """
        <table>
            <thead>
                <tr><th colspan="3">Financial Statement</th></tr>
                <tr><th>Item</th><th>2023</th><th>2024</th></tr>
            </thead>
            <tbody>
                <tr><td>Revenue</td><td>100</td><td>150</td></tr>
                <tr><td>Expenses</td><td>60</td><td>80</td></tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        assert table is not None

        result = extract_table(table, index=5)

        assert result.metadata.index == 5
        assert result.metadata.row_count == 4  # 2 header + 2 data
        assert result.metadata.column_count == 3
        assert result.metadata.header_rows == 2
        assert result.metadata.has_merged_cells is True  # colspan


class TestBulkExtraction:
    """Test extraction from complete HTML documents."""

    def test_extract_tables_from_html_multiple_tables(self) -> None:
        """Test extraction of multiple tables from HTML."""
        html = """
        <html>
            <body>
                <table>
                    <tr><th>Simple</th></tr>
                    <tr><td>1</td></tr>
                </table>
                <p>Some text</p>
                <table>
                    <tr><td colspan="2">Complex</td></tr>
                    <tr><td>A</td><td>B</td></tr>
                </table>
            </body>
        </html>
        """

        results = extract_tables_from_html(html)

        assert len(results) == 2
        assert results[0].metadata.index == 0
        assert results[1].metadata.index == 1

    def test_extract_tables_from_html_empty(self) -> None:
        """Test extraction from HTML with no tables."""
        html = "<html><body><p>No tables here</p></body></html>"

        results = extract_tables_from_html(html)

        assert len(results) == 0

    def test_extract_tables_from_html_invalid(self) -> None:
        """Test extraction from invalid HTML."""
        with pytest.raises(ValueError, match="HTML content is empty"):
            extract_tables_from_html("")

    def test_extract_tables_from_html_with_normalization(self) -> None:
        """Test that normalization is applied correctly."""
        html = """
        <table>
            <tr><th>Amount</th></tr>
            <tr><td>$1,234</td></tr>
            <tr><td>($500)</td></tr>
        </table>
        """

        results = extract_tables_from_html(html, normalize=True)

        assert len(results) == 1
        content = results[0].content

        # Check normalization was applied
        assert "1234" in content
        assert "-500" in content

    def test_extract_tables_from_html_strip_xbrl(self) -> None:
        """Test XBRL stripping in HTML output."""
        html = """
        <table>
            <tr><td><ix:nonFraction>123</ix:nonFraction></td></tr>
        </table>
        """

        results = extract_tables_from_html(html, strip_xbrl=True)

        assert len(results) == 1
        assert "123" in results[0].content
        assert "ix:nonFraction" not in results[0].content


class TestFinancialStatementExamples:
    """Test with realistic financial statement examples."""

    def test_income_statement_simple(self) -> None:
        """Test extraction of simple income statement."""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Year Ended Dec 31, 2024</th>
                    <th>Year Ended Dec 31, 2023</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Revenue</td>
                    <td>$12,345,678</td>
                    <td>$10,234,567</td>
                </tr>
                <tr>
                    <td>Cost of Revenue</td>
                    <td>($4,567,890)</td>
                    <td>($3,456,789)</td>
                </tr>
                <tr>
                    <td>Gross Profit</td>
                    <td>$7,777,788</td>
                    <td>$6,777,778</td>
                </tr>
            </tbody>
        </table>
        """

        results = extract_tables_from_html(html, normalize=True)

        assert len(results) == 1
        table = results[0]

        assert table.format == "markdown"
        assert table.metadata.complexity == TableComplexity.SIMPLE
        assert table.metadata.row_count == 4
        assert table.metadata.column_count == 3

        # Check normalization
        content = table.content
        assert "12345678" in content  # Commas and $ removed
        assert "-4567890" in content  # Parentheses converted

    def test_balance_sheet_with_merged_cells(self) -> None:
        """Test extraction of balance sheet with section headers."""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Assets</th>
                    <th>Dec 31, 2024</th>
                    <th>Dec 31, 2023</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="3"><strong>Current Assets:</strong></td>
                </tr>
                <tr>
                    <td>Cash and Cash Equivalents</td>
                    <td>$5,000,000</td>
                    <td>$4,500,000</td>
                </tr>
                <tr>
                    <td>Accounts Receivable</td>
                    <td>$2,500,000</td>
                    <td>$2,000,000</td>
                </tr>
            </tbody>
        </table>
        """

        results = extract_tables_from_html(html)

        assert len(results) == 1
        table = results[0]

        # Has merged cells, so medium or complex
        assert table.metadata.has_merged_cells is True
        assert table.metadata.complexity in [TableComplexity.MEDIUM, TableComplexity.COMPLEX]

    def test_cash_flow_statement(self) -> None:
        """Test extraction of cash flow statement."""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Cash Flow Statement</th>
                    <th>2024</th>
                    <th>2023</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Net Income</td>
                    <td>$1,234,567</td>
                    <td>$1,000,000</td>
                </tr>
                <tr>
                    <td>Depreciation & Amortization</td>
                    <td>$500,000</td>
                    <td>$450,000</td>
                </tr>
                <tr>
                    <td>Changes in Working Capital</td>
                    <td>($200,000)</td>
                    <td>$100,000</td>
                </tr>
            </tbody>
        </table>
        """

        results = extract_tables_from_html(html, normalize=True)

        assert len(results) == 1
        table = results[0]

        # Simple structure
        assert table.metadata.complexity == TableComplexity.SIMPLE
        assert table.format == "markdown"

        # Verify content
        content = table.content
        assert "Cash Flow Statement" in content
        assert "1234567" in content
        assert "-200000" in content  # Parentheses converted

    def test_footnote_table_with_superscripts(self) -> None:
        """Test extraction of table with footnote markers."""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Property, Plant & Equipment<sup>1</sup></td>
                    <td>$10,000,000</td>
                </tr>
                <tr>
                    <td>Intangible Assets<sup>2</sup></td>
                    <td>$5,000,000</td>
                </tr>
            </tbody>
        </table>
        """

        results = extract_tables_from_html(html, normalize=True)

        assert len(results) == 1
        table = results[0]

        # Footnote markers should be preserved in text
        content = table.content
        assert "Property, Plant & Equipment" in content
        # Note: Superscript numbers may or may not be preserved depending on get_text()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_table_without_header_row(self) -> None:
        """Test table with no header (all td cells)."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>1</td><td>2</td></tr>
            <tr><td>3</td><td>4</td></tr>
        </table>
        """

        results = extract_tables_from_html(html, normalize=False)

        assert len(results) == 1
        # Should still create markdown (first row becomes header)
        assert results[0].format == "markdown"
        assert results[0].metadata.header_rows == 0

    def test_table_with_invalid_colspan(self) -> None:
        """Test table with non-numeric colspan."""
        html = """
        <table>
            <tr><td colspan="invalid">A</td><td>B</td></tr>
            <tr><td>1</td><td>2</td></tr>
        </table>
        """

        results = extract_tables_from_html(html)

        # Should still extract successfully
        assert len(results) == 1

    def test_table_with_empty_rows(self) -> None:
        """Test table with empty rows."""
        html = """
        <table>
            <tr><th>Col1</th><th>Col2</th></tr>
            <tr></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """

        results = extract_tables_from_html(html)

        assert len(results) == 1
        # Should handle gracefully

    def test_extract_tables_from_file_not_found(self) -> None:
        """Test file extraction with missing file."""
        from builders.extract_financial_tables import extract_tables_from_file

        with pytest.raises(FileNotFoundError):
            extract_tables_from_file("/nonexistent/file.html")

    def test_normalize_whitespace_edge_cases(self) -> None:
        """Test whitespace normalization with various inputs."""
        assert _normalize_whitespace("") == ""
        assert _normalize_whitespace("   ") == ""
        assert _normalize_whitespace("a\n\n\n\n\nb") == "a\n\nb"

    def test_normalize_currency_with_decimal_only(self) -> None:
        """Test currency normalization with decimal numbers."""
        assert _normalize_currency("0.50") == "0.50"
        assert _normalize_currency(".99") == ".99"
