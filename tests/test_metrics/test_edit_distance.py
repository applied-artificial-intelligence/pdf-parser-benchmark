"""Tests for edit distance metrics.

This module tests the normalized Levenshtein edit distance implementation,
including edge cases, normalization integration, and different metric variants.
"""

import pytest

from pdf_bench.metrics.edit_distance import (
    character_error_rate,
    edit_similarity,
    normalized_edit_distance,
    raw_edit_distance,
)


class TestNormalizedEditDistance:
    """Tests for normalized_edit_distance function."""

    def test_identical_texts(self) -> None:
        """Test that identical texts have zero distance."""
        assert normalized_edit_distance("hello", "hello") == 0.0

    def test_completely_different_texts(self) -> None:
        """Test that completely different texts have distance close to 1.0."""
        # No overlap in characters
        distance = normalized_edit_distance("abc", "xyz")
        assert distance == 1.0

    def test_single_character_difference(self) -> None:
        """Test single character substitution."""
        # "hello" -> "hallo": 1 substitution / 5 chars
        distance = normalized_edit_distance("hello", "hallo")
        assert distance == pytest.approx(0.2)

    def test_insertion(self) -> None:
        """Test character insertion."""
        # "cat" -> "cats": 1 insertion / 4 chars
        distance = normalized_edit_distance("cat", "cats")
        assert distance == pytest.approx(0.25)

    def test_deletion(self) -> None:
        """Test character deletion."""
        # "cats" -> "cat": 1 deletion / 4 chars
        distance = normalized_edit_distance("cats", "cat")
        assert distance == pytest.approx(0.25)

    def test_multiple_edits(self) -> None:
        """Test multiple edits (classic Levenshtein example)."""
        # "kitten" -> "sitting": 3 edits / 7 chars
        # k->s, e->i, +g
        distance = normalized_edit_distance("kitten", "sitting")
        assert distance == pytest.approx(3 / 7)

    def test_empty_string_handling(self) -> None:
        """Test handling of empty strings."""
        # Both empty with normalize=False
        with pytest.raises(ValueError, match="Both input texts are empty"):
            normalized_edit_distance("", "")

        # One empty
        assert normalized_edit_distance("hello", "", normalize=False) == 1.0
        assert normalized_edit_distance("", "hello", normalize=False) == 1.0

    def test_empty_after_normalization(self) -> None:
        """Test strings that become empty after normalization."""
        # Whitespace-only strings become empty after normalization
        distance = normalized_edit_distance("   ", "  \t  ")
        assert distance == 0.0

        # One becomes empty
        distance = normalized_edit_distance("hello", "   ")
        assert distance == 1.0

    def test_normalization_default(self) -> None:
        """Test that normalization is applied by default."""
        # Whitespace differences should be normalized away
        distance = normalized_edit_distance("hello world", "hello  world")
        assert distance == 0.0

        # Smart quotes normalized to ASCII
        distance = normalized_edit_distance('"hello"', '"hello"')
        assert distance == 0.0

    def test_normalization_disabled(self) -> None:
        """Test behavior when normalization is disabled."""
        # Whitespace differences count as edits
        distance = normalized_edit_distance("hello world", "hello  world", normalize=False)
        assert distance > 0.0

    def test_normalization_options(self) -> None:
        """Test selective normalization options."""
        # Without ligature normalization
        text1 = "first"
        text2 = "\ufb01rst"  # fi ligature + rst
        distance = normalized_edit_distance(text1, text2, ligatures=False)
        assert distance > 0.0

        # With ligature normalization
        distance = normalized_edit_distance(text1, text2, ligatures=True)
        assert distance == 0.0

    def test_unicode_normalization(self) -> None:
        """Test Unicode normalization handling."""
        # NFC vs NFD (composed vs decomposed)
        nfc = "café"  # é as single character
        nfd = "cafe\u0301"  # e + combining acute accent
        distance = normalized_edit_distance(nfc, nfd)
        assert distance == 0.0

    def test_case_sensitivity(self) -> None:
        """Test that comparison is case-sensitive after normalization."""
        # Normalization preserves case
        distance = normalized_edit_distance("Hello", "hello")
        assert distance > 0.0

    def test_length_normalization(self) -> None:
        """Test that normalization divides by max length."""
        # Shorter text requires fewer edits, but normalized by max length
        # "a" -> "ab": 1 insertion / 2 chars = 0.5
        distance1 = normalized_edit_distance("a", "ab")
        assert distance1 == pytest.approx(0.5)

        # "ab" -> "a": 1 deletion / 2 chars = 0.5
        distance2 = normalized_edit_distance("ab", "a")
        assert distance2 == pytest.approx(0.5)


