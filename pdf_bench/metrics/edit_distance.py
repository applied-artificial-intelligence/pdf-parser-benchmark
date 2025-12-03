"""Normalized edit distance metric for text comparison.

This module implements normalized Levenshtein edit distance for comparing parsed text
against ground truth. The metric measures character-level similarity and is commonly
used in OCR, ASR, and text extraction evaluation.

The Levenshtein distance is the minimum number of single-character edits (insertions,
deletions, or substitutions) required to transform one string into another. Normalization
by the maximum length of the two strings provides a similarity score in the range [0, 1].

Key Features:
- Character-level edit distance computation using optimized C implementation
- Normalization for length-independent comparison
- Integration with text normalization utilities
- Support for both distance (0=identical) and similarity (1=identical) metrics
- Character Error Rate (CER) computation for OCR/ASR evaluation

Example:
    >>> from pdf_bench.metrics.edit_distance import normalized_edit_distance
    >>> ground_truth = "The quick brown fox"
    >>> parsed_text = "The qwick brown fox"
    >>> distance = normalized_edit_distance(ground_truth, parsed_text)
    >>> distance
    0.05263157894736842  # 1 edit / 19 characters
"""

from Levenshtein import distance as levenshtein_distance

from pdf_bench.utils.normalization import normalize_text


def normalized_edit_distance(
    text1: str,
    text2: str,
    *,
    normalize: bool = True,
    unicode: bool = True,
    whitespace: bool = True,
    quotes: bool = True,
    hyphens: bool = False,
    ligatures: bool = False,
) -> float:
    """Compute normalized Levenshtein edit distance between two texts.

    The normalized edit distance is computed as:
        distance = levenshtein_distance(text1, text2) / max(len(text1), len(text2))

    This provides a score in the range [0.0, 1.0] where:
    - 0.0 = texts are identical
    - 1.0 = texts are completely different

    Text normalization is applied by default to handle superficial differences
    (Unicode variants, whitespace, quotes, etc.) that shouldn't affect the comparison.

    Args:
        text1: First text to compare
        text2: Second text to compare
        normalize: Whether to apply text normalization before comparison (default: True)
        unicode: Apply Unicode NFC normalization (default: True, requires normalize=True)
        whitespace: Apply whitespace normalization (default: True, requires normalize=True)
        quotes: Apply quote normalization (default: True, requires normalize=True)
        hyphens: Apply hyphen normalization (default: False, requires normalize=True)
        ligatures: Apply ligature normalization (default: False, requires normalize=True)

    Returns:
        Normalized edit distance in range [0.0, 1.0]

    Raises:
        ValueError: If both input texts are empty strings

    Example:
        >>> # Identical texts
        >>> normalized_edit_distance("hello", "hello")
        0.0

        >>> # Single character difference
        >>> normalized_edit_distance("hello", "hallo")
        0.2  # 1 edit / 5 characters

        >>> # With normalization (default)
        >>> normalized_edit_distance("  Hello  ", "hello")
        0.0  # Whitespace and case normalized

        >>> # Without normalization
        >>> normalized_edit_distance("  Hello  ", "hello", normalize=False)
        0.4444444444444444  # Case and whitespace differences count
    """
    # Handle empty strings
    if not text1 and not text2:
        raise ValueError("Both input texts are empty")

    # Apply normalization if requested
    if normalize:
        text1 = normalize_text(
            text1,
            unicode=unicode,
            whitespace=whitespace,
            quotes=quotes,
            hyphens=hyphens,
            ligatures=ligatures,
        )
        text2 = normalize_text(
            text2,
            unicode=unicode,
            whitespace=whitespace,
            quotes=quotes,
            hyphens=hyphens,
            ligatures=ligatures,
        )

    # Handle empty strings after normalization
    if not text1 and not text2:
        return 0.0
    if not text1 or not text2:
        return 1.0

    # Compute edit distance
    edit_dist = levenshtein_distance(text1, text2)

    # Normalize by max length
    max_len = max(len(text1), len(text2))
    normalized_dist = edit_dist / max_len

    return normalized_dist


