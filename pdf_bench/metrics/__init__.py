"""Metric implementations for benchmarking."""

from pdf_bench.metrics.ast_parser import Element, MarkdownASTParser
from pdf_bench.metrics.edit_distance import (
    character_error_rate,
    edit_similarity,
    normalized_edit_distance,
    raw_edit_distance,
)
from pdf_bench.metrics.tree_edit_distance import (
    ast_to_tree,
    normalized_tree_edit_distance,
    tree_edit_distance,
    tree_similarity,
)

__all__ = [
    # Edit distance metrics
    "normalized_edit_distance",
    "edit_similarity",
    "character_error_rate",
    "raw_edit_distance",
    # AST parsing
    "MarkdownASTParser",
    "Element",
    # Tree-edit distance
    "ast_to_tree",
    "tree_edit_distance",
    "normalized_tree_edit_distance",
    "tree_similarity",
]
