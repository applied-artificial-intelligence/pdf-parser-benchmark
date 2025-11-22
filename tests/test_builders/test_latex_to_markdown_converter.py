"""
Unit tests for unified LaTeX→Markdown converter with fallback.

Tests the fallback logic between LaTeXML and Pandoc, including:
- LaTeXML success (no fallback)
- LaTeXML failure → Pandoc fallback → success
- Both fail → clear error
- Tool preference handling
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add builders to path
import sys
builders_path = Path(__file__).parent.parent.parent / 'builders'
sys.path.insert(0, str(builders_path))

# Import after path is set
import latex_to_markdown_converter
from latex_to_markdown_converter import (
    convert_latex_to_markdown,
    LatexToMarkdownConversionError,
)


class TestLatexToMarkdownConverter:
    """Test unified converter with fallback logic."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def simple_tex_file(self, temp_dir):
        """Create a simple .tex file for testing."""
        tex_file = temp_dir / "simple.tex"
        tex_file.write_text(
            r"""\documentclass{article}
\title{Test}
\begin{document}
\maketitle
\section{Introduction}
Test content.
\end{document}
"""
        )
        return tex_file

    @pytest.fixture
    def complex_tex_file(self, temp_dir):
        """Create a complex .tex file for testing."""
        tex_file = temp_dir / "complex.tex"
        tex_file.write_text(
            r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}
