"""Tests for cell content F1 metric."""

from pdf_bench.metrics import CellF1Scores, GFMTable, cell_accuracy, cell_content_f1_score


class TestCellContentF1Score:
    """Tests for cell_content_f1_score function."""

    def test_identical_tables(self) -> None:
        """Test F1 score for identical tables."""
        table1 = [["A", "B"], ["1", "2"]]
        table2 = [["A", "B"], ["1", "2"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.precision == 1.0
        assert scores.recall == 1.0
        assert scores.f1 == 1.0
        assert scores.true_positives == 4
        assert scores.false_positives == 0
        assert scores.false_negatives == 0

    def test_completely_different_tables(self) -> None:
        """Test F1 score for completely different tables."""
        table1 = [["A", "B"], ["1", "2"]]
        table2 = [["X", "Y"], ["3", "4"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.precision == 0.0
        assert scores.recall == 0.0
        assert scores.f1 == 0.0
        assert scores.true_positives == 0
        assert scores.false_positives == 4
        assert scores.false_negatives == 4

    def test_partial_match(self) -> None:
        """Test F1 score for partially matching tables."""
        table1 = [["A", "B"], ["1", "2"]]
        table2 = [["A", "B"], ["1", "3"]]  # One cell different

        scores = cell_content_f1_score(table1, table2)

        assert scores.true_positives == 3
        assert scores.false_positives == 1
        assert scores.false_negatives == 1
        assert scores.precision == 3 / 4
        assert scores.recall == 3 / 4
        assert scores.f1 == 0.75

    def test_empty_tables(self) -> None:
        """Test F1 score for empty tables."""
        table1: list[list[str]] = []
        table2: list[list[str]] = []

        scores = cell_content_f1_score(table1, table2)

        # Empty tables should have perfect score
        assert scores.f1 == 0.0  # No cells to compare
        assert scores.true_positives == 0
        assert scores.false_positives == 0
        assert scores.false_negatives == 0

    def test_one_empty_table(self) -> None:
        """Test F1 score when one table is empty."""
        table1 = [["A", "B"]]
        table2: list[list[str]] = []

        scores = cell_content_f1_score(table1, table2)

        # After padding, table2 becomes [[""]], so we're comparing:
        # table1_padded = [["A", "B"]]
        # table2_padded = [["", ""]]
        # This gives us 2 FP (A and B vs empty cells)
        assert scores.precision == 0.0
        assert scores.recall == 0.0
        assert scores.false_positives == 2
        assert scores.false_negatives == 0

    def test_mismatched_dimensions_more_rows(self) -> None:
        """Test handling of tables with different number of rows."""
        table1 = [["A", "B"], ["1", "2"], ["X", "Y"]]  # 3 rows
        table2 = [["A", "B"], ["1", "2"]]  # 2 rows

        scores = cell_content_f1_score(table1, table2)

        # First 4 cells match, last 2 cells are FP (from table1)
        assert scores.true_positives == 4
        assert scores.false_positives == 2
        assert scores.false_negatives == 0

    def test_mismatched_dimensions_more_cols(self) -> None:
        """Test handling of tables with different number of columns."""
        table1 = [["A", "B", "C"], ["1", "2", "3"]]  # 3 cols
        table2 = [["A", "B"], ["1", "2"]]  # 2 cols

        scores = cell_content_f1_score(table1, table2)

        # First 4 cells match, last 2 cells (C, 3) are FP
        assert scores.true_positives == 4
        assert scores.false_positives == 2
        assert scores.false_negatives == 0

    def test_mismatched_dimensions_both(self) -> None:
        """Test handling of tables with different rows and columns."""
        table1 = [["A", "B", "C"], ["1", "2", "3"], ["X", "Y", "Z"]]  # 3x3
        table2 = [["A", "B"], ["1", "2"]]  # 2x2

        scores = cell_content_f1_score(table1, table2)

        # First 4 cells match, 5 cells are FP (extra in table1)
        assert scores.true_positives == 4
        assert scores.false_positives == 5
        assert scores.false_negatives == 0

    def test_normalize_whitespace(self) -> None:
        """Test that whitespace normalization works."""
        table1 = [["A  ", "  B"], ["1", " 2 "]]
        table2 = [["A", "B"], ["1", "2"]]

        scores = cell_content_f1_score(table1, table2, normalize=True)

        # With normalization, all should match
        assert scores.f1 == 1.0

    def test_case_insensitive_comparison(self) -> None:
        """Test case-insensitive comparison when normalize=False."""
        table1 = [["A", "B"], ["hello", "WORLD"]]
        table2 = [["a", "b"], ["HELLO", "world"]]

        # Case-sensitive should not match
        scores_sensitive = cell_content_f1_score(
            table1, table2, normalize=False, case_sensitive=True
        )
        assert scores_sensitive.f1 == 0.0

        # Case-insensitive should match
        scores_insensitive = cell_content_f1_score(
            table1, table2, normalize=False, case_sensitive=False
        )
        assert scores_insensitive.f1 == 1.0

    def test_normalize_unicode(self) -> None:
        """Test Unicode normalization."""
        # Different Unicode representations of café
        table1 = [["café"]]  # é as single character (U+00E9)
        table2 = [["café"]]  # é as e + combining acute (U+0065 U+0301)

        scores = cell_content_f1_score(table1, table2, normalize=True)

        # Should match after normalization
        assert scores.f1 == 1.0

    def test_empty_cells_dont_count(self) -> None:
        """Test that empty-empty cell matches don't count as TP."""
        table1 = [["A", ""], ["", "B"]]
        table2 = [["A", ""], ["", "B"]]

        scores = cell_content_f1_score(table1, table2)

        # Only non-empty matches count
        assert scores.true_positives == 2  # Just A and B
        assert scores.false_positives == 0
        assert scores.false_negatives == 0

    def test_with_gfm_table(self) -> None:
        """Test F1 score with GFMTable objects."""
        table1 = GFMTable(
            cells=[["Name", "Age"], ["Alice", "30"], ["Bob", "25"]],
            alignment=["left", "left"],
            num_rows=3,
            num_cols=2,
        )
        table2 = GFMTable(
            cells=[["Name", "Age"], ["Alice", "30"], ["Bob", "26"]],  # Different age
            alignment=["left", "left"],
            num_rows=3,
            num_cols=2,
        )

        scores = cell_content_f1_score(table1, table2)

        # 5 cells match (Name, Age, Alice, 30, Bob), 1 differs (25 vs 26)
        assert scores.true_positives == 5
        assert scores.false_positives == 1
        assert scores.false_negatives == 1
        assert scores.f1 == 5 / 6  # 2 * (5/6 * 5/6) / (10/6) = 5/6


class TestCellAccuracy:
    """Tests for cell_accuracy function."""

    def test_perfect_accuracy(self) -> None:
        """Test accuracy for identical tables."""
        table1 = [["A", "B"], ["1", "2"]]
        table2 = [["A", "B"], ["1", "2"]]

        accuracy = cell_accuracy(table1, table2)

        assert accuracy == 1.0

    def test_zero_accuracy(self) -> None:
        """Test accuracy for completely different tables."""
        table1 = [["A", "B"], ["1", "2"]]
        table2 = [["X", "Y"], ["3", "4"]]

        accuracy = cell_accuracy(table1, table2)

        assert accuracy == 0.0

    def test_partial_accuracy(self) -> None:
        """Test accuracy for partially matching tables."""
        table1 = [["A", "B"], ["1", "2"]]
        table2 = [["A", "B"], ["1", "3"]]

        accuracy = cell_accuracy(table1, table2)

        # Cell content differs at position (1,1): "2" vs "3"
        # TP = 3 (A, B, 1)
        # FP = 1 (cell "2" in prediction)
        # FN = 1 (cell "3" in ground truth)
        # Accuracy = TP / (TP + FP + FN) = 3 / 5 = 0.6
        assert accuracy == 0.6

    def test_empty_tables_accuracy(self) -> None:
        """Test accuracy for empty tables."""
        table1: list[list[str]] = []
        table2: list[list[str]] = []

        accuracy = cell_accuracy(table1, table2)

        # Empty tables should have perfect accuracy
        assert accuracy == 1.0

    def test_accuracy_with_normalization(self) -> None:
        """Test accuracy with normalization enabled."""
        table1 = [["  A  ", "B"], ["1", "2"]]
        table2 = [["A", "B  "], ["1", "2"]]

        accuracy = cell_accuracy(table1, table2, normalize=True)

        assert accuracy == 1.0


class TestCellF1Scores:
    """Tests for CellF1Scores dataclass."""

    def test_scores_creation(self) -> None:
        """Test creating CellF1Scores object."""
        scores = CellF1Scores(
            precision=0.8,
            recall=0.75,
            f1=0.77,
            true_positives=6,
            false_positives=2,
            false_negatives=2,
            total_cells=10,
        )

        assert scores.precision == 0.8
        assert scores.recall == 0.75
        assert scores.f1 == 0.77
        assert scores.true_positives == 6
        assert scores.false_positives == 2
        assert scores.false_negatives == 2
        assert scores.total_cells == 10


class TestPadTables:
    """Tests for _pad_tables helper function."""

    def test_pad_tables_same_size(self) -> None:
        """Test padding tables of the same size (no-op)."""
        from pdf_bench.metrics.cell_content_f1 import _pad_tables

        t1 = [["A", "B"], ["1", "2"]]
        t2 = [["X", "Y"], ["3", "4"]]

        p1, p2 = _pad_tables(t1, t2)

        assert p1 == t1
        assert p2 == t2

    def test_pad_tables_different_rows(self) -> None:
        """Test padding tables with different number of rows."""
        from pdf_bench.metrics.cell_content_f1 import _pad_tables

        t1 = [["A", "B"], ["1", "2"], ["X", "Y"]]
        t2 = [["C", "D"]]

        p1, p2 = _pad_tables(t1, t2)

        assert len(p1) == 3
        assert len(p2) == 3
        assert p2[1] == ["", ""]
        assert p2[2] == ["", ""]

    def test_pad_tables_different_cols(self) -> None:
        """Test padding tables with different number of columns."""
        from pdf_bench.metrics.cell_content_f1 import _pad_tables

        t1 = [["A", "B", "C"]]
        t2 = [["X"]]

        p1, p2 = _pad_tables(t1, t2)

        assert p1[0] == ["A", "B", "C"]
        assert p2[0] == ["X", "", ""]

    def test_pad_empty_tables(self) -> None:
        """Test padding empty tables."""
        from pdf_bench.metrics.cell_content_f1 import _pad_tables

        t1: list[list[str]] = []
        t2: list[list[str]] = []

        p1, p2 = _pad_tables(t1, t2)

        assert p1 == []
        assert p2 == []

    def test_pad_one_empty_table(self) -> None:
        """Test padding when one table is empty."""
        from pdf_bench.metrics.cell_content_f1 import _pad_tables

        t1 = [["A", "B"]]
        t2: list[list[str]] = []

        p1, p2 = _pad_tables(t1, t2)

        assert p1 == [["A", "B"]]
        # Empty table padded to match t1's dimensions (1 row x 2 cols)
        assert p2 == [["", ""]]


class TestCompareCells:
    """Tests for _compare_cells helper function."""

    def test_compare_identical_cells(self) -> None:
        """Test comparing identical cells."""
        from pdf_bench.metrics.cell_content_f1 import _compare_cells

        t1 = [["A", "B"], ["1", "2"]]
        t2 = [["A", "B"], ["1", "2"]]

        tp, fp, fn = _compare_cells(t1, t2)

        assert tp == 4
        assert fp == 0
        assert fn == 0

    def test_compare_different_cells(self) -> None:
        """Test comparing completely different cells."""
        from pdf_bench.metrics.cell_content_f1 import _compare_cells

        t1 = [["A", "B"]]
        t2 = [["X", "Y"]]

        tp, fp, fn = _compare_cells(t1, t2)

        assert tp == 0
        assert fp == 2
        assert fn == 2

    def test_compare_with_empty_cells(self) -> None:
        """Test comparing with empty cells."""
        from pdf_bench.metrics.cell_content_f1 import _compare_cells

        t1 = [["A", ""]]
        t2 = [["A", "B"]]

        tp, fp, fn = _compare_cells(t1, t2)

        assert tp == 1  # A matches
        assert fp == 0  # No false positives
        assert fn == 1  # B in ground truth but not in prediction

    def test_compare_with_normalization(self) -> None:
        """Test cell comparison with normalization."""
        from pdf_bench.metrics.cell_content_f1 import _compare_cells

        t1 = [["  A  ", "B"]]
        t2 = [["A", "  B  "]]

        tp, fp, fn = _compare_cells(t1, t2, normalize=True)

        assert tp == 2
        assert fp == 0
        assert fn == 0

    def test_compare_case_insensitive(self) -> None:
        """Test case-insensitive comparison."""
        from pdf_bench.metrics.cell_content_f1 import _compare_cells

        t1 = [["Hello", "WORLD"]]
        t2 = [["hello", "world"]]

        tp, fp, fn = _compare_cells(t1, t2, normalize=False, case_sensitive=False)

        assert tp == 2
        assert fp == 0
        assert fn == 0


class TestEdgeCases:
    """Edge case tests for cell content F1."""

    def test_very_large_table(self) -> None:
        """Test F1 score for very large table."""
        # Create 100x100 table
        size = 100
        table1 = [[f"cell_{i}_{j}" for j in range(size)] for i in range(size)]
        table2 = [[f"cell_{i}_{j}" for j in range(size)] for i in range(size)]

        scores = cell_content_f1_score(table1, table2)

        assert scores.f1 == 1.0
        assert scores.true_positives == size * size

    def test_single_cell_table(self) -> None:
        """Test F1 score for single cell table."""
        table1 = [["A"]]
        table2 = [["A"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.f1 == 1.0

    def test_single_cell_different(self) -> None:
        """Test F1 score for single cell with different content."""
        table1 = [["A"]]
        table2 = [["B"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.f1 == 0.0
        assert scores.true_positives == 0
        assert scores.false_positives == 1
        assert scores.false_negatives == 1

    def test_unicode_content(self) -> None:
        """Test F1 score with Unicode content."""
        table1 = [["中文", "😀"], ["日本語", "🌍"]]
        table2 = [["中文", "😀"], ["日本語", "🌍"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.f1 == 1.0

    def test_special_characters(self) -> None:
        """Test F1 score with special characters."""
        table1 = [["<tag>", "&amp;"], ["©", "™"]]
        table2 = [["<tag>", "&amp;"], ["©", "™"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.f1 == 1.0

    def test_very_long_cells(self) -> None:
        """Test F1 score with very long cell content."""
        long_text = "A" * 1000
        table1 = [[long_text, "B"]]
        table2 = [[long_text, "B"]]

        scores = cell_content_f1_score(table1, table2)

        assert scores.f1 == 1.0

    def test_jagged_table(self) -> None:
        """Test F1 score with jagged table (different row lengths)."""
        # This tests the padding logic
        table1 = [["A", "B", "C"], ["1", "2"]]  # Second row shorter
        table2 = [["A", "B"], ["1", "2", "3"]]  # First row shorter

        scores = cell_content_f1_score(table1, table2)

        # After padding:
        # table1 = [['A', 'B', 'C'], ['1', '2', '']]
        # table2 = [['A', 'B', ''], ['1', '2', '3']]
        # Matches: A, B, 1, 2 = 4 TP
        # Differs: C vs '', '' vs '', '' vs 3 = 3 FP + 1 FN
        assert scores.true_positives == 4