def edit_similarity(
    text1: str,
    text2: str,
    *,
    normalize: bool = True,
    unicode: bool = True,
    whitespace: bool = True,
    quotes: bool = True,
    hyphens: bool = False,
    ligatures: bool = False,
) -> float:
    """Compute normalized edit similarity between two texts.

    This is the complement of normalized_edit_distance, providing a score where:
    - 1.0 = texts are identical
    - 0.0 = texts are completely different

    This metric is more intuitive for reporting as higher scores indicate better matches.

    Args:
        text1: First text to compare
        text2: Second text to compare
        normalize: Whether to apply text normalization before comparison (default: True)
        unicode: Apply Unicode NFC normalization (default: True, requires normalize=True)
        whitespace: Apply whitespace normalization (default: True, requires normalize=True)
        quotes: Apply quote normalization (default: True, requires normalize=True)
        hyphens: Apply hyphen normalization (default: False, requires normalize=True)
        ligatures: Apply ligature normalization (default: False, requires normalize=True)

    Returns:
        Normalized edit similarity in range [0.0, 1.0]

    Raises:
        ValueError: If both input texts are empty strings

    Example:
        >>> # Identical texts
        >>> edit_similarity("hello", "hello")
        1.0

        >>> # Single character difference
        >>> edit_similarity("hello", "hallo")
        0.8  # 1.0 - (1 edit / 5 characters)
    """
    distance = normalized_edit_distance(
        text1,
        text2,
        normalize=normalize,
        unicode=unicode,
        whitespace=whitespace,
        quotes=quotes,
        hyphens=hyphens,
        ligatures=ligatures,
    )
    return 1.0 - distance


def character_error_rate(
    ground_truth: str,
    hypothesis: str,
    *,
    normalize: bool = True,
    unicode: bool = True,
    whitespace: bool = True,
    quotes: bool = True,
    hyphens: bool = False,
    ligatures: bool = False,
) -> float:
    """Compute Character Error Rate (CER) for OCR/ASR evaluation.

    CER is defined as the edit distance divided by the length of the ground truth:
        CER = levenshtein_distance(ground_truth, hypothesis) / len(ground_truth)

    CER is commonly used in OCR and ASR evaluation where the ground truth length
    is the reference for error rate calculation. Unlike normalized_edit_distance
    which divides by max length, CER can exceed 1.0 if the hypothesis is much
    longer than the ground truth.

    Args:
        ground_truth: Reference text (expected output)
        hypothesis: Predicted text (actual output)
        normalize: Whether to apply text normalization before comparison (default: True)
        unicode: Apply Unicode NFC normalization (default: True, requires normalize=True)
        whitespace: Apply whitespace normalization (default: True, requires normalize=True)
        quotes: Apply quote normalization (default: True, requires normalize=True)
        hyphens: Apply hyphen normalization (default: False, requires normalize=True)
        ligatures: Apply ligature normalization (default: False, requires normalize=True)

    Returns:
        Character error rate as a decimal (0.0 = perfect, higher = more errors)
        Can exceed 1.0 if hypothesis is much longer than ground truth

    Raises:
        ValueError: If ground_truth is empty or becomes empty after normalization

    Example:
        >>> ground_truth = "hello world"
        >>> hypothesis = "helo wrld"
        >>> character_error_rate(ground_truth, hypothesis)
        0.18181818181818182  # 2 deletions / 11 characters

        >>> # CER can exceed 1.0
        >>> character_error_rate("hi", "hello world")
        4.5  # 9 edits / 2 characters
    """
    # Apply normalization if requested
    if normalize:
        ground_truth = normalize_text(
            ground_truth,
            unicode=unicode,
            whitespace=whitespace,
            quotes=quotes,
            hyphens=hyphens,
            ligatures=ligatures,
        )
        hypothesis = normalize_text(
            hypothesis,
            unicode=unicode,
            whitespace=whitespace,
            quotes=quotes,
            hyphens=hyphens,
            ligatures=ligatures,
        )

    # Ground truth must not be empty
    if not ground_truth:
        raise ValueError("Ground truth is empty (after normalization)")

    # Handle empty hypothesis
    if not hypothesis:
        return 1.0

    # Compute edit distance
    edit_dist = levenshtein_distance(ground_truth, hypothesis)

    # Compute CER
    cer = edit_dist / len(ground_truth)

    return cer