\section{Math}
Inline: $E = mc^2$
Display:
\begin{equation}
\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\end{equation}
\end{document}
"""
        )
        return tex_file

    def test_file_not_found(self, temp_dir):
        """Test error when input file doesn't exist."""
        nonexistent = temp_dir / "nonexistent.tex"
        output = temp_dir / "output.md"

        with pytest.raises(FileNotFoundError) as exc_info:
            convert_latex_to_markdown(nonexistent, output)

        assert "not found" in str(exc_info.value).lower()

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    @patch('latex_to_markdown_converter.LaTeXMLToMarkdownConverter')
    def test_latexml_success_no_fallback(
        self,
        mock_converter_class,
        mock_wrapper_class,
        simple_tex_file,
        temp_dir
    ):
        """Test successful LaTeXML conversion (no fallback to Pandoc)."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability check
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock LaTeXML wrapper
            mock_wrapper = MagicMock()
            mock_wrapper.convert_to_html.return_value = {
                'success': True,
                'returncode': 0,
                'stdout': '',
                'stderr': '',
                'error': None,
            }
            mock_wrapper_class.return_value = mock_wrapper

            # Mock LaTeXML to Markdown converter
            mock_converter = MagicMock()
            mock_converter.convert.return_value = "# Test\n\nTest content.\n"
            mock_converter_class.return_value = mock_converter

            # Convert
            result = convert_latex_to_markdown(simple_tex_file, output_file)

            # Verify result
            assert result['success'] is True
            assert result['tool_used'] == 'latexml'
            assert result['markdown_path'] == output_file
            assert isinstance(result['duration'], float)
            assert result['duration'] > 0

            # Verify LaTeXML was called
            mock_wrapper_class.assert_called_once()
            mock_wrapper.convert_to_html.assert_called_once()

            # Verify output was written
            assert output_file.exists()
            assert "Test" in output_file.read_text()

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    @patch('latex_to_markdown_converter.PandocWrapper')
    def test_latexml_fail_pandoc_success(
        self,
        mock_pandoc_class,
        mock_latexml_class,
        simple_tex_file,
        temp_dir
    ):
        """Test LaTeXML failure → Pandoc fallback → success."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability (available but fails)
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock LaTeXML wrapper (fails)
            mock_latexml = MagicMock()
            from latexml_wrapper import LaTeXMLConversionError
            mock_latexml.convert_to_html.side_effect = LaTeXMLConversionError("LaTeXML failed")
            mock_latexml_class.return_value = mock_latexml

            # Mock Pandoc availability
            with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=True):
                # Mock Pandoc wrapper (succeeds)
                mock_pandoc = MagicMock()
                mock_pandoc.convert_to_markdown.return_value = {
                    'success': True,
                    'returncode': 0,
                    'stdout': '',
                    'stderr': '',
                    'error': None,
                }
                mock_pandoc_class.return_value = mock_pandoc

                # Convert
                result = convert_latex_to_markdown(simple_tex_file, output_file)

                # Verify result
                assert result['success'] is True
                assert result['tool_used'] == 'pandoc'
                assert result['markdown_path'] == output_file

                # Verify errors list contains LaTeXML failure
                assert len(result['errors']) > 0
                assert any('LaTeXML' in err for err in result['errors'])

                # Verify both tools were attempted
                mock_latexml_class.assert_called_once()
                mock_pandoc_class.assert_called_once()

    @patch('latex_to_markdown_converter.PandocWrapper')
    def test_prefer_pandoc(self, mock_pandoc_class, simple_tex_file, temp_dir):
        """Test preferring Pandoc over LaTeXML."""
        output_file = temp_dir / "output.md"

        # Mock Pandoc availability
        with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=True):
            # Mock Pandoc wrapper (succeeds)
            mock_pandoc = MagicMock()
            mock_pandoc.convert_to_markdown.return_value = {
                'success': True,
                'returncode': 0,
                'stdout': '',
                'stderr': '',
                'error': None,
            }
            mock_pandoc_class.return_value = mock_pandoc

            # Convert with prefer_latexml=False
            result = convert_latex_to_markdown(
                simple_tex_file,
                output_file,
                prefer_latexml=False
            )

            # Verify result
            assert result['success'] is True
            assert result['tool_used'] == 'pandoc'

            # Verify Pandoc was called
            mock_pandoc_class.assert_called_once()

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    @patch('latex_to_markdown_converter.PandocWrapper')
    def test_both_tools_fail(
        self,
        mock_pandoc_class,
        mock_latexml_class,
        simple_tex_file,
        temp_dir
    ):
        """Test both LaTeXML and Pandoc fail → raise error."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability (available but fails)
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock LaTeXML wrapper (fails)
            mock_latexml = MagicMock()
            from latexml_wrapper import LaTeXMLConversionError
            mock_latexml.convert_to_html.side_effect = LaTeXMLConversionError("LaTeXML failed")
            mock_latexml_class.return_value = mock_latexml

            # Mock Pandoc availability (available but fails)
            with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=True):
                # Mock Pandoc wrapper (fails)
                mock_pandoc = MagicMock()
                from pandoc_wrapper import PandocConversionError
                mock_pandoc.convert_to_markdown.side_effect = PandocConversionError("Pandoc failed")
                mock_pandoc_class.return_value = mock_pandoc

                # Convert should raise error
                with pytest.raises(LatexToMarkdownConversionError) as exc_info:
                    convert_latex_to_markdown(simple_tex_file, output_file)

                # Verify error message contains details
                error_msg = str(exc_info.value)
                assert "all conversion methods failed" in error_msg.lower()
                assert "LaTeXML" in error_msg
                assert "Pandoc" in error_msg

    def test_neither_tool_installed(self, simple_tex_file, temp_dir):
        """Test error when neither LaTeXML nor Pandoc is installed."""
        output_file = temp_dir / "output.md"

        # Mock both tools as unavailable
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=False):
            with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=False):
                # Convert should raise error
                with pytest.raises(LatexToMarkdownConversionError) as exc_info:
                    convert_latex_to_markdown(simple_tex_file, output_file)

                # Verify error message
                error_msg = str(exc_info.value)
                assert "all conversion methods failed" in error_msg.lower()

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    def test_latexml_only(self, mock_latexml_class, simple_tex_file, temp_dir):
        """Test conversion when only LaTeXML is available."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability (available and succeeds)
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock Pandoc unavailable
            with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=False):
                # Mock LaTeXML wrapper
                mock_latexml = MagicMock()
                mock_latexml.convert_to_html.return_value = {
                    'success': True,
                    'returncode': 0,
                    'stdout': '',
                    'stderr': '',
                    'error': None,
                }
                mock_latexml_class.return_value = mock_latexml

                # Mock converter
                with patch('latex_to_markdown_converter.LaTeXMLToMarkdownConverter') as mock_conv:
                    mock_converter = MagicMock()
                    mock_converter.convert.return_value = "# Test\n"
                    mock_conv.return_value = mock_converter

                    # Convert
                    result = convert_latex_to_markdown(simple_tex_file, output_file)

                    # Verify result
                    assert result['success'] is True
                    assert result['tool_used'] == 'latexml'

    @patch('latex_to_markdown_converter.PandocWrapper')
    def test_pandoc_only(self, mock_pandoc_class, simple_tex_file, temp_dir):
        """Test conversion when only Pandoc is available."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML unavailable
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=False):
            # Mock Pandoc availability (available and succeeds)
            with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=True):
                # Mock Pandoc wrapper
                mock_pandoc = MagicMock()
                mock_pandoc.convert_to_markdown.return_value = {
                    'success': True,
                    'returncode': 0,
                    'stdout': '',
                    'stderr': '',
                    'error': None,
                }
                mock_pandoc_class.return_value = mock_pandoc

                # Convert
                result = convert_latex_to_markdown(simple_tex_file, output_file)

                # Verify result
                assert result['success'] is True
                assert result['tool_used'] == 'pandoc'

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    @patch('latex_to_markdown_converter.LaTeXMLToMarkdownConverter')
    def test_latexml_with_warnings(
        self,
        mock_converter_class,
        mock_wrapper_class,
        simple_tex_file,
        temp_dir
    ):
        """Test LaTeXML conversion with stderr warnings."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock LaTeXML wrapper with warnings in stderr
            mock_wrapper = MagicMock()
            mock_wrapper.convert_to_html.return_value = {
                'success': True,
                'returncode': 0,
                'stdout': '',
                'stderr': 'Warning: Missing package xyz',
                'error': None,
            }
            mock_wrapper_class.return_value = mock_wrapper

            # Mock converter
            mock_converter = MagicMock()
            mock_converter.convert.return_value = "# Test\n"
            mock_converter_class.return_value = mock_converter

            # Convert
            result = convert_latex_to_markdown(simple_tex_file, output_file)

            # Verify result
            assert result['success'] is True
            assert result['tool_used'] == 'latexml'

            # Verify warnings were captured
            assert len(result['warnings']) > 0
            assert any('Warning' in warn for warn in result['warnings'])

    @patch('latex_to_markdown_converter.PandocWrapper')
    def test_pandoc_with_warnings(self, mock_pandoc_class, simple_tex_file, temp_dir):
        """Test Pandoc conversion with stderr warnings."""
        output_file = temp_dir / "output.md"

        # Mock Pandoc availability
        with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=True):
            # Mock Pandoc wrapper with warnings
            mock_pandoc = MagicMock()
            mock_pandoc.convert_to_markdown.return_value = {
                'success': True,
                'returncode': 0,
                'stdout': '',
                'stderr': 'Warning: Unknown macro',
                'error': None,
            }
            mock_pandoc_class.return_value = mock_pandoc

            # Convert
            result = convert_latex_to_markdown(
                simple_tex_file,
                output_file,
                prefer_latexml=False
            )

            # Verify result
            assert result['success'] is True
            assert result['tool_used'] == 'pandoc'

            # Verify warnings were captured
            assert len(result['warnings']) > 0
            assert any('Warning' in warn for warn in result['warnings'])

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    def test_latexml_timeout(self, mock_wrapper_class, simple_tex_file, temp_dir):
        """Test LaTeXML timeout → fallback to Pandoc."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock LaTeXML wrapper (timeout)
            mock_latexml = MagicMock()
            from latexml_wrapper import LaTeXMLTimeoutError
            mock_latexml.convert_to_html.side_effect = LaTeXMLTimeoutError("Timeout")
            mock_wrapper_class.return_value = mock_latexml

            # Mock Pandoc availability
            with patch('latex_to_markdown_converter.PandocWrapper.is_available', return_value=True):
                with patch('latex_to_markdown_converter.PandocWrapper') as mock_pandoc_class:
                    # Mock Pandoc wrapper (succeeds)
                    mock_pandoc = MagicMock()
                    mock_pandoc.convert_to_markdown.return_value = {
                        'success': True,
                        'returncode': 0,
                        'stdout': '',
                        'stderr': '',
                        'error': None,
                    }
                    mock_pandoc_class.return_value = mock_pandoc

                    # Convert
                    result = convert_latex_to_markdown(simple_tex_file, output_file, timeout=60)

                    # Verify result
                    assert result['success'] is True
                    assert result['tool_used'] == 'pandoc'

                    # Verify errors contains timeout message
                    assert len(result['errors']) > 0
                    assert any('Timeout' in err or 'timeout' in err.lower() for err in result['errors'])

    @patch('latex_to_markdown_converter.LaTeXMLWrapper')
    @patch('latex_to_markdown_converter.LaTeXMLToMarkdownConverter')
    def test_custom_timeout(
        self,
        mock_converter_class,
        mock_wrapper_class,
        simple_tex_file,
        temp_dir
    ):
        """Test custom timeout is passed to converters."""
        output_file = temp_dir / "output.md"

        # Mock LaTeXML availability
        with patch('latex_to_markdown_converter.LaTeXMLWrapper.is_available', return_value=True):
            # Mock LaTeXML wrapper
            mock_wrapper = MagicMock()
            mock_wrapper.convert_to_html.return_value = {
                'success': True,
                'returncode': 0,
                'stdout': '',
                'stderr': '',
                'error': None,
            }
            mock_wrapper_class.return_value = mock_wrapper

            # Mock converter
            mock_converter = MagicMock()
            mock_converter.convert.return_value = "# Test\n"
            mock_converter_class.return_value = mock_converter

            # Convert with custom timeout
            result = convert_latex_to_markdown(simple_tex_file, output_file, timeout=600)

            # Verify timeout was passed to wrapper
            mock_wrapper_class.assert_called_once_with(timeout=600)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
