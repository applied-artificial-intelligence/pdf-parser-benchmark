"""Tests for element F1 score metric."""

from pdf_bench.metrics.ast_parser import MarkdownASTParser
from pdf_bench.metrics.element_f1 import (
    ElementScores,
    calculate_precision_recall_f1,
    count_elements,
    element_f1_score,
)


class TestCountElements:
    """Tests for count_elements function."""

    def test_count_empty_ast(self) -> None:
        """Test counting elements in empty AST."""
        counts = count_elements([])
        assert counts == {}

    def test_count_single_element(self) -> None:
        """Test counting single element."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Heading")
        counts = count_elements(ast)

        assert "heading" in counts
        assert counts["heading"] >= 1

    def test_count_multiple_same_type(self) -> None:
        """Test counting multiple elements of same type."""
        parser = MarkdownASTParser()
        ast = parser.parse("# H1\n## H2\n### H3")
        counts = count_elements(ast)

        assert counts["heading"] == 3

    def test_count_different_types(self) -> None:
        """Test counting different element types."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Title\n\nParagraph\n\n- List item")
        counts = count_elements(ast)

        assert counts["heading"] >= 1
        assert counts["paragraph"] >= 1
        assert counts["list"] >= 1

    def test_count_nested_elements(self) -> None:
        """Test that nested elements are counted."""
        parser = MarkdownASTParser()
        ast = parser.parse("**Bold text**")
        counts = count_elements(ast)

        # Should count paragraph, strong, and text
        assert "paragraph" in counts
        assert "strong" in counts
        assert "text" in counts

    def test_blank_lines_not_counted(self) -> None:
        """Test that blank lines are filtered out."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Title\n\n\n\nParagraph")
        counts = count_elements(ast)

        # blank_line should not appear
        assert "blank_line" not in counts


class TestCalculatePrecisionRecallF1:
    """Tests for precision/recall/F1 calculation."""

    def test_perfect_match(self) -> None:
        """Test scores when counts match perfectly."""
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(5, 5)

        assert precision == 1.0
        assert recall == 1.0
        assert f1 == 1.0
        assert tp == 5
        assert fp == 0
        assert fn == 0

    def test_zero_counts(self) -> None:
        """Test scores with zero counts (both empty)."""
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(0, 0)

        assert precision == 1.0
        assert recall == 1.0
        assert f1 == 1.0
        assert tp == 0
        assert fp == 0
        assert fn == 0

    def test_missing_elements(self) -> None:
        """Test when prediction misses elements."""
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(5, 3)

        assert precision == 1.0  # All predicted are correct
        assert recall == 0.6  # Only got 3 out of 5
        assert abs(f1 - 0.75) < 1e-10  # Floating point comparison
        assert tp == 3
        assert fp == 0
        assert fn == 2

    def test_extra_elements(self) -> None:
        """Test when prediction has extra elements."""
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(3, 5)

        assert precision == 0.6  # Only 3 out of 5 are correct
        assert recall == 1.0  # Got all 3 ground truth elements
        assert abs(f1 - 0.75) < 1e-10  # Floating point comparison
        assert tp == 3
        assert fp == 2
        assert fn == 0

    def test_ground_truth_zero_predicted_nonzero(self) -> None:
        """Test when ground truth is zero but prediction has elements."""
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(0, 5)

        assert precision == 0.0  # All predictions are false
        assert recall == 0.0  # No ground truth to recall
        assert f1 == 0.0
        assert tp == 0
        assert fp == 5
        assert fn == 0

    def test_ground_truth_nonzero_predicted_zero(self) -> None:
        """Test when ground truth has elements but prediction is zero."""
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(5, 0)

        assert precision == 0.0  # No predictions to be precise
        assert recall == 0.0  # Didn't recall any
        assert f1 == 0.0
        assert tp == 0
        assert fp == 0
        assert fn == 5

    def test_partial_match(self) -> None:
        """Test with various partial matches."""
        # Got 7 out of 10
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(10, 7)

        assert precision == 1.0
        assert recall == 0.7
        assert abs(f1 - 0.8235294117647058) < 1e-10

        # Got 7 but predicted 12 (5 false positives)
        precision, recall, f1, tp, fp, fn = calculate_precision_recall_f1(7, 12)

        assert abs(precision - 0.5833333333333334) < 1e-10
        assert recall == 1.0


class TestElementF1Score:
    """Tests for element_f1_score function."""

    def test_identical_documents(self) -> None:
        """Test F1 score for identical documents."""
        parser = MarkdownASTParser()
        ast = parser.parse("# Title\n\nParagraph\n\n- Item 1\n- Item 2")

        scores = element_f1_score(ast, ast)

        assert scores["overall"]["f1"] == 1.0
        assert scores["overall"]["precision"] == 1.0
        assert scores["overall"]["recall"] == 1.0
        assert scores["overall"]["macro_f1"] == 1.0

    def test_empty_documents(self) -> None:
        """Test F1 score for empty documents."""
        scores = element_f1_score([], [])

        assert scores["overall"]["f1"] == 1.0
        assert scores["overall"]["macro_f1"] == 1.0
        assert scores["per_element"] == {}

    def test_completely_different(self) -> None:
        """Test when documents are completely different."""
        parser = MarkdownASTParser()
        gt = parser.parse("# Title\n\nParagraph")
        pred = parser.parse("- List item 1\n- List item 2")

        scores = element_f1_score(gt, pred)

        # Should have low overall F1
        assert scores["overall"]["f1"] < 0.5

    def test_per_element_scores(self) -> None:
        """Test that per-element scores are calculated."""
        parser = MarkdownASTParser()
        gt = parser.parse("# H1\n## H2\n\nText")
        pred = parser.parse("# H1\n\nText")

        scores = element_f1_score(gt, pred)

        # Check per-element scores exist
        assert "per_element" in scores
        assert "heading" in scores["per_element"]
        assert "paragraph" in scores["per_element"]

        # Headings: got 1 out of 2
        heading_scores = scores["per_element"]["heading"]
        assert heading_scores.ground_truth_count == 2
        assert heading_scores.predicted_count == 1
        assert heading_scores.recall == 0.5

    def test_element_scores_dataclass(self) -> None:
        """Test ElementScores dataclass structure."""
        parser = MarkdownASTParser()
        gt = parser.parse("# Title")
        pred = parser.parse("# Title")

        scores = element_f1_score(gt, pred)
        heading_scores = scores["per_element"]["heading"]

        assert isinstance(heading_scores, ElementScores)
        assert heading_scores.element_type == "heading"
        assert heading_scores.precision == 1.0
        assert heading_scores.recall == 1.0
        assert heading_scores.f1 == 1.0
        assert heading_scores.true_positives >= 1
        assert heading_scores.false_positives == 0
        assert heading_scores.false_negatives == 0

    def test_missing_elements(self) -> None:
        """Test when prediction misses some elements."""
        parser = MarkdownASTParser()
        gt = parser.parse("# Title\n\nPara 1\n\nPara 2\n\nPara 3")
        pred = parser.parse("# Title\n\nPara 1")

        scores = element_f1_score(gt, pred)

        # Overall F1 should be less than 1 but greater than 0
        assert 0.0 < scores["overall"]["f1"] < 1.0

        # Heading should be perfect
        assert scores["per_element"]["heading"].f1 == 1.0

        # Paragraphs should have lower recall
        para_scores = scores["per_element"]["paragraph"]
        assert para_scores.recall < 1.0

    def test_extra_elements(self) -> None:
        """Test when prediction has extra elements."""
        parser = MarkdownASTParser()
        gt = parser.parse("# Title")
        pred = parser.parse("# Title\n\n- Extra\n- List\n- Items")

        scores = element_f1_score(gt, pred)

        # Should have precision issues
        assert scores["overall"]["precision"] < 1.0

        # List elements should show false positives
        if "list" in scores["per_element"]:
            list_scores = scores["per_element"]["list"]
            assert list_scores.false_positives > 0

    def test_macro_vs_micro_averaging(self) -> None:
        """Test difference between macro and micro averaging."""
        parser = MarkdownASTParser()
        # Many headings, one paragraph
        gt = parser.parse("# H1\n## H2\n### H3\n#### H4\n\nParagraph")
        # Got all headings, missed paragraph
        pred = parser.parse("# H1\n## H2\n### H3\n#### H4")

        scores = element_f1_score(gt, pred)

        # Macro averages over element types (heading, paragraph, etc.)
        # Micro sums all TP, FP, FN across types

        macro_f1 = scores["overall"]["macro_f1"]
        micro_f1 = scores["overall"]["micro_f1"]

        # They should be different
        # Macro gives equal weight to each type
        # Micro gives more weight to types with more elements
        assert macro_f1 != micro_f1


class TestRealWorldExamples:
    """Tests with realistic scenarios."""

    def test_partial_extraction(self) -> None:
        """Test realistic partial extraction scenario."""
        parser = MarkdownASTParser()

        ground_truth = """# Document Title

