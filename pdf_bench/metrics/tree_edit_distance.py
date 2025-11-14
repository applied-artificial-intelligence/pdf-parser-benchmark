"""Tree-edit distance metric for structural similarity.

This module implements AST-based tree-edit distance using the Zhang-Shasha algorithm
via the zss library. It measures structural similarity between Markdown documents by
comparing their Abstract Syntax Trees.

The tree-edit distance represents the minimum number of edit operations (insertions,
deletions, substitutions) needed to transform one tree into another. This provides a
more nuanced similarity measure than character-level metrics, capturing document
structure rather than just content.

Key Features:
- Conversion of mistune AST to zss tree format
- Zhang-Shasha algorithm via zss library
- Normalized scores in range [0.0, 1.0]
- Structural comparison independent of text content

Example:
    >>> from pdf_bench.metrics import MarkdownASTParser, tree_edit_distance
    >>> parser = MarkdownASTParser()
    >>> ast1 = parser.parse("# Title\\n\\nParagraph")
    >>> ast2 = parser.parse("# Title\\n\\nParagraph\\n\\n- List")
    >>> distance = tree_edit_distance(ast1, ast2)
    >>> distance
    0.16666666666666666  # Some structural difference
"""

from typing import Any

from zss import Node, simple_distance  # type: ignore[import-untyped]


def ast_to_tree(ast: list[dict[str, Any]]) -> Node:
    """Convert mistune AST to zss tree format.

    Recursively transforms a mistune AST (list of token dictionaries) into a
    zss Node tree suitable for tree-edit distance calculation.

    Args:
        ast: Mistune AST tokens from MarkdownASTParser.parse()

    Returns:
        Root node of the zss tree. For ASTs with multiple root-level elements,
        creates a synthetic "document" root node.

    Example:
        >>> from pdf_bench.metrics import MarkdownASTParser
        >>> parser = MarkdownASTParser()
        >>> ast = parser.parse("# Heading")
        >>> tree = ast_to_tree(ast)
        >>> tree.label
        'document'
        >>> len(tree.children)
        1
    """
    # Create synthetic root for multi-root ASTs
    root = Node("document")

    for token in ast:
        child_node = _token_to_node(token)
        root.addkid(child_node)

    return root


def _token_to_node(token: dict[str, Any]) -> Node:
    """Convert a single AST token to a zss Node.

    Args:
        token: Single token dictionary from mistune AST

    Returns:
        zss Node representing this token and its descendants
    """
    token_type = token.get("type", "unknown")

    # Create node with type as label
    # For headings, include level; for lists, include ordered/unordered
    label = _create_node_label(token, token_type)
    node = Node(label)

    # Recursively add children
    if "children" in token and isinstance(token["children"], list):
        for child_token in token["children"]:
            child_node = _token_to_node(child_token)
            node.addkid(child_node)

    return node


def _create_node_label(token: dict[str, Any], token_type: str) -> str:
    """Create a descriptive label for a tree node.

    Args:
        token: AST token dictionary
        token_type: Type of the token

    Returns:
        Label string that captures structural information
    """
    # For headings, include level (H1, H2, etc.)
    if token_type == "heading":
        level = token.get("attrs", {}).get("level", "?")
        return f"H{level}"

    # For lists, distinguish ordered vs unordered
    if token_type == "list":
        ordered = token.get("attrs", {}).get("ordered", False)
        return "list:ordered" if ordered else "list:unordered"

    # For code blocks, distinguish by language if present
    if token_type == "block_code":
        info = token.get("attrs", {}).get("info", "")
        if info:
            return f"code:{info}"
        return "code"

    # Default: use type as-is
    return token_type


def tree_edit_distance(
    ast1: list[dict[str, Any]], ast2: list[dict[str, Any]]
) -> int:
    """Calculate raw tree-edit distance between two ASTs.

    Uses the Zhang-Shasha algorithm to compute the minimum number of edit
    operations (insert, delete, substitute) needed to transform tree1 into tree2.

    Args:
        ast1: First Markdown AST from MarkdownASTParser.parse()
        ast2: Second Markdown AST to compare

    Returns:
        Integer edit distance (0 = identical structure)

    Example:
        >>> from pdf_bench.metrics import MarkdownASTParser
        >>> parser = MarkdownASTParser()
        >>> ast1 = parser.parse("# Title")
        >>> ast2 = parser.parse("# Title")
        >>> tree_edit_distance(ast1, ast2)
        0
    """
    tree1 = ast_to_tree(ast1)
    tree2 = ast_to_tree(ast2)
    return int(simple_distance(tree1, tree2))


def normalized_tree_edit_distance(
    ast1: list[dict[str, Any]], ast2: list[dict[str, Any]]
) -> float:
    """Calculate normalized tree-edit distance between two ASTs.

    Normalizes the raw edit distance by the maximum tree size to produce a
    score in the range [0.0, 1.0]:
    - 0.0 = identical structure
    - 1.0 = completely different structure

    Args:
        ast1: First Markdown AST from MarkdownASTParser.parse()
        ast2: Second Markdown AST to compare

    Returns:
        Normalized distance in range [0.0, 1.0]

    Example:
        >>> from pdf_bench.metrics import MarkdownASTParser
        >>> parser = MarkdownASTParser()
        >>> ast1 = parser.parse("# Title\\n\\nText")
        >>> ast2 = parser.parse("# Title\\n\\nText")
        >>> normalized_tree_edit_distance(ast1, ast2)
        0.0
    """
    tree1 = ast_to_tree(ast1)
    tree2 = ast_to_tree(ast2)

    # Calculate tree sizes (number of nodes)
    size1 = _count_nodes(tree1)
    size2 = _count_nodes(tree2)
    max_size = max(size1, size2)

    # Handle edge case: both trees empty
    if max_size == 0:
        return 0.0

    # Calculate and normalize distance
    raw_distance = simple_distance(tree1, tree2)
    return float(raw_distance) / float(max_size)


def tree_similarity(
    ast1: list[dict[str, Any]], ast2: list[dict[str, Any]]
) -> float:
    """Calculate tree similarity score between two ASTs.

    Similarity is the complement of normalized distance:
    - 1.0 = identical structure
    - 0.0 = completely different structure

    Args:
        ast1: First Markdown AST from MarkdownASTParser.parse()
        ast2: Second Markdown AST to compare

    Returns:
        Similarity score in range [0.0, 1.0]

    Example:
        >>> from pdf_bench.metrics import MarkdownASTParser
        >>> parser = MarkdownASTParser()
        >>> ast1 = parser.parse("# Title")
        >>> ast2 = parser.parse("# Title")
        >>> tree_similarity(ast1, ast2)
        1.0
    """
    distance = normalized_tree_edit_distance(ast1, ast2)
    return 1.0 - distance


def _count_nodes(node: Node) -> int:
    """Count total nodes in a tree.

    Args:
        node: Root node of the tree

    Returns:
        Total number of nodes including root
    """
    count = 1  # Count this node
    for child in node.children:
        count += _count_nodes(child)
    return count
