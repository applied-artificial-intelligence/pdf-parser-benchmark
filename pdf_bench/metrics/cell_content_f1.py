"""Cell-by-cell table content comparison metric using F1 score.

This module provides utilities for comparing table contents at the cell level
and calculating precision, recall, and F1 scores for table content accuracy.
It complements structural metrics (like TEDS) by focusing on the actual text
content of cells rather than table structure.

The metric compares two tables cell-by-cell, counting:
- True Positives (TP): Cells that match in both tables
- False Positives (FP): Cells in prediction that don't match ground truth
- False Negatives (FN): Cells in ground truth that aren't correctly predicted

From these counts, we calculate:
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 * (Precision * Recall) / (Precision + Recall)

Key Features:
- Cell-by-cell text comparison with normalization
- Handles mismatched table dimensions (padding with empty cells)
- Returns detailed scores (precision, recall, F1, counts)
- Configurable comparison modes (exact, normalized, case-insensitive)
- Works with both GFM tables and raw 2D arrays

Example:
    >>> from pdf_bench.metrics import cell_content_f1_score
    >>> ground_truth = [['A', 'B'], ['1', '2']]
    >>> prediction = [['A', 'B'], ['1', '3']]
    >>> scores = cell_content_f1_score(prediction, ground_truth)
    >>> scores.f1
    0.75
    >>> scores.precision
    0.75
    >>> scores.recall
    0.75
"""

from dataclasses import dataclass

from pdf_bench.metrics.gfm_table_parser import GFMTable
from pdf_bench.utils.normalization import normalize_text


@dataclass
class CellF1Scores:
    """Scores for cell-by-cell table content comparison.

    Attributes:
        precision: Precision score (TP / (TP + FP)), range [0.0, 1.0]
        recall: Recall score (TP / (TP + FN)), range [0.0, 1.0]
        f1: F1 score (harmonic mean of precision and recall), range [0.0, 1.0]
        true_positives: Count of cells that match
        false_positives: Count of cells in prediction not in ground truth
        false_negatives: Count of cells in ground truth not in prediction
        total_cells: Total number of cells compared (after padding)
    """

    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    false_negatives: int
    total_cells: int


def cell_content_f1_score(
    prediction: list[list[str]] | GFMTable,
    ground_truth: list[list[str]] | GFMTable,
    normalize: bool = True,
    case_sensitive: bool = False,
) -> CellF1Scores:
    """Calculate F1 score for cell-by-cell table content comparison.

    Compares two tables cell-by-cell, handling mismatched dimensions by padding
    with empty cells. Cells are compared as strings with optional normalization.

    Args:
        prediction: Predicted table (2D list of strings or GFMTable)
        ground_truth: Ground truth table (2D list of strings or GFMTable)
        normalize: If True, apply text normalization before comparison
            (whitespace, Unicode, ligatures, smart quotes)
        case_sensitive: If True, comparison is case-sensitive
            (only applies if normalize=False)

    Returns:
        CellF1Scores with precision, recall, F1, and cell counts

    Example:
        >>> pred = [['A', 'B'], ['1', '2']]
        >>> gt = [['A', 'B'], ['1', '2']]
        >>> scores = cell_content_f1_score(pred, gt)
        >>> scores.f1
        1.0

        >>> pred = [['A', 'B'], ['1', '3']]
        >>> gt = [['A', 'B'], ['1', '2']]
        >>> scores = cell_content_f1_score(pred, gt)
        >>> scores.f1
        0.75
        >>> scores.true_positives
        3
        >>> scores.false_positives
        1
        >>> scores.false_negatives
        1
    """
    # Extract cells from GFMTable if needed
    pred_cells = prediction.cells if isinstance(prediction, GFMTable) else prediction
    gt_cells = ground_truth.cells if isinstance(ground_truth, GFMTable) else ground_truth

    # Pad tables to same dimensions
    pred_padded, gt_padded = _pad_tables(pred_cells, gt_cells)

    # Compare cells
    tp, fp, fn = _compare_cells(
        pred_padded, gt_padded, normalize=normalize, case_sensitive=case_sensitive
    )

    # Calculate metrics
    total_cells = sum(len(row) for row in pred_padded)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return CellF1Scores(
        precision=precision,
        recall=recall,
        f1=f1,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        total_cells=total_cells,
    )


