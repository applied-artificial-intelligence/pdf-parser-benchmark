"""Text normalization utilities for fair comparison of parsed output and ground truth.

This module provides functions to normalize text before computing similarity metrics.
Normalization ensures that superficial textual variations don't affect comparison results.

The normalization pipeline handles:
- Unicode NFC normalization (canonical composition)
- Whitespace collapsing and cleanup
- Smart quote normalization to ASCII equivalents
- Optional hyphen and ligature normalization
- Optional markdown/HTML stripping (format-agnostic comparison)

Example:
    >>> from pdf_bench.utils.normalization import normalize_text
    >>> text = "  "Smart   quotes"  "
    >>> normalize_text(text)
    '"Smart quotes"'

    >>> # Strip markdown/HTML for format-agnostic comparison
    >>> md_text = "# Header\\n<table><tr><td>Cell</td></tr></table>"
    >>> normalize_text(md_text, strip_formatting=True)
    'Header Cell'
"""

import re
import unicodedata
from typing import Final

# Unicode character mappings for quote normalization
_QUOTE_MAP: Final[dict[str, str]] = {
    # Single quotes
    "\u2018": "'",  # Left single quotation mark
    "\u2019": "'",  # Right single quotation mark
    "\u201a": "'",  # Single low-9 quotation mark
    "\u201b": "'",  # Single high-reversed-9 quotation mark
    "\u2039": "'",  # Single left-pointing angle quotation mark
    "\u203a": "'",  # Single right-pointing angle quotation mark
    # Double quotes
    "\u201c": '"',  # Left double quotation mark
    "\u201d": '"',  # Right double quotation mark
    "\u201e": '"',  # Double low-9 quotation mark
    "\u201f": '"',  # Double high-reversed-9 quotation mark
    "\u00ab": '"',  # Left-pointing double angle quotation mark
    "\u00bb": '"',  # Right-pointing double angle quotation mark
}

# Unicode character mappings for hyphen normalization
_HYPHEN_MAP: Final[dict[str, str]] = {
    "\u2013": "-",  # En dash
    "\u2014": "-",  # Em dash
    "\u2015": "-",  # Horizontal bar
    "\u2212": "-",  # Minus sign
    "\u00ad": "",  # Soft hyphen (removed)
}

# Unicode ligature mappings
_LIGATURE_MAP: Final[dict[str, str]] = {
    "\ufb00": "ff",  # Latin small ligature ff
    "\ufb01": "fi",  # Latin small ligature fi
    "\ufb02": "fl",  # Latin small ligature fl
    "\ufb03": "ffi",  # Latin small ligature ffi
    "\ufb04": "ffl",  # Latin small ligature ffl
    "\ufb05": "ft",  # Latin small ligature long s t
    "\ufb06": "st",  # Latin small ligature st
}


def strip_markdown(text: str) -> str:
    """Strip markdown formatting from text.

    Removes common markdown syntax while preserving the underlying text content.
    This enables format-agnostic comparison between parsers that output different
    formats (plain text vs markdown).

    Handles:
    - Headers (# ## ### etc.)
    - Bold/italic (**text**, *text*, __text__, _text_)
    - Links [text](url) -> text
    - Images ![alt](url) -> alt
    - Code blocks and inline code
    - Blockquotes (>)
    - Horizontal rules (---, ***)
    - List markers (-, *, +, 1.)

    Args:
        text: Input text with potential markdown formatting

    Returns:
        Text with markdown syntax removed

    Example:
        >>> strip_markdown("# Header\\n**bold** and *italic*")
        'Header bold and italic'
    """
    # Remove code blocks (``` ... ```)
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Remove inline code (`code`)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove images ![alt](url) -> alt
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

    # Remove links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove headers (# at start of line)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # **bold**
    text = re.sub(r"__([^_]+)__", r"\1", text)  # __bold__
    text = re.sub(r"\*([^*]+)\*", r"\1", text)  # *italic*
    text = re.sub(r"_([^_]+)_", r"\1", text)  # _italic_

    # Remove blockquotes (> at start of line)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Remove list markers (but keep the content)
    text = re.sub(r"^[\s]*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*\d+\.\s+", "", text, flags=re.MULTILINE)

    return text


