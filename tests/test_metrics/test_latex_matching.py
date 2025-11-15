"""Tests for LaTeX string matching metric."""

from pdf_bench.metrics.latex_matching import (
    LaTeXF1Scores,
    extract_latex_expressions,
    latex_accuracy,
    latex_exact_match_f1,
    latex_f1_score,
    normalize_latex_expressions,
)


class TestExtractLatexExpressions:
    """Test LaTeX expression extraction from Markdown."""

    def test_extract_inline_dollar(self):
        """Test extraction of $...$ inline math."""
        text = "The equation $x = 1$ is simple."
        exprs = extract_latex_expressions(text)
        assert exprs == ["x = 1"]

    def test_extract_display_double_dollar(self):
        """Test extraction of $$...$$ display math."""
        text = "Display equation: $$y = 2$$"
        exprs = extract_latex_expressions(text)
        assert exprs == ["y = 2"]

    def test_extract_inline_paren(self):
        r"""Test extraction of \(...\) inline math."""
        text = r"Inline math \(a + b\) here"
        exprs = extract_latex_expressions(text)
        assert exprs == ["a + b"]

    def test_extract_display_bracket(self):
        r"""Test extraction of \[...\] display math."""
        text = r"Display: \[c + d\] end"
        exprs = extract_latex_expressions(text)
        assert exprs == ["c + d"]

    def test_extract_multiple_expressions(self):
        """Test extraction of multiple expressions."""
        text = "Inline $x = 1$ and display $$y = 2$$ here"
        exprs = extract_latex_expressions(text)
        assert exprs == ["x = 1", "y = 2"]

    def test_extract_preserves_order(self):
        """Test that expressions are returned in document order."""
        text = "First $$a$$ then $b$ finally $$c$$"
        exprs = extract_latex_expressions(text)
        assert exprs == ["a", "b", "c"]

    def test_extract_empty_text(self):
        """Test extraction from text with no math."""
        text = "Just plain text with no math"
        exprs = extract_latex_expressions(text)
        assert exprs == []

    def test_extract_nested_delimiters(self):
        """Test handling of nested/escaped delimiters."""
        # LaTeX with escaped dollar signs
        text = r"The symbol $\$ is used for money"
        exprs = extract_latex_expressions(text)
        # Should extract the math expression containing escaped $
        assert len(exprs) == 1

    def test_extract_multiline(self):
        """Test extraction from multiline math."""
        text = """
        Equation:
        $$
        x = \\frac{a}{b}
        $$
        End
        """
        exprs = extract_latex_expressions(text)
        assert len(exprs) == 1
        assert "frac" in exprs[0]

    def test_extract_complex_math(self):
        """Test extraction of complex mathematical expressions."""
        text = r"The formula $\int_0^\infty e^{-x} dx = 1$ proves convergence"
        exprs = extract_latex_expressions(text)
        assert len(exprs) == 1
        assert "int" in exprs[0]
        assert "infty" in exprs[0]

    def test_extract_mixed_modes(self):
        r"""Test extraction with all four delimiter types."""
        text = r"A $a$ B $$b$$ C \(c\) D \[d\] E"
        exprs = extract_latex_expressions(text)
        assert exprs == ["a", "b", "c", "d"]


class TestNormalizeLatexExpressions:
    """Test normalization of extracted LaTeX expressions."""

    def test_normalize_single_expression(self):
        """Test normalization of a single expression."""
        exprs = [r"\left( x \right)"]
        normalized = normalize_latex_expressions(exprs)
        assert normalized == ["(x)"]

    def test_normalize_multiple_expressions(self):
        """Test normalization of multiple expressions."""
        exprs = [r"\left( a \right)", r"\frac{  b  }{  c  }"]
        normalized = normalize_latex_expressions(exprs)
        assert normalized[0] == "(a)"
        assert r"\frac{b}{c}" in normalized[1]

    def test_normalize_empty_list(self):
        """Test normalization of empty expression list."""
        exprs = []
        normalized = normalize_latex_expressions(exprs)
        assert normalized == []

    def test_normalize_preserves_order(self):
        """Test that normalization preserves expression order."""
        exprs = ["x", "y", "z"]
        normalized = normalize_latex_expressions(exprs)
        assert normalized == ["x", "y", "z"]


