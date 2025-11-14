"""Tests for tree-edit distance metric."""

from zss import Node  # type: ignore[import-untyped]

from pdf_bench.metrics.ast_parser import MarkdownASTParser
from pdf_bench.metrics.tree_edit_distance import (
    _count_nodes,
    _create_node_label,
    _token_to_node,
    ast_to_tree,
    normalized_tree_edit_distance,
    tree_edit_distance,
    tree_similarity,
)


class TestASTToTree:
    """Tests for AST to tree conversion."""

    def test_ast_to_tree_empty(self) -> None:
        """Test conversion of empty AST."""
        tree = ast_to_tree([])
        assert tree.label == "document"
        assert len(tree.children) == 0

    def test_ast_to_tree_single_element(self) -> None:
        """Test conversion of AST with single element."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Heading")

        tree = ast_to_tree(ast)
        assert tree.label == "document"
        # Should have heading and possibly blank_line
        assert len(tree.children) >= 1
        # First non-blank child should be H1
        heading_children = [c for c in tree.children if c.label == "H1"]
        assert len(heading_children) == 1

    def test_ast_to_tree_multiple_elements(self) -> None:
        """Test conversion with multiple root elements."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Title\n\nParagraph text")

        tree = ast_to_tree(ast)
        assert tree.label == "document"
        assert len(tree.children) >= 2  # heading, paragraph, possibly blank_line

    def test_ast_to_tree_nested_structure(self) -> None:
        """Test conversion preserves nesting."""
        parser = MarkdownASTParser()
        ast = parser.parse("- Item 1\n  - Nested item")

        tree = ast_to_tree(ast)

        # Find the list node
        list_nodes = [c for c in tree.children if c.label == "list:unordered"]
        assert len(list_nodes) == 1

        # List should have children (list_item nodes)
        assert len(list_nodes[0].children) > 0


class TestTokenToNode:
    """Tests for token to node conversion."""

    def test_token_to_node_simple(self) -> None:
        """Test converting simple token."""
        token = {"type": "paragraph"}
        node = _token_to_node(token)
        assert node.label == "paragraph"
        assert len(node.children) == 0

    def test_token_to_node_with_children(self) -> None:
        """Test converting token with children."""
        token = {
            "type": "paragraph",
            "children": [
                {"type": "text", "raw": "hello"},
                {"type": "text", "raw": "world"},
            ],
        }
        node = _token_to_node(token)
        assert node.label == "paragraph"
        assert len(node.children) == 2
        assert all(c.label == "text" for c in node.children)

    def test_token_to_node_heading(self) -> None:
        """Test converting heading with level."""
        token = {"type": "heading", "attrs": {"level": 2}}
        node = _token_to_node(token)
        assert node.label == "H2"

    def test_token_to_node_ordered_list(self) -> None:
        """Test converting ordered list."""
        token = {"type": "list", "attrs": {"ordered": True}}
        node = _token_to_node(token)
        assert node.label == "list:ordered"

    def test_token_to_node_unordered_list(self) -> None:
        """Test converting unordered list."""
        token = {"type": "list", "attrs": {"ordered": False}}
        node = _token_to_node(token)
        assert node.label == "list:unordered"

    def test_token_to_node_code_block_with_language(self) -> None:
        """Test converting code block with language."""
        token = {"type": "block_code", "attrs": {"info": "python"}}
        node = _token_to_node(token)
        assert node.label == "code:python"

    def test_token_to_node_code_block_without_language(self) -> None:
        """Test converting code block without language."""
        token = {"type": "block_code"}
        node = _token_to_node(token)
        assert node.label == "code"


class TestCreateNodeLabel:
    """Tests for node label creation."""

    def test_create_label_heading(self) -> None:
        """Test label creation for headings."""
        token = {"type": "heading", "attrs": {"level": 3}}
        label = _create_node_label(token, "heading")
        assert label == "H3"

    def test_create_label_ordered_list(self) -> None:
        """Test label creation for ordered list."""
        token = {"type": "list", "attrs": {"ordered": True}}
        label = _create_node_label(token, "list")
        assert label == "list:ordered"

    def test_create_label_unordered_list(self) -> None:
        """Test label creation for unordered list."""
        token = {"type": "list", "attrs": {"ordered": False}}
        label = _create_node_label(token, "list")
        assert label == "list:unordered"

    def test_create_label_code_with_language(self) -> None:
        """Test label creation for code block with language."""
        token = {"type": "block_code", "attrs": {"info": "javascript"}}
        label = _create_node_label(token, "block_code")
        assert label == "code:javascript"

    def test_create_label_code_without_language(self) -> None:
        """Test label creation for code block without language."""
        token = {"type": "block_code", "attrs": {}}
        label = _create_node_label(token, "block_code")
        assert label == "code"

    def test_create_label_generic(self) -> None:
        """Test label creation for generic types."""
        token = {"type": "paragraph"}
        label = _create_node_label(token, "paragraph")
        assert label == "paragraph"


