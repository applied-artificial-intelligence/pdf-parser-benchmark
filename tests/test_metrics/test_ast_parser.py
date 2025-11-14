"""Tests for Markdown AST parser."""

from pdf_bench.metrics.ast_parser import Element, MarkdownASTParser


class TestMarkdownASTParser:
    """Tests for MarkdownASTParser class."""

    def test_init_default_plugins(self) -> None:
        """Test parser initialization with default plugins."""
        parser = MarkdownASTParser()
        assert parser._plugins == ["table", "strikethrough", "task_lists"]

    def test_init_custom_plugins(self) -> None:
        """Test parser initialization with custom plugins."""
        parser = MarkdownASTParser(plugins=["table"])
        assert parser._plugins == ["table"]

    def test_parse_empty_text(self) -> None:
        """Test parsing empty text."""
        parser = MarkdownASTParser()
        ast = parser.parse("")
        # Empty text produces a blank_line token
        assert len(ast) == 1
        assert ast[0]["type"] == "blank_line"

    def test_parse_simple_heading(self) -> None:
        """Test parsing a simple heading."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Hello World")

        # Find heading token
        heading = next(t for t in ast if t["type"] == "heading")
        assert heading["attrs"]["level"] == 1
        assert heading["children"][0]["raw"] == "Hello World"

    def test_parse_multiple_headings(self) -> None:
        """Test parsing multiple heading levels."""
        parser = MarkdownASTParser()
        ast = parser.parse("# H1\n## H2\n### H3")

        headings = [t for t in ast if t["type"] == "heading"]
        assert len(headings) == 3
        assert headings[0]["attrs"]["level"] == 1
        assert headings[1]["attrs"]["level"] == 2
        assert headings[2]["attrs"]["level"] == 3

    def test_parse_paragraph(self) -> None:
        """Test parsing a paragraph."""
        parser = MarkdownASTParser()
        ast = parser.parse("This is a paragraph.")

        paragraph = next(t for t in ast if t["type"] == "paragraph")
        assert paragraph["children"][0]["raw"] == "This is a paragraph."

    def test_parse_paragraph_with_inline_formatting(self) -> None:
        """Test parsing paragraph with bold and italic."""
        parser = MarkdownASTParser()
        ast = parser.parse("Text with **bold** and *italic*.")

        paragraph = next(t for t in ast if t["type"] == "paragraph")
        assert len(paragraph["children"]) > 1  # Multiple inline elements

        # Check for strong (bold) element
        strong = next(c for c in paragraph["children"] if c["type"] == "strong")
        assert strong["children"][0]["raw"] == "bold"

        # Check for emphasis (italic) element
        emphasis = next(c for c in paragraph["children"] if c["type"] == "emphasis")
        assert emphasis["children"][0]["raw"] == "italic"

    def test_parse_unordered_list(self) -> None:
        """Test parsing an unordered list."""
        parser = MarkdownASTParser()
        ast = parser.parse("- Item 1\n- Item 2\n- Item 3")

        list_token = next(t for t in ast if t["type"] == "list")
        assert list_token["attrs"]["ordered"] is False
        assert len(list_token["children"]) == 3

    def test_parse_ordered_list(self) -> None:
        """Test parsing an ordered list."""
        parser = MarkdownASTParser()
        ast = parser.parse("1. First\n2. Second\n3. Third")

        list_token = next(t for t in ast if t["type"] == "list")
        assert list_token["attrs"]["ordered"] is True
        assert len(list_token["children"]) == 3

    def test_parse_nested_list(self) -> None:
        """Test parsing nested lists."""
        parser = MarkdownASTParser()
        markdown = """- Item 1
  - Nested 1.1
  - Nested 1.2