class TestLatexExactMatchF1:
    """Test F1 score calculation for normalized expressions."""

    def test_perfect_match(self):
        """Test F1 with perfect match."""
        gt = ["x=1", "y=2"]
        pred = ["x=1", "y=2"]
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 2
        assert scores.fp == 0
        assert scores.fn == 0
        assert scores.precision == 1.0
        assert scores.recall == 1.0
        assert scores.f1 == 1.0

    def test_no_match(self):
        """Test F1 with no matches."""
        gt = ["x=1"]
        pred = ["y=2"]
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 0
        assert scores.fp == 1
        assert scores.fn == 1
        assert scores.precision == 0.0
        assert scores.recall == 0.0
        assert scores.f1 == 0.0

    def test_partial_match(self):
        """Test F1 with partial match."""
        gt = ["x=1", "y=2", "z=3"]
        pred = ["x=1", "y=2"]
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 2
        assert scores.fp == 0
        assert scores.fn == 1
        assert scores.precision == 1.0
        assert scores.recall == 2 / 3
        assert abs(scores.f1 - 0.8) < 0.01  # F1 ≈ 0.8

    def test_extra_predictions(self):
        """Test F1 with extra predictions (false positives)."""
        gt = ["x=1"]
        pred = ["x=1", "y=2", "z=3"]
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 1
        assert scores.fp == 2
        assert scores.fn == 0
        assert scores.precision == 1 / 3
        assert scores.recall == 1.0
        assert abs(scores.f1 - 0.5) < 0.01  # F1 = 0.5

    def test_empty_ground_truth(self):
        """Test F1 with empty ground truth."""
        gt = []
        pred = ["x=1"]
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 0
        assert scores.fp == 1
        assert scores.fn == 0
        assert scores.precision == 0.0
        assert scores.recall == 0.0
        assert scores.f1 == 0.0

    def test_empty_prediction(self):
        """Test F1 with empty prediction."""
        gt = ["x=1"]
        pred = []
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 0
        assert scores.fp == 0
        assert scores.fn == 1
        assert scores.precision == 0.0
        assert scores.recall == 0.0
        assert scores.f1 == 0.0

    def test_both_empty(self):
        """Test F1 with both empty."""
        gt = []
        pred = []
        scores = latex_exact_match_f1(gt, pred)
        assert scores.tp == 0
        assert scores.fp == 0
        assert scores.fn == 0
        assert scores.precision == 0.0
        assert scores.recall == 0.0
        assert scores.f1 == 0.0

    def test_duplicate_expressions(self):
        """Test F1 with duplicate expressions."""
        gt = ["x=1", "x=1"]
        pred = ["x=1"]
        scores = latex_exact_match_f1(gt, pred)
        # Only one x=1 in prediction, so only 1 TP
        assert scores.tp == 1
        assert scores.fp == 0
        assert scores.fn == 1  # Second x=1 in GT is unmatched

    def test_greedy_matching(self):
        """Test that matching is greedy (first match wins)."""
        gt = ["a", "b"]
        pred = ["a", "a"]  # Two 'a's in prediction
        scores = latex_exact_match_f1(gt, pred)
        # First 'a' in pred matches first 'a' in GT
        # Second 'a' in pred has no match (FP)
        # 'b' in GT has no match (FN)
        assert scores.tp == 1
        assert scores.fp == 1
        assert scores.fn == 1


