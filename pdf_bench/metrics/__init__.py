"""Metric implementations for benchmarking."""

from pdf_bench.metrics.ast_parser import Element, MarkdownASTParser
from pdf_bench.metrics.edit_distance import (
    character_error_rate,
    edit_similarity,
    normalized_edit_distance,
    raw_edit_distance,
)
from pdf_bench.metrics.element_f1 import ElementScores, element_f1_score
from pdf_bench.metrics.table_normalization import (
    TableCell,
    extract_table_array,
    normalize_html_table,
    tables_equal,
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
    # Element F1 score
    "element_f1_score",
    "ElementScores",
    # Table normalization
    "normalize_html_table",
    "extract_table_array",
    "tables_equal",
    "TableCell",
]
