"""
Unit tests for LaTeX source extractor.

Tests extraction of LaTeX source files from arXiv tarballs,
main .tex file identification, and dependency handling.
"""

# Add builders to path
import sys
import tarfile
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "builders"))

from latex_extractor import LaTeXExtractor, extract_latex_source


class TestLaTeXExtractor:
    """Test LaTeXExtractor class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def simple_tarball(self, temp_dir):
        """
        Create a simple tarball with a single .tex file.

        Structure:
        - main.tex (with \\documentclass and \\begin{document})
        """
        # Create source directory
        source_dir = temp_dir / "simple_source"
        source_dir.mkdir()

        # Create main.tex
        main_tex = source_dir / "main.tex"
        main_tex.write_text(
            r"""\documentclass{article}
\usepackage{amsmath}

\title{Simple Test Paper}
\author{Test Author}

\begin{document}
\maketitle

\section{Introduction}
This is a simple test document.

\section{Methods}
We used standard methods.

\end{document}
"""
        )

        # Create tarball
        tarball_path = temp_dir / "simple.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(main_tex, arcname="main.tex")

        return tarball_path

    @pytest.fixture
    def multi_file_tarball(self, temp_dir):
        """
        Create a tarball with multiple .tex files and dependencies.

        Structure:
        - paper.tex (main file)
        - sections/intro.tex (included file)
        - sections/methods.tex (included file)
        - figures/diagram.png
        - references.bib
        - custom.sty
        """
        # Create source directory
        source_dir = temp_dir / "multi_source"
        source_dir.mkdir()

        # Create main paper.tex
        paper_tex = source_dir / "paper.tex"
        paper_tex.write_text(
            r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{custom}

\title{Multi-File Test Paper}
\author{Test Author}

\begin{document}
\maketitle

\input{sections/intro}
\input{sections/methods}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""
        )

        # Create sections subdirectory
        sections_dir = source_dir / "sections"
        sections_dir.mkdir()

        # Create intro.tex
        intro_tex = sections_dir / "intro.tex"
        intro_tex.write_text(
            r"""\section{Introduction}
This is the introduction.

\begin{figure}
\centering
\includegraphics{figures/diagram.png}
\caption{System diagram}
\end{figure}
"""
        )

        # Create methods.tex
        methods_tex = sections_dir / "methods.tex"
        methods_tex.write_text(
            r"""\section{Methods}
We used standard methods.
"""
        )

        # Create figures subdirectory
        figures_dir = source_dir / "figures"
        figures_dir.mkdir()

        # Create dummy PNG (just a few bytes, not a real image)
        diagram_png = figures_dir / "diagram.png"
        diagram_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        # Create references.bib
        bib_file = source_dir / "references.bib"
        bib_file.write_text(
            r"""@article{example2023,
  author = {Example, A.},
  title = {An Example Paper},
  journal = {Journal of Examples},
  year = {2023}
}
"""
        )

        # Create custom.sty
        sty_file = source_dir / "custom.sty"
        sty_file.write_text(
            r"""\ProvidesPackage{custom}
\newcommand{\customcmd}{Custom Command}
"""
        )

        # Create tarball
        tarball_path = temp_dir / "multi_file.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    tar.add(file_path, arcname=str(arcname))

        return tarball_path

    @pytest.fixture
    def ambiguous_tarball(self, temp_dir):
        """
        Create a tarball with multiple .tex files where the main file is ambiguous.

        Structure:
        - document.tex (has \\documentclass but minimal content)
        - article.tex (also has \\documentclass and more content)
        - helper.tex (no \\documentclass, just macros)
        """
        source_dir = temp_dir / "ambiguous_source"
        source_dir.mkdir()

        # Create document.tex (smaller file)
        document_tex = source_dir / "document.tex"
        document_tex.write_text(
            r"""\documentclass{article}
\begin{document}
Minimal content.
\end{document}
"""
        )

        # Create article.tex (larger file with more indicators)
        article_tex = source_dir / "article.tex"
        article_tex.write_text(
            r"""\documentclass{article}
\usepackage{amsmath}

\title{Test Article}
\author{Test Author}

\begin{document}
\maketitle

\section{Introduction}
This is the main article file.

\section{Methods}
Detailed methods.

\section{Results}
Results go here.

\end{document}
"""
        )

        # Create helper.tex (no documentclass)
        helper_tex = source_dir / "helper.tex"
        helper_tex.write_text(
            r"""\newcommand{\mymacro}{Some macro}
