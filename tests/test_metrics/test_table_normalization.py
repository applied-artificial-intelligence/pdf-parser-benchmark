"""Tests for HTML table normalization module."""

from __future__ import annotations

from pdf_bench.metrics.table_normalization import (
    TableCell,
    extract_table_array,
    normalize_html_table,
    tables_equal,
)


class TestTableCell:
    """Tests for TableCell class."""

    def test_init_basic(self) -> None:
        """Test basic cell initialization."""
        cell = TableCell("Hello")
        assert cell.content == "Hello"
        assert cell.rowspan == 1
        assert cell.colspan == 1
        assert cell.is_header is False

    def test_init_with_spans(self) -> None:
        """Test cell with rowspan and colspan."""
        cell = TableCell("Data", rowspan=2, colspan=3)
        assert cell.content == "Data"
        assert cell.rowspan == 2
        assert cell.colspan == 3

    def test_init_header_cell(self) -> None:
        """Test header cell."""
        cell = TableCell("Header", is_header=True)
        assert cell.is_header is True

    def test_content_stripped(self) -> None:
        """Test that content is stripped of whitespace."""
        cell = TableCell("  Spaces  \n\t")
        assert cell.content == "Spaces"


class TestNormalizeHTMLTable:
    """Tests for normalize_html_table function."""

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_html_table("") == ""

    def test_no_table(self) -> None:
        """Test HTML without table."""
        html = "<div>Not a table</div>"
        assert normalize_html_table(html) == ""

    def test_lowercase_tags(self) -> None:
        """Test that tags are lowercased."""
        html = "<TABLE><TR><TD>Data</TD></TR></TABLE>"
        normalized = normalize_html_table(html)
        assert "<table>" in normalized
        assert "<tr>" in normalized
        assert "<td>" in normalized
        assert "<TABLE>" not in normalized

    def test_lowercase_attributes(self) -> None:
        """Test that attributes are lowercased."""
        html = '<table CLASS="data" ID="tbl1"><tr><td>X</td></tr></table>'
        normalized = normalize_html_table(html)
        assert 'class="data"' in normalized
        assert 'id="tbl1"' in normalized
        assert "CLASS" not in normalized

    def test_sort_attributes(self) -> None:
        """Test that attributes are sorted alphabetically."""
        html = '<table id="tbl1" class="data"><tr><td>X</td></tr></table>'
        normalized = normalize_html_table(html)

        # Find the table tag
        table_start = normalized.find("<table")
        table_end = normalized.find(">", table_start)
        table_tag = normalized[table_start:table_end]

        # Check order: class comes before id
        class_pos = table_tag.find("class")
        id_pos = table_tag.find("id")
        assert class_pos < id_pos

    def test_normalize_whitespace(self) -> None:
        """Test whitespace normalization in cell content."""
        html = "<table><tr><td>  Multiple   Spaces  </td></tr></table>"
        normalized = normalize_html_table(html)
        assert "Multiple   Spaces" in normalized  # Preserves internal spaces

    def test_remove_empty_attributes(self) -> None:
        """Test that empty attributes are removed."""
        html = '<table class=""><tr><td>X</td></tr></table>'
        normalized = normalize_html_table(html)
        assert 'class=""' not in normalized

    def test_complex_table(self) -> None:
        """Test normalization of complex table."""
        html = """
        <TABLE class="styled" ID="data-table">
            <TR>
                <TH rowspan="2">Header</TH>
                <TD colspan="2">Spanned</TD>
            </TR>
            <TR>
                <TD>A</TD>
                <TD>B</TD>
            </TR>
        </TABLE>
        """
        normalized = normalize_html_table(html)

        # Check all tags lowercased
        assert "<table" in normalized
        assert "<th" in normalized
        assert "<td" in normalized

        # Check attributes normalized
        assert 'class="styled"' in normalized
        assert 'id="data-table"' in normalized


