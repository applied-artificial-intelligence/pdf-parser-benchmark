r"""LaTeX string matching metric for mathematical expression comparison.

This module provides functions to extract LaTeX mathematical expressions from
Markdown documents and compare them using exact string matching after normalization.

The metric is designed for evaluating PDF-to-Markdown conversion accuracy on
documents containing mathematical notation. It extracts both inline and display
math, normalizes using LaTeX-aware rules, and computes precision, recall, and F1.

Example:
    >>> from pdf_bench.metrics.latex_matching import latex_f1_score
    >>> ground_truth = "The equation $x = 1$ and $$y = 2$$"
    >>> prediction = "The equation $x=1$ and $$y=2$$"
    >>> scores = latex_f1_score(ground_truth, prediction)
    >>> scores.f1
    1.0
"""

import re
from dataclasses import dataclass
from typing import Final

from pdf_bench.utils.latex_normalization import normalize_latex

# Regex patterns for extracting LaTeX expressions
# Inline math: $...$ and \(...\)
# Display math: $$...$$ and \[...\]
_INLINE_DOLLAR_PATTERN: Final[str] = r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)"
_INLINE_PAREN_PATTERN: Final[str] = r"\\\((.*?)\\\)"
_DISPLAY_DOUBLE_PATTERN: Final[str] = r"\$\$(.*?)\$\$"
_DISPLAY_BRACKET_PATTERN: Final[str] = r"\\\[(.*?)\\\]"


@dataclass(frozen=True)
class LaTeXF1Scores:
    """Results from LaTeX F1 score calculation.

    Attributes:
        precision: Precision score (0.0-1.0)
        recall: Recall score (0.0-1.0)
        f1: F1 score (0.0-1.0)
        tp: True positives (matched expressions)
        fp: False positives (extra expressions in prediction)
        fn: False negatives (missing expressions from ground truth)
        total_gt: Total expressions in ground truth
        total_pred: Total expressions in prediction
    """

    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int
    total_gt: int
    total_pred: int


def extract_latex_expressions(text: str) -> list[str]:
    r"""Extract all LaTeX mathematical expressions from Markdown text.

    Extracts both inline and display math expressions:
    - Inline: $...$ and \(...\)
    - Display: $$...$$ and \[...\]

    Expressions are returned in the order they appear in the text.
    Each expression is the raw LaTeX content without delimiters.

    Args:
        text: Input Markdown text containing LaTeX expressions

    Returns:
        List of LaTeX expression strings (without delimiters)

    Example:
        >>> text = "Inline $x = 1$ and display $$y = 2$$"
        >>> extract_latex_expressions(text)
        ['x = 1', 'y = 2']
    """
    expressions: list[str] = []

    # Track positions to maintain order
    expr_positions: list[tuple[int, str]] = []

    # Extract display math first ($$...$$ and \[...\])
    for match in re.finditer(_DISPLAY_DOUBLE_PATTERN, text, re.DOTALL):
        expr_positions.append((match.start(), match.group(1)))

    for match in re.finditer(_DISPLAY_BRACKET_PATTERN, text, re.DOTALL):
        expr_positions.append((match.start(), match.group(1)))

    # Extract inline math ($...$, but not $$)
    for match in re.finditer(_INLINE_DOLLAR_PATTERN, text, re.DOTALL):
        expr_positions.append((match.start(), match.group(1)))

    # Extract inline math with \(...\)
    for match in re.finditer(_INLINE_PAREN_PATTERN, text, re.DOTALL):
        expr_positions.append((match.start(), match.group(1)))

    # Sort by position and extract expressions
    expr_positions.sort(key=lambda x: x[0])
    expressions = [expr for _, expr in expr_positions]

    return expressions


def normalize_latex_expressions(expressions: list[str]) -> list[str]:
    r"""Normalize a list of LaTeX expressions.

    Applies LaTeX normalization to each expression:
    - Removes sizing commands (\left, \right, etc.)
    - Normalizes spacing commands
    - Collapses whitespace
    - Normalizes command spacing

    Args:
        expressions: List of raw LaTeX expressions

    Returns:
        List of normalized LaTeX expressions

    Example:
        >>> exprs = [r"\left( x \right)", r"\frac{a}{b}"]
        >>> normalize_latex_expressions(exprs)
        ['(x)', '\\frac{a}{b}']
    """
    return [normalize_latex(expr) for expr in expressions]