"""
        )

        # Create tarball
        tarball_path = temp_dir / "ambiguous.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(document_tex, arcname="document.tex")
            tar.add(article_tex, arcname="article.tex")
            tar.add(helper_tex, arcname="helper.tex")

        return tarball_path

    @pytest.fixture
    def tarball_with_build_artifacts(self, temp_dir):
        """
        Create a tarball with build artifacts that should be excluded.

        Structure:
        - main.tex
        - main.aux (build artifact)
        - main.log (build artifact)
        - main.pdf (output, not source)
        """
        source_dir = temp_dir / "artifacts_source"
        source_dir.mkdir()

        # Create main.tex
        main_tex = source_dir / "main.tex"
        main_tex.write_text(
            r"""\documentclass{article}
\begin{document}
Test content.
\end{document}
"""
        )

        # Create build artifacts
        (source_dir / "main.aux").write_text("\\relax")
        (source_dir / "main.log").write_text("LaTeX log file")
        (source_dir / "main.pdf").write_bytes(b"%PDF-1.4" + b"\x00" * 100)

        # Create tarball
        tarball_path = temp_dir / "with_artifacts.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    tar.add(file_path, arcname=file_path.name)

        return tarball_path

    def test_extract_simple_tarball(self, simple_tarball, temp_dir):
        """Test extraction of a simple tarball with one .tex file."""
        output_dir = temp_dir / "output_simple"

        extractor = LaTeXExtractor(simple_tarball, output_dir)
        result = extractor.extract()

        # Check success
        assert result["success"] is True
        assert result["error"] is None

        # Check main .tex file identified
        assert result["main_tex"] is not None
        assert result["main_tex"].name == "main.tex"

        # Check file was extracted
        assert (output_dir / "main.tex").exists()

        # Check content
        content = result["main_tex"].read_text()
        assert r"\documentclass{article}" in content
        assert r"\begin{document}" in content

    def test_extract_multi_file_tarball(self, multi_file_tarball, temp_dir):
        """Test extraction of a multi-file tarball with dependencies."""
        output_dir = temp_dir / "output_multi"

        extractor = LaTeXExtractor(multi_file_tarball, output_dir)
        result = extractor.extract()

        # Check success
        assert result["success"] is True
        assert result["error"] is None

        # Check main .tex file identified
        assert result["main_tex"] is not None
        assert result["main_tex"].name == "paper.tex"

        # Check all files extracted
        assert len(result["all_files"]) >= 6  # paper.tex + 2 sections + image + bib + sty

        # Check dependencies identified
        dependency_names = {dep.name for dep in result["dependencies"]}
        assert "diagram.png" in dependency_names
        assert "references.bib" in dependency_names
        assert "custom.sty" in dependency_names

        # Check structure preserved
        assert (output_dir / "paper.tex").exists()
        assert (output_dir / "sections" / "intro.tex").exists()
        assert (output_dir / "sections" / "methods.tex").exists()
        assert (output_dir / "figures" / "diagram.png").exists()

    def test_identify_main_tex_by_name(self, simple_tarball, temp_dir):
        """Test main .tex file identification by common name (main.tex)."""
        output_dir = temp_dir / "output_by_name"

        extractor = LaTeXExtractor(simple_tarball, output_dir)
        result = extractor.extract()

        assert result["success"] is True
        assert result["main_tex"].name == "main.tex"

    def test_identify_main_tex_by_content(self, ambiguous_tarball, temp_dir):
        """Test main .tex file identification by content score."""
        output_dir = temp_dir / "output_by_content"

        extractor = LaTeXExtractor(ambiguous_tarball, output_dir)
        result = extractor.extract()

        assert result["success"] is True
        # article.tex should be identified (more content, higher score)
        assert result["main_tex"].name == "article.tex"

    def test_exclude_build_artifacts(self, tarball_with_build_artifacts, temp_dir):
        """Test that build artifacts are excluded from extraction."""
        output_dir = temp_dir / "output_no_artifacts"

        extractor = LaTeXExtractor(tarball_with_build_artifacts, output_dir)
        result = extractor.extract()

        assert result["success"] is True

        # Check that .tex file was extracted
        extracted_names = {f.name for f in result["all_files"]}
        assert "main.tex" in extracted_names

        # Check that build artifacts were excluded
        assert "main.aux" not in extracted_names
        assert "main.log" not in extracted_names
        # Note: .pdf is not in exclude list (could be a figure), so it may be extracted

    def test_empty_tarball(self, temp_dir):
        """Test handling of empty tarball."""
        # Create empty tarball
        tarball_path = temp_dir / "empty.tar.gz"
        with tarfile.open(tarball_path, "w:gz"):
            pass

        output_dir = temp_dir / "output_empty"

        extractor = LaTeXExtractor(tarball_path, output_dir)
        result = extractor.extract()

        assert result["success"] is False
        assert "No files extracted" in result["error"]

    def test_tarball_without_tex_files(self, temp_dir):
        """Test handling of tarball without .tex files."""
        # Create tarball with only non-.tex files
        source_dir = temp_dir / "no_tex_source"
        source_dir.mkdir()

        (source_dir / "readme.txt").write_text("No LaTeX here")
        (source_dir / "data.csv").write_text("1,2,3")

        tarball_path = temp_dir / "no_tex.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(source_dir / "readme.txt", arcname="readme.txt")
            tar.add(source_dir / "data.csv", arcname="data.csv")

        output_dir = temp_dir / "output_no_tex"

        extractor = LaTeXExtractor(tarball_path, output_dir)
        result = extractor.extract()

        assert result["success"] is False
        assert "No .tex files found" in result["error"]

    def test_convenience_function(self, simple_tarball, temp_dir):
        """Test the convenience function extract_latex_source()."""
        output_dir = temp_dir / "output_convenience"

        result = extract_latex_source(simple_tarball, output_dir)

        assert result["success"] is True
        assert result["main_tex"] is not None
        assert result["main_tex"].name == "main.tex"

    def test_copy_to_directory(self, multi_file_tarball, temp_dir):
        """Test copying extracted files to a new directory."""
        output_dir = temp_dir / "output_original"
        dest_dir = temp_dir / "output_copy"

        extractor = LaTeXExtractor(multi_file_tarball, output_dir)
        result = extractor.copy_to_directory(dest_dir, preserve_structure=True)

        assert result["success"] is True
        assert "copied_to" in result

        # Check files were copied with structure preserved
        assert (dest_dir / "paper.tex").exists()
        assert (dest_dir / "sections" / "intro.tex").exists()
        assert (dest_dir / "figures" / "diagram.png").exists()

    def test_copy_to_directory_flat(self, multi_file_tarball, temp_dir):
        """Test copying extracted files to a new directory (flat structure)."""
        output_dir = temp_dir / "output_original_flat"
        dest_dir = temp_dir / "output_copy_flat"

        extractor = LaTeXExtractor(multi_file_tarball, output_dir)
        result = extractor.copy_to_directory(dest_dir, preserve_structure=False)

        assert result["success"] is True

        # Check files were copied (but in flat structure)
        assert (dest_dir / "paper.tex").exists()
        assert (dest_dir / "intro.tex").exists()  # Flattened from sections/
        assert (dest_dir / "diagram.png").exists()  # Flattened from figures/

        # Check subdirectories were NOT created
        assert not (dest_dir / "sections").exists()
        assert not (dest_dir / "figures").exists()


class TestMainFileHeuristics:
    """Test main .tex file identification heuristics."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def create_tex_file(self, path: Path, content: str) -> None:
        """Helper to create a .tex file with given content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def test_heuristic_common_names(self, temp_dir):
        """Test that common main file names are recognized."""
        common_names = ["main.tex", "paper.tex", "article.tex", "manuscript.tex"]

        for name in common_names:
            output_dir = temp_dir / f"test_{name}"
            output_dir.mkdir()

            # Create file with minimal content
            tex_file = output_dir / name
            self.create_tex_file(
                tex_file, r"\documentclass{article}\begin{document}Test\end{document}"
            )

            extractor = LaTeXExtractor(Path("dummy.tar.gz"), output_dir)
            main_file = extractor._identify_main_tex([tex_file])

            assert main_file is not None
            assert main_file.name == name

    def test_heuristic_documentclass_required(self, temp_dir):
        """Test that \\documentclass is required for content-based identification."""
        output_dir = temp_dir / "test_documentclass"
        output_dir.mkdir()

        # File without \documentclass should not be identified as main
        tex_file = output_dir / "test.tex"
        self.create_tex_file(tex_file, r"\begin{document}Test\end{document}")

        extractor = LaTeXExtractor(Path("dummy.tar.gz"), output_dir)
        main_file = extractor._identify_main_tex([tex_file])

        # Should fall back to size-based heuristic (returns the only file)
        assert main_file == tex_file

    def test_heuristic_scoring(self, temp_dir):
        """Test that files with more indicators get higher scores."""
        output_dir = temp_dir / "test_scoring"
        output_dir.mkdir()

        # Minimal file
        minimal = output_dir / "minimal.tex"
        self.create_tex_file(minimal, r"\documentclass{article}\begin{document}Test\end{document}")

        # Rich file with more indicators
        rich = output_dir / "rich.tex"
        self.create_tex_file(
            rich,
            r"""\documentclass{article}
\begin{document}
\maketitle
\section{Introduction}
\section{Methods}
\end{document}""",
        )

        extractor = LaTeXExtractor(Path("dummy.tar.gz"), output_dir)
        main_file = extractor._identify_main_tex([minimal, rich])

        assert main_file is not None
        assert main_file.name == "rich.tex"  # Should have higher score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