Introduction paragraph.

## Section 1

Content for section 1.

- Point 1
- Point 2
- Point 3

## Section 2

More content.
"""

        # Parser missed lists
        predicted = """# Document Title

Introduction paragraph.

## Section 1

Content for section 1.

## Section 2

More content.
"""

        gt_ast = parser.parse(ground_truth)
        pred_ast = parser.parse(predicted)

        scores = element_f1_score(gt_ast, pred_ast)

        # Should have good heading/paragraph scores
        assert scores["per_element"]["heading"].f1 > 0.8
        assert scores["per_element"]["paragraph"].f1 > 0.8

        # Lists should show problems
        if "list" in scores["per_element"]:
            assert scores["per_element"]["list"].f1 < 1.0

    def test_structure_only_comparison(self) -> None:
        """Test that only structure matters, not content."""
        parser = MarkdownASTParser()

        doc1 = "# Title\n\nParagraph A"
        doc2 = "# Title\n\nCompletely different paragraph B"

        ast1 = parser.parse(doc1)
        ast2 = parser.parse(doc2)

        scores = element_f1_score(ast1, ast2)

        # Structure is identical, so F1 should be 1.0
        assert scores["overall"]["f1"] == 1.0

    def test_nested_structure(self) -> None:
        """Test with nested structures."""
        parser = MarkdownASTParser()

        gt = """- Item 1
  - Nested 1.1
  - Nested 1.2
