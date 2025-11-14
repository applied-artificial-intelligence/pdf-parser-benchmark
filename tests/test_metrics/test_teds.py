"""Tests for TEDS (Tree Edit Distance based Similarity) metric."""

from __future__ import annotations

from zss import Node

from pdf_bench.metrics.teds import (
    html_table_to_tree,
    teds_score,
    teds_score_with_content,
    tree_size,
)


class TestHTMLTableToTree:
    """Tests for html_table_to_tree function."""

    def test_empty_string(self) -> None:
        """Test conversion of empty string."""
        tree = html_table_to_tree("")
        assert tree.label == "table"
        assert len(tree.children) == 0

    def test_no_table(self) -> None:
        """Test HTML without table."""
        tree = html_table_to_tree("<div>Not a table</div>")
        assert tree.label == "table"
        assert len(tree.children) == 0

    def test_simple_table_1x1(self) -> None:
        """Test simple 1x1 table."""
        html = "<table><tr><td>A</td></tr></table>"
        tree = html_table_to_tree(html)

        assert tree.label == "table"
        assert len(tree.children) == 1  # one tr
        assert tree.children[0].label == "tr"
        assert len(tree.children[0].children) == 1  # one td
        assert tree.children[0].children[0].label == "td"

    def test_simple_table_2x2(self) -> None:
        """Test simple 2x2 table."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>C</td><td>D</td></tr>
        </table>
        """
        tree = html_table_to_tree(html)

        assert tree.label == "table"
        assert len(tree.children) == 2  # two rows
        assert all(child.label == "tr" for child in tree.children)
        assert all(len(row.children) == 2 for row in tree.children)  # two cells each

    def test_table_with_headers(self) -> None:
        """Test table with th elements."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        tree = html_table_to_tree(html)

        # First row should have th cells
        first_row = tree.children[0]
        assert all(child.label == "th" for child in first_row.children)

        # Second row should have td cells
        second_row = tree.children[1]
        assert all(child.label == "td" for child in second_row.children)

    def test_table_with_colspan(self) -> None:
        """Test that colspan is included in label."""
        html = '<table><tr><td colspan="2">Wide</td></tr></table>'
        tree = html_table_to_tree(html)

        cell = tree.children[0].children[0]
        assert "2x1" in cell.label  # colspan=2, rowspan=1

    def test_table_with_rowspan(self) -> None:
        """Test that rowspan is included in label."""
        html = '<table><tr><td rowspan="3">Tall</td></tr></table>'
        tree = html_table_to_tree(html)

        cell = tree.children[0].children[0]
        assert "1x3" in cell.label  # colspan=1, rowspan=3

    def test_table_with_colspan_and_rowspan(self) -> None:
        """Test table with both colspan and rowspan."""
        html = '<table><tr><td colspan="2" rowspan="2">Big</td></tr></table>'
        tree = html_table_to_tree(html)

        cell = tree.children[0].children[0]
        assert "2x2" in cell.label

    def test_table_with_tbody(self) -> None:
        """Test table with tbody element."""
        html = """
        <table>
            <tbody>
                <tr><td>A</td></tr>
            </tbody>
        </table>
        """
        tree = html_table_to_tree(html)

        assert tree.label == "table"
        # Should have tbody as child
        assert len(tree.children) == 1
        assert tree.children[0].label == "tbody"


class TestTreeSize:
    """Tests for tree_size function."""

    def test_single_node(self) -> None:
        """Test size of single node."""
        node = Node("root")
        assert tree_size(node) == 1

    def test_linear_tree(self) -> None:
        """Test size of linear tree."""
        root = Node("root")
        child1 = Node("child1")
        child2 = Node("child2")

        root.addkid(child1)
        child1.addkid(child2)

        assert tree_size(root) == 3

    def test_branching_tree(self) -> None:
        """Test size of branching tree."""
        root = Node("root")
        child1 = Node("child1")
        child2 = Node("child2")

        root.addkid(child1)
        root.addkid(child2)

        assert tree_size(root) == 3

    def test_complex_tree(self) -> None:
        """Test size of complex tree."""
        #       root
        #      /    \
        #     c1    c2
        #    /  \
        #   c3  c4
        root = Node("root")
        c1 = Node("c1")
        c2 = Node("c2")
        c3 = Node("c3")
        c4 = Node("c4")

        root.addkid(c1)
        root.addkid(c2)
        c1.addkid(c3)
        c1.addkid(c4)

        assert tree_size(root) == 5


class TestTEDSScore:
    """Tests for teds_score function."""

    def test_identical_simple_tables(self) -> None:
        """Test TEDS for identical simple tables."""
        html = "<table><tr><td>A</td><td>B</td></tr></table>"
        score = teds_score(html, html)
        assert score == 1.0

    def test_identical_complex_tables(self) -> None:
        """Test TEDS for identical complex tables."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
            <tr><td>Bob</td><td>25</td></tr>
        </table>
        """
        score = teds_score(html, html)
        assert score == 1.0

    def test_same_structure_different_content(self) -> None:
        """Test that structure-only TEDS ignores content."""
        html1 = "<table><tr><td>A</td><td>B</td></tr></table>"
        html2 = "<table><tr><td>X</td><td>Y</td></tr></table>"
        score = teds_score(html1, html2)
        assert score == 1.0  # Same structure, different content

    def test_different_number_of_rows(self) -> None:
        """Test TEDS with different number of rows."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = """
        <table>
            <tr><td>A</td></tr>
            <tr><td>B</td></tr>
        </table>
        """
        score = teds_score(html1, html2)
        assert 0.0 < score < 1.0  # Partial match

    def test_different_number_of_columns(self) -> None:
        """Test TEDS with different number of columns."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = "<table><tr><td>A</td><td>B</td></tr></table>"
        score = teds_score(html1, html2)
        assert 0.0 < score < 1.0  # Partial match

    def test_completely_different_tables(self) -> None:
        """Test TEDS with very different tables."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = """
        <table>
            <tr><td>1</td><td>2</td><td>3</td></tr>
            <tr><td>4</td><td>5</td><td>6</td></tr>
            <tr><td>7</td><td>8</td><td>9</td></tr>
        </table>
        """
        score = teds_score(html1, html2)
        assert score < 0.5  # Very different

    def test_empty_tables(self) -> None:
        """Test TEDS with empty tables."""
        html1 = "<table></table>"
        html2 = "<table></table>"
        score = teds_score(html1, html2)
        assert score == 1.0  # Both empty

    def test_one_empty_table(self) -> None:
        """Test TEDS with one empty table."""
        html1 = "<table></table>"
        html2 = "<table><tr><td>A</td></tr></table>"
        score = teds_score(html1, html2)
        assert score == 0.0  # One empty, one not

    def test_colspan_difference(self) -> None:
        """Test that different colspan values affect score."""
        html1 = "<table><tr><td colspan='2'>A</td></tr></table>"
        html2 = "<table><tr><td>A</td><td>B</td></tr></table>"
        score = teds_score(html1, html2)
        # Different structure due to colspan
        assert score < 1.0

    def test_rowspan_difference(self) -> None:
        """Test that different rowspan values affect score."""
        html1 = "<table><tr><td rowspan='2'>A</td></tr></table>"
        html2 = "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"
        score = teds_score(html1, html2)
        assert score < 1.0

    def test_th_vs_td(self) -> None:
        """Test that th vs td affects structure."""
        html1 = "<table><tr><th>Header</th></tr></table>"
        html2 = "<table><tr><td>Header</td></tr></table>"
        score = teds_score(html1, html2)
        # Different tags (th vs td)
        assert score < 1.0

    def test_case_insensitive(self) -> None:
        """Test that TEDS is case-insensitive for tags."""
        html1 = "<TABLE><TR><TD>A</TD></TR></TABLE>"
        html2 = "<table><tr><td>A</td></tr></table>"
        score = teds_score(html1, html2)
        # Normalization should make these identical
        assert score == 1.0


class TestTEDSScoreWithContent:
    """Tests for teds_score_with_content function."""

    def test_identical_tables(self) -> None:
        """Test content-aware TEDS for identical tables."""
        html = "<table><tr><td>Alice</td><td>30</td></tr></table>"
        score = teds_score_with_content(html, html)
        assert score == 1.0

    def test_same_structure_different_content(self) -> None:
        """Test content-aware TEDS penalizes different content."""
        html1 = "<table><tr><td>Alice</td><td>30</td></tr></table>"
        html2 = "<table><tr><td>Bob</td><td>25</td></tr></table>"
        score = teds_score_with_content(html1, html2)
        # Same structure but different content
        assert score < 1.0

    def test_partial_content_match(self) -> None:
        """Test partial content match."""
        html1 = "<table><tr><td>Alice</td><td>30</td></tr></table>"
        html2 = "<table><tr><td>Alice</td><td>25</td></tr></table>"
        score = teds_score_with_content(html1, html2)
        # One cell matches, one doesn't
        assert 0.0 < score < 1.0

    def test_empty_cells(self) -> None:
        """Test handling of empty cells."""
        html1 = "<table><tr><td></td><td>A</td></tr></table>"
        html2 = "<table><tr><td></td><td>A</td></tr></table>"
        score = teds_score_with_content(html1, html2)
        assert score == 1.0


class TestEdgeCases:
    """Edge case tests for TEDS."""

    def test_malformed_html(self) -> None:
        """Test handling of malformed HTML."""
        html1 = "<table><tr><td>Unclosed"
        html2 = "<table><tr><td>A</td></tr></table>"
        # Should not crash
        score = teds_score(html1, html2)
        assert 0.0 <= score <= 1.0

    def test_very_large_table(self) -> None:
        """Test with large table."""
        # Create 10x10 table
        rows = []
        for i in range(10):
            cells = [f"<td>Cell{i}{j}</td>" for j in range(10)]
            rows.append(f"<tr>{''.join(cells)}</tr>")
        html = f"<table>{''.join(rows)}</table>"

        score = teds_score(html, html)
        assert score == 1.0

    def test_nested_tables(self) -> None:
        """Test handling of nested tables."""
        html1 = """
        <table>
            <tr>
                <td><table><tr><td>Nested</td></tr></table></td>
            </tr>
        </table>
        """
        html2 = """
        <table>
            <tr>
                <td><table><tr><td>Nested</td></tr></table></td>
            </tr>
        </table>
        """
        score = teds_score(html1, html2)
        assert score == 1.0

    def test_unicode_content(self) -> None:
        """Test handling of Unicode content."""
        html1 = "<table><tr><td>Hëllö 世界</td></tr></table>"
        html2 = "<table><tr><td>Different</td></tr></table>"

        # Structure-only should be 1.0
        score_struct = teds_score(html1, html2)
        assert score_struct == 1.0

        # Content-aware should be < 1.0
        score_content = teds_score_with_content(html1, html2)
        assert score_content < 1.0

    def test_whitespace_variations(self) -> None:
        """Test that whitespace doesn't affect score."""
        html1 = "<table><tr><td>A</td></tr></table>"
        html2 = """
        <table>
            <tr>
                <td>A</td>
            </tr>
        </table>
        """
        score = teds_score(html1, html2)
        assert score == 1.0

    def test_attribute_order(self) -> None:
        """Test that attribute order doesn't affect score."""
        html1 = '<table class="x" id="y"><tr><td>A</td></tr></table>'
        html2 = '<table id="y" class="x"><tr><td>A</td></tr></table>'
        score = teds_score(html1, html2)
        assert score == 1.0