- Item 2"""

        ast = parser.parse(markdown)

        # Top-level list
        top_list = next(t for t in ast if t["type"] == "list")
        assert top_list["attrs"]["depth"] == 0

        # Find nested list
        first_item = top_list["children"][0]
        nested_list = next(
            c for c in first_item["children"] if c["type"] == "list"
        )
        assert nested_list["attrs"]["depth"] == 1
        assert len(nested_list["children"]) == 2

    def test_parse_table(self) -> None:
        """Test parsing a table with table plugin."""
        parser = MarkdownASTParser()
        markdown = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""

        ast = parser.parse(markdown)

        table = next(t for t in ast if t["type"] == "table")
        assert "children" in table

        # Check for table_head and table_body
        table_head = next(c for c in table["children"] if c["type"] == "table_head")
        table_body = next(c for c in table["children"] if c["type"] == "table_body")

        # Header should have 2 cells
        assert len(table_head["children"]) == 2

        # Body should have 1 row with 2 cells
        rows = table_body["children"]
        assert len(rows) == 2
        assert all(len(row["children"]) == 2 for row in rows)

    def test_parse_code_block_fenced(self) -> None:
        """Test parsing a fenced code block."""
        parser = MarkdownASTParser()
        markdown = """```python
def hello():
    print("Hello")
```"""

        ast = parser.parse(markdown)

        code_block = next(t for t in ast if t["type"] == "block_code")
        assert code_block["style"] == "fenced"
        assert code_block["attrs"]["info"] == "python"
        assert 'def hello()' in code_block["raw"]

    def test_parse_code_block_without_language(self) -> None:
        """Test parsing code block without language specifier."""
        parser = MarkdownASTParser()
        markdown = """```
plain code
```"""

        ast = parser.parse(markdown)

        code_block = next(t for t in ast if t["type"] == "block_code")
        # Without language, attrs may not exist or info may be absent
        assert "attrs" not in code_block or code_block.get("attrs", {}).get("info", "") == ""
        assert "plain code" in code_block["raw"]

    def test_extract_elements_headings(self) -> None:
        """Test extracting elements from headings."""
        parser = MarkdownASTParser()
        ast = parser.parse("# H1\n## H2")

        elements = parser.extract_elements(ast)

        headings = [e for e in elements if e.type == "heading"]
        assert len(headings) == 2
        assert headings[0].level == 1
        assert headings[1].level == 2

    def test_extract_elements_lists(self) -> None:
        """Test extracting elements from lists."""
        parser = MarkdownASTParser()
        ast = parser.parse("- Item 1\n- Item 2")

        elements = parser.extract_elements(ast)

        lists = [e for e in elements if e.type == "list"]
        assert len(lists) == 1
        assert lists[0].level == 0
        assert lists[0].attrs is not None
        assert lists[0].attrs["ordered"] is False

    def test_extract_elements_code_blocks(self) -> None:
        """Test extracting elements from code blocks."""
        parser = MarkdownASTParser()
        ast = parser.parse("```python\ncode\n```")

        elements = parser.extract_elements(ast)

        code_blocks = [e for e in elements if e.type == "block_code"]
        assert len(code_blocks) == 1
        assert code_blocks[0].attrs is not None
        assert code_blocks[0].attrs["info"] == "python"
        assert code_blocks[0].raw_text == "code\n"

    def test_extract_elements_recursive(self) -> None:
        """Test that extraction recurses into children."""
        parser = MarkdownASTParser()
        ast = parser.parse("**bold text**")

        elements = parser.extract_elements(ast)

        # Should have: paragraph, strong, text
        types = [e.type for e in elements]
        assert "paragraph" in types
        assert "strong" in types
        assert "text" in types

    def test_count_elements_simple(self) -> None:
        """Test counting elements in simple document."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Title\n\nParagraph text")

        counts = parser.count_elements(ast)

        assert counts["heading"] == 1
        assert counts["paragraph"] == 1

    def test_count_elements_mixed(self) -> None:
        """Test counting elements in mixed document."""
        parser = MarkdownASTParser()
        markdown = """# Title
## Subtitle

Paragraph 1

Paragraph 2

- Item 1
- Item 2
"""

        ast = parser.parse(markdown)
        counts = parser.count_elements(ast)

        assert counts["heading"] == 2
        assert counts["paragraph"] == 2
        assert counts["list"] == 1
        assert counts["list_item"] == 2

    def test_count_elements_filters_blank_lines(self) -> None:
        """Test that blank lines are not counted."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Title\n\n\n\nParagraph")

        counts = parser.count_elements(ast)

        # blank_line should not appear in counts
        assert "blank_line" not in counts
        assert counts["heading"] == 1
        assert counts["paragraph"] == 1

    def test_count_by_type_and_level_headings(self) -> None:
        """Test counting headings by level."""
        parser = MarkdownASTParser()
        markdown = "# H1\n# H1 again\n## H2\n### H3\n### H3 again\n### H3 third"

        ast = parser.parse(markdown)
        counts = parser.count_by_type_and_level(ast)

        assert counts[("heading", 1)] == 2
        assert counts[("heading", 2)] == 1
        assert counts[("heading", 3)] == 3

    def test_count_by_type_and_level_lists(self) -> None:
        """Test counting lists by depth."""
        parser = MarkdownASTParser()
        markdown = """- Item 1
  - Nested