- Item 2
"""

        pred = """- Item 1
  - Nested 1.1
- Item 2
"""

        gt_ast = parser.parse(gt)
        pred_ast = parser.parse(pred)

        scores = element_f1_score(gt_ast, pred_ast)

        # Should have some list_item mismatch
        if "list_item" in scores["per_element"]:
            assert scores["per_element"]["list_item"].f1 < 1.0


class TestEdgeCases:
    """Edge case tests."""

    def test_one_empty_one_full(self) -> None:
        """Test when one document is empty."""
        parser = MarkdownASTParser()
        empty_ast = parser.parse("")
        full_ast = parser.parse("# Title\n\nText")

        scores = element_f1_score(empty_ast, full_ast)

        # Precision and recall should be 0
        assert scores["overall"]["precision"] == 0.0
        assert scores["overall"]["recall"] == 0.0
        assert scores["overall"]["f1"] == 0.0

    def test_very_imbalanced(self) -> None:
        """Test with very imbalanced element counts."""
        parser = MarkdownASTParser()

        # 20 paragraphs, 1 heading
        paras = "\n\n".join([f"Paragraph {i}" for i in range(20)])
        gt = f"# Title\n\n{paras}"

        # Just the heading
        pred = "# Title"

        gt_ast = parser.parse(gt)
        pred_ast = parser.parse(pred)

        scores = element_f1_score(gt_ast, pred_ast)

        # Heading should be perfect
        assert scores["per_element"]["heading"].f1 == 1.0

        # Paragraphs should have terrible recall
        assert scores["per_element"]["paragraph"].recall < 0.1

        # Micro F1 should be low (dominated by paragraphs)
        assert scores["overall"]["micro_f1"] < 0.2

        # Macro F1 should be higher (averages heading and paragraph)
        assert scores["overall"]["macro_f1"] > scores["overall"]["micro_f1"]

    def test_type_only_in_ground_truth(self) -> None:
        """Test when element type exists only in ground truth."""
        parser = MarkdownASTParser()

        gt = parser.parse("```python\ncode\n```")
        pred = parser.parse("Text instead")

        scores = element_f1_score(gt, pred)

        # Code block should have zero recall
        if "block_code" in scores["per_element"]:
            assert scores["per_element"]["block_code"].recall == 0.0

    def test_type_only_in_prediction(self) -> None:
        """Test when element type exists only in prediction."""
        parser = MarkdownASTParser()

        gt = parser.parse("Text")
        pred = parser.parse("```python\ncode\n```")

        scores = element_f1_score(gt, pred)

        # Code block should have zero precision
        if "block_code" in scores["per_element"]:
            assert scores["per_element"]["block_code"].precision == 0.0


class TestMacroMicroDifference:
    """Tests specifically for macro vs micro averaging."""

    def test_macro_averaging(self) -> None:
        """Test macro averaging calculation."""
        parser = MarkdownASTParser()

        # Create scenario: perfect on headings, bad on paragraphs
        gt = parser.parse("# H1\n\nP1\n\nP2\n\nP3\n\nP4\n\nP5")
        pred = parser.parse("# H1")

        scores = element_f1_score(gt, pred)

        # Macro should average the F1 scores
        heading_f1 = scores["per_element"]["heading"].f1
        para_f1 = scores["per_element"]["paragraph"].f1

        expected_macro = (heading_f1 + para_f1) / 2

        # Account for other element types (text, etc.)
        # Macro averages over all element types present
        num_types = len(scores["per_element"])
        sum_f1 = sum(s.f1 for s in scores["per_element"].values())
        expected_macro = sum_f1 / num_types

        assert abs(scores["overall"]["macro_f1"] - expected_macro) < 1e-10

    def test_micro_averaging(self) -> None:
        """Test micro averaging calculation."""
        parser = MarkdownASTParser()

        gt = parser.parse("# H1\n\nP1\n\nP2")
        pred = parser.parse("# H1\n\nP1")

        scores = element_f1_score(gt, pred)

        # Micro sums all TP, FP, FN
        total_tp = sum(s.true_positives for s in scores["per_element"].values())
        total_fp = sum(s.false_positives for s in scores["per_element"].values())
        total_fn = sum(s.false_negatives for s in scores["per_element"].values())

        # Calculate expected micro scores
        expected_precision = total_tp / (total_tp + total_fp)
        expected_recall = total_tp / (total_tp + total_fn)
        expected_f1 = (
            2 * expected_precision * expected_recall / (expected_precision + expected_recall)
        )

        assert abs(scores["overall"]["micro_precision"] - expected_precision) < 1e-10
        assert abs(scores["overall"]["micro_recall"] - expected_recall) < 1e-10
        assert abs(scores["overall"]["micro_f1"] - expected_f1) < 1e-10
