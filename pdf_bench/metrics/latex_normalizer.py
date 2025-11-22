"""Normalize LaTeX equations for semantic comparison.

Treats semantically equivalent LaTeX commands as identical:
- \\textbf{x} == \\mathbf{x} (both mean bold)
- \\dfrac{a}{b} == \\frac{a}{b} (both mean fraction)
- \\Biggl( == \\Bigg( (both mean big parenthesis)
- Extra whitespace, braces, etc.
"""

import re
from typing import List, Tuple


def normalize_latex(latex: str) -> str:
    """
    Normalize LaTeX code to canonical form for comparison.

    Handles:
    - Command equivalents (\\textbf → \\mathbf)
    - Size commands (\\dfrac → \\frac, \\Biggl → \\Big)
    - Whitespace normalization
    - Brace simplification
    """
    # Remove comments
    latex = re.sub(r'%.*$', '', latex, flags=re.MULTILINE)

    # Normalize bold commands
    latex = re.sub(r'\\textbf\{', r'\\mathbf{', latex)
    latex = re.sub(r'\\text\{\\bf\s+', r'\\mathbf{', latex)

    # Normalize fraction commands
    latex = re.sub(r'\\dfrac', r'\\frac', latex)
    latex = re.sub(r'\\tfrac', r'\\frac', latex)

    # Normalize delimiter sizes (all → \\big)
    for size in ['Bigg', 'bigg', 'Big', 'big']:
        latex = re.sub(rf'\\{size}l\(', r'\\big(', latex)
        latex = re.sub(rf'\\{size}r\)', r'\\big)', latex)
        latex = re.sub(rf'\\{size}l\[', r'\\big[', latex)
        latex = re.sub(rf'\\{size}r\]', r'\\big]', latex)
        latex = re.sub(rf'\\{size}\(', r'\\big(', latex)
        latex = re.sub(rf'\\{size}\)', r'\\big)', latex)
        latex = re.sub(rf'\\{size}\[', r'\\big[', latex)
        latex = re.sub(rf'\\{size}\]', r'\\big]', latex)

    # Normalize spacing commands
    latex = re.sub(r'\\,', ' ', latex)  # thin space
    latex = re.sub(r'\\:', ' ', latex)  # medium space
    latex = re.sub(r'\\;', ' ', latex)  # thick space
    latex = re.sub(r'\\quad', ' ', latex)
    latex = re.sub(r'\\qquad', ' ', latex)
    latex = re.sub(r'\\indent', '', latex)
    latex = re.sub(r'\\hspace\{[^}]*\}', '', latex)
    latex = re.sub(r'\\vspace\{[^}]*\}', '', latex)

    # Normalize text commands
    latex = re.sub(r'\\text\{([^}]*)\}', r'\1', latex)
    latex = re.sub(r'\\mathrm\{', r'\\text{', latex)

    # Normalize whitespace
    latex = re.sub(r'\s+', ' ', latex)  # Multiple spaces → single
    latex = re.sub(r'\s*\^\s*', '^', latex)  # Spaces around ^
    latex = re.sub(r'\s*_\s*', '_', latex)  # Spaces around _
    latex = re.sub(r'\{\s+', '{', latex)  # Space after {
    latex = re.sub(r'\s+\}', '}', latex)  # Space before }

    # Normalize operators (add space around operators for consistency)
    latex = re.sub(r'\s*([+\-=])\s*', r' \1 ', latex)  # Space around +, -, =
    latex = re.sub(r'\s+', ' ', latex)  # Clean up multiple spaces again

    # Remove unnecessary braces
    # {x} → x when not needed (but keep for commands)
    latex = re.sub(r'(?<!\\[a-zA-Z])\{([a-zA-Z0-9])\}', r'\1', latex)

    # Normalize operatorname
    latex = re.sub(r'\\operatorname\{', r'\\text{', latex)

    return latex.strip()


def extract_equations(markdown: str) -> Tuple[List[str], List[str]]:
    """
    Extract display and inline equations from markdown.

    Returns:
        (display_equations, inline_equations)
    """
    # Extract display equations $$...$$
    display = re.findall(r'\$\$(.+?)\$\$', markdown, flags=re.DOTALL)

    # Extract inline equations $...$
    # But not $$...$$ (already captured)
    inline = re.findall(r'(?<!\$)\$([^\$]+?)\$(?!\$)', markdown)

    return display, inline


def strip_equations(markdown: str) -> str:
    """
    Remove all equations from markdown, leaving only prose.
    """
    # Remove display equations
    text = re.sub(r'\$\$.*?\$\$', '', markdown, flags=re.DOTALL)

    # Remove inline equations
    text = re.sub(r'(?<!\$)\$[^\$]+?\$(?!\$)', '', text)

    return text


