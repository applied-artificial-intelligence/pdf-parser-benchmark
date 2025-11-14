r"""LaTeX normalization utilities for fair comparison of mathematical expressions.

This module provides functions to normalize LaTeX expressions before comparing
them. Normalization handles common variations in LaTeX formatting that don't
affect the mathematical meaning.

The normalization pipeline handles:
- Whitespace collapsing within commands and expressions
- Removal of sizing commands (\left, \right, \big, \Big, etc.)
- Removal of redundant braces {{a}} → {a}
- Normalization of command formatting
- Handling both inline ($...$) and display ($$...$$, \[...\]) math modes

Example:
    >>> from pdf_bench.utils.latex_normalization import normalize_latex
    >>> latex = r"\left( \frac{a}{b} \right)"
    >>> normalize_latex(latex)
    '(\\frac{a}{b})'
"""

import re
from typing import Final

# Sizing commands to remove (they don't affect mathematical meaning)
_SIZING_COMMANDS: Final[list[str]] = [
    r"\\left",
    r"\\right",
    r"\\big",
    r"\\Big",
    r"\\bigg",
    r"\\Bigg",
    r"\\bigl",
    r"\\bigr",
    r"\\Bigl",
    r"\\Bigr",
    r"\\biggl",
    r"\\biggr",
    r"\\Biggl",
    r"\\Biggr",
]

# Additional spacing commands to remove or normalize
_SPACING_COMMANDS: Final[dict[str, str]] = {
    r"\,": " ",  # thin space → space
    r"\:": " ",  # medium space → space
    r"\;": " ",  # thick space → space
    r"\!": "",  # negative thin space → removed
    r"\quad": " ",  # quad space → space
    r"\qquad": " ",  # double quad → space
    r"\ ": " ",  # explicit space → space
}


def remove_sizing_commands(latex: str) -> str:
    r"""Remove sizing commands from LaTeX expressions.

    Sizing commands like \left, \right, \big, \Big, etc. affect visual
    appearance but not mathematical meaning. Removing them allows fair
    comparison of mathematically equivalent expressions.

    Args:
        latex: Input LaTeX string

    Returns:
        LaTeX with sizing commands removed

    Example:
        >>> remove_sizing_commands(r"\left( x \right)")
        '( x )'
        >>> remove_sizing_commands(r"\Big[ \frac{a}{b} \Big]")
        '[ \\frac{a}{b} ]'
    """
    result = latex
    for cmd in _SIZING_COMMANDS:
        # Remove the command, preserving any following delimiter
        result = re.sub(cmd + r"(?=\s|\W|$)", "", result)
    return result


def remove_redundant_braces(latex: str) -> str:
    """Remove redundant nested braces from LaTeX expressions.

    Reduces multiple levels of braces to single level where appropriate:
    - {{a}} → {a}
    - {{{x}}} → {x}

    However, preserves necessary braces:
    - {\frac{a}{b}} → {\frac{a}{b}} (command argument)
    - {a}^{2} → {a}^{2} (grouping for superscript)

    Args:
        latex: Input LaTeX string

    Returns:
        LaTeX with redundant braces removed

    Example:
        >>> remove_redundant_braces("{{a}}")
        '{a}'
        >>> remove_redundant_braces("{{{x}}}")
        '{x}'
        >>> remove_redundant_braces(r"{\frac{a}{b}}")
        '{\\frac{a}{b}}'
    """
    # Repeatedly remove redundant double braces until no more can be removed
    # This handles cases like {{{a}}} → {{a}} → {a}
    prev = ""
    result = latex
    max_iterations = 10  # Safety limit to prevent infinite loops

    for _ in range(max_iterations):
        if result == prev:
            break
        prev = result

        # Pattern: {{ followed by content followed by }}
        # But only if the content doesn't contain balanced braces that would break
        # We use a simple approach: remove {{<non-brace>}} first
        result = re.sub(r"\{\{([^{}]+)\}\}", r"{\1}", result)

    # Second pass: handle nested cases more carefully
    # Replace {<single-token>} patterns where token doesn't need grouping
    # For now, keep it simple and just handle the obvious {{...}} cases
    # More sophisticated brace removal would need proper LaTeX parsing

    return result


