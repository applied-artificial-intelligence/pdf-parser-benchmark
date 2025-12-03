"""Text similarity metrics using character n-gram matching.

This module implements advanced text similarity metrics for comparing parsed text
against ground truth. The primary metric is chrF++, a character n-gram F-score
that provides robust evaluation of text similarity while being more flexible
than exact string matching.

chrF++ (Character n-gram F-score):
- Character-level F-score based on n-gram overlap
- Considers both unigrams and higher-order n-grams
- Robust to minor variations in word order and morphology
- Commonly used in machine translation and text generation evaluation
- Implemented via the sacrebleu library for compatibility with MT benchmarks

Key Features:
- Integration with sacrebleu for standardized chrF++ computation
- Text normalization support for fair comparison
- Graceful handling of empty strings
- Scores range from 0.0 (no similarity) to 100.0 (identical)

Example:
    >>> from pdf_bench.metrics.text_metrics import chrf_plus_plus_score
    >>> reference = "The quick brown fox jumps over the lazy dog"
    >>> hypothesis = "The quick brown fox jumped over the lazy dog"
    >>> score = chrf_plus_plus_score(reference, hypothesis)
    >>> score
    96.15...  # High similarity despite small difference
"""

from sacrebleu.metrics import CHRF

from pdf_bench.utils.normalization import normalize_text


def chrf_plus_plus_score(
    reference: str,
    hypothesis: str,
    *,
    normalize: bool = True,
    unicode: bool = True,
    whitespace: bool = True,
    quotes: bool = True,
    hyphens: bool = False,
    ligatures: bool = False,
) -> float:
    """Compute chrF++ score between reference and hypothesis texts.

    chrF++ is a character n-gram F-score that measures text similarity based on
    character-level overlap. It computes precision and recall of character n-grams
    (default: 1-6 grams) and combines them into an F-score.

    The score ranges from 0.0 to 100.0:
    - 100.0 = texts are identical (perfect match)
    - 0.0 = no character n-gram overlap

    chrF++ is particularly useful for:
    - Evaluating text with minor spelling variations
    - Comparing texts with word order differences
    - Measuring similarity in morphologically rich languages
    - OCR and PDF extraction evaluation

    Text normalization is applied by default to handle superficial differences
    (Unicode variants, whitespace, quotes, etc.) that shouldn't affect the comparison.

    Args:
        reference: Reference text (ground truth)
        hypothesis: Hypothesis text (predicted output)
        normalize: Whether to apply text normalization before comparison (default: True)
        unicode: Apply Unicode NFC normalization (default: True, requires normalize=True)
        whitespace: Apply whitespace normalization (default: True, requires normalize=True)
        quotes: Apply quote normalization (default: True, requires normalize=True)
        hyphens: Apply hyphen normalization (default: False, requires normalize=True)
        ligatures: Apply ligature normalization (default: False, requires normalize=True)

    Returns:
        chrF++ score in range [0.0, 100.0], where higher is better

    Example:
        >>> # Perfect match
        >>> chrf_plus_plus_score("hello world", "hello world")
        100.0

        >>> # Small difference
        >>> chrf_plus_plus_score("hello world", "helo world")
        90.90909090909091

        >>> # With normalization (default)
        >>> chrf_plus_plus_score("  Hello  ", "hello")
        100.0  # Whitespace and case normalized

        >>> # Empty strings return 0.0
        >>> chrf_plus_plus_score("", "")
        0.0
        >>> chrf_plus_plus_score("hello", "")
        0.0
    """
    # Apply normalization if requested
    if normalize:
        reference = normalize_text(
            reference,
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

    # Handle empty strings - return 0.0 for any empty case
    # This is more intuitive than raising an error and consistent with
    # the metric's interpretation (0.0 = no similarity)
    if not reference or not hypothesis:
        return 0.0

    # Initialize chrF++ metric
    # word_order=2 enables chrF++ (includes word bigrams)
    # char_order=6 considers character 1-6 grams (standard setting)
    chrf = CHRF(word_order=2, char_order=6)

    # Compute chrF++ score
    # sacrebleu expects reference as list of strings (for multi-reference support)
    # and hypothesis as a single string
    result = chrf.sentence_score(hypothesis=hypothesis, references=[reference])

    # Return the score (already in range [0, 100])
    return float(result.score)
