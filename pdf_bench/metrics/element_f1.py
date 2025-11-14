"""Element F1 score metric for structural element extraction evaluation.

This module implements F1 score calculation for evaluating how well a PDF parser
extracts specific document elements (headings, lists, tables, code blocks, etc.).
It provides precision, recall, and F1 scores both overall and per-element-type.

The metric compares element counts in ground truth vs parsed output, making it
particularly useful for evaluating structural extraction quality independent of
text content accuracy.

Key Features:
- Element-type counting from Markdown ASTs
- Precision, recall, F1 score calculation
- Per-element-type breakdown
- Macro-averaged and micro-averaged scores
- Handles zero counts gracefully

Example:
    >>> from pdf_bench.metrics import MarkdownASTParser, element_f1_score
    >>> parser = MarkdownASTParser()
    >>> gt_ast = parser.parse("# Title\\n\\n- Item 1\\n- Item 2")
    >>> pred_ast = parser.parse("# Title\\n\\n- Item 1")
    >>> scores = element_f1_score(gt_ast, pred_ast)
    >>> scores['overall']['f1']
    0.8  # Missing one list item
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ElementScores:
    """Scores for a single element type.

    Attributes:
        element_type: Type of element (heading, list, paragraph, etc.)
        precision: Precision score (TP / (TP + FP))
        recall: Recall score (TP / (TP + FN))
        f1: F1 score (harmonic mean of precision and recall)
        true_positives: Count of correctly identified elements
        false_positives: Count of incorrectly identified elements
        false_negatives: Count of missed elements
        ground_truth_count: Total elements in ground truth
        predicted_count: Total elements in prediction
    """

    element_type: str
    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    false_negatives: int
    ground_truth_count: int
    predicted_count: int


def count_elements(ast: list[dict[str, Any]]) -> dict[str, int]:
    """Count element types in an AST.

    Recursively counts all element types, filtering out blank lines and other
    non-structural elements.

    Args:
        ast: Markdown AST from MarkdownASTParser.parse()

    Returns:
        Dictionary mapping element types to counts

    Example:
        >>> from pdf_bench.metrics import MarkdownASTParser
        >>> parser = MarkdownASTParser()
        >>> ast = parser.parse("# H1\\n## H2\\n\\nText")
        >>> counts = count_elements(ast)
        >>> counts['heading']
        2
        >>> counts['paragraph']
        1
    """
    counts: dict[str, int] = {}

    def _count_recursive(tokens: list[dict[str, Any]]) -> None:
        for token in tokens:
            token_type = token.get("type", "unknown")

            # Skip blank lines
            if token_type == "blank_line":
                continue

            # Count this element
            counts[token_type] = counts.get(token_type, 0) + 1

            # Recurse into children
            if "children" in token and isinstance(token["children"], list):
                _count_recursive(token["children"])

    _count_recursive(ast)
    return counts


def calculate_precision_recall_f1(
    ground_truth_count: int, predicted_count: int
) -> tuple[float, float, float, int, int, int]:
    """Calculate precision, recall, and F1 score for an element type.

    Uses min() to calculate true positives, assuming that if both ground truth
    and prediction have N elements, we count min(N_gt, N_pred) as correct.

    Args:
        ground_truth_count: Number of elements in ground truth
        predicted_count: Number of elements in prediction

    Returns:
        Tuple of (precision, recall, f1, tp, fp, fn)

    Example:
        >>> calculate_precision_recall_f1(5, 3)
        (1.0, 0.6, 0.75, 3, 0, 2)
        >>> calculate_precision_recall_f1(0, 0)
        (1.0, 1.0, 1.0, 0, 0, 0)
    """
    # True positives: minimum of ground truth and predicted
    tp = min(ground_truth_count, predicted_count)

    # False positives: predicted more than ground truth
    fp = max(0, predicted_count - ground_truth_count)

    # False negatives: predicted fewer than ground truth
    fn = max(0, ground_truth_count - predicted_count)

    # Calculate precision
    if predicted_count == 0:
        precision = 1.0 if ground_truth_count == 0 else 0.0
    else:
        precision = tp / predicted_count

    # Calculate recall
    if ground_truth_count == 0:
        recall = 1.0 if predicted_count == 0 else 0.0
    else:
        recall = tp / ground_truth_count

    # Calculate F1
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1, tp, fp, fn


def element_f1_score(
    ground_truth_ast: list[dict[str, Any]], predicted_ast: list[dict[str, Any]]
) -> dict[str, Any]:
    """Calculate element F1 scores comparing ground truth and predicted ASTs.

    Computes precision, recall, and F1 scores for each element type, plus
    macro-averaged overall scores.

    Args:
        ground_truth_ast: Ground truth Markdown AST
        predicted_ast: Predicted/parsed Markdown AST

    Returns:
        Dictionary with structure:
        {
            'overall': {
                'precision': float,
                'recall': float,
                'f1': float,
                'macro_precision': float,
                'macro_recall': float,
                'macro_f1': float
            },
            'per_element': {
                'heading': ElementScores(...),
                'paragraph': ElementScores(...),
                ...
            }
        }

    Example:
        >>> from pdf_bench.metrics import MarkdownASTParser
        >>> parser = MarkdownASTParser()
        >>> gt = parser.parse("# Title\\n\\nText")
        >>> pred = parser.parse("# Title")
        >>> scores = element_f1_score(gt, pred)
        >>> scores['overall']['f1']
        0.6666666666666666
        >>> scores['per_element']['heading'].f1
        1.0
    """
    # Count elements in both ASTs
    gt_counts = count_elements(ground_truth_ast)
    pred_counts = count_elements(predicted_ast)

    # Get all element types from both
    all_types = set(gt_counts.keys()) | set(pred_counts.keys())

    # Calculate scores per element type
    per_element_scores: dict[str, ElementScores] = {}

    for element_type in all_types:
        gt_count = gt_counts.get(element_type, 0)
        pred_count = pred_counts.get(element_type, 0)

        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(
            gt_count, pred_count
        )

        per_element_scores[element_type] = ElementScores(
            element_type=element_type,
            precision=precision,
            recall=recall,
            f1=f1,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            ground_truth_count=gt_count,
            predicted_count=pred_count,
        )

    # Calculate macro-averaged scores (average over element types)
    if per_element_scores:
        macro_precision = sum(s.precision for s in per_element_scores.values()) / len(
            per_element_scores
        )
        macro_recall = sum(s.recall for s in per_element_scores.values()) / len(
            per_element_scores
        )
        macro_f1 = sum(s.f1 for s in per_element_scores.values()) / len(
            per_element_scores
        )
    else:
        # Empty documents
        macro_precision = 1.0
        macro_recall = 1.0
        macro_f1 = 1.0

    # Calculate micro-averaged scores (sum all TP, FP, FN)
    total_tp = sum(s.true_positives for s in per_element_scores.values())
    total_fp = sum(s.false_positives for s in per_element_scores.values())
    total_fn = sum(s.false_negatives for s in per_element_scores.values())

    if total_tp + total_fp == 0:
        micro_precision = 1.0 if total_fn == 0 else 0.0
    else:
        micro_precision = total_tp / (total_tp + total_fp)

    if total_tp + total_fn == 0:
        micro_recall = 1.0 if total_fp == 0 else 0.0
    else:
        micro_recall = total_tp / (total_tp + total_fn)

    if micro_precision + micro_recall == 0:
        micro_f1 = 0.0
    else:
        micro_f1 = (
            2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)
        )

    return {
        "overall": {
            "macro_precision": macro_precision,
            "macro_recall": macro_recall,
            "macro_f1": macro_f1,
            "micro_precision": micro_precision,
            "micro_recall": micro_recall,
            "micro_f1": micro_f1,
            # For convenience, include micro scores as default "overall"
            "precision": micro_precision,
            "recall": micro_recall,
            "f1": micro_f1,
        },
        "per_element": per_element_scores,
    }