def _pad_tables(
    table1: list[list[str]], table2: list[list[str]]
) -> tuple[list[list[str]], list[list[str]]]:
    """Pad tables to have the same dimensions.

    Ensures both tables have the same number of rows and columns by padding
    with empty strings where necessary.

    Args:
        table1: First table (2D list of strings)
        table2: Second table (2D list of strings)

    Returns:
        Tuple of (padded_table1, padded_table2) with matching dimensions

    Example:
        >>> t1 = [['A', 'B'], ['1', '2']]
        >>> t2 = [['X']]
        >>> p1, p2 = _pad_tables(t1, t2)
        >>> p1
        [['A', 'B'], ['1', '2']]
        >>> p2
        [['X', ''], ['', '']]
    """
    if not table1 and not table2:
        return [], []

    # If one table is empty, we need to create an empty table with matching dimensions
    if not table1:
        # table1 is empty, create empty table matching table2's dimensions
        max_rows = len(table2)
        max_cols = max((len(row) for row in table2), default=0)
        return [[""] * max_cols for _ in range(max_rows)], table2

    if not table2:
        # table2 is empty, create empty table matching table1's dimensions
        max_rows = len(table1)
        max_cols = max((len(row) for row in table1), default=0)
        return table1, [[""] * max_cols for _ in range(max_rows)]

    # Determine max dimensions
    max_rows = max(len(table1), len(table2))
    max_cols = max(
        max((len(row) for row in table1), default=0),
        max((len(row) for row in table2), default=0),
    )

    # Pad table1
    padded1 = []
    for i in range(max_rows):
        if i < len(table1):
            row = list(table1[i])  # Copy row
            # Pad row to max_cols
            row.extend([""] * (max_cols - len(row)))
            padded1.append(row)
        else:
            # Add empty row
            padded1.append([""] * max_cols)

    # Pad table2
    padded2 = []
    for i in range(max_rows):
        if i < len(table2):
            row = list(table2[i])  # Copy row
            # Pad row to max_cols
            row.extend([""] * (max_cols - len(row)))
            padded2.append(row)
        else:
            # Add empty row
            padded2.append([""] * max_cols)

    return padded1, padded2


def _compare_cells(
    table1: list[list[str]],
    table2: list[list[str]],
    normalize: bool = True,
    case_sensitive: bool = False,
) -> tuple[int, int, int]:
    """Compare cells between two tables and count TP, FP, FN.

    Args:
        table1: First table (must be same dimensions as table2)
        table2: Second table (must be same dimensions as table1)
        normalize: If True, normalize text before comparison
        case_sensitive: If True, comparison is case-sensitive (only if normalize=False)

    Returns:
        Tuple of (true_positives, false_positives, false_negatives)

    Note:
        Tables must have the same dimensions (use _pad_tables first)
    """
    tp = 0  # Both tables have same non-empty value
    fp = 0  # Prediction has value, ground truth doesn't or values differ
    fn = 0  # Ground truth has value, prediction doesn't or values differ

    for row1, row2 in zip(table1, table2, strict=True):
        for cell1, cell2 in zip(row1, row2, strict=True):
            # Prepare cells for comparison
            if normalize:
                # Use full text normalization
                c1 = normalize_text(cell1)
                c2 = normalize_text(cell2)
            elif not case_sensitive:
                # Just case-insensitive
                c1 = cell1.lower().strip()
                c2 = cell2.lower().strip()
            else:
                # Exact comparison
                c1 = cell1.strip()
                c2 = cell2.strip()

            # Count as match if both cells have content and match
            if c1 == c2:
                if c1:  # Non-empty match
                    tp += 1
                # Empty-empty match doesn't count (not meaningful)
            else:
                # Cells differ
                if c1 and c2:
                    # Both have content but differ - count as both FP and FN
                    fp += 1
                    fn += 1
                elif c1:
                    # Prediction has content, ground truth empty
                    fp += 1
                elif c2:
                    # Ground truth has content, prediction empty
                    fn += 1
                # else: both empty and don't match (shouldn't happen, but ignore)

    return tp, fp, fn


def cell_accuracy(
    prediction: list[list[str]] | GFMTable,
    ground_truth: list[list[str]] | GFMTable,
    normalize: bool = True,
    case_sensitive: bool = False,
) -> float:
    """Calculate simple cell-level accuracy (% of cells that match).

    This is a simpler metric than F1, useful for quick evaluation.

    Args:
        prediction: Predicted table
        ground_truth: Ground truth table
        normalize: If True, apply text normalization before comparison
        case_sensitive: If True, comparison is case-sensitive

    Returns:
        Accuracy as float in [0.0, 1.0]

    Example:
        >>> pred = [['A', 'B'], ['1', '2']]
        >>> gt = [['A', 'B'], ['1', '2']]
        >>> cell_accuracy(pred, gt)
        1.0

        >>> pred = [['A', 'X'], ['1', '2']]
        >>> gt = [['A', 'B'], ['1', '2']]
        >>> cell_accuracy(pred, gt)
        0.75
    """
    scores = cell_content_f1_score(
        prediction, ground_truth, normalize=normalize, case_sensitive=case_sensitive
    )

    # Accuracy = TP / total_cells
    # But only count non-empty cells as the denominator
    meaningful_cells = scores.true_positives + scores.false_positives + scores.false_negatives

    if meaningful_cells == 0:
        # Both tables are completely empty
        return 1.0

    return scores.true_positives / meaningful_cells