def latex_exact_match_f1(
    ground_truth_exprs: list[str], predicted_exprs: list[str]
) -> LaTeXF1Scores:
    """Calculate F1 score for LaTeX expressions using exact string matching.

    Compares two lists of LaTeX expressions (already normalized) and computes
    precision, recall, and F1 based on exact string matches.

    Matching algorithm:
    - True Positive (TP): Expression in GT matches an expression in prediction
    - False Positive (FP): Expression in prediction has no match in GT
    - False Negative (FN): Expression in GT has no match in prediction

    Each GT expression can match at most one predicted expression (greedy matching).

    Args:
        ground_truth_exprs: Normalized LaTeX expressions from ground truth
        predicted_exprs: Normalized LaTeX expressions from prediction

    Returns:
        LaTeXF1Scores with precision, recall, F1, and counts

    Example:
        >>> gt = ['x=1', 'y=2']
        >>> pred = ['x=1', 'y=2', 'z=3']
        >>> scores = latex_exact_match_f1(gt, pred)
        >>> scores.precision
        0.6666666666666666
        >>> scores.recall
        1.0
    """
    # Make a copy to track which predictions have been matched
    pred_remaining = predicted_exprs.copy()

    tp = 0

    # Greedy matching: match each GT expression to first available prediction
    for gt_expr in ground_truth_exprs:
        if gt_expr in pred_remaining:
            # Found a match
            pred_remaining.remove(gt_expr)  # Remove first occurrence
            tp += 1

    # False positives: predictions that weren't matched
    fp = len(pred_remaining)

    # False negatives: GT expressions that weren't matched
    fn = len(ground_truth_exprs) - tp

    # Calculate metrics
    precision = tp / len(predicted_exprs) if len(predicted_exprs) > 0 else 0.0
    recall = tp / len(ground_truth_exprs) if len(ground_truth_exprs) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return LaTeXF1Scores(
        precision=precision,
        recall=recall,
        f1=f1,
        tp=tp,
        fp=fp,
        fn=fn,
        total_gt=len(ground_truth_exprs),
        total_pred=len(predicted_exprs),
    )


def latex_f1_score(ground_truth: str, prediction: str) -> LaTeXF1Scores:
    """Calculate LaTeX F1 score between ground truth and prediction Markdown.

    This is the main function for computing LaTeX string matching metrics.
    It performs the complete pipeline:
    1. Extract LaTeX expressions from both texts
    2. Normalize all expressions
    3. Compute F1 score based on exact matches

    Args:
        ground_truth: Ground truth Markdown text with LaTeX
        prediction: Predicted Markdown text with LaTeX

    Returns:
        LaTeXF1Scores with precision, recall, F1, and detailed counts

    Example:
        >>> gt = "Equation $x = 1$ and $$y = 2$$"
        >>> pred = "Equation $x=1$ and $$y=2$$"
        >>> scores = latex_f1_score(gt, pred)
        >>> scores.f1
        1.0
        >>> scores.tp
        2
    """
    # Extract LaTeX expressions
    gt_exprs = extract_latex_expressions(ground_truth)
    pred_exprs = extract_latex_expressions(prediction)

    # Normalize expressions
    gt_normalized = normalize_latex_expressions(gt_exprs)
    pred_normalized = normalize_latex_expressions(pred_exprs)

    # Compute F1 score
    return latex_exact_match_f1(gt_normalized, pred_normalized)


def latex_accuracy(ground_truth: str, prediction: str) -> float:
    """Calculate simple accuracy for LaTeX expressions.

    Accuracy = TP / (TP + FP + FN)

    This gives a single number indicating what fraction of all expressions
    (from both GT and prediction) were correctly matched.

    Args:
        ground_truth: Ground truth Markdown text with LaTeX
        prediction: Predicted Markdown text with LaTeX

    Returns:
        Accuracy score (0.0-1.0)

    Example:
        >>> gt = "Equation $x = 1$"
        >>> pred = "Equation $x=1$"
        >>> latex_accuracy(gt, pred)
        1.0
    """
    scores = latex_f1_score(ground_truth, prediction)
    total = scores.tp + scores.fp + scores.fn
    return scores.tp / total if total > 0 else 0.0
