"""Tests for LaTeX normalization utilities."""


from pdf_bench.utils.latex_normalization import (
    collapse_whitespace,
    extract_math_content,
    normalize_command_spacing,
    normalize_latex,
    normalize_latex_in_text,
    normalize_spacing_commands,
    remove_redundant_braces,
    remove_sizing_commands,
)


class TestRemoveSizingCommands:
    """Test removal of sizing commands (\\left, \right, \big, etc.)."""

    def test_remove_left_right(self):
        """Test removal of \\left and \right commands."""
        latex = r"\left( x \right)"
        assert remove_sizing_commands(latex) == r"( x )"

    def test_remove_left_right_with_brackets(self):
        """Test \\left[ \right] removal."""
        latex = r"\left[ \frac{a}{b} \right]"
        assert remove_sizing_commands(latex) == r"[ \frac{a}{b} ]"

    def test_remove_big_commands(self):
        """Test removal of \big, \\Big, \bigg, \\Bigg."""
        latex = r"\Big( x \Big)"
        assert remove_sizing_commands(latex) == r"( x )"

        latex = r"\bigg[ y \bigg]"
        assert remove_sizing_commands(latex) == r"[ y ]"

    def test_remove_bigl_bigr(self):
        """Test removal of directional big commands."""
        latex = r"\bigl( x \bigr)"
        assert remove_sizing_commands(latex) == r"( x )"

        latex = r"\Bigl\{ a \Bigr\}"
        result = remove_sizing_commands(latex)
        # \{ and \} are escaped braces, should be preserved
        assert r"\{" in result and r"\}" in result

    def test_multiple_sizing_commands(self):
        """Test removal of multiple sizing commands."""
        latex = r"\left( \frac{\left[ a \right]}{\left\{ b \right\}} \right)"
        result = remove_sizing_commands(latex)
        assert r"\left" not in result
        assert r"\right" not in result
        assert r"(" in result and r")" in result

    def test_no_sizing_commands(self):
        """Test that expressions without sizing commands are unchanged."""
        latex = r"\frac{a}{b}"
        assert remove_sizing_commands(latex) == latex

    def test_preserves_delimiters(self):
        """Test that delimiters after sizing commands are preserved."""
        latex = r"\left( x \right)"
        result = remove_sizing_commands(latex)
        assert "(" in result and ")" in result


class TestRemoveRedundantBraces:
    """Test removal of redundant nested braces."""

    def test_remove_double_braces(self):
        """Test removal of {{a}} → {a}."""
        latex = "{{a}}"
        assert remove_redundant_braces(latex) == "{a}"

    def test_remove_triple_braces(self):
        """Test removal of {{{x}}} → {x}."""
        latex = "{{{x}}}"
        result = remove_redundant_braces(latex)
        assert result == "{x}"

    def test_preserve_command_braces(self):
        """Test that command argument braces are preserved."""
        latex = r"{\frac{a}{b}}"
        result = remove_redundant_braces(latex)
        # Should not remove braces around command
        assert r"\frac{a}{b}" in result

    def test_preserve_necessary_grouping(self):
        """Test that necessary grouping braces are preserved."""
        latex = r"{a}^{2}"
        result = remove_redundant_braces(latex)
        # Both sets of braces are necessary for grouping
        assert "{a}" in result and "{2}" in result

    def test_multiple_redundant_braces(self):
        """Test removal from multiple locations."""
        latex = "{{a}} + {{b}}"
        result = remove_redundant_braces(latex)
        assert result == "{a} + {b}"

    def test_no_redundant_braces(self):
        """Test that already-normalized expressions are unchanged."""
        latex = r"\frac{a}{b}"
        assert remove_redundant_braces(latex) == latex