def strip_html(text: str) -> str:
    """Strip HTML tags from text.

    Removes HTML/XML tags while preserving the text content between them.
    This enables format-agnostic comparison between parsers that output
    HTML tables vs plain text.

    Args:
        text: Input text with potential HTML tags

    Returns:
        Text with HTML tags removed

    Example:
        >>> strip_html("<table><tr><td>Cell 1</td><td>Cell 2</td></tr></table>")
        'Cell 1 Cell 2'
    """
    # Replace tags with space to prevent word concatenation
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def fix_number_spacing(text: str) -> str:
    """Fix numbers that have been incorrectly split by spaces.

    Some parsers (notably Google Document AI) insert spaces into numbers,
    e.g., "45. 87" instead of "45.87". This function fixes such issues.

    Args:
        text: Input text with potential spacing issues in numbers

    Returns:
        Text with number spacing corrected

    Example:
        >>> fix_number_spacing("The value is 45. 87 dollars")
        'The value is 45.87 dollars'
    """
    # Fix "45. 87" -> "45.87"
    text = re.sub(r"(\d+)\.\s+(\d+)", r"\1.\2", text)
    # Fix "$ 100" -> "$100" (currency symbols)
    text = re.sub(r"(\$)\s+(\d)", r"\1\2", text)
    return text