class TestTreeEditDistance:
    """Tests for tree edit distance calculation."""

    def test_identical_trees_zero_distance(self) -> None:
        """Test that identical trees have zero distance."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title\n\nParagraph")
        ast2 = parser.parse("# Title\n\nParagraph")

        distance = tree_edit_distance(ast1, ast2)
        assert distance == 0

    def test_empty_trees_zero_distance(self) -> None:
        """Test that empty trees have zero distance."""
        distance = tree_edit_distance([], [])
        assert distance == 0

    def test_different_trees_nonzero_distance(self) -> None:
        """Test that different trees have nonzero distance."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title")
        ast2 = parser.parse("## Subtitle")

        distance = tree_edit_distance(ast1, ast2)
        assert distance > 0

    def test_single_element_difference(self) -> None:
        """Test distance with single element difference."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title\n\nParagraph")
        ast2 = parser.parse("# Title\n\nParagraph\n\n- List")

        distance = tree_edit_distance(ast1, ast2)
        # Should be non-zero (added elements)
        assert distance > 0

    def test_heading_level_difference(self) -> None:
        """Test that heading levels are distinguished."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# H1")
        ast2 = parser.parse("## H2")

        distance = tree_edit_distance(ast1, ast2)
        # Different labels (H1 vs H2) should have distance > 0
        assert distance > 0

    def test_list_type_difference(self) -> None:
        """Test that ordered vs unordered lists are distinguished."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("- Unordered")
        ast2 = parser.parse("1. Ordered")

        distance = tree_edit_distance(ast1, ast2)
        # Different list types should have distance > 0
        assert distance > 0


class TestNormalizedTreeEditDistance:
    """Tests for normalized tree edit distance."""

    def test_identical_trees_zero_distance(self) -> None:
        """Test that identical trees have normalized distance 0.0."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title\n\nText")
        ast2 = parser.parse("# Title\n\nText")

        distance = normalized_tree_edit_distance(ast1, ast2)
        assert distance == 0.0

    def test_empty_trees_zero_distance(self) -> None:
        """Test that empty trees have normalized distance 0.0."""
        distance = normalized_tree_edit_distance([], [])
        assert distance == 0.0

    def test_normalized_in_range(self) -> None:
        """Test that normalized distance is in [0, 1]."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title")
        ast2 = parser.parse("# Title\n\nParagraph\n\n- List")

        distance = normalized_tree_edit_distance(ast1, ast2)
        assert 0.0 <= distance <= 1.0

    def test_completely_different_trees(self) -> None:
        """Test distance for very different structures."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Simple")
        ast2 = parser.parse("- List 1\n- List 2\n- List 3\n\nParagraph")

        distance = normalized_tree_edit_distance(ast1, ast2)
        # Should have significant distance but not necessarily 1.0
        assert distance > 0.3

    def test_small_difference(self) -> None:
        """Test distance for small differences."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title\n\nText\n\n- Item 1\n- Item 2")
        ast2 = parser.parse("# Title\n\nText\n\n- Item 1\n- Item 2\n- Item 3")

        distance = normalized_tree_edit_distance(ast1, ast2)
        # Small change should have small distance
        assert 0.0 < distance < 0.5


class TestTreeSimilarity:
    """Tests for tree similarity score."""

    def test_identical_trees_full_similarity(self) -> None:
        """Test that identical trees have similarity 1.0."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title")
        ast2 = parser.parse("# Title")

        similarity = tree_similarity(ast1, ast2)
        assert similarity == 1.0

    def test_similarity_in_range(self) -> None:
        """Test that similarity is in [0, 1]."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title")
        ast2 = parser.parse("# Title\n\nParagraph")

        similarity = tree_similarity(ast1, ast2)
        assert 0.0 <= similarity <= 1.0

    def test_similarity_complement_of_distance(self) -> None:
        """Test that similarity = 1 - distance."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("# Title\n\nText")
        ast2 = parser.parse("# Title\n\nDifferent text\n\n- List")

        distance = normalized_tree_edit_distance(ast1, ast2)
        similarity = tree_similarity(ast1, ast2)

        assert abs(similarity - (1.0 - distance)) < 1e-10


