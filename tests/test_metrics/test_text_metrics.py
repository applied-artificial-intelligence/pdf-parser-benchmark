"""Tests for text similarity metrics.

This module tests the chrF++ text similarity metric implementation,
including edge cases, normalization integration, and score accuracy.
"""

import pytest

from pdf_bench.metrics.text_metrics import chrf_plus_plus_score


class TestChrFPlusPlusScore:
    """Tests for chrf_plus_plus_score function."""

    def test_perfect_match(self) -> None:
        """Test that identical texts have perfect score of 100.0."""
        score = chrf_plus_plus_score("hello world", "hello world")
        assert score == 100.0

    def test_empty_strings_both(self) -> None:
        """Test that both empty strings return 0.0."""
        score = chrf_plus_plus_score("", "")
        assert score == 0.0

    def test_empty_reference(self) -> None:
        """Test that empty reference returns 0.0."""
        score = chrf_plus_plus_score("", "hello world")
        assert score == 0.0

    def test_empty_hypothesis(self) -> None:
        """Test that empty hypothesis returns 0.0."""
        score = chrf_plus_plus_score("hello world", "")
        assert score == 0.0

    def test_empty_after_normalization_both(self) -> None:
        """Test strings that become empty after normalization."""
        # Whitespace-only strings become empty after normalization
        score = chrf_plus_plus_score("   ", "  \t  ")
        assert score == 0.0

    def test_empty_after_normalization_one(self) -> None:
        """Test one string becomes empty after normalization."""
        score = chrf_plus_plus_score("hello", "   ")
        assert score == 0.0

    def test_completely_different_texts(self) -> None:
        """Test that completely different texts have low score."""
        # No character overlap
        score = chrf_plus_plus_score("abc", "xyz")
        assert score == pytest.approx(0.0)

    def test_partial_match_spelling_variation(self) -> None:
        """Test partial match with spelling variation."""
        # "hello" vs "helo" - missing one 'l'
        score = chrf_plus_plus_score("hello world", "helo world")
        # Should have moderate score (not perfect)
        assert 50.0 < score < 100.0

    def test_partial_match_word_order(self) -> None:
        """Test partial match with word order difference."""
        # chrF++ is robust to word order changes due to character n-grams
        score = chrf_plus_plus_score("hello world", "world hello")
        # Should have moderate score despite word order change
        assert score > 50.0

    def test_partial_match_morphological_variation(self) -> None:
        """Test partial match with morphological variation."""
        # "jumped" vs "jumps" - different verb form
        reference = "The quick brown fox jumps over the lazy dog"
        hypothesis = "The quick brown fox jumped over the lazy dog"
        score = chrf_plus_plus_score(reference, hypothesis)
        # Should have high score - only small difference
        assert score > 85.0

    def test_unicode_text_identical(self) -> None:
        """Test Unicode text handling with identical texts."""
        text = "Café résumé naïve"
        score = chrf_plus_plus_score(text, text)
        assert score == 100.0

    def test_unicode_normalization(self) -> None:
        """Test Unicode normalization (NFC vs NFD)."""
        # NFD: "e" + combining acute accent
        nfd_text = "cafe\u0301"  # café in NFD form
        # NFC: "é" as single character
        nfc_text = "café"  # café in NFC form
        score = chrf_plus_plus_score(nfd_text, nfc_text)
        # With normalization, should be perfect match
        assert score == 100.0

    def test_whitespace_normalization_default(self) -> None:
        """Test that whitespace normalization is applied by default."""
        score = chrf_plus_plus_score("hello  world", "hello world")
        assert score == 100.0

    def test_whitespace_leading_trailing(self) -> None:
        """Test leading/trailing whitespace normalization."""
        score = chrf_plus_plus_score("  hello world  ", "hello world")
        assert score == 100.0

    def test_whitespace_tabs_and_newlines(self) -> None:
        """Test tab and newline normalization."""
        score = chrf_plus_plus_score("hello\tworld\n", "hello world")
        assert score == 100.0

    def test_quote_normalization_default(self) -> None:
        """Test that quote normalization is applied by default."""
        # Smart quotes vs ASCII quotes
        score = chrf_plus_plus_score('"hello"', '"hello"')
        assert score == 100.0

    def test_quote_normalization_single_quotes(self) -> None:
        """Test single quote normalization."""
        score = chrf_plus_plus_score("'hello'", "'hello'")
        assert score == 100.0

    def test_normalization_disabled(self) -> None:
        """Test behavior when normalization is disabled."""
        # With normalization disabled, Unicode differences should affect score
        nfd_text = "cafe\u0301"  # NFD form
        nfc_text = "café"  # NFC form
        score = chrf_plus_plus_score(nfd_text, nfc_text, normalize=False)
        # Score should be less than perfect
        assert score < 100.0

    def test_normalization_selective_unicode(self) -> None:
        """Test selective Unicode normalization."""
        nfd_text = "cafe\u0301"
        nfc_text = "café"
        # With Unicode normalization enabled (default)
        score = chrf_plus_plus_score(nfd_text, nfc_text, unicode=True)
        assert score == 100.0
        # With Unicode normalization disabled
        score = chrf_plus_plus_score(
            nfd_text, nfc_text, normalize=True, unicode=False
        )
        assert score < 100.0

    def test_normalization_selective_whitespace(self) -> None:
        """Test selective whitespace normalization."""
        # With whitespace normalization enabled (default)
        score = chrf_plus_plus_score("hello  world", "hello world", whitespace=True)
        assert score == 100.0
        # Just verify the option is accepted without error
        score = chrf_plus_plus_score(
            "hello world", "hello world", normalize=True, whitespace=False
        )
        assert score == 100.0

    def test_normalization_selective_quotes(self) -> None:
        """Test selective quote normalization."""
        # With quote normalization enabled (default)
        score = chrf_plus_plus_score('"hello"', '"hello"', quotes=True)
        assert score == 100.0
        # Just verify the option is accepted without error
        score = chrf_plus_plus_score(
            '"hello"', '"hello"', normalize=True, quotes=False
        )
        assert 0.0 <= score <= 100.0

    def test_normalization_hyphens(self) -> None:
        """Test hyphen normalization."""
        # En-dash vs hyphen
        score = chrf_plus_plus_score("1–10", "1-10", hyphens=True)
        assert score == 100.0
        # Without hyphen normalization
        score = chrf_plus_plus_score("1–10", "1-10", hyphens=False)
        assert score < 100.0

    def test_normalization_ligatures(self) -> None:
        """Test ligature normalization."""
        # fi ligature vs separate characters
        ligature_text = "\ufb01rst"  # first with fi ligature
        normal_text = "first"
        score = chrf_plus_plus_score(ligature_text, normal_text, ligatures=True)
        assert score == 100.0
        # Without ligature normalization
        score = chrf_plus_plus_score(ligature_text, normal_text, ligatures=False)
        assert score < 100.0

    def test_real_world_pdf_extraction(self) -> None:
        """Test realistic PDF extraction scenario."""
        # Ground truth from source document
        reference = (
            "The quick brown fox jumps over the lazy dog. "
            "This is a test of PDF extraction accuracy."
        )
        # Extracted text with minor OCR errors
        hypothesis = (
            "The quick brown fox jumps over the lazy dog. "
            "This is a test of PDF extracton accuracy."
        )
        score = chrf_plus_plus_score(reference, hypothesis)
        # Should have high score despite small error
        assert score > 94.0

    def test_score_range(self) -> None:
        """Test that scores are always in valid range [0.0, 100.0]."""
        # Test various text pairs
        test_pairs = [
            ("hello", "hello"),
            ("hello", "hallo"),
            ("hello", ""),
            ("", "hello"),
            ("abc", "xyz"),
            ("The quick brown fox", "The brown quick fox"),
        ]
        for ref, hyp in test_pairs:
            score = chrf_plus_plus_score(ref, hyp)
            assert 0.0 <= score <= 100.0, f"Score {score} out of range for ({ref}, {hyp})"

    def test_symmetry(self) -> None:
        """Test that score is symmetric (reference/hypothesis order doesn't matter)."""
        text1 = "hello world"
        text2 = "world hello"
        score1 = chrf_plus_plus_score(text1, text2)
        score2 = chrf_plus_plus_score(text2, text1)
        # chrF++ should be symmetric
        assert score1 == pytest.approx(score2)

    def test_case_sensitivity(self) -> None:
        """Test case handling with normalization."""
        # Normalization includes lowercasing via whitespace normalization
        # (which strips and collapses, but doesn't lowercase)
        # However, chrF++ itself is case-sensitive
        score = chrf_plus_plus_score("Hello", "hello", normalize=False)
        # Should have moderate score (case difference)
        assert 40.0 < score < 100.0

    def test_long_text(self) -> None:
        """Test with longer text samples."""
        reference = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
        )
        hypothesis = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
        )
        score = chrf_plus_plus_score(reference, hypothesis)
        assert score == 100.0

    def test_special_characters(self) -> None:
        """Test handling of special characters."""
        text = "Hello! How are you? I'm fine, thanks. #python @user"
        score = chrf_plus_plus_score(text, text)
        assert score == 100.0

    def test_numbers(self) -> None:
        """Test handling of numeric text."""
        reference = "The value is 123.456 with error ±0.001"
        hypothesis = "The value is 123.456 with error ±0.001"
        score = chrf_plus_plus_score(reference, hypothesis)
        assert score == 100.0

    def test_mixed_content(self) -> None:
        """Test mixed alphanumeric and special characters."""
        reference = "Model: GPT-4, Temperature: 0.7, Max tokens: 2048"
        hypothesis = "Model: GPT-4, Temperature: 0.7, Max tokens: 2048"
        score = chrf_plus_plus_score(reference, hypothesis)
        assert score == 100.0
