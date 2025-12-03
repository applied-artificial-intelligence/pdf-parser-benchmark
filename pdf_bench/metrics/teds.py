"""TEDS (Tree Edit Distance based Similarity) metric for table structure comparison.

This module implements TEDS, a metric for evaluating table structure recognition
accuracy. TEDS measures the similarity between predicted and ground truth HTML
tables using tree edit distance.

Reference:
    Zhong, X., ShafieiBavani, E., & Jimeno Yepes, A. (2020).
    Image-based table recognition: data, model, and evaluation.
    ECCV 2020.

TEDS is computed as:
    TEDS = 1 - (TreeEditDistance(T_pred, T_gt) / max(|T_pred|, |T_gt|))

Where:
- T_pred and T_gt are tree representations of predicted and ground truth tables
- |T| is the number of nodes in tree T
- TreeEditDistance is the minimum cost edit distance between trees
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag
from zss import Node, simple_distance

from pdf_bench.metrics.table_normalization import normalize_html_table


def html_table_to_tree(html: str) -> Node:
    """Convert HTML table to tree structure for TEDS computation.

    Args:
        html: HTML string containing a table element

    Returns:
        zss.Node representing the table structure

    Example:
        >>> html = '<table><tr><td>A</td></tr></table>'
        >>> tree = html_table_to_tree(html)
        >>> tree.label
        'table'
    """
    # Normalize the HTML first
    normalized = normalize_html_table(html)
    if not normalized:
        # Return empty tree
        return Node("table")

    soup = BeautifulSoup(normalized, "html.parser")
    table = soup.find("table")

    if not table:
        return Node("table")

    return _tag_to_node(table)


def _tag_to_node(tag: Tag) -> Node:
    """Recursively convert BeautifulSoup Tag to zss Node.

    Args:
        tag: BeautifulSoup Tag object

    Returns:
        zss.Node with tag name as label and children converted
    """
    # Create node with tag name as label
    label = tag.name.lower()

    # For cells, include colspan/rowspan in label for structural accuracy
    if label in ("td", "th"):
        colspan = tag.get("colspan", "1")
        rowspan = tag.get("rowspan", "1")
        # Only include in label if not default (1)
        if colspan != "1" or rowspan != "1":
            label = f"{label}[{colspan}x{rowspan}]"

    # Convert children tags (ignore text content for structure comparison)
    children = []
    for child in tag.children:
        if isinstance(child, Tag):
            children.append(_tag_to_node(child))

    # Create node with children
    node = Node(label)
    for child in children:
        node.addkid(child)

    return node


def tree_size(node: Node) -> int:
    """Calculate the number of nodes in a tree.

    Args:
        node: Root node of tree

    Returns:
        Total number of nodes including root
    """
    return 1 + sum(tree_size(child) for child in node.children)


def teds_score(pred_html: str, gt_html: str) -> float:
    """Calculate TEDS (Tree Edit Distance based Similarity) score.

    TEDS measures table structure similarity on a scale of 0.0 to 1.0,
    where 1.0 indicates identical structure and 0.0 indicates completely
    different structures.

    Args:
        pred_html: Predicted HTML table string
        gt_html: Ground truth HTML table string

    Returns:
        TEDS score in range [0.0, 1.0]
            - 1.0: Perfect match (identical structure)
            - 0.0: Complete mismatch
            - Higher values indicate more similar structures

    Example:
        >>> gt = '<table><tr><td>A</td><td>B</td></tr></table>'
        >>> pred = '<table><tr><td>X</td><td>Y</td></tr></table>'
        >>> score = teds_score(pred, gt)
        >>> score == 1.0  # Structure identical, content differs
        True

        >>> pred_wrong = '<table><tr><td>A</td></tr></table>'
        >>> score = teds_score(pred_wrong, gt)
        >>> score < 1.0  # Different structure (1 cell vs 2 cells)
        True
    """
    # Convert tables to trees
    pred_tree = html_table_to_tree(pred_html)
    gt_tree = html_table_to_tree(gt_html)

    # Handle empty tables
    pred_size = tree_size(pred_tree)
    gt_size = tree_size(gt_tree)

    # If both empty, perfect match
    if pred_size == 1 and gt_size == 1:  # Only root "table" node
        return 1.0

    # If one is empty and other isn't, score is 0
    if pred_size == 1 or gt_size == 1:
        return 0.0

    # Compute tree edit distance
    distance = float(simple_distance(pred_tree, gt_tree))

    # Normalize by max tree size
    max_size = max(pred_size, gt_size)

    # TEDS formula: 1 - (distance / max_size)
    teds = 1.0 - (distance / max_size)

    # Ensure result is in [0, 1]
    return max(0.0, min(1.0, teds))


def teds_score_with_content(pred_html: str, gt_html: str) -> float:
    """Calculate TEDS score including cell content comparison.

    This variant of TEDS includes cell text content in the tree labels,
    making it more strict than structure-only TEDS.

    Args:
        pred_html: Predicted HTML table string
        gt_html: Ground truth HTML table string

    Returns:
        TEDS score in range [0.0, 1.0] considering both structure and content

    Note:
        This is a stricter metric than standard TEDS. Use `teds_score()`
        for structure-only comparison.
    """
    # Convert tables with content to trees
    pred_tree = _html_table_to_tree_with_content(pred_html)
    gt_tree = _html_table_to_tree_with_content(gt_html)

    # Handle empty tables
    pred_size = tree_size(pred_tree)
    gt_size = tree_size(gt_tree)

    if pred_size == 1 and gt_size == 1:
        return 1.0

    if pred_size == 1 or gt_size == 1:
        return 0.0

    # Compute tree edit distance
    distance = float(simple_distance(pred_tree, gt_tree))

    # Normalize
    max_size = max(pred_size, gt_size)
    teds = 1.0 - (distance / max_size)

    return max(0.0, min(1.0, teds))


def _html_table_to_tree_with_content(html: str) -> Node:
    """Convert HTML table to tree with cell content in labels.

    Args:
        html: HTML string containing a table element

    Returns:
        zss.Node with tag names and cell content as labels
    """
    normalized = normalize_html_table(html)
    if not normalized:
        return Node("table")

    soup = BeautifulSoup(normalized, "html.parser")
    table = soup.find("table")

    if not table:
        return Node("table")

    return _tag_to_node_with_content(table)


def _tag_to_node_with_content(tag: Tag) -> Node:
    """Convert Tag to Node with content included in cell labels.

    Args:
        tag: BeautifulSoup Tag object

    Returns:
        zss.Node with content-aware labels
    """
    label = tag.name.lower()

    # For cells, include content in label
    if label in ("td", "th"):
        content = tag.get_text(strip=True)
        colspan = tag.get("colspan", "1")
        rowspan = tag.get("rowspan", "1")

        # Build label: tag[spans]:content
        span_str = ""
        if colspan != "1" or rowspan != "1":
            span_str = f"[{colspan}x{rowspan}]"

        label = f"{label}{span_str}:{content}"

    # Convert children
    children = []
    for child in tag.children:
        if isinstance(child, Tag):
            children.append(_tag_to_node_with_content(child))

    node = Node(label)
    for child in children:
        node.addkid(child)

    return node