def normalize_spacing_commands(latex: str) -> str:
    r"""Normalize LaTeX spacing commands to standard spaces.

    Converts various spacing commands to standard spaces or removes them:
    - \,, \:, \; → space
    - \!, negative space → removed
    - \quad, \qquad → space
    - \  (explicit space) → space

    Args:
        latex: Input LaTeX string

    Returns:
        LaTeX with normalized spacing

    Example:
        >>> normalize_spacing_commands(r"a\,b\;c")
        'a b c'
        >>> normalize_spacing_commands(r"x\!y")
        'xy'
    """
    result = latex
    for cmd, replacement in _SPACING_COMMANDS.items():
        result = result.replace(cmd, replacement)
    return result


def collapse_whitespace(latex: str) -> str:
    """Collapse multiple spaces and normalize whitespace in LaTeX.

    This function:
    1. Normalizes line endings (CRLF, CR → LF)
    2. Collapses multiple spaces to single space
    3. Removes spaces around braces and operators (except where needed)
    4. Strips leading/trailing whitespace

    Note: This is less aggressive than general text whitespace normalization,
    as LaTeX has specific spacing rules.

    Args:
        latex: Input LaTeX string

    Returns:
        LaTeX with normalized whitespace

    Example:
        >>> collapse_whitespace("a    b   c")
        'a b c'
        >>> collapse_whitespace("{ a  b }")
        '{a b}'
    """
    # Normalize line endings
    latex = latex.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple spaces to single space
    latex = re.sub(r" +", " ", latex)

    # Collapse multiple newlines/whitespace to single space
    latex = re.sub(r"\s+", " ", latex)

    # Remove spaces after opening braces/brackets/parens and before closing ones
    latex = re.sub(r"\{\s+", "{", latex)
    latex = re.sub(r"\s+\}", "}", latex)
    latex = re.sub(r"\[\s+", "[", latex)
    latex = re.sub(r"\s+\]", "]", latex)
    latex = re.sub(r"\(\s+", "(", latex)
    latex = re.sub(r"\s+\)", ")", latex)

    # Remove spaces around common operators (but preserve in commands)
    # Be careful not to break command names like \operatorname
    latex = re.sub(r"\s*=\s*", "=", latex)
    latex = re.sub(r"\s*<\s*", "<", latex)
    latex = re.sub(r"\s*>\s*", ">", latex)

    # Strip leading/trailing whitespace
    latex = latex.strip()

    return latex


def normalize_command_spacing(latex: str) -> str:
    r"""Normalize spacing around LaTeX commands.

    Ensures consistent spacing after command names:
    - \frac  {a}{b} → \frac{a}{b}
    - \sqrt  { x } → \sqrt{x}

    Args:
        latex: Input LaTeX string

    Returns:
        LaTeX with normalized command spacing

    Example:
        >>> normalize_command_spacing(r"\frac  {a}{b}")
        '\\frac{a}{b}'
        >>> normalize_command_spacing(r"\sqrt  { x }")
        '\\sqrt{x}'
    """
    # Remove spaces between command and its first argument
    # Pattern: \commandname followed by spaces followed by {
    latex = re.sub(r"(\\[a-zA-Z]+)\s+(?=\{)", r"\1", latex)

    # Also handle commands followed by non-letter (e.g., \sin x)
    # but preserve the space (e.g., \sin x should stay \sin x)

    return latex