class TestExtractTableArray:
    """Tests for extract_table_array function."""

    def test_empty_string(self) -> None:
        """Test extraction from empty string."""
        assert extract_table_array("") == []

    def test_no_table(self) -> None:
        """Test extraction from non-table HTML."""
        assert extract_table_array("<div>Not a table</div>") == []

    def test_simple_table_1x1(self) -> None:
        """Test simple 1x1 table."""
        html = "<table><tr><td>A</td></tr></table>"
        result = extract_table_array(html)
        assert result == [["A"]]

    def test_simple_table_2x2(self) -> None:
        """Test simple 2x2 table."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>C</td><td>D</td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["A", "B"], ["C", "D"]]

    def test_table_with_headers(self) -> None:
        """Test table with th elements."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["Name", "Age"], ["Alice", "30"]]

    def test_colspan_simple(self) -> None:
        """Test table with simple colspan."""
        html = """
        <table>
            <tr><td colspan="2">Merged</td></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["Merged", "Merged"], ["A", "B"]]

    def test_rowspan_simple(self) -> None:
        """Test table with simple rowspan."""
        html = """
        <table>
            <tr><td rowspan="2">Tall</td><td>A</td></tr>
            <tr><td>B</td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["Tall", "A"], ["Tall", "B"]]

    def test_colspan_and_rowspan(self) -> None:
        """Test table with both colspan and rowspan."""
        html = """
        <table>
            <tr><td colspan="2" rowspan="2">Big</td><td>X</td></tr>
            <tr><td>Y</td></tr>
            <tr><td>A</td><td>B</td><td>C</td></tr>
        </table>
        """
        result = extract_table_array(html)
        expected = [
            ["Big", "Big", "X"],
            ["Big", "Big", "Y"],
            ["A", "B", "C"],
        ]
        assert result == expected

    def test_complex_spanning_table(self) -> None:
        """Test complex table with multiple spans."""
        html = """
        <table>
            <tr>
                <th rowspan="2">Category</th>
                <th colspan="2">Values</th>
            </tr>
            <tr>
                <th>Min</th>
                <th>Max</th>
            </tr>
            <tr>
                <td>A</td>
                <td>1</td>
                <td>10</td>
            </tr>
        </table>
        """
        result = extract_table_array(html)
        expected = [
            ["Category", "Values", "Values"],
            ["Category", "Min", "Max"],
            ["A", "1", "10"],
        ]
        assert result == expected

    def test_irregular_table(self) -> None:
        """Test table with rows having different numbers of cells."""
        html = """
        <table>
            <tr><td>A</td><td>B</td><td>C</td></tr>
            <tr><td>D</td><td>E</td></tr>
            <tr><td>F</td></tr>
        </table>
        """
        result = extract_table_array(html)

        # Should pad with empty strings
        assert len(result) == 3
        assert len(result[0]) == 3
        assert result[0] == ["A", "B", "C"]
        assert result[1][0] == "D"
        assert result[1][1] == "E"
        # Third position should be empty
        assert result[1][2] == ""

    def test_whitespace_handling(self) -> None:
        """Test that cell whitespace is properly stripped."""
        html = """
        <table>
            <tr><td>  Spaces  </td><td> \n Newline \t </td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["Spaces", "Newline"]]

    def test_empty_cells(self) -> None:
        """Test handling of empty cells."""
        html = """
        <table>
            <tr><td>A</td><td></td><td>C</td></tr>
            <tr><td></td><td>B</td><td></td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["A", "", "C"], ["", "B", ""]]

    def test_nested_html_in_cells(self) -> None:
        """Test cells with nested HTML."""
        html = """
        <table>
            <tr>
                <td><b>Bold</b> text</td>
                <td><a href="#">Link</a></td>
            </tr>
        </table>
        """
        result = extract_table_array(html)
        # get_text() extracts text from nested tags
        # Note: BeautifulSoup's get_text(strip=True) removes the space
        # between </b> and "text", resulting in "Boldtext"
        assert result == [["Boldtext", "Link"]]


