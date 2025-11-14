"""Tests for text normalization utilities.

This module tests all normalization functions with edge cases, real-world examples,
and idempotency checks.
"""

import unicodedata

from pdf_bench.utils.normalization import (
    normalize_hyphens,
    normalize_ligatures,
    normalize_quotes,
    normalize_text,
    normalize_unicode,
    normalize_whitespace,
)


class TestNormalizeUnicode:
    """Tests for Unicode normalization."""

    def test_nfc_normalization(self) -> None:
        """Test that NFD text is converted to NFC."""
        # "café" in NFD form (e + combining acute accent)
        nfd_text = "cafe\u0301"
        # "café" in NFC form (single character)
        nfc_text = "café"

        result = normalize_unicode(nfd_text)
        assert result == nfc_text
        assert unicodedata.is_normalized("NFC", result)

    def test_already_nfc(self) -> None:
        """Test that NFC text remains unchanged."""
        nfc_text = "café"
        result = normalize_unicode(nfc_text)
        assert result == nfc_text
        assert unicodedata.is_normalized("NFC", result)

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_unicode("") == ""

    def test_ascii_only(self) -> None:
        """Test that ASCII text is unchanged."""
        ascii_text = "Hello World 123"
        assert normalize_unicode(ascii_text) == ascii_text

    def test_mixed_normalization(self) -> None:
        """Test text with mixed NFC and NFD characters."""
        # Mix of NFC "é" and NFD "e" + combining acute
        mixed = "café cafe\u0301"
        result = normalize_unicode(mixed)
        assert result == "café café"
        assert unicodedata.is_normalized("NFC", result)

    def test_idempotent(self) -> None:
        """Test that normalization is idempotent."""
        nfd_text = "cafe\u0301"
        once = normalize_unicode(nfd_text)
        twice = normalize_unicode(once)
        assert once == twice


class TestNormalizeWhitespace:
    """Tests for whitespace normalization."""

    def test_collapse_multiple_spaces(self) -> None:
        """Test collapsing multiple spaces to single space."""
        text = "Hello    world"
        assert normalize_whitespace(text) == "Hello world"

    def test_normalize_line_endings(self) -> None:
        """Test normalization of different line ending types."""
        # CRLF
        assert normalize_whitespace("line1\r\nline2") == "line1\nline2"
        # CR
        assert normalize_whitespace("line1\rline2") == "line1\nline2"
        # LF (unchanged)
        assert normalize_whitespace("line1\nline2") == "line1\nline2"

    def test_replace_tabs(self) -> None:
        """Test replacement of tabs with spaces."""
        text = "Hello\tworld"
        assert normalize_whitespace(text) == "Hello world"

    def test_strip_lines(self) -> None:
        """Test stripping leading/trailing whitespace from lines."""
        text = "  Hello  \n  World  "
        assert normalize_whitespace(text) == "Hello\nWorld"

    def test_collapse_blank_lines(self) -> None:
        """Test collapsing multiple blank lines to single blank line."""
        text = "line1\n\n\n\nline2"
        assert normalize_whitespace(text) == "line1\n\nline2"

    def test_strip_leading_trailing_blank_lines(self) -> None:
        """Test stripping leading/trailing blank lines."""
        text = "\n\nHello\n\n"
        assert normalize_whitespace(text) == "Hello"

    def test_complex_whitespace(self) -> None:
        """Test complex whitespace scenario."""
        text = "  Hello    world\r\n\n\n\ttest  \n\n"
        expected = "Hello world\n\ntest"
        assert normalize_whitespace(text) == expected

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_whitespace("") == ""

    def test_only_whitespace(self) -> None:
        """Test string with only whitespace."""
        assert normalize_whitespace("   \n\n  \t  ") == ""

    def test_idempotent(self) -> None:
        """Test that normalization is idempotent."""
        text = "  Hello    world\n\n\ntest  "
        once = normalize_whitespace(text)
        twice = normalize_whitespace(once)
        assert once == twice


class TestNormalizeQuotes:
    """Tests for quote normalization."""

    def test_double_curly_quotes(self) -> None:
        """Test normalization of curly double quotes."""
        text = "\u201cHello world\u201d"
        assert normalize_quotes(text) == '"Hello world"'

    def test_single_curly_quotes(self) -> None:
        """Test normalization of curly single quotes."""
        text = "\u2018Hello world\u2019"
        assert normalize_quotes(text) == "'Hello world'"

    def test_mixed_quotes(self) -> None:
        """Test normalization of mixed quote types."""
        text = "He said \u201chello\u201d with a \u2018smile\u2019"
        assert normalize_quotes(text) == "He said \"hello\" with a 'smile'"

    def test_angle_quotes(self) -> None:
        """Test normalization of angle quotation marks."""
        # Double angle quotes
        text = "«Hello»"
        assert normalize_quotes(text) == '"Hello"'
        # Single angle quotes
        text = "‹Hello›"
        assert normalize_quotes(text) == "'Hello'"

    def test_low_quotation_marks(self) -> None:
        """Test normalization of low quotation marks."""
        # Single low-9
        text = "‚Hello'"
        assert normalize_quotes(text) == "'Hello'"
        # Double low-9
        text = '„Hello"'
        assert normalize_quotes(text) == '"Hello"'

    def test_already_ascii_quotes(self) -> None:
        """Test that ASCII quotes remain unchanged."""
        text = "\"Hello\" and 'world'"
        assert normalize_quotes(text) == text

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_quotes("") == ""

    def test_no_quotes(self) -> None:
        """Test text without quotes."""
        text = "Hello world"
        assert normalize_quotes(text) == text

    def test_idempotent(self) -> None:
        """Test that normalization is idempotent."""
        text = "\u201cHello\u201d \u2018world\u2019"
        once = normalize_quotes(text)
        twice = normalize_quotes(once)
        assert once == twice