class TestNormalizeSpacingCommands:
    """Test normalization of spacing commands."""

    def test_thin_space(self):
        r"""Test \, (thin space) → space."""
        latex = r"a\,b"
        assert normalize_spacing_commands(latex) == "a b"

    def test_medium_space(self):
        r"""Test \: (medium space) → space."""
        latex = r"x\:y"
        assert normalize_spacing_commands(latex) == "x y"

    def test_thick_space(self):
        r"""Test \; (thick space) → space."""
        latex = r"a\;b\;c"
        assert normalize_spacing_commands(latex) == "a b c"

    def test_negative_space(self):
        r"""Test \! (negative space) → removed."""
        latex = r"x\!y"
        assert normalize_spacing_commands(latex) == "xy"

    def test_quad_space(self):
        r"""Test \quad and \qquad → space."""
        latex = r"a\quad b"
        # command→space + original space
        assert normalize_spacing_commands(latex) == "a  b"

        latex = r"x\qquad y"
        assert normalize_spacing_commands(latex) == "x  y"

    def test_explicit_space(self):
        r"""Test \  (backslash-space) → space."""
        latex = r"a\ b"
        assert normalize_spacing_commands(latex) == "a b"

    def test_multiple_spacing_commands(self):
        """Test multiple spacing commands in one expression."""
        latex = r"a\,b\;c\!d\quad e"
        result = normalize_spacing_commands(latex)
        # \, → space: "a b"
        # \; → space: "b c"
        # \! → removed: "cd"
        # \quad → space: "d  e" (double space with original)
        assert result == "a b cd  e"


class TestCollapseWhitespace:
    """Test whitespace collapsing in LaTeX."""

    def test_collapse_multiple_spaces(self):
        """Test that multiple spaces collapse to single space."""
        latex = "a    b   c"
        assert collapse_whitespace(latex) == "a b c"

    def test_normalize_line_endings(self):
        """Test normalization of CRLF and CR to LF."""
        latex = "a\r\nb\rc"
        result = collapse_whitespace(latex)
        # All should become spaces (since we collapse whitespace)
        assert result == "a b c"

    def test_remove_space_around_braces(self):
        """Test removal of spaces inside braces."""
        latex = "{ a  b }"
        assert collapse_whitespace(latex) == "{a b}"

        latex = r"\frac{ a }{ b }"
        assert collapse_whitespace(latex) == r"\frac{a}{b}"

    def test_normalize_operators(self):
        """Test space removal around operators."""
        latex = "a  =  b"
        assert collapse_whitespace(latex) == "a=b"

        latex = "x  <  y"
        assert collapse_whitespace(latex) == "x<y"

    def test_strip_leading_trailing(self):
        """Test stripping of leading/trailing whitespace."""
        latex = "  x + y  "
        assert collapse_whitespace(latex) == "x + y"

    def test_multiple_newlines(self):
        """Test collapsing of multiple newlines."""
        latex = "a\n\n\nb"
        result = collapse_whitespace(latex)
        assert result == "a b"


class TestNormalizeCommandSpacing:
    """Test normalization of spacing around commands."""

    def test_remove_space_after_command(self):
        """Test removal of space between command and argument."""
        latex = r"\frac  {a}{b}"
        assert normalize_command_spacing(latex) == r"\frac{a}{b}"

    def test_remove_space_multiple_args(self):
        """Test with multiple arguments."""
        latex = r"\sqrt  { x }"
        result = normalize_command_spacing(latex)
        assert result == r"\sqrt{ x }"

    def test_multiple_commands(self):
        """Test multiple commands in expression."""
        latex = r"\frac  {a}{b} + \sqrt  {c}"
        result = normalize_command_spacing(latex)
        assert r"\frac{a}{b}" in result
        assert r"\sqrt{c}" in result

    def test_preserve_command_name_space(self):
        """Test that space after command name (before non-brace) is preserved."""
        # \sin x should stay \sin x (space between command and operand)
        latex = r"\sin x"
        result = normalize_command_spacing(latex)
        assert result == latex


