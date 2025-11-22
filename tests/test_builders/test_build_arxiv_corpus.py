"""
Integration tests for arXiv corpus builder.

These tests validate the complete corpus building pipeline:
- Loading targets from YAML
- Processing papers (download, extract, convert)
- Metadata generation
- Error handling and fallback mechanisms
"""

# Mock the imports before importing the builder
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "builders"))


@pytest.fixture
def mock_arxiv_client():
    """Mock ArxivClient for testing."""
    with patch("build_arxiv_corpus.ArxivClient") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock successful downloads
        mock_client.download_pdf = Mock()
        mock_client.download_source = Mock()

        yield mock_client


@pytest.fixture
def mock_latex_extractor():
    """Mock LaTeXExtractor for testing."""
    with patch("build_arxiv_corpus.LaTeXExtractor") as mock_extractor_class:
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor

        # Mock successful extraction
        mock_extractor.extract.return_value = {
            "success": True,
            "main_tex": Path("/tmp/extracted/main.tex"),
            "all_files": [
                Path("/tmp/extracted/main.tex"),
                Path("/tmp/extracted/refs.bib"),
            ],
            "dependencies": [Path("/tmp/extracted/refs.bib")],
            "error": None,
        }

        yield mock_extractor


@pytest.fixture
def mock_latex_converter():
    """Mock convert_latex_to_markdown for testing."""
    with patch("build_arxiv_corpus.convert_latex_to_markdown") as mock_convert:
        mock_convert.return_value = {
            "success": True,
            "tool_used": "latexml",
            "markdown_path": Path("/tmp/output/ground_truth.md"),
            "duration": 12.5,
            "warnings": [],
            "errors": [],
        }

        yield mock_convert


@pytest.fixture
def sample_targets_file(tmp_path):
    """Create a sample targets YAML file."""
    targets_data = {
        "description": "Test arXiv corpus",
        "total_documents": 2,
        "documents": [
            {
                "id": "arxiv_001",
                "arxiv_id": "2303.18223",
                "title": "A Survey of Large Language Models",
                "authors": ["Author 1", "Author 2"],
                "categories": ["cs.CL", "cs.AI"],
                "publication_date": "2023-03-31",
                "url_pdf": "https://arxiv.org/pdf/2303.18223.pdf",
                "url_source": "https://arxiv.org/e-print/2303.18223",
                "url_ar5iv": "https://ar5iv.labs.arxiv.org/html/2303.18223",
                "pages": 62,
                "license": "arXiv non-exclusive license",
                "complexity": {
                    "math": "low",
                    "tables": "high",
                    "figures": "high",
                },
                "layout": "two-column",
                "notes": "Test paper 1",
            },
            {
                "id": "arxiv_002",
                "arxiv_id": "2303.08774",
                "title": "GPT-4 Technical Report",
                "authors": ["OpenAI"],
                "categories": ["cs.CL", "cs.AI"],
                "publication_date": "2023-03-15",
                "url_pdf": "https://arxiv.org/pdf/2303.08774.pdf",
                "url_source": "https://arxiv.org/e-print/2303.08774",
                "url_ar5iv": "https://ar5iv.labs.arxiv.org/html/2303.08774",
                "pages": 100,
                "license": "arXiv non-exclusive license",
                "complexity": {
                    "math": "low",
                    "tables": "high",
                    "figures": "high",
                },
                "layout": "single-column",
                "notes": "Test paper 2",
            },
        ],
    }

    targets_file = tmp_path / "test_targets.yaml"
    with open(targets_file, "w") as f:
        yaml.dump(targets_data, f)

    return targets_file


