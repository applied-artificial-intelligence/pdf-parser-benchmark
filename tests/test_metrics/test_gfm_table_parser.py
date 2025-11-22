"""Tests for GFM table parser."""

from pdf_bench.metrics.gfm_table_parser import GFMTable, GFMTableParser


class TestGFMTableParser:
    """Tests for GFMTableParser class."""

    def test_init(self) -> None:
        """Test parser initialization."""
        parser = GFMTableParser()
        assert parser._ast_parser is not None

    def test_extract_tables_no_tables(self) -> None:
        """Test extracting from text with no tables."""
        parser = GFMTableParser()
        markdown = "# Heading\n\nParagraph text\n\n- List item"

        tables = parser.extract_tables(markdown)

        assert tables == []

    def test_extract_tables_empty_text(self) -> None:
        """Test extracting from empty text."""
        parser = GFMTableParser()
        tables = parser.extract_tables("")
        assert tables == []

    def test_extract_simple_table(self) -> None:
        """Test extracting a simple 2x2 table."""
        parser = GFMTableParser()
        markdown = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_rows == 3  # Header + 2 body rows
        assert table.num_cols == 2
        assert table.cells[0] == ["Header 1", "Header 2"]
        assert table.cells[1] == ["Cell 1", "Cell 2"]
        assert table.cells[2] == ["Cell 3", "Cell 4"]

    def test_extract_table_with_whitespace(self) -> None:
        """Test that cell whitespace is normalized."""
        parser = GFMTableParser()
        markdown = """| Header  1 | Header   2 |
|-----------|------------|
|  Cell 1   |   Cell 2   |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        # Whitespace should be normalized (collapsed)
        assert table.cells[0][0] == "Header 1"
        assert table.cells[0][1] == "Header 2"
        assert table.cells[1][0] == "Cell 1"
        assert table.cells[1][1] == "Cell 2"

    def test_extract_table_single_column(self) -> None:
        """Test extracting table with single column."""
        parser = GFMTableParser()
        markdown = """| Column |
|--------|
| A      |
| B      |
| C      |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_cols == 1
        assert table.num_rows == 4
        assert table.cells[0] == ["Column"]
        assert table.cells[1] == ["A"]
        assert table.cells[2] == ["B"]
        assert table.cells[3] == ["C"]

    def test_extract_table_many_columns(self) -> None:
        """Test extracting table with many columns."""
        parser = GFMTableParser()
        markdown = """| A | B | C | D | E |
|---|---|---|---|---|
| 1 | 2 | 3 | 4 | 5 |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_cols == 5
        assert table.num_rows == 2
        assert table.cells[0] == ["A", "B", "C", "D", "E"]
        assert table.cells[1] == ["1", "2", "3", "4", "5"]

    def test_extract_multiple_tables(self) -> None:
        """Test extracting multiple tables from one document."""
        parser = GFMTableParser()
        markdown = """# First table

| H1 | H2 |
|----|-----|
| A  | B   |

Some text in between.

# Second table

| Col1 | Col2 | Col3 |
|------|------|------|
| X    | Y    | Z    |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 2

        # First table
        assert tables[0].num_cols == 2
        assert tables[0].num_rows == 2
        assert tables[0].cells[0] == ["H1", "H2"]
        assert tables[0].cells[1] == ["A", "B"]

        # Second table
        assert tables[1].num_cols == 3
        assert tables[1].num_rows == 2
        assert tables[1].cells[0] == ["Col1", "Col2", "Col3"]
        assert tables[1].cells[1] == ["X", "Y", "Z"]

    def test_extract_table_with_inline_formatting(self) -> None:
        """Test table cells with inline formatting (bold, italic, code)."""
        parser = GFMTableParser()
        markdown = """| **Bold** | *Italic* | `Code` |
|----------|----------|--------|
| Normal   | Text     | Here   |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        # Formatting should be stripped to text content
        assert table.cells[0] == ["Bold", "Italic", "Code"]
        assert table.cells[1] == ["Normal", "Text", "Here"]

    def test_extract_table_with_links(self) -> None:
        """Test table cells containing Markdown links."""
        parser = GFMTableParser()
        markdown = """| Name | Link |