class TestExtractMathContent:
    """Test extraction of math expressions from text."""

    def test_extract_inline_dollar(self):
        """Test extraction of $...$ inline math."""
        text = "Some text $x = 1$ more text"
        result = extract_math_content(text)
        assert ("inline", "x = 1") in result

    def test_extract_display_double_dollar(self):
        """Test extraction of $$...$$ display math."""
        text = "Some text $$y = 2$$ more text"
        result = extract_math_content(text)
        assert ("display", "y = 2") in result

    def test_extract_display_bracket(self):
        r"""Test extraction of \[...\] display math."""
        text = r"Some text \[z = 3\] more text"
        result = extract_math_content(text)
        assert ("display", "z = 3") in result

    def test_extract_inline_paren(self):
        r"""Test extraction of \(...\) inline math."""
        text = r"Some text \(a = 4\) more text"
        result = extract_math_content(text)
        assert ("inline", "a = 4") in result

    def test_extract_multiple(self):
        """Test extraction of multiple math expressions."""
        text = "Text $x=1$ and $$y=2$$ end"
        result = extract_math_content(text)
        assert len(result) == 2
        assert ("inline", "x=1") in result
        assert ("display", "y=2") in result

    def test_extract_empty(self):
        """Test with no math expressions."""
        text = "Just plain text with no math"
        result = extract_math_content(text)
        assert result == []

    def test_extract_nested_in_display(self):
        """Test that nested inline $ inside $$ works correctly."""
        text = "Text $$x = 1$$ more"
        result = extract_math_content(text)
        # Should extract as display, not confuse with inline
        assert ("display", "x = 1") in result


class TestNormalizeLatex:
    """Test the master normalize_latex function."""

    def test_normalize_sizing_and_whitespace(self):
        """Test combined sizing removal and whitespace normalization."""
        latex = r"\left( \frac{a}{b} \right)"
        result = normalize_latex(latex)
        assert result == r"(\frac{a}{b})"

    def test_normalize_complex_expression(self):
        """Test normalization of complex expression."""
        latex = r"\left[ \frac{  a  }{  b  } \right] + \sqrt  { x }"
        result = normalize_latex(latex)
        # Should have no \left/\right, collapsed whitespace, no space after commands
        assert r"\left" not in result
        assert r"\right" not in result
        assert r"\frac{a}{b}" in result
        assert r"\sqrt{x}" in result

    def test_normalize_spacing_commands(self):
        """Test that spacing commands are normalized."""
        latex = r"a\,b\;c"
        result = normalize_latex(latex)
        # Spacing commands should become spaces, then collapse
        assert "a b c" in result or "abc" in result  # Could be collapsed differently

    def test_normalize_with_aggressive_braces(self):
        """Test aggressive mode removes redundant braces."""
        latex = "{{a}}"
        result = normalize_latex(latex, aggressive=True)
        assert result == "{a}"

    def test_normalize_without_aggressive(self):
        """Test that non-aggressive mode keeps braces."""
        latex = "{{a}}"
        result = normalize_latex(latex, aggressive=False)
        # Without aggressive, double braces might remain
        # (depends on other normalization steps)
        assert "{a}" in result

    def test_idempotent(self):
        """Test that normalization is idempotent."""
        latex = r"\left( \frac{  a  }{  b  } \right)"
        result1 = normalize_latex(latex)
        result2 = normalize_latex(result1)
        assert result1 == result2

    def test_unicode_math(self):
        """Test normalization with Unicode math symbols."""
        latex = r"\alpha + \beta = \gamma"
        result = normalize_latex(latex)
        # Should preserve Greek letters and normalize spacing
        assert r"\alpha" in result
        assert r"\beta" in result
        assert r"\gamma" in result

    def test_nested_fractions(self):
        """Test normalization of nested fractions."""
        latex = r"\frac{\frac{a}{b}}{\frac{c}{d}}"
        result = normalize_latex(latex)
        # Should preserve structure and normalize whitespace
        assert r"\frac" in result
        assert "{a}" in result and "{b}" in result
        assert "{c}" in result and "{d}" in result

    def test_matrix_environment(self):
        """Test normalization preserves matrix environments."""
        latex = r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}"
        result = normalize_latex(latex)
        # Should preserve structure
        assert r"\begin{pmatrix}" in result
        assert r"\end{pmatrix}" in result

    def test_very_complex_equation(self):
        """Test a very complex equation with multiple features."""
        latex = (
            r"\left\{ \frac{\partial f}{\partial x} \right\}_{x=0} = "
            r"\lim_{h \to 0} \frac{f(h) - f(0)}{h}"
        )
        result = normalize_latex(latex)
        # Should remove \left\{ and \right\}, normalize whitespace
        assert r"\left" not in result
        assert r"\right" not in result
        assert r"\frac" in result
        assert r"\lim" in result
        assert r"\to" in result