class TestArxivCorpusBuilder:
    """Test ArxivCorpusBuilder class."""

    def test_load_targets(self, sample_targets_file, tmp_path):
        """Test loading targets from YAML file."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        builder = ArxivCorpusBuilder(
            targets_file=sample_targets_file,
            output_dir=tmp_path / "corpus",
        )

        targets = builder._load_targets()

        assert len(targets) == 2
        assert targets[0]["arxiv_id"] == "2303.18223"
        assert targets[1]["arxiv_id"] == "2303.08774"

    def test_load_targets_missing_file(self, tmp_path):
        """Test loading targets from missing file."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        builder = ArxivCorpusBuilder(
            targets_file=tmp_path / "missing.yaml",
            output_dir=tmp_path / "corpus",
        )

        targets = builder._load_targets()

        assert targets == []

    def test_build_with_limit(
        self,
        sample_targets_file,
        tmp_path,
        mock_arxiv_client,
        mock_latex_extractor,
        mock_latex_converter,
    ):
        """Test building corpus with limit."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        # Create mock PDF and markdown files
        output_dir = tmp_path / "corpus"

        def create_mock_files(*args, **kwargs):
            """Create mock files when called."""
            # Create paper directory
            paper_dir = output_dir / "2303.18223"
            paper_dir.mkdir(parents=True, exist_ok=True)

            # Create mock files
            (paper_dir / "paper.pdf").write_bytes(b"mock pdf")
            (paper_dir / "source.tar.gz").write_bytes(b"mock tarball")
            (paper_dir / "ground_truth.md").write_text("# Mock Markdown")

        # Patch file creation
        mock_arxiv_client.download_pdf.side_effect = create_mock_files

        builder = ArxivCorpusBuilder(
            targets_file=sample_targets_file,
            output_dir=output_dir,
            limit=1,
        )

        stats = builder.build()

        assert stats["total"] == 1
        assert stats["success"] <= 1
        assert stats["failed"] + stats["success"] == 1

    def test_skip_existing(
        self,
        sample_targets_file,
        tmp_path,
        mock_arxiv_client,
        mock_latex_extractor,
        mock_latex_converter,
    ):
        """Test skipping existing papers."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        output_dir = tmp_path / "corpus"

        # Create existing paper
        paper_dir = output_dir / "2303.18223"
        paper_dir.mkdir(parents=True, exist_ok=True)
        (paper_dir / "ground_truth.md").write_text("# Existing")

        builder = ArxivCorpusBuilder(
            targets_file=sample_targets_file,
            output_dir=output_dir,
            skip_existing=True,
            limit=1,
        )

        stats = builder.build()

        assert stats["skipped"] == 1
        assert stats["success"] == 0
        assert stats["failed"] == 0

    def test_calculate_hash(self, tmp_path):
        """Test SHA256 hash calculation."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        builder = ArxivCorpusBuilder(
            targets_file=Path("dummy.yaml"),
            output_dir=tmp_path,
        )

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        hash_value = builder._calculate_hash(test_file)

        assert hash_value.startswith("sha256:")
        assert len(hash_value) == 71  # 'sha256:' + 64 hex chars

    def test_create_metadata(self, tmp_path):
        """Test metadata creation."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        builder = ArxivCorpusBuilder(
            targets_file=Path("dummy.yaml"),
            output_dir=tmp_path,
        )

        # Create test files
        pdf_path = tmp_path / "paper.pdf"
        pdf_path.write_bytes(b"mock pdf content")

        gt_path = tmp_path / "ground_truth.md"
        gt_path.write_text("# Mock Markdown")

        target = {
            "id": "arxiv_001",
            "arxiv_id": "2303.18223",
            "title": "Test Paper",
            "authors": ["Author 1"],
            "categories": ["cs.CL"],
            "publication_date": "2023-03-31",
            "url_pdf": "https://arxiv.org/pdf/2303.18223.pdf",
            "url_source": "https://arxiv.org/e-print/2303.18223",
            "pages": 10,
            "license": "CC-BY-4.0",
            "complexity": {"math": "low", "tables": "low", "figures": "low"},
            "layout": "single-column",
        }

        conversion_result = {
            "success": True,
            "tool_used": "latexml",
            "duration": 10.0,
            "warnings": [],
            "errors": [],
        }

        metadata = builder._create_metadata(
            target=target,
            pdf_path=pdf_path,
            ground_truth_path=gt_path,
            conversion_result=conversion_result,
        )

        assert metadata["arxiv_id"] == "2303.18223"
        assert metadata["title"] == "Test Paper"
        assert metadata["conversion_method"] == "latexml"
        assert metadata["pdf_hash"].startswith("sha256:")
        assert metadata["ground_truth_hash"].startswith("sha256:")
        assert metadata["pdf_size_bytes"] > 0

    def test_percentage_calculation(self, tmp_path):
        """Test percentage calculation."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        builder = ArxivCorpusBuilder(
            targets_file=Path("dummy.yaml"),
            output_dir=tmp_path,
        )

        assert builder._percentage(8, 10) == 80.0
        assert builder._percentage(0, 10) == 0.0
        assert builder._percentage(10, 10) == 100.0
        assert builder._percentage(0, 0) == 0.0  # Edge case


class TestErrorHandling:
    """Test error handling and fallback mechanisms."""

    def test_download_failure(
        self,
        sample_targets_file,
        tmp_path,
        mock_latex_extractor,
        mock_latex_converter,
    ):
        """Test handling of download failures."""
        from build_arxiv_corpus import ArxivCorpusBuilder, ArxivDownloadError

        with patch("build_arxiv_corpus.ArxivClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Simulate download failure
            mock_client.download_pdf.side_effect = ArxivDownloadError("Download failed")

            builder = ArxivCorpusBuilder(
                targets_file=sample_targets_file,
                output_dir=tmp_path / "corpus",
                limit=1,
            )

            stats = builder.build()

            assert stats["failed"] >= 1
            assert len(stats["failures"]) >= 1

    def test_latex_extraction_failure(
        self,
        sample_targets_file,
        tmp_path,
        mock_arxiv_client,
        mock_latex_converter,
    ):
        """Test handling of LaTeX extraction failures."""
        from build_arxiv_corpus import ArxivCorpusBuilder

        output_dir = tmp_path / "corpus"

        def create_mock_downloads(*args, **kwargs):
            """Create mock download files."""
            paper_dir = output_dir / "2303.18223"
            paper_dir.mkdir(parents=True, exist_ok=True)
            (paper_dir / "paper.pdf").write_bytes(b"mock pdf")
            (paper_dir / "source.tar.gz").write_bytes(b"mock tarball")

        mock_arxiv_client.download_pdf.side_effect = create_mock_downloads

        with patch("build_arxiv_corpus.LaTeXExtractor") as mock_extractor_class:
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor

            # Simulate extraction failure
            mock_extractor.extract.return_value = {
                "success": False,
                "error": "No .tex files found",
            }

            builder = ArxivCorpusBuilder(
                targets_file=sample_targets_file,
                output_dir=output_dir,
                limit=1,
            )

            stats = builder.build()

            assert stats["failed"] >= 1

    def test_conversion_failure(
        self,
        sample_targets_file,
        tmp_path,
        mock_arxiv_client,
        mock_latex_extractor,
    ):
        """Test handling of LaTeX→Markdown conversion failures."""
        from build_arxiv_corpus import (
            ArxivCorpusBuilder,
            LatexToMarkdownConversionError,
        )

        output_dir = tmp_path / "corpus"

        def create_mock_downloads(*args, **kwargs):
            """Create mock download files."""
            paper_dir = output_dir / "2303.18223"
            paper_dir.mkdir(parents=True, exist_ok=True)
            (paper_dir / "paper.pdf").write_bytes(b"mock pdf")
            (paper_dir / "source.tar.gz").write_bytes(b"mock tarball")

        mock_arxiv_client.download_pdf.side_effect = create_mock_downloads

        with patch("build_arxiv_corpus.convert_latex_to_markdown") as mock_convert:
            # Simulate conversion failure
            mock_convert.side_effect = LatexToMarkdownConversionError(
                "All conversion methods failed"
            )

            builder = ArxivCorpusBuilder(
                targets_file=sample_targets_file,
                output_dir=output_dir,
                limit=1,
            )

            stats = builder.build()

            assert stats["failed"] >= 1
            assert any("conversion failed" in str(err).lower() for _, err in stats["failures"])


class TestValidation:
    """Test corpus validation."""

    def test_validate_empty_corpus(self, tmp_path):
        """Test validation of empty corpus."""
        from validate_arxiv_corpus import ArxivCorpusValidator

        corpus_dir = tmp_path / "empty_corpus"
        corpus_dir.mkdir()

        validator = ArxivCorpusValidator(corpus_dir=corpus_dir)
        stats = validator.validate()

        assert stats["total_papers"] == 0
        assert stats["valid_papers"] == 0
        assert stats["invalid_papers"] == 0

    def test_validate_valid_paper(self, tmp_path):
        """Test validation of a valid paper."""
        from validate_arxiv_corpus import ArxivCorpusValidator

        corpus_dir = tmp_path / "corpus"
        paper_dir = corpus_dir / "2303.18223"
        paper_dir.mkdir(parents=True)

        # Create valid paper files
        pdf_content = b"mock pdf content"
        (paper_dir / "paper.pdf").write_bytes(pdf_content)

        gt_content = "# Mock Markdown\n\nTest content"
        (paper_dir / "ground_truth.md").write_text(gt_content)

        # Calculate hashes
        import hashlib

        pdf_hash = "sha256:" + hashlib.sha256(pdf_content).hexdigest()
        gt_hash = "sha256:" + hashlib.sha256(gt_content.encode()).hexdigest()

        metadata = {
            "document_id": "arxiv_001",
            "arxiv_id": "2303.18223",
            "title": "Test Paper",
            "pdf_hash": pdf_hash,
            "pdf_size_bytes": len(pdf_content),
            "ground_truth_path": "ground_truth.md",
            "ground_truth_hash": gt_hash,
            "source": "arxiv",
            "conversion_method": "latexml",
            "conversion_success": True,
        }

        with open(paper_dir / "metadata.yaml", "w") as f:
            yaml.dump(metadata, f)

        validator = ArxivCorpusValidator(corpus_dir=corpus_dir)
        stats = validator.validate()

        assert stats["total_papers"] == 1
        assert stats["valid_papers"] == 1
        assert stats["invalid_papers"] == 0

    def test_validate_missing_files(self, tmp_path):
        """Test validation of paper with missing files."""
        from validate_arxiv_corpus import ArxivCorpusValidator

        corpus_dir = tmp_path / "corpus"
        paper_dir = corpus_dir / "2303.18223"
        paper_dir.mkdir(parents=True)

        # Create only metadata (missing PDF and ground truth)
        metadata = {
            "document_id": "arxiv_001",
            "arxiv_id": "2303.18223",
            "title": "Test Paper",
            "pdf_hash": "sha256:abc123",
            "pdf_size_bytes": 1000,
            "ground_truth_path": "ground_truth.md",
            "ground_truth_hash": "sha256:def456",
            "source": "arxiv",
            "conversion_method": "latexml",
            "conversion_success": True,
        }

        with open(paper_dir / "metadata.yaml", "w") as f:
            yaml.dump(metadata, f)

        validator = ArxivCorpusValidator(corpus_dir=corpus_dir)
        stats = validator.validate()

        assert stats["total_papers"] == 1
        assert stats["invalid_papers"] == 1
        assert stats["missing_files"] > 0

    def test_validate_hash_mismatch(self, tmp_path):
        """Test validation of paper with hash mismatch."""
        from validate_arxiv_corpus import ArxivCorpusValidator

        corpus_dir = tmp_path / "corpus"
        paper_dir = corpus_dir / "2303.18223"
        paper_dir.mkdir(parents=True)

        # Create files
        (paper_dir / "paper.pdf").write_bytes(b"actual content")
        (paper_dir / "ground_truth.md").write_text("# Actual Markdown")

        # Metadata with wrong hashes
        metadata = {
            "document_id": "arxiv_001",
            "arxiv_id": "2303.18223",
            "title": "Test Paper",
            "pdf_hash": "sha256:wronghash",
            "pdf_size_bytes": 1000,
            "ground_truth_path": "ground_truth.md",
            "ground_truth_hash": "sha256:wronghash",
            "source": "arxiv",
            "conversion_method": "latexml",
            "conversion_success": True,
        }

        with open(paper_dir / "metadata.yaml", "w") as f:
            yaml.dump(metadata, f)

        validator = ArxivCorpusValidator(corpus_dir=corpus_dir)
        stats = validator.validate()

        assert stats["total_papers"] == 1
        assert stats["invalid_papers"] == 1
        assert stats["hash_mismatches"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