- Item 2"""

        ast = parser.parse(markdown)
        counts = parser.count_by_type_and_level(ast)

        # Top-level list at depth 0
        assert counts[("list", 0)] == 1
        # Nested list at depth 1
        assert counts[("list", 1)] == 1

    def test_count_by_type_and_level_mixed(self) -> None:
        """Test counting mixed elements."""
        parser = MarkdownASTParser()
        markdown = """# H1
## H2
Paragraph
- List"""

        ast = parser.parse(markdown)
        counts = parser.count_by_type_and_level(ast)

        assert counts[("heading", 1)] == 1
        assert counts[("heading", 2)] == 1
        assert counts[("paragraph", None)] >= 1  # At least one paragraph
        assert counts[("list", 0)] == 1


class TestElement:
    """Tests for Element dataclass."""

    def test_element_creation_basic(self) -> None:
        """Test creating a basic element."""
        element = Element(type="heading", level=1)

        assert element.type == "heading"
        assert element.level == 1
        assert element.children == 0
        assert element.raw_text is None
        assert element.attrs is None

    def test_element_creation_full(self) -> None:
        """Test creating element with all fields."""
        element = Element(
            type="list",
            level=0,
            children=3,
            attrs={"ordered": False},
        )

        assert element.type == "list"
        assert element.level == 0
        assert element.children == 3
        assert element.attrs == {"ordered": False}

    def test_element_with_text(self) -> None:
        """Test element with raw text content."""
        element = Element(type="text", raw_text="Hello World")

        assert element.type == "text"
        assert element.raw_text == "Hello World"


class TestEdgeCases:
    """Edge case tests for AST parser."""

    def test_parse_whitespace_only(self) -> None:
        """Test parsing whitespace-only text."""
        parser = MarkdownASTParser()
        ast = parser.parse("   \n\n   \n")

        # Should just have blank lines
        assert all(t["type"] == "blank_line" for t in ast)

    def test_parse_special_characters(self) -> None:
        """Test parsing text with special characters."""
        parser = MarkdownASTParser()
        text = "Text with <tags> & special © characters™"
        ast = parser.parse(text)

        paragraph = next(t for t in ast if t["type"] == "paragraph")
        # HTML tags are parsed as inline_html
        inline_html = next(c for c in paragraph["children"] if c["type"] == "inline_html")
        assert inline_html["raw"] == "<tags>"
        # Special characters should be in text nodes
        text_nodes = [c for c in paragraph["children"] if c["type"] == "text"]
        assert any("©" in node["raw"] for node in text_nodes)

    def test_parse_very_long_document(self) -> None:
        """Test parsing a large document."""
        parser = MarkdownASTParser()

        # Generate large markdown
        sections = []
        for i in range(100):
            sections.append(f"# Section {i}\n\nParagraph {i}\n")

        markdown = "\n".join(sections)
        ast = parser.parse(markdown)

        headings = [t for t in ast if t["type"] == "heading"]
        assert len(headings) == 100

    def test_count_elements_empty_ast(self) -> None:
        """Test counting elements in empty AST."""
        parser = MarkdownASTParser()
        counts = parser.count_elements([])

        assert counts == {}

    def test_extract_elements_empty_ast(self) -> None:
        """Test extracting elements from empty AST."""
        parser = MarkdownASTParser()
        elements = parser.extract_elements([])

        assert elements == []

    def test_no_table_plugin(self) -> None:
        """Test that tables are not parsed without table plugin."""
        parser = MarkdownASTParser(plugins=[])  # No plugins
        markdown = "| Header |\n|--------|\n| Cell |"

        ast = parser.parse(markdown)

        # Without table plugin, should be parsed as paragraph
        assert not any(t["type"] == "table" for t in ast)
        assert any(t["type"] == "paragraph" for t in ast)