class TestNormalizeHyphens:
    """Tests for hyphen normalization."""

    def test_en_dash(self) -> None:
        """Test normalization of en-dash."""
        text = "Range: 1–10"
        assert normalize_hyphens(text) == "Range: 1-10"

    def test_em_dash(self) -> None:
        """Test normalization of em-dash."""
        text = "Long break—here"
        assert normalize_hyphens(text) == "Long break-here"

    def test_minus_sign(self) -> None:
        """Test normalization of minus sign."""
        text = "Temperature: −5°C"
        assert normalize_hyphens(text) == "Temperature: -5°C"

    def test_soft_hyphen_removal(self) -> None:
        """Test removal of soft hyphens."""
        text = "super\u00adcalifragilistic"
        assert normalize_hyphens(text) == "supercalifragilistic"

    def test_mixed_hyphens(self) -> None:
        """Test normalization of mixed hyphen types."""
        text = "1–10, break—here, −5, soft\u00adhyphen"
        assert normalize_hyphens(text) == "1-10, break-here, -5, softhyphen"

    def test_already_ascii_hyphen(self) -> None:
        """Test that ASCII hyphens remain unchanged."""
        text = "well-known"
        assert normalize_hyphens(text) == text

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_hyphens("") == ""

    def test_idempotent(self) -> None:
        """Test that normalization is idempotent."""
        text = "1–10—test"
        once = normalize_hyphens(text)
        twice = normalize_hyphens(once)
        assert once == twice


class TestNormalizeLigatures:
    """Tests for ligature normalization."""

    def test_fi_ligature(self) -> None:
        """Test normalization of fi ligature."""
        text = "The \ufb01rst"
        assert normalize_ligatures(text) == "The first"

    def test_fl_ligature(self) -> None:
        """Test normalization of fl ligature."""
        text = "\ufb02oor"
        assert normalize_ligatures(text) == "floor"

    def test_ffi_ligature(self) -> None:
        """Test normalization of ffi ligature."""
        text = "O\ufb03ce"
        assert normalize_ligatures(text) == "Office"

    def test_ffl_ligature(self) -> None:
        """Test normalization of ffl ligature."""
        text = "Ba\ufb04e"
        assert normalize_ligatures(text) == "Baffle"

    def test_ff_ligature(self) -> None:
        """Test normalization of ff ligature."""
        text = "O\ufb00er"
        assert normalize_ligatures(text) == "Offer"

    def test_st_ligature(self) -> None:
        """Test normalization of st ligature."""
        text = "\ufb06ory"
        assert normalize_ligatures(text) == "story"

    def test_mixed_ligatures(self) -> None:
        """Test normalization of mixed ligature types."""
        text = "\ufb01rst \ufb02oor o\ufb03ce"
        assert normalize_ligatures(text) == "first floor office"

    def test_no_ligatures(self) -> None:
        """Test text without ligatures."""
        text = "Hello world"
        assert normalize_ligatures(text) == text

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_ligatures("") == ""

    def test_idempotent(self) -> None:
        """Test that normalization is idempotent."""
        text = "\ufb01rst \ufb02oor"
        once = normalize_ligatures(text)
        twice = normalize_ligatures(once)
        assert once == twice


