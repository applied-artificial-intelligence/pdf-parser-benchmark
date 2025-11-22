"""Utility functions and helpers.

SPDX-License-Identifier: MIT
Copyright (c) 2025 PDF-Bench Contributors
"""

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
from pdf_bench.utils.normalization import (
    normalize_hyphens,
    normalize_ligatures,
    normalize_quotes,
    normalize_text,
    normalize_unicode,
    normalize_whitespace,
)

__all__ = [
    # LaTeX normalization
    "normalize_latex",
    "normalize_latex_in_text",
    "extract_math_content",
    "remove_sizing_commands",
    "remove_redundant_braces",
    "normalize_spacing_commands",
    "normalize_command_spacing",
    "collapse_whitespace",
    # Text normalization
    "normalize_text",
    "normalize_unicode",
    "normalize_whitespace",
    "normalize_quotes",
    "normalize_hyphens",
    "normalize_ligatures",
]
