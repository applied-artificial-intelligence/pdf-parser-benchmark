"""
Unit tests for Pandoc wrapper.

Tests subprocess wrapper for Pandoc, error handling, timeouts,
and conversion functionality.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add builders to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'builders'))

from pandoc_wrapper import (
    PandocWrapper,
    PandocError,
    PandocNotInstalledError,
    PandocConversionError,
    PandocTimeoutError,
    convert_tex_to_markdown,
)


class TestPandocWrapper:
    """Test PandocWrapper class."""

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
\usepackage{amsmath}

\title{Simple Test Document}
\author{Test Author}

\begin{document}
\maketitle

\section{Introduction}
This is a simple test document.

\end{document}
"""
        )
        return tex_file

    @pytest.fixture
    def math_tex_file(self, temp_dir):
        """Create a .tex file with math for testing."""
        tex_file = temp_dir / "math.tex"
        tex_file.write_text(
            r"""\documentclass{article}
\usepackage{amsmath}

\begin{document}

\section{Math Test}

Inline math: $E = mc^2$

Display math:
\begin{equation}
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
\end{equation}

\end{document}
"""
        )
        return tex_file

    def test_is_available(self):
        """Test static method to check if Pandoc is available."""
        # This will return the actual state of the system
        available = PandocWrapper.is_available()
        assert isinstance(available, bool)

    def test_initialization_when_not_installed(self):
        """Test that initialization raises error when Pandoc not installed."""
        with patch('pandoc_wrapper.shutil.which', return_value=None):
            with pytest.raises(PandocNotInstalledError) as exc_info:
                PandocWrapper()

            assert "not installed" in str(exc_info.value).lower()
            assert "apt-get install pandoc" in str(exc_info.value)

    @patch('pandoc_wrapper.shutil.which')
    def test_initialization_with_pandoc(self, mock_which):
        """Test initialization when pandoc is available."""
        mock_which.return_value = '/usr/bin/pandoc'

        wrapper = PandocWrapper()

        assert wrapper.pandoc_path == Path('/usr/bin/pandoc')
        assert wrapper.timeout == PandocWrapper.DEFAULT_TIMEOUT

    @patch('pandoc_wrapper.shutil.which')
    def test_initialization_with_custom_path(self, mock_which):
        """Test initialization with custom command path."""
        custom_path = Path('/opt/pandoc/bin/pandoc')

        wrapper = PandocWrapper(pandoc_path=custom_path)

        assert wrapper.pandoc_path == custom_path

    @patch('pandoc_wrapper.shutil.which')
    def test_initialization_with_custom_timeout(self, mock_which):
        """Test initialization with custom timeout."""
        mock_which.return_value = '/usr/bin/pandoc'

        wrapper = PandocWrapper(timeout=600)

        assert wrapper.timeout == 600

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_success(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test successful Markdown conversion."""
        mock_which.return_value = '/usr/bin/pandoc'

        # Mock successful subprocess run
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        result = wrapper.convert_to_markdown(simple_tex_file, output_file)

        assert result['success'] is True
        assert result['returncode'] == 0
        assert result['output_file'] == output_file
        assert result['error'] is None

        # Verify subprocess was called with correct args
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert '/usr/bin/pandoc' in args
        assert str(simple_tex_file) in args
        assert '-o' in args
        assert str(output_file) in args
        assert '--from' in args
        assert 'latex' in args
        assert '--to' in args
        assert 'markdown' in args

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_failure(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion failure."""
        mock_which.return_value = '/usr/bin/pandoc'

        # Mock failed subprocess run
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "Error: undefined control sequence"
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        with pytest.raises(PandocConversionError) as exc_info:
            wrapper.convert_to_markdown(simple_tex_file, output_file)

        assert "exit code 1" in str(exc_info.value)
        assert "undefined control sequence" in str(exc_info.value)

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_timeout(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion timeout."""
        mock_which.return_value = '/usr/bin/pandoc'

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='pandoc', timeout=60)

        wrapper = PandocWrapper(timeout=60)
        output_file = temp_dir / "output.md"

        with pytest.raises(PandocTimeoutError) as exc_info:
            wrapper.convert_to_markdown(simple_tex_file, output_file)

        assert "timed out" in str(exc_info.value).lower()
        assert "60" in str(exc_info.value)

    @patch('pandoc_wrapper.shutil.which')
    def test_convert_to_markdown_file_not_found(self, mock_which, temp_dir):
        """Test Markdown conversion with non-existent input file."""
        mock_which.return_value = '/usr/bin/pandoc'

        wrapper = PandocWrapper()
        nonexistent_file = temp_dir / "nonexistent.tex"
        output_file = temp_dir / "output.md"

        with pytest.raises(FileNotFoundError):
            wrapper.convert_to_markdown(nonexistent_file, output_file)

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_with_options(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion with custom options."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        result = wrapper.convert_to_markdown(
            simple_tex_file,
            output_file,
            from_format='latex',
            to_format='markdown',
            standalone=True,
            wrap='none',
            columns=100,
        )

        assert result['success'] is True

        # Verify options were passed
        args = mock_run.call_args[0][0]
        assert '--from' in args
        assert 'latex' in args
        assert '--to' in args
        assert 'markdown' in args
        assert '--standalone' in args
        assert '--wrap' in args
        assert 'none' in args
        assert '--columns' in args
        assert '100' in args

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_with_quiet(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion with quiet option."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        result = wrapper.convert_to_markdown(simple_tex_file, output_file, quiet=True)

        assert result['success'] is True

        # Verify quiet option was passed
        args = mock_run.call_args[0][0]
        assert '--quiet' in args

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_with_verbose(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion with verbose option."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Verbose output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        result = wrapper.convert_to_markdown(simple_tex_file, output_file, verbose=True)

        assert result['success'] is True

        # Verify verbose option was passed
        args = mock_run.call_args[0][0]
        assert '--verbose' in args

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_without_standalone(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion without standalone option."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        result = wrapper.convert_to_markdown(simple_tex_file, output_file, standalone=False)

        assert result['success'] is True

        # Verify standalone option was not passed
        args = mock_run.call_args[0][0]
        assert '--standalone' not in args

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_to_markdown_with_extract_media(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test Markdown conversion with extract_media option."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"
        media_dir = temp_dir / "media"

        result = wrapper.convert_to_markdown(
            simple_tex_file,
            output_file,
            extract_media=str(media_dir)
        )

        assert result['success'] is True

        # Verify extract_media option was passed
        args = mock_run.call_args[0][0]
        assert '--extract-media' in args
        assert str(media_dir) in args


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def simple_tex_file(self, temp_dir):
        """Create a simple .tex file for testing."""
        tex_file = temp_dir / "simple.tex"
        tex_file.write_text(r"\documentclass{article}\begin{document}Test\end{document}")
        return tex_file

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_tex_to_markdown_convenience(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test convert_tex_to_markdown convenience function."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        output_file = temp_dir / "output.md"

        result = convert_tex_to_markdown(simple_tex_file, output_file)

        assert result['success'] is True
        mock_run.assert_called_once()

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_convert_tex_to_markdown_with_timeout(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test convenience function with custom timeout."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        output_file = temp_dir / "output.md"

        result = convert_tex_to_markdown(simple_tex_file, output_file, timeout=600)

        assert result['success'] is True

        # Verify timeout was used
        assert mock_run.call_args[1]['timeout'] == 600


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def malformed_tex_file(self, temp_dir):
        """Create a malformed .tex file for testing error handling."""
        tex_file = temp_dir / "malformed.tex"
        tex_file.write_text(
            r"""\documentclass{article}
\begin{document}
\undefinedcommand{test}
\end{document}
"""
        )
        return tex_file

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_conversion_with_stderr_output(self, mock_run, mock_which, malformed_tex_file, temp_dir):
        """Test that stderr is captured even on success."""
        mock_which.return_value = '/usr/bin/pandoc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = "Warning: Some packages not found"
        mock_run.return_value = mock_process

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        result = wrapper.convert_to_markdown(malformed_tex_file, output_file)

        assert result['success'] is True
        assert result['stderr'] == "Warning: Some packages not found"

    @patch('pandoc_wrapper.shutil.which')
    @patch('pandoc_wrapper.subprocess.run')
    def test_unexpected_exception(self, mock_run, mock_which, malformed_tex_file, temp_dir):
        """Test handling of unexpected exceptions."""
        mock_which.return_value = '/usr/bin/pandoc'

        # Mock unexpected exception
        mock_run.side_effect = OSError("Unexpected system error")

        wrapper = PandocWrapper()
        output_file = temp_dir / "output.md"

        with pytest.raises(PandocConversionError) as exc_info:
            wrapper.convert_to_markdown(malformed_tex_file, output_file)

        assert "unexpected error" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