def extract_math_content(text: str) -> list[tuple[str, str]]:
    r"""Extract mathematical expressions from text.

    Identifies and extracts both inline and display math from text:
    - Inline: $...$ or \(...\)
    - Display: $$...$$ or \[...\]

    Args:
        text: Input text containing LaTeX math

    Returns:
        List of (mode, content) tuples where mode is 'inline' or 'display'

    Example:
        >>> extract_math_content("Some text $x = 1$ and $$y = 2$$")
        [('inline', 'x = 1'), ('display', 'y = 2')]
    """
    math_expressions: list[tuple[str, str]] = []

    # Extract display math first ($$...$$ and \[...\])
    # Display math with $$...$$
    for match in re.finditer(r"\$\$(.*?)\$\$", text, re.DOTALL):
        math_expressions.append(("display", match.group(1)))

    # Display math with \[...\]
    for match in re.finditer(r"\\\[(.*?)\\\]", text, re.DOTALL):
        math_expressions.append(("display", match.group(1)))

    # Extract inline math ($...$ and \(...\))
    # Inline math with $...$, but not $$
    for match in re.finditer(r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)", text, re.DOTALL):
        math_expressions.append(("inline", match.group(1)))

    # Inline math with \(...\)
    for match in re.finditer(r"\\\((.*?)\\\)", text, re.DOTALL):
        math_expressions.append(("inline", match.group(1)))

    return math_expressions


def normalize_latex(latex: str, *, aggressive: bool = False) -> str:
    r"""Master normalization function for LaTeX expressions.

    Applies all LaTeX normalizations in the correct order:
    1. Remove sizing commands (\left, \right, etc.)
    2. Normalize spacing commands
    3. Normalize command spacing
    4. Collapse whitespace
    5. Remove redundant braces (if aggressive=True)

    The function is designed to be idempotent: applying it multiple times
    produces the same result as applying it once.

    Args:
        latex: Input LaTeX string or text containing LaTeX
        aggressive: If True, applies more aggressive normalization including
                   redundant brace removal. Default is False for safety.

    Returns:
        Normalized LaTeX expression

    Example:
        >>> normalize_latex(r"\left( \frac{a}{b} \right)")
        '(\\frac{a}{b})'
        >>> normalize_latex(r"\frac  { a }{ b }")
        '\\frac{a}{b}'
        >>> normalize_latex("{{a}}", aggressive=True)
        '{a}'
    """
    result = latex

    # 1. Remove sizing commands
    result = remove_sizing_commands(result)

    # 2. Normalize spacing commands
    result = normalize_spacing_commands(result)

    # 3. Normalize command spacing
    result = normalize_command_spacing(result)

    # 4. Collapse whitespace
    result = collapse_whitespace(result)

    # 5. Remove redundant braces (optional, can be risky)
    if aggressive:
        result = remove_redundant_braces(result)

    return result


def normalize_latex_in_text(text: str, *, aggressive: bool = False) -> str:
    """Normalize all LaTeX expressions within a text document.

    Finds all inline and display math expressions in the text and normalizes
    them while preserving the surrounding text unchanged.

    Args:
        text: Input text containing LaTeX math expressions
        aggressive: If True, applies aggressive normalization. Default False.

    Returns:
        Text with all LaTeX expressions normalized

    Example:
        >>> text = "The equation $\\\\left( x \\\\right)$ shows that"
        >>> normalize_latex_in_text(text)
        'The equation $(x)$ shows that'
    """
    result = text

    # Replace $$...$$ display math
    def replace_display_double(match: re.Match[str]) -> str:
        normalized = normalize_latex(match.group(1), aggressive=aggressive)
        return f"$${normalized}$$"

    result = re.sub(r"\$\$(.*?)\$\$", replace_display_double, result, flags=re.DOTALL)

    # Replace \[...\] display math
    def replace_display_bracket(match: re.Match[str]) -> str:
        normalized = normalize_latex(match.group(1), aggressive=aggressive)
        return f"\\[{normalized}\\]"

    result = re.sub(r"\\\[(.*?)\\\]", replace_display_bracket, result, flags=re.DOTALL)

    # Replace $...$ inline math (but not $$)
    def replace_inline_dollar(match: re.Match[str]) -> str:
        normalized = normalize_latex(match.group(1), aggressive=aggressive)
        return f"${normalized}$"

    result = re.sub(
        r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)",
        replace_inline_dollar,
        result,
        flags=re.DOTALL,
    )

    # Replace \(...\) inline math
    def replace_inline_paren(match: re.Match[str]) -> str:
        normalized = normalize_latex(match.group(1), aggressive=aggressive)
        return f"\\({normalized}\\)"

    result = re.sub(r"\\\((.*?)\\\)", replace_inline_paren, result, flags=re.DOTALL)

    return result