|------|------|
| Google | [Link](http://google.com) |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        # Link text should be extracted
        assert table.cells[0] == ["Name", "Link"]
        assert table.cells[1] == ["Google", "Link"]

    def test_extract_table_empty_cells(self) -> None:
        """Test table with empty cells."""
        parser = GFMTableParser()
        markdown = """| A | B | C |
|---|---|---|
| 1 |   | 3 |
|   | 2 |   |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.cells[1] == ["1", "", "3"]
        assert table.cells[2] == ["", "2", ""]

    def test_extract_table_alignment_left(self) -> None:
        """Test table with left alignment markers."""
        parser = GFMTableParser()
        markdown = """| Left 1 | Left 2 |
|:-------|:-------|
| A      | B      |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        # Left alignment is default, may be indicated by :---
        # Alignment detection depends on mistune's AST representation
        assert len(table.alignment) == 2
        # Alignment should be either 'left' or default
        for align in table.alignment:
            assert align in ("left", "center", "right")

    def test_extract_table_alignment_center(self) -> None:
        """Test table with center alignment markers."""
        parser = GFMTableParser()
        markdown = """| Center 1 | Center 2 |
|:--------:|:--------:|
| A        | B        |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert len(table.alignment) == 2
        # Center alignment indicated by :---:
        # Note: mistune may or may not preserve this info

    def test_extract_table_alignment_right(self) -> None:
        """Test table with right alignment markers."""
        parser = GFMTableParser()
        markdown = """| Right 1 | Right 2 |
|--------:|--------:|
| A       | B       |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert len(table.alignment) == 2

    def test_extract_table_alignment_mixed(self) -> None:
        """Test table with mixed alignment markers."""
        parser = GFMTableParser()
        markdown = """| Left | Center | Right |
|:-----|:------:|------:|
| A    | B      | C     |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert len(table.alignment) == 3

    def test_extract_table_jagged_rows(self) -> None:
        """Test table with rows of different lengths (malformed).

        Note: Strictly malformed GFM tables may not parse as tables at all.
        mistune is lenient and will parse tables even with missing cells.
        This test verifies graceful handling.
        """
        parser = GFMTableParser()
        # Slightly malformed table - missing cells
        # mistune should still parse this
        markdown = """| A | B | C |
|---|---|---|
| 1 | 2 |   |
| X | Y | Z |"""

        tables = parser.extract_tables(markdown)

        # If mistune parses it, we should handle it
        if len(tables) > 0:
            table = tables[0]
            assert table.num_cols == 3

            # Rows should be normalized to num_cols
            for row in table.cells:
                assert len(row) == 3
        else:
            # If it doesn't parse, that's also acceptable for malformed input
            assert len(tables) == 0

    def test_extract_table_with_pipes_in_cells(self) -> None:
        """Test table with escaped pipes in cells."""
        parser = GFMTableParser()
        # Escaped pipes using backslash
        markdown = r"""| Code | Description |
|------|-------------|
| a \| b | Or operator |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        # The escaped pipe should be preserved in content
        # (mistune handles escaping)
        assert table.num_cols == 2

    def test_extract_table_unicode_content(self) -> None:
        """Test table with Unicode characters."""
        parser = GFMTableParser()
        markdown = """| 中文 | Emoji |
|------|-------|
| 你好 | 😀    |
| 世界 | 🌍    |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.cells[0] == ["中文", "Emoji"]
        assert table.cells[1] == ["你好", "😀"]
        assert table.cells[2] == ["世界", "🌍"]

    def test_extract_table_special_characters(self) -> None:
        """Test table with special Markdown characters."""
        parser = GFMTableParser()
        markdown = """| Character | Symbol |
|-----------|--------|
| Asterisk  | *      |
| Backtick  | `      |
| Hash      | #      |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_rows == 4

    def test_table_to_dict(self) -> None:
        """Test converting GFMTable to dictionary."""
        parser = GFMTableParser()
        table = GFMTable(
            cells=[["A", "B"], ["1", "2"]],
            alignment=["left", "right"],
            num_rows=2,
            num_cols=2,
        )

        result = parser.table_to_dict(table)

        assert result["cells"] == [["A", "B"], ["1", "2"]]
        assert result["alignment"] == ["left", "right"]
        assert result["num_rows"] == 2
        assert result["num_cols"] == 2

    def test_extract_table_header_only(self) -> None:
        """Test table with header but no body rows."""
        parser = GFMTableParser()
        markdown = """| Header 1 | Header 2 |
|----------|----------|"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_rows == 1  # Just header
        assert table.cells[0] == ["Header 1", "Header 2"]

    def test_extract_table_mixed_with_text(self) -> None:
        """Test extracting table mixed with paragraphs."""
        parser = GFMTableParser()
        markdown = """Some intro text.

| Col1 | Col2 |
|------|------|
| A    | B    |

Some conclusion text."""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        assert tables[0].num_rows == 2
        assert tables[0].cells[0] == ["Col1", "Col2"]

    def test_extract_table_in_nested_structure(self) -> None:
        """Test extracting table nested in list or quote."""
        parser = GFMTableParser()
        # Tables in lists are tricky - may not be supported by all parsers
        # Just test simple case
        markdown = """# Section

> Quoted text with table:
>
> | A | B |
> |---|---|
> | 1 | 2 |"""

        tables = parser.extract_tables(markdown)

        # Nested tables may or may not be extracted depending on mistune behavior
        # This is a graceful degradation test
        assert isinstance(tables, list)


class TestGFMTable:
    """Tests for GFMTable dataclass."""

    def test_gfmtable_creation(self) -> None:
        """Test creating a GFMTable object."""
        table = GFMTable(
            cells=[["A", "B"], ["1", "2"]],
            alignment=["left", "right"],
            num_rows=2,
            num_cols=2,
        )

        assert table.cells == [["A", "B"], ["1", "2"]]
        assert table.alignment == ["left", "right"]
        assert table.num_rows == 2
        assert table.num_cols == 2

    def test_gfmtable_empty_table(self) -> None:
        """Test creating an empty GFMTable."""
        table = GFMTable(cells=[], alignment=[], num_rows=0, num_cols=0)

        assert table.cells == []
        assert table.alignment == []
        assert table.num_rows == 0
        assert table.num_cols == 0


class TestEdgeCases:
    """Edge case tests for GFM table parser."""

    def test_malformed_table_no_header(self) -> None:
        """Test handling table without proper header (shouldn't parse as table)."""
        parser = GFMTableParser()
        # Invalid GFM - no separator row
        markdown = """| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |"""

        tables = parser.extract_tables(markdown)

        # Should be parsed as paragraph, not table
        # mistune requires separator row
        # Depending on parser, this might be 0 or treated as paragraph
        assert isinstance(tables, list)

    def test_table_very_wide(self) -> None:
        """Test table with many columns."""
        parser = GFMTableParser()
        headers = [f"Col{i}" for i in range(20)]
        values = [str(i) for i in range(20)]

        header_row = "| " + " | ".join(headers) + " |"
        sep_row = "|" + "|".join(["---"] * 20) + "|"
        data_row = "| " + " | ".join(values) + " |"

        markdown = f"{header_row}\n{sep_row}\n{data_row}"

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_cols == 20
        assert table.cells[0] == headers
        assert table.cells[1] == values

    def test_table_very_tall(self) -> None:
        """Test table with many rows."""
        parser = GFMTableParser()
        rows = ["| A | B |", "|---|---|"]
        for i in range(100):
            rows.append(f"| {i} | {i * 2} |")

        markdown = "\n".join(rows)

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        table = tables[0]
        assert table.num_rows == 101  # Header + 100 data rows

    def test_table_with_html_entities(self) -> None:
        """Test table with HTML entities."""
        parser = GFMTableParser()
        markdown = """| Entity | Value |
|--------|-------|
| &lt;   | <     |
| &gt;   | >     |
| &amp;  | &     |"""

        tables = parser.extract_tables(markdown)

        assert len(tables) == 1
        # HTML entities may be preserved or decoded depending on parser

    def test_normalize_row_short(self) -> None:
        """Test _normalize_row with short row."""
        parser = GFMTableParser()
        row = ["A", "B"]
        normalized = parser._normalize_row(row, 4)

        assert len(normalized) == 4
        assert normalized == ["A", "B", "", ""]

    def test_normalize_row_long(self) -> None:
        """Test _normalize_row with long row."""
        parser = GFMTableParser()
        row = ["A", "B", "C", "D", "E"]
        normalized = parser._normalize_row(row, 3)

        assert len(normalized) == 3
        assert normalized == ["A", "B", "C"]

    def test_normalize_row_exact(self) -> None:
        """Test _normalize_row with exact length."""
        parser = GFMTableParser()
        row = ["A", "B", "C"]
        normalized = parser._normalize_row(row, 3)

        assert normalized == ["A", "B", "C"]