class TestEditSimilarity:
    """Tests for edit_similarity function."""

    def test_identical_texts(self) -> None:
        """Test that identical texts have similarity 1.0."""
        assert edit_similarity("hello", "hello") == 1.0

    def test_completely_different_texts(self) -> None:
        """Test that completely different texts have similarity 0.0."""
        similarity = edit_similarity("abc", "xyz")
        assert similarity == 0.0

    def test_complement_of_distance(self) -> None:
        """Test that similarity = 1 - distance."""
        text1 = "hello"
        text2 = "hallo"

        distance = normalized_edit_distance(text1, text2)
        similarity = edit_similarity(text1, text2)

        assert similarity == pytest.approx(1.0 - distance)

    def test_similarity_range(self) -> None:
        """Test that similarity is always in [0, 1] range."""
        # Various text pairs
        pairs = [
            ("hello", "hello"),
            ("hello", "hallo"),
            ("kitten", "sitting"),
            ("abc", "xyz"),
        ]

        for text1, text2 in pairs:
            similarity = edit_similarity(text1, text2)
            assert 0.0 <= similarity <= 1.0


class TestCharacterErrorRate:
    """Tests for character_error_rate function."""

    def test_identical_texts(self) -> None:
        """Test that identical texts have CER of 0.0."""
        cer = character_error_rate("hello world", "hello world")
        assert cer == 0.0

    def test_single_error(self) -> None:
        """Test single character error."""
        # "hello" has 5 chars, 1 error
        cer = character_error_rate("hello", "hallo")
        assert cer == pytest.approx(0.2)

    def test_multiple_errors(self) -> None:
        """Test multiple character errors."""
        # "hello world" has 11 chars, 2 deletions
        cer = character_error_rate("hello world", "helo wrld")
        assert cer == pytest.approx(2 / 11)

    def test_cer_can_exceed_one(self) -> None:
        """Test that CER can exceed 1.0 if hypothesis is much longer."""
        # Ground truth: 2 chars, hypothesis requires many edits
        cer = character_error_rate("hi", "hello world")
        assert cer > 1.0

    def test_empty_ground_truth_raises(self) -> None:
        """Test that empty ground truth raises ValueError."""
        with pytest.raises(ValueError, match="Ground truth is empty"):
            character_error_rate("", "hello", normalize=False)

    def test_empty_hypothesis(self) -> None:
        """Test that empty hypothesis gives CER of 1.0."""
        cer = character_error_rate("hello", "", normalize=False)
        assert cer == 1.0

    def test_ocr_example(self) -> None:
        """Test realistic OCR scenario."""
        ground_truth = "The quick brown fox jumps over the lazy dog"
        hypothesis = "The quik brown fox jmps over the lzy dog"  # 3 chars missing
        # Actual edits: quick->quik (1 del), jumps->jmps (1 del), lazy->lzy (1 del) = 3 deletions
        # Ground truth: 44 chars

        cer = character_error_rate(ground_truth, hypothesis)
        # Verify the actual edit distance
        from pdf_bench.metrics.edit_distance import raw_edit_distance
        from pdf_bench.utils.normalization import normalize_text

        actual_edits = raw_edit_distance(ground_truth, hypothesis)
        gt_normalized = normalize_text(ground_truth)
        assert cer == pytest.approx(actual_edits / len(gt_normalized))


class TestRawEditDistance:
    """Tests for raw_edit_distance function."""

    def test_identical_texts(self) -> None:
        """Test that identical texts have distance 0."""
        assert raw_edit_distance("hello", "hello") == 0

    def test_single_edit(self) -> None:
        """Test single character edit."""
        assert raw_edit_distance("hello", "hallo") == 1

    def test_multiple_edits(self) -> None:
        """Test multiple edits."""
        # "kitten" -> "sitting": 3 edits
        assert raw_edit_distance("kitten", "sitting") == 3

    def test_empty_strings(self) -> None:
        """Test handling of empty strings."""
        assert raw_edit_distance("hello", "", normalize=False) == 5
        assert raw_edit_distance("", "hello", normalize=False) == 5
        assert raw_edit_distance("", "", normalize=False) == 0

    def test_returns_integer(self) -> None:
        """Test that raw distance returns integer."""
        distance = raw_edit_distance("hello", "hallo")
        assert isinstance(distance, int)