def normalize_prose(text: str) -> str:
    """
    Normalize prose text for comparison.

    - Lowercase
    - Remove extra whitespace
    - Remove punctuation variations
    """
    # Remove YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)

    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Code

    # Normalize headers (remove # symbols)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Lowercase for comparison
    text = text.lower()

    return text.strip()


def compare_equations(ground_truth: str, parser_output: str) -> dict:
    """
    Compare equations between ground truth and parser output.

    Returns metrics:
        - display_match_rate: % of display equations that match
        - inline_match_rate: % of inline equations that match
        - display_extraction_rate: % of display equations found
        - inline_extraction_rate: % of inline equations found
    """
    gt_display, gt_inline = extract_equations(ground_truth)
    out_display, out_inline = extract_equations(parser_output)

    # Normalize all equations
    gt_display_norm = [normalize_latex(eq) for eq in gt_display]
    out_display_norm = [normalize_latex(eq) for eq in out_display]

    gt_inline_norm = [normalize_latex(eq) for eq in gt_inline]
    out_inline_norm = [normalize_latex(eq) for eq in out_inline]

    # Count matches (exact match after normalization)
    display_matches = sum(1 for eq in out_display_norm if eq in gt_display_norm)
    inline_matches = sum(1 for eq in out_inline_norm if eq in gt_inline_norm)

    return {
        'display_equations': {
            'ground_truth': len(gt_display),
            'extracted': len(out_display),
            'matched': display_matches,
            'extraction_rate': len(out_display) / len(gt_display) if gt_display else 0,
            'match_rate': display_matches / len(out_display) if out_display else 0
        },
        'inline_equations': {
            'ground_truth': len(gt_inline),
            'extracted': len(out_inline),
            'matched': inline_matches,
            'extraction_rate': len(out_inline) / len(gt_inline) if gt_inline else 0,
            'match_rate': inline_matches / len(out_inline) if out_inline else 0
        }
    }


def compare_prose(ground_truth: str, parser_output: str) -> dict:
    """
    Compare prose text (equations stripped) between ground truth and output.

    Returns:
        - word_count_gt: words in ground truth
        - word_count_out: words in parser output
        - word_preservation_rate: ratio of word counts
        - text_similarity: normalized text similarity
    """
    import difflib

    # Strip equations
    gt_prose = strip_equations(ground_truth)
    out_prose = strip_equations(parser_output)

    # Normalize
    gt_norm = normalize_prose(gt_prose)
    out_norm = normalize_prose(out_prose)

    # Count words
    gt_words = len(gt_norm.split())
    out_words = len(out_norm.split())

    # Calculate similarity
    similarity = difflib.SequenceMatcher(None, gt_norm, out_norm).ratio()

    return {
        'word_count_gt': gt_words,
        'word_count_out': out_words,
        'word_preservation_rate': out_words / gt_words if gt_words else 0,
        'text_similarity': similarity
    }


def compare_structure(ground_truth: str, parser_output: str) -> dict:
    """
    Compare document structure (headers) between ground truth and output.
    """
    # Extract headers
    gt_headers = re.findall(r'^(#+)\s+(.+)$', ground_truth, flags=re.MULTILINE)
    out_headers = re.findall(r'^(#+)\s+(.+)$', parser_output, flags=re.MULTILINE)

    # Count by level
    gt_h1 = sum(1 for level, _ in gt_headers if level == '#')
    gt_h2 = sum(1 for level, _ in gt_headers if level == '##')
    gt_h3 = sum(1 for level, _ in gt_headers if level == '###')

    out_h1 = sum(1 for level, _ in out_headers if level == '#')
    out_h2 = sum(1 for level, _ in out_headers if level == '##')
    out_h3 = sum(1 for level, _ in out_headers if level == '###')

    return {
        'headers_gt': len(gt_headers),
        'headers_out': len(out_headers),
        'h1': {'gt': gt_h1, 'out': out_h1},
        'h2': {'gt': gt_h2, 'out': out_h2},
        'h3': {'gt': gt_h3, 'out': out_h3}
    }


def evaluate_academic_paper(ground_truth_path: str, parser_output_path: str) -> dict:
    """
    Complete evaluation of an academic paper extraction.

    Returns comprehensive metrics for equations, prose, and structure.
    """
    from pathlib import Path

    gt = Path(ground_truth_path).read_text()
    out = Path(parser_output_path).read_text()

    return {
        'equations': compare_equations(gt, out),
        'prose': compare_prose(gt, out),
        'structure': compare_structure(gt, out)
    }
