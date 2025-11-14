"""Tests for synthetic corpus builder."""

import hashlib
from pathlib import Path

import pytest
import yaml

from builders.build_synthetic import PandocBuilder


@pytest.fixture
def builder():
    """Create PandocBuilder instance."""
    return PandocBuilder()


@pytest.fixture
def temp_markdown(tmp_path):
    """Create a temporary Markdown file."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Document\n\nThis is a test.\n")
    return md_file


@pytest.fixture
def temp_yaml(tmp_path):
    """Create a temporary YAML metadata file."""
    yaml_file = tmp_path / "test.yaml"
    metadata = {
        "document_id": "test-001",
        "title": "Test Document",
        "file_paths": {"ground_truth": "test.md", "pdf": "test.pdf"},
        "validation": {"ground_truth_exists": True, "pdf_exists": False},
    }
    with open(yaml_file, "w") as f:
        yaml.dump(metadata, f)
    return yaml_file


class TestPandocBuilder:
    """Tests for PandocBuilder class."""

    def test_init_verifies_pandoc(self):
        """Test that __init__ verifies Pandoc is available."""
        # Should not raise
        builder = PandocBuilder()
        assert builder.pandoc_path == "pandoc"
        assert builder.latex_engine == "pdflatex"

    def test_init_with_custom_args(self):
        """Test initialization with custom arguments."""
        builder = PandocBuilder(
            pandoc_path="/usr/bin/pandoc",
            latex_engine="xelatex",
            extra_args=["--toc", "--template=custom"],
        )
        assert builder.pandoc_path == "/usr/bin/pandoc"
        assert builder.latex_engine == "xelatex"
        assert builder.extra_args == ["--toc", "--template=custom"]

    def test_init_fails_if_pandoc_not_found(self):
        """Test that __init__ raises if Pandoc is not found."""
        with pytest.raises(RuntimeError, match="Pandoc not found"):
            PandocBuilder(pandoc_path="/nonexistent/pandoc")

    def test_build_pdf_creates_file(self, builder, temp_markdown, tmp_path):
        """Test that build_pdf creates a PDF file."""
        output_pdf = tmp_path / "test.pdf"

        result = builder.build_pdf(temp_markdown, output_pdf, title="Test")

        assert output_pdf.exists()
        assert "pdf_path" in result
        assert "pdf_hash" in result
        assert Path(result["pdf_path"]) == output_pdf

    def test_build_pdf_raises_if_markdown_not_found(self, builder, tmp_path):
        """Test that build_pdf raises if Markdown file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.md"
        output_pdf = tmp_path / "test.pdf"

        with pytest.raises(FileNotFoundError):
            builder.build_pdf(nonexistent, output_pdf)

    def test_build_pdf_hash_is_sha256(self, builder, temp_markdown, tmp_path):
        """Test that PDF hash is a valid SHA256 hex string."""
        output_pdf = tmp_path / "test.pdf"

        result = builder.build_pdf(temp_markdown, output_pdf)

        # SHA256 hex string is 64 characters
        assert len(result["pdf_hash"]) == 64
        assert all(c in "0123456789abcdef" for c in result["pdf_hash"])

    def test_build_pdf_hash_matches_file(self, builder, temp_markdown, tmp_path):
        """Test that returned hash matches actual file hash."""
        output_pdf = tmp_path / "test.pdf"

        result = builder.build_pdf(temp_markdown, output_pdf)

        # Calculate hash manually
        sha256 = hashlib.sha256()
        with open(output_pdf, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        expected_hash = sha256.hexdigest()

        assert result["pdf_hash"] == expected_hash

    def test_build_pdf_creates_output_directory(self, builder, temp_markdown, tmp_path):
        """Test that build_pdf creates output directory if needed."""
        nested_dir = tmp_path / "nested" / "dir"
        output_pdf = nested_dir / "test.pdf"

        builder.build_pdf(temp_markdown, output_pdf)

        assert nested_dir.exists()
        assert output_pdf.exists()

    def test_update_metadata_adds_hash(self, builder, temp_yaml):
        """Test that update_metadata adds PDF hash."""
        builder.update_metadata(temp_yaml, "abc123")

        with open(temp_yaml) as f:
            metadata = yaml.safe_load(f)

        assert metadata["pdf_hash"] == "abc123"

    def test_update_metadata_updates_pdf_path(self, builder, temp_yaml):
        """Test that update_metadata updates PDF path."""
        builder.update_metadata(temp_yaml, "abc123", pdf_path="output/test.pdf")

        with open(temp_yaml) as f:
            metadata = yaml.safe_load(f)

        assert metadata["file_paths"]["pdf"] == "output/test.pdf"

    def test_update_metadata_updates_validation(self, builder, temp_yaml):
        """Test that update_metadata sets pdf_exists to True."""
        builder.update_metadata(temp_yaml, "abc123")

        with open(temp_yaml) as f:
            metadata = yaml.safe_load(f)

        assert metadata["validation"]["pdf_exists"] is True

    def test_calculate_hash_consistent(self, builder, tmp_path):
        """Test that _calculate_hash is consistent for same file."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"test content")

        hash1 = builder._calculate_hash(test_file)
        hash2 = builder._calculate_hash(test_file)

        assert hash1 == hash2

    def test_calculate_hash_different_for_different_files(self, builder, tmp_path):
        """Test that different files produce different hashes."""
        file1 = tmp_path / "file1.bin"
        file2 = tmp_path / "file2.bin"
        file1.write_bytes(b"content 1")
        file2.write_bytes(b"content 2")

        hash1 = builder._calculate_hash(file1)
        hash2 = builder._calculate_hash(file2)

        assert hash1 != hash2


class TestBuildAllSynthetic:
    """Tests for build_all_synthetic function."""

    def test_skips_markdown_without_yaml(self, tmp_path, capsys):
        """Test that Markdown files without YAML are skipped."""
        from builders.build_synthetic import build_all_synthetic

        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        build_all_synthetic(tmp_path)

        captured = capsys.readouterr()
        assert "Skipping test.md (no YAML metadata)" in captured.out

    def test_builds_all_valid_documents(self, tmp_path):
        """Test that all valid documents are built."""
        from builders.build_synthetic import build_all_synthetic

        # Create 2 test documents
        for i in range(1, 3):
            md_file = tmp_path / f"doc{i}.md"
            yaml_file = tmp_path / f"doc{i}.yaml"

            md_file.write_text(f"# Document {i}\n\nContent {i}\n")

            metadata = {
                "document_id": f"doc-{i}",
                "title": f"Document {i}",
            }
            with open(yaml_file, "w") as f:
                yaml.dump(metadata, f)

        results = build_all_synthetic(tmp_path)

        assert len(results) == 2
        assert all("error" not in r for r in results)
        assert all((tmp_path / f"doc{i}.pdf").exists() for i in range(1, 3))