class TestTablesEqual:
    """Tests for tables_equal function."""

    def test_identical_simple_tables(self) -> None:
        """Test that identical simple tables are equal."""
        html1 = "<table><tr><td>A</td><td>B</td></tr></table>"
        html2 = "<table><tr><td>A</td><td>B</td></tr></table>"
        assert tables_equal(html1, html2)

    def test_case_insensitive(self) -> None:
        """Test that comparison is case-insensitive for tags."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = "<TABLE><TR><TD>A</TD></TR></TABLE>"
        assert tables_equal(html1, html2)

    def test_attribute_order_ignored(self) -> None:
        """Test that attribute order doesn't matter."""
        html1 = '<table class="x" id="y"><tr><td>A</td></tr></table>'
        html2 = '<table id="y" class="x"><tr><td>A</td></tr></table>'
        assert tables_equal(html1, html2)

    def test_whitespace_ignored(self) -> None:
        """Test that extra whitespace doesn't affect equality."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = """
        <table>
            <tr>
                <td>A</td>
            </tr>
        </table>
        """
        assert tables_equal(html1, html2)

    def test_different_content(self) -> None:
        """Test that different content makes tables unequal."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = "<table><tr><td>B</td></tr></table>"
        assert not tables_equal(html1, html2)

    def test_different_structure(self) -> None:
        """Test that different structures make tables unequal."""
        html1 = "<table><tr><td>A</td><td>B</td></tr></table>"
        html2 = "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"
        assert not tables_equal(html1, html2)

    def test_different_spans(self) -> None:
        """Test that different spans make tables unequal."""
        html1 = "<table><tr><td colspan='2'>A</td></tr></table>"
        html2 = "<table><tr><td>A</td><td>B</td></tr></table>"
        # First table: [['A', 'A']]
        # Second table: [['A', 'B']]
        assert not tables_equal(html1, html2)

    def test_empty_tables(self) -> None:
        """Test that empty tables are equal."""
        html1 = "<table></table>"
        html2 = "<table></table>"
        assert tables_equal(html1, html2)

    def test_no_table_vs_empty_table(self) -> None:
        """Test comparison when one has no table."""
        html1 = "<div>Not a table</div>"
        html2 = "<table></table>"
        assert tables_equal(html1, html2)  # Both extract to []


class TestEdgeCases:
    """Edge case tests for table normalization."""

    def test_malformed_html(self) -> None:
        """Test handling of malformed HTML."""
        html = "<table><tr><td>Unclosed cell"
        # BeautifulSoup should handle this gracefully
        result = extract_table_array(html)
        assert len(result) == 1
        assert result[0][0] == "Unclosed cell"

    def test_very_large_colspan(self) -> None:
        """Test handling of very large colspan."""
        html = "<table><tr><td colspan='100'>Wide</td></tr></table>"
        result = extract_table_array(html)
        assert len(result) == 1
        assert len(result[0]) == 100
        assert all(cell == "Wide" for cell in result[0])

    def test_very_large_rowspan(self) -> None:
        """Test handling of very large rowspan."""
        html = """
        <table>
            <tr><td rowspan='50'>Tall</td><td>A</td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert len(result) == 1  # Only one row in HTML
        # Rowspan only affects how cells are distributed,
        # but we only have 1 row defined
        assert result[0][0] == "Tall"

    def test_zero_colspan_rowspan(self) -> None:
        """Test handling of zero/invalid span values."""
        # Note: HTML spec doesn't allow 0, but test defensive handling
        html = "<table><tr><td colspan='0' rowspan='0'>X</td></tr></table>"
        result = extract_table_array(html)
        # BeautifulSoup should parse this, treating 0 as default (1)
        assert len(result) > 0

    def test_unicode_content(self) -> None:
        """Test handling of Unicode content."""
        html = """
        <table>
            <tr><td>Hëllö</td><td>世界</td><td>🎉</td></tr>
        </table>
        """
        result = extract_table_array(html)
        assert result == [["Hëllö", "世界", "🎉"]]

    def test_table_with_tbody_thead_tfoot(self) -> None:
        """Test table with tbody, thead, tfoot elements."""
        html = """
        <table>
            <thead><tr><th>Header</th></tr></thead>
            <tbody><tr><td>Body</td></tr></tbody>
            <tfoot><tr><td>Footer</td></tr></tfoot>
        </table>
        """
        result = extract_table_array(html)
        assert len(result) == 3
        assert result[0][0] == "Header"
        assert result[1][0] == "Body"
        assert result[2][0] == "Footer"

    def test_table_with_caption(self) -> None:
        """Test that table caption is ignored."""
        html = """
        <table>
            <caption>Table Caption</caption>
            <tr><td>Data</td></tr>
        </table>
        """
        result = extract_table_array(html)
        # Caption should be ignored
        assert len(result) == 1
        assert result[0] == ["Data"]

    def test_empty_rows_ignored(self) -> None:
        """Test that rows without cells are handled."""
        html = """
        <table>
            <tr></tr>
            <tr><td>A</td></tr>
            <tr></tr>
        </table>
        """
        result = extract_table_array(html)
        # Empty rows without cells should be filtered out
        assert result == [["A"]]