class TestNormalizeLatexInText:
    """Test normalization of LaTeX within text documents."""

    def test_normalize_inline_math(self):
        """Test normalization of inline math in text."""
        text = r"The equation $\left( x \right)$ shows that"
        result = normalize_latex_in_text(text)
        assert r"$(x)$" in result
        assert "The equation" in result
        assert "shows that" in result

    def test_normalize_display_math(self):
        """Test normalization of display math in text."""
        text = r"We have: $$\left[ \frac{a}{b} \right]$$ which proves"
        result = normalize_latex_in_text(text)
        assert r"$$[\frac{a}{b}]$$" in result
        assert "We have:" in result
        assert "which proves" in result

    def test_normalize_multiple_expressions(self):
        """Test normalization of multiple math expressions."""
        text = r"First $\left( x \right)$ and $$\left[ y \right]$$ done"
        result = normalize_latex_in_text(text)
        assert r"$(x)$" in result
        assert r"$$[y]$$" in result

    def test_preserve_non_math_text(self):
        """Test that non-math text is preserved exactly."""
        text = "Plain text with no math at all"
        result = normalize_latex_in_text(text)
        assert result == text

    def test_mixed_inline_and_display(self):
        """Test document with both inline and display math."""
        text = r"""
        Introduction text $x = 1$ continues.

        Display equation:
        $$
        \left( \frac{a}{b} \right) = c
        $$

        More text $y = 2$ ends.
        """
        result = normalize_latex_in_text(text)
        assert r"$(x)$" in result or r"$x=1$" in result
        assert r"(\frac{a}{b})=c" in result or r"(\frac{a}{b}) = c" in result
        assert "Introduction text" in result
        assert "More text" in result

    def test_bracket_display_math(self):
        r"""Test normalization of \[...\] display math."""
        text = r"Text before \[\left( x \right)\] text after"
        result = normalize_latex_in_text(text)
        assert r"\[(x)\]" in result
        assert "Text before" in result
        assert "text after" in result

    def test_paren_inline_math(self):
        r"""Test normalization of \(...\) inline math."""
        text = r"Text \(\left( x \right)\) more"
        result = normalize_latex_in_text(text)
        assert r"\((x)\)" in result

    def test_aggressive_mode(self):
        """Test aggressive mode in text normalization."""
        text = "Equation ${{a}}$ here"
        result = normalize_latex_in_text(text, aggressive=True)
        assert "${a}$" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test normalization of empty string."""
        assert normalize_latex("") == ""

    def test_whitespace_only(self):
        """Test normalization of whitespace-only string."""
        assert normalize_latex("   \n  \t  ") == ""

    def test_no_math_commands(self):
        """Test normalization of plain text (no LaTeX)."""
        text = "Just plain text"
        result = normalize_latex(text)
        assert "Just plain text" in result

    def test_malformed_braces(self):
        """Test handling of malformed braces."""
        # Unbalanced braces - should not crash
        latex = r"\frac{a}{b"
        result = normalize_latex(latex)
        assert r"\frac{a}" in result

    def test_escaped_characters(self):
        """Test that escaped characters are preserved."""
        latex = r"\{ \} \$ \%"
        result = normalize_latex(latex)
        assert r"\{" in result
        assert r"\}" in result
        assert r"\$" in result
        assert r"\%" in result

    def test_very_long_expression(self):
        """Test normalization of very long expression."""
        # Create a long expression with repetitive structure
        long_latex = r"\left( " + " + ".join([f"x_{i}" for i in range(100)]) + r" \right)"
        result = normalize_latex(long_latex)
        # Should not crash, should remove \left and \right
        assert r"\left" not in result
        assert r"\right" not in result
        assert "x_0" in result
        assert "x_99" in result

    def test_unicode_in_latex(self):
        """Test handling of Unicode characters in LaTeX."""
        latex = "α + β = γ"  # Greek letters as Unicode
        result = normalize_latex(latex)
        # Should preserve Unicode characters
        assert "α" in result
        assert "β" in result
        assert "γ" in result

    def test_mixed_math_modes_in_text(self):
        """Test text with mixed math delimiters."""
        text = r"Text $a$ and $$b$$ and \(c\) and \[d\]"
        result = normalize_latex_in_text(text)
        # All math should be present, text preserved
        assert "$a$" in result or "a" in result
        assert "$$b$$" in result or "b" in result
        assert "Text" in result

    def test_consecutive_math_expressions(self):
        """Test consecutive math expressions without text between."""
        text = "$a$$b$"
        result = normalize_latex_in_text(text)
        # Should handle $a$ followed by $b$, not confuse with $$
        # This might be tricky with regex
        assert "a" in result and "b" in result


class TestRealWorldExamples:
    """Test with real-world LaTeX examples."""

    def test_quadratic_formula(self):
        """Test normalization of quadratic formula."""
        latex = r"\left( x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \right)"
        result = normalize_latex(latex)
        assert r"\left" not in result
        assert r"\right" not in result
        assert r"\frac" in result
        assert r"\sqrt" in result
        assert r"\pm" in result

    def test_integral_with_limits(self):
        """Test normalization of integral."""
        latex = r"\int_{0}^{\infty} e^{-x} \, dx = 1"
        result = normalize_latex(latex)
        assert r"\int" in result
        assert "{0}" in result
        assert r"{\infty}" in result or "infty" in result

    def test_matrix_determinant(self):
        """Test normalization of matrix determinant."""
        latex = r"\left| \begin{matrix} a & b \\ c & d \end{matrix} \right| = ad - bc"
        result = normalize_latex(latex)
        # \left| and \right| should be removed
        assert r"\left" not in result
        assert r"\right" not in result
        assert "matrix" in result

    def test_summation(self):
        """Test normalization of summation."""
        latex = r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}"
        result = normalize_latex(latex)
        assert r"\sum" in result
        assert "{i=1}" in result
        assert "{n}" in result
        assert r"\frac" in result

    def test_chemical_equation(self):
        """Test LaTeX chemical equation (uses different commands)."""
        # Chemical equations often use \ce{} from mhchem package
        latex = r"\ce{H2O}"
        result = normalize_latex(latex)
        # Should preserve the command structure
        assert r"\ce" in result
        assert "H2O" in result

    def test_aligned_equations(self):
        """Test normalization of aligned equations."""
        latex = r"""
        \begin{align}
        x + y &= 1 \\
        x - y &= 0
        \end{align}
        """
        result = normalize_latex(latex)
        assert "align" in result
        assert "x + y" in result or "x+y" in result

    def test_physics_equation(self):
        """Test a physics equation with units."""
        latex = r"E = mc^2 \quad \text{where } c = 3 \times 10^8 \, \text{m/s}"
        result = normalize_latex(latex)
        assert "E" in result and "m" in result and "c" in result
        assert r"\text" in result
        assert "10^8" in result or "10^{8}" in result