class TestLatexF1Score:
    """Test end-to-end LaTeX F1 score calculation."""

    def test_perfect_match_with_normalization(self):
        """Test perfect match with different formatting."""
        gt = r"Equation $\left( x \right)$ here"
        pred = r"Equation $(x)$ here"
        scores = latex_f1_score(gt, pred)
        # After normalization, both should match
        assert scores.f1 == 1.0
        assert scores.tp == 1

    def test_different_expressions(self):
        """Test with completely different math."""
        gt = "Formula $x = 1$"
        pred = "Formula $y = 2$"
        scores = latex_f1_score(gt, pred)
        assert scores.tp == 0
        assert scores.fp == 1
        assert scores.fn == 1

    def test_missing_expression(self):
        """Test with missing expression in prediction."""
        gt = "Equations $x = 1$ and $y = 2$"
        pred = "Equations $x=1$"
        scores = latex_f1_score(gt, pred)
        assert scores.tp == 1
        assert scores.fn == 1
        assert scores.recall == 0.5

    def test_extra_expression(self):
        """Test with extra expression in prediction."""
        gt = "Equation $x = 1$"
        pred = "Equation $x=1$ and $y=2$"
        scores = latex_f1_score(gt, pred)
        assert scores.tp == 1
        assert scores.fp == 1
        assert scores.precision == 0.5

    def test_no_math(self):
        """Test with no mathematical expressions."""
        gt = "Just plain text"
        pred = "Just plain text"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 0.0
        assert scores.total_gt == 0
        assert scores.total_pred == 0

    def test_complex_document(self):
        """Test with realistic document."""
        gt = r"""
        The quadratic formula is $x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}$.

        In general:
        $$
        \int_0^\infty e^{-x}dx=1
        $$
        """
        pred = r"""
        The quadratic formula is $x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}$.

        In general:
        $$
        \int_0^\infty e^{-x}dx=1
        $$
        """
        scores = latex_f1_score(gt, pred)
        # After normalization, should match
        assert scores.tp == 2
        assert scores.f1 == 1.0

    def test_mixed_delimiters(self):
        r"""Test with different delimiter styles."""
        gt = r"Math: $a$ and \[b\]"
        pred = r"Math: $a$ and $$b$$"
        scores = latex_f1_score(gt, pred)
        # Both have 'a' and 'b', should match
        assert scores.tp == 2
        assert scores.f1 == 1.0

    def test_ordering_matters(self):
        """Test that order of expressions doesn't affect matching."""
        gt = "First $a$ then $b$"
        pred = "First $a$ then $b$"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0

    def test_whitespace_normalization(self):
        """Test that whitespace differences are normalized."""
        gt = r"Equation $\frac{  a  }{  b  }$"
        pred = r"Equation $\frac{a}{b}$"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0

    def test_sizing_command_normalization(self):
        """Test that sizing commands are normalized."""
        gt = r"Formula $\left( \frac{a}{b} \right)$"
        pred = r"Formula $(\frac{a}{b})$"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0


class TestLatexAccuracy:
    """Test simple accuracy metric."""

    def test_accuracy_perfect(self):
        """Test 100% accuracy."""
        gt = "Math $x = 1$ and $y = 2$"
        pred = "Math $x=1$ and $y=2$"
        acc = latex_accuracy(gt, pred)
        assert acc == 1.0

    def test_accuracy_partial(self):
        """Test partial accuracy."""
        gt = "Equations $x = 1$ and $y = 2$ and $z = 3$"
        pred = "Equations $x=1$ and $y=2$"
        # TP=2, FP=0, FN=1, accuracy = 2/(2+0+1) = 2/3
        acc = latex_accuracy(gt, pred)
        assert abs(acc - 2 / 3) < 0.01

    def test_accuracy_no_match(self):
        """Test 0% accuracy."""
        gt = "Equation $x = 1$"
        pred = "Equation $y = 2$"
        # TP=0, FP=1, FN=1, accuracy = 0/(0+1+1) = 0
        acc = latex_accuracy(gt, pred)
        assert acc == 0.0

    def test_accuracy_no_math(self):
        """Test accuracy with no math."""
        gt = "Plain text"
        pred = "Plain text"
        acc = latex_accuracy(gt, pred)
        assert acc == 0.0  # No expressions to match


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_malformed_latex(self):
        """Test handling of malformed LaTeX."""
        # Unbalanced delimiters
        gt = "Equation $x = 1"
        pred = "Equation $x=1$"
        scores = latex_f1_score(gt, pred)
        # Should extract what it can
        assert isinstance(scores, LaTeXF1Scores)

    def test_very_long_expression(self):
        """Test with very long LaTeX expression."""
        long_expr = " + ".join([f"x_{i}" for i in range(100)])
        gt = f"Sum: ${long_expr}$"
        pred = f"Sum: ${long_expr}$"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0

    def test_unicode_in_latex(self):
        """Test LaTeX with Unicode characters."""
        gt = r"Greek: $\alpha+\beta=\gamma$"
        pred = r"Greek: $\alpha+\beta=\gamma$"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0

    def test_nested_structures(self):
        """Test with nested LaTeX structures."""
        gt = r"Formula $\frac{\frac{a}{b}}{\frac{c}{d}}$"
        pred = r"Formula $\frac{\frac{a}{b}}{\frac{c}{d}}$"
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0

    def test_special_characters(self):
        """Test LaTeX with special characters."""
        gt = r"Set: $\{x \mid x>0\}$"
        pred = r"Set: $\{x \mid x>0\}$"
        scores = latex_f1_score(gt, pred)
        # After normalization, should match
        assert scores.f1 == 1.0

    def test_empty_expressions(self):
        """Test with empty LaTeX delimiters."""
        gt = "Empty $$$ here"
        pred = "Empty $$ here"
        # Should handle gracefully
        scores = latex_f1_score(gt, pred)
        assert isinstance(scores, LaTeXF1Scores)