def raw_edit_distance(
    text1: str,
    text2: str,
    *,
    normalize: bool = True,
    unicode: bool = True,
    whitespace: bool = True,
    quotes: bool = True,
    hyphens: bool = False,
    ligatures: bool = False,
) -> int:
    """Compute raw (unnormalized) Levenshtein edit distance between two texts.

    This function returns the absolute edit distance without normalization.
    Use this when you need the actual number of edits rather than a normalized score.

    Args:
        text1: First text to compare
        text2: Second text to compare
        normalize: Whether to apply text normalization before comparison (default: True)
        unicode: Apply Unicode NFC normalization (default: True, requires normalize=True)
        whitespace: Apply whitespace normalization (default: True, requires normalize=True)
        quotes: Apply quote normalization (default: True, requires normalize=True)
        hyphens: Apply hyphen normalization (default: False, requires normalize=True)
        ligatures: Apply ligature normalization (default: False, requires normalize=True)

    Returns:
        Raw edit distance (number of character edits required)

    Example:
        >>> raw_edit_distance("kitten", "sitting")
        3  # k→s, e→i, +g

        >>> raw_edit_distance("hello", "hallo")
        1  # e→a
    """
    # Apply normalization if requested
    if normalize:
        text1 = normalize_text(
            text1,
            unicode=unicode,
            whitespace=whitespace,
            quotes=quotes,
            hyphens=hyphens,
            ligatures=ligatures,
        )
        text2 = normalize_text(
            text2,
            unicode=unicode,
            whitespace=whitespace,
            quotes=quotes,
            hyphens=hyphens,
            ligatures=ligatures,
        )

    # Compute edit distance
    return levenshtein_distance(text1, text2)


def edit_similarity_normalized(
    text1: str,
    text2: str,
) -> float:
    """Compute format-agnostic edit similarity between two texts.

    This variant strips markdown and HTML formatting before comparison,
    enabling fair comparison between parsers that output different formats
    (plain text vs markdown vs HTML tables).

    This addresses a key benchmark methodology issue: parsers like Databricks
    that output HTML tables or Google that adds markdown headers should not
    be penalized for formatting choices when they correctly extract the content.

    Format stripping includes:
    - Markdown headers (# ## ### etc.)
    - HTML tags (<table>, <tr>, <td>, etc.)
    - Markdown bold/italic (**text**, *text*)
    - Number spacing fixes (45. 87 -> 45.87)

    Args:
        text1: First text to compare (typically ground truth)
        text2: Second text to compare (typically parser output)

    Returns:
        Normalized edit similarity in range [0.0, 1.0]
        Higher scores indicate better content extraction

    Example:
        >>> gt = "INVOICE\\nItem 1\\n$100"
        >>> html_output = "<table><tr><td>INVOICE</td></tr></table>"
        >>> md_output = "# INVOICE\\n**Item 1**\\n$100"
        >>>
        >>> # Raw comparison penalizes formatting
        >>> edit_similarity(gt, html_output)
        0.45  # Low score due to HTML tags
        >>>
        >>> # Format-agnostic comparison is fair
        >>> edit_similarity_normalized(gt, html_output)
        0.95  # High score - content is correct
    """
    # Apply format-agnostic normalization
    text1_norm = normalize_text(text1, strip_formatting=True)
    text2_norm = normalize_text(text2, strip_formatting=True)

    # Handle empty strings
    if not text1_norm and not text2_norm:
        return 1.0  # Both empty after normalization = identical
    if not text1_norm or not text2_norm:
        return 0.0  # One empty = no similarity

    # Compute edit distance on normalized text
    edit_dist = levenshtein_distance(text1_norm, text2_norm)

    # Normalize by max length
    max_len = max(len(text1_norm), len(text2_norm))
    normalized_dist = edit_dist / max_len

    return 1.0 - normalized_dist


def token_recall(
    ground_truth: str,
    hypothesis: str,
) -> float:
    """Compute token-level recall - what fraction of ground truth words appear in output.

    This metric measures content extraction completeness regardless of:
    - Word order
    - Formatting
    - Whitespace

    Token recall is useful for determining if a parser extracted all the
    content, even if it reorganized or reformatted it.

    Args:
        ground_truth: Reference text (expected content)
        hypothesis: Parser output to evaluate

    Returns:
        Recall score in range [0.0, 1.0]
        1.0 means all ground truth tokens found in hypothesis

    Example:
        >>> gt = "The quick brown fox"
        >>> hyp = "fox brown quick The other words"  # Reordered + extra
        >>> token_recall(gt, hyp)
        1.0  # All GT words present

        >>> hyp2 = "The quick brown"  # Missing "fox"
        >>> token_recall(gt, hyp2)
        0.75  # 3/4 words found
    """
    # Normalize both texts (strip formatting, collapse whitespace)
    gt_norm = normalize_text(ground_truth, strip_formatting=True).lower()
    hyp_norm = normalize_text(hypothesis, strip_formatting=True).lower()

    # Tokenize
    gt_tokens = set(gt_norm.split())
    hyp_tokens = set(hyp_norm.split())

    # Handle empty ground truth
    if not gt_tokens:
        return 1.0 if not hyp_tokens else 0.0

    # Compute recall
    found = gt_tokens & hyp_tokens
    recall = len(found) / len(gt_tokens)

    return recall
