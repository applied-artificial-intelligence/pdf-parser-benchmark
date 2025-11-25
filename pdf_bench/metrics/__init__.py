"""Metric implementations for benchmarking.

SPDX-License-Identifier: MIT
Copyright (c) 2025 PDF-Bench Contributors
"""

from pdf_bench.metrics.ast_parser import Element, MarkdownASTParser
from pdf_bench.metrics.cell_content_f1 import (
    CellF1Scores,
    cell_accuracy,
    cell_content_f1_score,
)
from pdf_bench.metrics.edit_distance import (
    character_error_rate,
    edit_similarity,
    edit_similarity_normalized,
    normalized_edit_distance,
    raw_edit_distance,
    token_recall,
)
from pdf_bench.metrics.element_f1 import ElementScores, element_f1_score
from pdf_bench.metrics.gfm_table_parser import GFMTable, GFMTableParser
from pdf_bench.metrics.latex_matching import (
    LaTeXF1Scores,
    extract_latex_expressions,
    latex_accuracy,
    latex_exact_match_f1,
    latex_f1_score,
    normalize_latex_expressions,
)
from pdf_bench.metrics.table_normalization import (
    TableCell,
    extract_table_array,
    normalize_html_table,
    tables_equal,
)
from pdf_bench.metrics.teds import (
    html_table_to_tree,
    teds_score,
    teds_score_with_content,
    tree_size,
)
from pdf_bench.metrics.text_metrics import chrf_plus_plus_score
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
    "edit_similarity_normalized",  # Format-agnostic version
    "token_recall",  # Content extraction completeness
    "character_error_rate",
    "raw_edit_distance",
    # Text similarity metrics
    "chrf_plus_plus_score",
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
    # TEDS (Table Edit Distance based Similarity)
    "teds_score",
    "teds_score_with_content",
    "html_table_to_tree",
    "tree_size",
    # GFM table parsing
    "GFMTableParser",
    "GFMTable",
    # Cell content F1
    "cell_content_f1_score",
    "cell_accuracy",
    "CellF1Scores",
    # LaTeX matching
    "latex_f1_score",
    "latex_accuracy",
    "latex_exact_match_f1",
    "extract_latex_expressions",
    "normalize_latex_expressions",
    "LaTeXF1Scores",
]