class TestRealWorldDocuments:
    """Test with realistic document examples."""

    def test_academic_paper_excerpt(self):
        """Test with excerpt from academic paper."""
        gt = r"""
        The main result states that for any $\epsilon>0$, there exists
        $N$ such that for all $n>N$:
        $$
        \left|\frac{1}{n}\sum_{i=1}^n x_i-\mu\right|<\epsilon
        $$
        This follows from the law of large numbers.
        """
        pred = r"""
        The main result states that for any $\epsilon>0$, there exists
        $N$ such that for all $n>N$:
        $$
        |\frac{1}{n}\sum_{i=1}^n x_i-\mu|<\epsilon
        $$
        This follows from the law of large numbers.
        """
        scores = latex_f1_score(gt, pred)
        # Should match after normalization (4 expressions total)
        assert scores.tp == 4  # $\epsilon>0$, $N$, $n>N$, and the display math
        assert scores.f1 == 1.0

    def test_physics_equations(self):
        """Test with physics equations."""
        gt = r"""
        Einstein's equation: $E = mc^2$
        Schrödinger equation: $i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi$
        """
        pred = r"""
        Einstein's equation: $E=mc^2$
        Schrödinger equation: $i\hbar\frac{\partial}{\partial t}\Psi=\hat{H}\Psi$
        """
        scores = latex_f1_score(gt, pred)
        assert scores.f1 == 1.0

    def test_math_textbook(self):
        """Test with math textbook style content."""
        gt = r"""
        **Theorem 1.1**: For all $x,y\in\mathbb{R}$,
        $$
        (x+y)^2=x^2+2xy+y^2
        $$
        **Proof**: By direct expansion.
        """
        pred = r"""
        **Theorem 1.1**: For all $x,y\in\mathbb{R}$,
        $$
        (x+y)^2=x^2+2xy+y^2
        $$
        **Proof**: By direct expansion.
        """
        scores = latex_f1_score(gt, pred)
        assert scores.tp == 2  # Both expressions match
        assert scores.f1 == 1.0  # Perfect match

    def test_missing_some_math(self):
        """Test when prediction misses some expressions."""
        gt = r"""
        Three equations: $a=1$, $b=2$, and $c=3$.
        """
        pred = r"""
        Three equations: $a=1$, $b=2$, and c=3.
        """
        scores = latex_f1_score(gt, pred)
        assert scores.tp == 2
        assert scores.fn == 1
        assert scores.recall < 1.0

    def test_hallucinated_math(self):
        """Test when prediction adds extra expressions."""
        gt = "One equation: $x = 1$"
        pred = "One equation: $x=1$ and also $y=2$ and $z=3$"
        scores = latex_f1_score(gt, pred)
        assert scores.tp == 1
        assert scores.fp == 2
        assert scores.precision < 1.0