class TestCountNodes:
    """Tests for node counting."""

    def test_count_single_node(self) -> None:
        """Test counting single node."""
        node = Node("root")
        assert _count_nodes(node) == 1

    def test_count_with_children(self) -> None:
        """Test counting nodes with children."""
        root = Node("root")
        root.addkid(Node("child1"))
        root.addkid(Node("child2"))

        assert _count_nodes(root) == 3

    def test_count_nested_structure(self) -> None:
        """Test counting deeply nested structure."""
        root = Node("root")
        child1 = Node("child1")
        child1.addkid(Node("grandchild"))
        root.addkid(child1)
        root.addkid(Node("child2"))

        assert _count_nodes(root) == 4


class TestRealWorldExamples:
    """Tests with realistic Markdown documents."""

    def test_simple_documents(self) -> None:
        """Test with simple but realistic documents."""
        parser = MarkdownASTParser()

        doc1 = """# Introduction

This is a simple document with one heading and one paragraph.
"""

        doc2 = """# Introduction

This is a simple document with one heading and one paragraph.

## Conclusion

A second section.
"""

        ast1 = parser.parse(doc1)
        ast2 = parser.parse(doc2)

        distance = normalized_tree_edit_distance(ast1, ast2)
        similarity = tree_similarity(ast1, ast2)

        # doc2 has additional section, so should have some distance
        assert distance > 0.0
        assert similarity < 1.0
        # But they share structure, so not completely different
        assert similarity > 0.3

    def test_list_documents(self) -> None:
        """Test documents with lists."""
        parser = MarkdownASTParser()

        doc1 = """# Tasks

- Task 1
- Task 2
- Task 3
"""

        doc2 = """# Tasks

- Task 1
- Task 2
"""

        ast1 = parser.parse(doc1)
        ast2 = parser.parse(doc2)

        distance = normalized_tree_edit_distance(ast1, ast2)

        # doc1 has one extra list item
        assert distance > 0.0
        assert distance < 0.5  # But mostly similar

    def test_different_structures(self) -> None:
        """Test documents with different structures."""
        parser = MarkdownASTParser()

        doc1 = """# Title

Paragraph 1

Paragraph 2
"""

        doc2 = """# Title

- Item 1
- Item 2
- Item 3
"""

        ast1 = parser.parse(doc1)
        ast2 = parser.parse(doc2)

        similarity = tree_similarity(ast1, ast2)

        # Same title but different content structure
        assert 0.2 < similarity < 0.8


class TestEdgeCases:
    """Edge case tests."""

    def test_one_empty_one_full(self) -> None:
        """Test distance between empty and non-empty AST."""
        parser = MarkdownASTParser()
        ast1 = parser.parse("")
        ast2 = parser.parse("# Title\n\nText")

        distance = normalized_tree_edit_distance(ast1, ast2)

        # Non-empty vs empty should have high distance
        assert distance > 0.5

    def test_very_large_trees(self) -> None:
        """Test with large documents."""
        parser = MarkdownASTParser()

        # Generate large markdown
        sections = []
        for i in range(50):
            sections.append(f"## Section {i}\n\nParagraph {i}\n")

        doc1 = "\n".join(sections)
        doc2 = "\n".join(sections[:45])  # Slightly smaller

        ast1 = parser.parse(doc1)
        ast2 = parser.parse(doc2)

        distance = normalized_tree_edit_distance(ast1, ast2)

        # Should detect the difference but recognize similarity
        assert 0.0 < distance < 0.2

    def test_whitespace_only_difference(self) -> None:
        """Test that structure is compared, not content."""
        parser = MarkdownASTParser()

        ast1 = parser.parse("# Title\n\nShort text")
        ast2 = parser.parse("# Title\n\nMuch longer text with more words")

        # Structure is identical even though text differs
        # Note: text content is in leaf nodes, structure should match
        distance = tree_edit_distance(ast1, ast2)

        # Depending on whether text nodes are compared, this may be 0
        # In our implementation, we just use type labels, so distance should be 0
        assert distance == 0