def normalize_unicode(text: str) -> str:
    """Normalize Unicode text to NFC (Normal Form Canonical Composition).

    Unicode normalization ensures that different byte sequences representing the same
    character are converted to a canonical form. This is important for text extracted
    from PDFs, which may use different Unicode encodings.

    NFC is chosen over NFD because it:
    - Preserves more semantic distinctions
    - Is more compact (combines base + combining characters)
    - Is the recommended form for most text processing

    Args:
        text: Input text to normalize

    Returns:
        Text normalized to Unicode NFC form

    Example:
        >>> # NFD: "e" + combining acute accent
        >>> nfd_text = "cafe\\u0301"
        >>> normalize_unicode(nfd_text)
        'café'
        >>> # NFC: "é" as single character
        >>> nfc_text = "café"
        >>> normalize_unicode(nfc_text)
        'café'
    """
    return unicodedata.normalize("NFC", text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text for consistent comparison.

    This function:
    1. Normalizes line endings (CRLF, CR → LF)
    2. Replaces tabs with spaces
    3. Collapses multiple spaces to single space
    4. Strips leading/trailing whitespace from each line
    5. Collapses multiple blank lines to single blank line
    6. Strips leading/trailing blank lines

    Args:
        text: Input text to normalize

    Returns:
        Text with normalized whitespace

    Example:
        >>> text = "Hello    world\\r\\n\\n\\n\\ttest"
        >>> normalize_whitespace(text)
        'Hello world\\n\\ntest'
    """
    # Normalize line endings (CRLF and CR to LF)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Split into lines for line-level processing
    lines = text.split("\n")

    # Process each line: collapse multiple spaces and strip
    normalized_lines = []
    for line in lines:
        # Collapse multiple spaces to single space
        line = re.sub(r" +", " ", line)
        # Strip leading/trailing whitespace
        line = line.strip()
        normalized_lines.append(line)

    # Join lines back together
    text = "\n".join(normalized_lines)

    # Collapse multiple blank lines to single blank line
    text = re.sub(r"\n\n+", "\n\n", text)

    # Strip leading/trailing blank lines
    text = text.strip()

    return text


def normalize_quotes(text: str) -> str:
    """Normalize smart/curly quotes to straight ASCII quotes.

    Converts various Unicode quotation marks to their ASCII equivalents:
    - Single curly quotes → '
    - Double curly quotes → "
    - Angle quotes → ' or "

    This normalization is important because PDF extraction may produce different
    quote characters depending on the source document and extraction method.

    Args:
        text: Input text to normalize

    Returns:
        Text with ASCII quotes

    Example:
        >>> text = "He said "hello" with a 'smile'"
        >>> normalize_quotes(text)
        'He said "hello" with a \\'smile\\''
    """
    for unicode_quote, ascii_quote in _QUOTE_MAP.items():
        text = text.replace(unicode_quote, ascii_quote)
    return text


def normalize_hyphens(text: str) -> str:
    """Normalize various hyphen and dash characters to ASCII hyphen.

    Converts:
    - En-dash (–) → hyphen (-)
    - Em-dash (—) → hyphen (-)
    - Minus sign (−) → hyphen (-)
    - Soft hyphens (removed completely)

    Args:
        text: Input text to normalize

    Returns:
        Text with normalized hyphens

    Example:
        >>> text = "Range: 1–10 and a long break—here"
        >>> normalize_hyphens(text)
        'Range: 1-10 and a long break-here'
    """
    for unicode_hyphen, ascii_hyphen in _HYPHEN_MAP.items():
        text = text.replace(unicode_hyphen, ascii_hyphen)
    return text


def normalize_ligatures(text: str) -> str:
    """Normalize Unicode ligatures to separate ASCII characters.

    Ligatures are typographic characters that combine two or more letters.
    They often appear in PDF extraction, especially from professionally
    typeset documents.

    Common ligatures:
    - fi → fi
    - fl → fl
    - ffi → ffi
    - ffl → ffl

    Args:
        text: Input text to normalize

    Returns:
        Text with ligatures expanded to separate characters

    Example:
        >>> text = "The ﬁrst ﬂoor has ﬃce"
        >>> normalize_ligatures(text)
        'The first floor has office'
    """
    for ligature, expansion in _LIGATURE_MAP.items():
        text = text.replace(ligature, expansion)
    return text


def normalize_text(
    text: str,
    *,
    unicode: bool = True,
    whitespace: bool = True,
    quotes: bool = True,
    hyphens: bool = False,
    ligatures: bool = False,
    strip_formatting: bool = False,
) -> str:
    """Master normalization function that applies all normalizations.

    This function applies normalizations in the correct order to ensure
    consistent results:
    1. Strip formatting (markdown/HTML) if enabled - FIRST to avoid regex issues
    2. Fix number spacing (e.g., "45. 87" -> "45.87")
    3. Unicode NFC normalization (if enabled)
    4. Ligature normalization (if enabled)
    5. Quote normalization (if enabled)
    6. Hyphen normalization (if enabled)
    7. Whitespace normalization (if enabled, applied last)

    The function is idempotent: applying it multiple times produces the
    same result as applying it once.

    Args:
        text: Input text to normalize
        unicode: Apply Unicode NFC normalization (default: True)
        whitespace: Apply whitespace normalization (default: True)
        quotes: Apply quote normalization (default: True)
        hyphens: Apply hyphen normalization (default: False)
        ligatures: Apply ligature normalization (default: False)
        strip_formatting: Strip markdown/HTML formatting for format-agnostic
            comparison (default: False). This is useful when comparing parsers
            that output different formats (plain text vs markdown vs HTML).

    Returns:
        Fully normalized text ready for comparison

    Example:
        >>> text = "  "Smart   quotes" and ﬁle  "
        >>> normalize_text(text, ligatures=True)
        '"Smart quotes" and file'

        >>> # Format-agnostic comparison
        >>> md_text = "# Header\\n<table><tr><td>Cell</td></tr></table>"
        >>> normalize_text(md_text, strip_formatting=True)
        'Header Cell'
    """
    # Strip formatting first (before other normalizations can be confused by markup)
    if strip_formatting:
        text = strip_markdown(text)
        text = strip_html(text)
        text = fix_number_spacing(text)

    # Apply Unicode normalization first (foundation for all other operations)
    if unicode:
        text = normalize_unicode(text)

    # Apply character-level normalizations
    if ligatures:
        text = normalize_ligatures(text)

    if quotes:
        text = normalize_quotes(text)

    if hyphens:
        text = normalize_hyphens(text)

    # Apply whitespace normalization last (cleanup after other operations)
    if whitespace:
        text = normalize_whitespace(text)

    return text