class TestNormalizeText:
    """Tests for master normalization function."""

    def test_all_normalizations_default(self) -> None:
        """Test that default parameters apply unicode, whitespace, and quotes."""
        text = "  \u201cSmart   quotes\u201d  "
        result = normalize_text(text)
        assert result == '"Smart quotes"'

    def test_all_normalizations_enabled(self) -> None:
        """Test with all normalizations enabled."""
        text = "  \u201cSmart\u201d \ufb01le—test  "
        result = normalize_text(text, hyphens=True, ligatures=True)
        assert result == '"Smart" file-test'

    def test_selective_normalization(self) -> None:
        """Test selective enabling of normalizations."""
        text = "  \u201cHello\u201d  "

        # Only whitespace
        result = normalize_text(text, unicode=False, quotes=False, whitespace=True)
        assert result == "\u201cHello\u201d"

        # Only quotes
        result = normalize_text(text, unicode=False, quotes=True, whitespace=False)
        assert result == '  "Hello"  '

        # Whitespace and quotes
        result = normalize_text(text, unicode=False, quotes=True, whitespace=True)
        assert result == '"Hello"'

    def test_disable_all(self) -> None:
        """Test with all normalizations disabled."""
        text = "  \u201cHello\u201d  "
        result = normalize_text(text, unicode=False, quotes=False, whitespace=False)
        assert result == text

    def test_normalization_order(self) -> None:
        """Test that normalizations are applied in correct order."""
        # Unicode normalization should happen first
        text = "cafe\u0301"  # NFD
        result = normalize_text(text)
        assert unicodedata.is_normalized("NFC", result)

        # Whitespace should happen last
        text = "  \u201cHello\u201d  "
        result = normalize_text(text)
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_idempotent(self) -> None:
        """Test that full normalization is idempotent."""
        text = "  \u201cSmart\u201d  \ufb01le—test  cafe\u0301  "
        once = normalize_text(text, hyphens=True, ligatures=True)
        twice = normalize_text(once, hyphens=True, ligatures=True)
        assert once == twice

    def test_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_text("") == ""

    def test_ascii_only_unchanged(self) -> None:
        """Test that ASCII-only text is minimally changed."""
        text = "Hello world"
        assert normalize_text(text) == text

    def test_real_world_pdf_example_1(self) -> None:
        """Test normalization of realistic PDF extraction."""
        # Simulated PDF extraction with various issues
        pdf_text = "  The  \ufb01rst  chapter—\u201cIntroduction\u201d—covers  basics.  "
        expected = 'The first chapter-"Introduction"-covers basics.'

        result = normalize_text(pdf_text, hyphens=True, ligatures=True)
        assert result == expected

    def test_real_world_pdf_example_2(self) -> None:
        """Test normalization of text with mixed encodings."""
        # Mix of Unicode issues
        pdf_text = "cafe\u0301\n\n\n\u201cHello\u201d  said  John."
        expected = 'café\n\n"Hello" said John.'

        result = normalize_text(pdf_text)
        assert result == expected

    def test_real_world_pdf_example_3(self) -> None:
        """Test normalization of text with ligatures and quotes."""
        # Professional typesetting output
        pdf_text = "The o\ufb03cial guide states: 'Use proper tools.'"
        expected = "The official guide states: 'Use proper tools.'"

        result = normalize_text(pdf_text, ligatures=True)
        assert result == expected

    def test_preserves_intentional_structure(self) -> None:
        """Test that normalization preserves intentional structure."""
        # Paragraphs should be preserved (double newline)
        text = "Paragraph 1.\n\nParagraph 2."
        result = normalize_text(text)
        assert "\n\n" in result
        assert result.count("\n") == 2

    def test_comparison_equivalence(self) -> None:
        """Test that different variations normalize to same result."""
        variations = [
            "  \u201cHello  world\u201d  ",
            "\u201cHello    world\u201d",
            "  \u201cHello world\u201d",
            "\u201cHello world\u201d  ",
        ]

        results = [normalize_text(v) for v in variations]
        assert len(set(results)) == 1  # All normalize to same result
        assert results[0] == '"Hello world"'


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_long_text(self) -> None:
        """Test normalization of very long text."""
        long_text = "Hello world. " * 10000
        result = normalize_text(long_text)
        assert result.startswith("Hello world.")
        assert len(result) < len(long_text)  # Whitespace should be reduced

    def test_only_special_characters(self) -> None:
        """Test text with only special characters."""
        text = "——––\u201c\u201d\ufb01\ufb02"
        result = normalize_text(text, hyphens=True, ligatures=True)
        assert result == '----""fifl'

    def test_unicode_combining_characters(self) -> None:
        """Test text with multiple combining characters."""
        # e with combining acute and combining tilde
        text = "e\u0301\u0303"
        result = normalize_text(text)
        assert unicodedata.is_normalized("NFC", result)

    def test_mixed_content_preservation(self) -> None:
        """Test that normalization preserves content, only changes form."""
        text = "café\ufb01rst"
        result = normalize_text(text, ligatures=True)
        # Should preserve meaning, just change representation
        assert "caf" in result
        assert "rst" in result

    def test_whitespace_only_lines(self) -> None:
        """Test handling of lines with only whitespace."""
        text = "Line 1\n    \nLine 2"
        result = normalize_text(text)
        assert result == "Line 1\n\nLine 2"

    def test_multiple_quote_types_in_sentence(self) -> None:
        """Test sentence with multiple quote types."""
        text = "He said \"I'm using 'air quotes' here\" ironically."
        result = normalize_text(text)
        assert result == "He said \"I'm using 'air quotes' here\" ironically."

    def test_non_breaking_space(self) -> None:
        """Test handling of non-breaking space (U+00A0)."""
        text = "Hello\u00a0world"
        # Non-breaking space is not normalized by default
        # (it has semantic meaning - prevents line breaks)
        result = normalize_text(text)
        # After whitespace normalization, it becomes regular space
        assert "Hello" in result and "world" in result