class TestNormalizationIntegration:
    """Tests for integration with text normalization utilities."""

    def test_whitespace_normalization(self) -> None:
        """Test whitespace normalization integration."""
        # Multiple spaces collapsed
        distance = normalized_edit_distance("hello  world", "hello world")
        assert distance == 0.0

        # Leading/trailing whitespace stripped
        distance = normalized_edit_distance("  hello  ", "hello")
        assert distance == 0.0

        # Tabs converted to spaces
        distance = normalized_edit_distance("hello\tworld", "hello world")
        assert distance == 0.0

    def test_quote_normalization(self) -> None:
        """Test quote normalization integration."""
        # Smart quotes to ASCII
        distance = normalized_edit_distance('"hello"', '"hello"')
        assert distance == 0.0

        # Single smart quotes
        distance = normalized_edit_distance("'hello'", "'hello'")
        assert distance == 0.0

    def test_unicode_normalization(self) -> None:
        """Test Unicode normalization integration."""
        # NFC vs NFD
        nfc = "naïve"
        nfd = "nai\u0308ve"
        distance = normalized_edit_distance(nfc, nfd)
        assert distance == 0.0

    def test_ligature_normalization(self) -> None:
        """Test ligature normalization when enabled."""
        # fi ligature
        distance = normalized_edit_distance("first", "\ufb01rst", ligatures=True)
        assert distance == 0.0

        # Without ligature normalization
        distance = normalized_edit_distance("first", "\ufb01rst", ligatures=False)
        assert distance > 0.0

    def test_hyphen_normalization(self) -> None:
        """Test hyphen normalization when enabled."""
        # En-dash to hyphen
        distance = normalized_edit_distance("1-10", "1\u201310", hyphens=True)
        assert distance == 0.0

        # Without hyphen normalization
        distance = normalized_edit_distance("1-10", "1\u201310", hyphens=False)
        assert distance > 0.0

    def test_combined_normalization(self) -> None:
        """Test multiple normalizations applied together."""
        text1 = 'The  "quick"  brown fox'
        text2 = 'The "quick" brown fox'

        # With full normalization
        distance = normalized_edit_distance(text1, text2)
        assert distance == 0.0

        # Without normalization
        distance = normalized_edit_distance(text1, text2, normalize=False)
        assert distance > 0.0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_strings(self) -> None:
        """Test with very long strings."""
        long_text = "a" * 10000
        almost_same = "a" * 9999 + "b"

        distance = normalized_edit_distance(long_text, almost_same)
        assert distance == pytest.approx(1 / 10000)

    def test_special_characters(self) -> None:
        """Test with special characters."""
        text1 = "Hello! How are you? I'm fine."
        text2 = "Hello! How are you? I'm fine."

        distance = normalized_edit_distance(text1, text2)
        assert distance == 0.0

    def test_multiline_text(self) -> None:
        """Test with multiline text."""
        text1 = "Line 1\nLine 2\nLine 3"
        text2 = "Line 1\nLine 2\nLine 3"

        # Identical multiline text
        distance = normalized_edit_distance(text1, text2)
        assert distance == 0.0

        # Test blank line collapsing
        text3 = "Line 1\n\n\nLine 2"
        text4 = "Line 1\n\nLine 2"
        # Should be identical after normalization (3 newlines -> 2 newlines)
        distance = normalized_edit_distance(text3, text4)
        assert distance == 0.0

    def test_only_punctuation(self) -> None:
        """Test with only punctuation."""
        distance = normalized_edit_distance("!!!", "???")
        assert distance == 1.0

    def test_numbers(self) -> None:
        """Test with numeric strings."""
        distance = normalized_edit_distance("12345", "12345")
        assert distance == 0.0

        distance = normalized_edit_distance("12345", "12346")
        assert distance == pytest.approx(0.2)

    def test_mixed_content(self) -> None:
        """Test with mixed content (text, numbers, symbols)."""
        text1 = "Product #123: $45.99 (10% off!)"
        text2 = "Product #123: $45.99 (10% off!)"

        distance = normalized_edit_distance(text1, text2)
        assert distance == 0.0


class TestRealWorldExamples:
    """Tests with realistic PDF extraction scenarios."""

    def test_pdf_extraction_whitespace(self) -> None:
        """Test typical PDF extraction whitespace issues."""
        ground_truth = "This is a sentence with normal spacing."
        parsed = "This  is  a  sentence  with  normal  spacing."

        # Should be identical after normalization
        distance = normalized_edit_distance(ground_truth, parsed)
        assert distance == 0.0

    def test_pdf_ligature_extraction(self) -> None:
        """Test PDF ligature extraction."""
        ground_truth = "The first officer was efficient"
        parsed = "The \ufb01rst o\ufb03cer was e\ufb03cient"  # fi, ffi ligatures

        # Should be identical with ligature normalization
        distance = normalized_edit_distance(ground_truth, parsed, ligatures=True)
        assert distance == 0.0

    def test_pdf_quote_extraction(self) -> None:
        """Test PDF smart quote extraction."""
        ground_truth = 'She said "hello" and smiled.'
        parsed = 'She said "hello" and smiled.'

        # Should be identical after quote normalization
        distance = normalized_edit_distance(ground_truth, parsed)
        assert distance == 0.0

    def test_ocr_errors(self) -> None:
        """Test typical OCR errors."""
        ground_truth = "recognize"
        parsed = "recognlze"  # i -> l (common OCR error)

        distance = normalized_edit_distance(ground_truth, parsed)
        # 1 substitution / 9 characters
        assert distance == pytest.approx(1 / 9)

        cer = character_error_rate(ground_truth, parsed)
        assert cer == pytest.approx(1 / 9)

    def test_missing_words(self) -> None:
        """Test when entire words are missing."""
        ground_truth = "The quick brown fox jumps over the lazy dog"
        parsed = "The brown fox jumps the lazy dog"  # "quick" and "over" missing

        distance = normalized_edit_distance(ground_truth, parsed)
        # Should have relatively high distance
        assert distance > 0.2
