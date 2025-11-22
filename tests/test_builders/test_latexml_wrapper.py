"""
Unit tests for LaTeXML wrapper.

Tests subprocess wrapper for LaTeXML, error handling, timeouts,
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

from latexml_wrapper import (
    LaTeXMLWrapper,
    LaTeXMLError,
    LaTeXMLNotInstalledError,
    LaTeXMLConversionError,
    LaTeXMLTimeoutError,
    convert_tex_to_html,
    convert_tex_to_xml,
)


class TestLaTeXMLWrapper:
    """Test LaTeXMLWrapper class."""

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
        """Test static method to check if LaTeXML is available."""
        # This will return the actual state of the system
        available = LaTeXMLWrapper.is_available()
        assert isinstance(available, bool)

    def test_initialization_when_not_installed(self):
        """Test that initialization raises error when LaTeXML not installed."""
        with patch('latexml_wrapper.shutil.which', return_value=None):
            with pytest.raises(LaTeXMLNotInstalledError) as exc_info:
                LaTeXMLWrapper()

            assert "not installed" in str(exc_info.value).lower()
            assert "apt-get install latexml" in str(exc_info.value)

    @patch('latexml_wrapper.shutil.which')
    def test_initialization_with_latexmlc(self, mock_which):
        """Test initialization when latexmlc is available."""
        mock_which.side_effect = lambda cmd: '/usr/bin/latexmlc' if cmd == 'latexmlc' else None

        wrapper = LaTeXMLWrapper()

        assert wrapper.latexmlc_path == Path('/usr/bin/latexmlc')
        assert wrapper.latexml_path is None
        assert wrapper.timeout == LaTeXMLWrapper.DEFAULT_TIMEOUT

    @patch('latexml_wrapper.shutil.which')
    def test_initialization_with_latexml(self, mock_which):
        """Test initialization when latexml is available."""
        mock_which.side_effect = lambda cmd: '/usr/bin/latexml' if cmd == 'latexml' else None

        wrapper = LaTeXMLWrapper()

        assert wrapper.latexml_path == Path('/usr/bin/latexml')
        assert wrapper.latexmlc_path is None

    @patch('latexml_wrapper.shutil.which')
    def test_initialization_with_custom_paths(self, mock_which):
        """Test initialization with custom command paths."""
        custom_path = Path('/opt/latexml/bin/latexmlc')

        wrapper = LaTeXMLWrapper(latexmlc_path=custom_path)

        assert wrapper.latexmlc_path == custom_path

    @patch('latexml_wrapper.shutil.which')
    def test_initialization_with_custom_timeout(self, mock_which):
        """Test initialization with custom timeout."""
        mock_which.return_value = '/usr/bin/latexmlc'

        wrapper = LaTeXMLWrapper(timeout=600)

        assert wrapper.timeout == 600

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_to_html_success(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test successful HTML conversion."""
        mock_which.return_value = '/usr/bin/latexmlc'

        # Mock successful subprocess run
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Conversion successful"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.html"

        result = wrapper.convert_to_html(simple_tex_file, output_file)

        assert result['success'] is True
        assert result['returncode'] == 0
        assert result['output_file'] == output_file
        assert result['error'] is None

        # Verify subprocess was called with correct args
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert '/usr/bin/latexmlc' in args
        assert '--format' in args
        assert 'html5' in args
        assert '--dest' in args
        assert str(simple_tex_file) in args

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_to_html_failure(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test HTML conversion failure."""
        mock_which.return_value = '/usr/bin/latexmlc'

        # Mock failed subprocess run
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "Error: undefined control sequence"
        mock_run.return_value = mock_process

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.html"

        with pytest.raises(LaTeXMLConversionError) as exc_info:
            wrapper.convert_to_html(simple_tex_file, output_file)

        assert "exit code 1" in str(exc_info.value)
        assert "undefined control sequence" in str(exc_info.value)

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_to_html_timeout(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test HTML conversion timeout."""
        mock_which.return_value = '/usr/bin/latexmlc'

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='latexmlc', timeout=60)

        wrapper = LaTeXMLWrapper(timeout=60)
        output_file = temp_dir / "output.html"

        with pytest.raises(LaTeXMLTimeoutError) as exc_info:
            wrapper.convert_to_html(simple_tex_file, output_file)

        assert "timed out" in str(exc_info.value).lower()
        assert "60" in str(exc_info.value)

    @patch('latexml_wrapper.shutil.which')
    def test_convert_to_html_file_not_found(self, mock_which, temp_dir):
        """Test HTML conversion with non-existent input file."""
        mock_which.return_value = '/usr/bin/latexmlc'

        wrapper = LaTeXMLWrapper()
        nonexistent_file = temp_dir / "nonexistent.tex"
        output_file = temp_dir / "output.html"

        with pytest.raises(FileNotFoundError):
            wrapper.convert_to_html(nonexistent_file, output_file)

    @patch('latexml_wrapper.shutil.which')
    def test_convert_to_html_without_latexmlc(self, mock_which, simple_tex_file, temp_dir):
        """Test HTML conversion when latexmlc is not available."""
        # Only latexml available, not latexmlc
        mock_which.side_effect = lambda cmd: '/usr/bin/latexml' if cmd == 'latexml' else None

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.html"

        with pytest.raises(LaTeXMLNotInstalledError) as exc_info:
            wrapper.convert_to_html(simple_tex_file, output_file)

        assert "latexmlc is not available" in str(exc_info.value)

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_to_html_with_options(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test HTML conversion with custom options."""
        mock_which.return_value = '/usr/bin/latexmlc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.html"

        result = wrapper.convert_to_html(
            simple_tex_file,
            output_file,
            format='xhtml',
            quiet=True,
            mathml=True,
        )

        assert result['success'] is True

        # Verify options were passed
        args = mock_run.call_args[0][0]
        assert 'xhtml' in args
        assert '--quiet' in args
        assert '--mathml' in args

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_to_xml_success(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test successful XML conversion."""
        mock_which.side_effect = lambda cmd: '/usr/bin/latexml' if cmd == 'latexml' else None

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Conversion successful"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.xml"

        result = wrapper.convert_to_xml(simple_tex_file, output_file)

        assert result['success'] is True
        assert result['returncode'] == 0
        assert result['output_file'] == output_file

        # Verify subprocess was called with correct args
        args = mock_run.call_args[0][0]
        assert '/usr/bin/latexml' in args
        assert '--dest' in args
        assert str(simple_tex_file) in args

    @patch('latexml_wrapper.shutil.which')
    def test_convert_to_xml_without_latexml(self, mock_which, simple_tex_file, temp_dir):
        """Test XML conversion when latexml is not available."""
        # Only latexmlc available, not latexml
        mock_which.side_effect = lambda cmd: '/usr/bin/latexmlc' if cmd == 'latexmlc' else None

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.xml"

        with pytest.raises(LaTeXMLNotInstalledError) as exc_info:
            wrapper.convert_to_xml(simple_tex_file, output_file)

        assert "latexml is not available" in str(exc_info.value)

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_to_xml_with_verbose(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test XML conversion with verbose option."""
        mock_which.side_effect = lambda cmd: '/usr/bin/latexml' if cmd == 'latexml' else None

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Verbose output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.xml"

        result = wrapper.convert_to_xml(simple_tex_file, output_file, verbose=True)

        assert result['success'] is True

        # Verify verbose option was passed
        args = mock_run.call_args[0][0]
        assert '--verbose' in args


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

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_tex_to_html_convenience(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test convert_tex_to_html convenience function."""
        mock_which.return_value = '/usr/bin/latexmlc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        output_file = temp_dir / "output.html"

        result = convert_tex_to_html(simple_tex_file, output_file)

        assert result['success'] is True
        mock_run.assert_called_once()

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_tex_to_xml_convenience(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test convert_tex_to_xml convenience function."""
        mock_which.side_effect = lambda cmd: '/usr/bin/latexml' if cmd == 'latexml' else None

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        output_file = temp_dir / "output.xml"

        result = convert_tex_to_xml(simple_tex_file, output_file)

        assert result['success'] is True
        mock_run.assert_called_once()

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_convert_tex_to_html_with_timeout(self, mock_run, mock_which, simple_tex_file, temp_dir):
        """Test convenience function with custom timeout."""
        mock_which.return_value = '/usr/bin/latexmlc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        output_file = temp_dir / "output.html"

        result = convert_tex_to_html(simple_tex_file, output_file, timeout=600)

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

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_conversion_with_stderr_output(self, mock_run, mock_which, malformed_tex_file, temp_dir):
        """Test that stderr is captured even on success."""
        mock_which.return_value = '/usr/bin/latexmlc'

        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Conversion completed"
        mock_process.stderr = "Warning: Some packages not found"
        mock_run.return_value = mock_process

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.html"

        result = wrapper.convert_to_html(malformed_tex_file, output_file)

        assert result['success'] is True
        assert result['stderr'] == "Warning: Some packages not found"

    @patch('latexml_wrapper.shutil.which')
    @patch('latexml_wrapper.subprocess.run')
    def test_unexpected_exception(self, mock_run, mock_which, malformed_tex_file, temp_dir):
        """Test handling of unexpected exceptions."""
        mock_which.return_value = '/usr/bin/latexmlc'

        # Mock unexpected exception
        mock_run.side_effect = OSError("Unexpected system error")

        wrapper = LaTeXMLWrapper()
        output_file = temp_dir / "output.html"

        with pytest.raises(LaTeXMLConversionError) as exc_info:
            wrapper.convert_to_html(malformed_tex_file, output_file)

        assert "unexpected error" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
