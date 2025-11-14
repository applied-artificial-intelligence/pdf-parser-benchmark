"""Tests for corpus validation script."""

from pathlib import Path

import pytest
import yaml

from scripts.validate_corpus import CorpusValidator, ValidationResult


@pytest.fixture
def temp_corpus_dir(tmp_path: Path) -> Path:
    """Create a temporary corpus directory for testing."""
    corpus_dir = tmp_path / "corpus" / "synthetic"
    corpus_dir.mkdir(parents=True)
    return corpus_dir


@pytest.fixture
def valid_pandoc_metadata() -> dict:
    """Create valid Pandoc-format metadata."""
    return {
        "document_id": "test-001",
        "source_type": "synthetic",
        "category": "synthetic",
        "title": "Test Document",
        "description": "A test document",
        "complexity": "basic",
        "file_paths": {
            "ground_truth": "test-001.md",
            "pdf": "test-001.pdf",
        },
        "pdf_hash": "abc123",
        "corpus": "synthetic",
    }


@pytest.fixture
def valid_docx_metadata() -> dict:
    """Create valid DOCX-format metadata."""
    return {
        "title": "Test DOCX",
        "corpus": "synthetic",
        "category": "docx_generated",
        "files": {
            "pdf": "test-docx.pdf",
            "ground_truth": "test-docx.md",
            "docx": "test-docx.docx",
        },
        "hashes": {"pdf_sha256": "xyz789"},
    }


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_init_defaults(self) -> None:
        """Test initialization with default values."""
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )
        assert result.document_id == "test"
        assert result.passed is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error(self) -> None:
        """Test adding an error marks as failed."""
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )
        result.add_error("Test error")

        assert result.passed is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"

    def test_add_warning(self) -> None:
        """Test adding a warning doesn't affect pass status."""
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )
        result.add_warning("Test warning")

        assert result.passed is True
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"


class TestCorpusValidator:
    """Tests for CorpusValidator class."""

    def test_init(self, temp_corpus_dir: Path) -> None:
        """Test validator initialization."""
        validator = CorpusValidator(temp_corpus_dir)
        assert validator.corpus_dir == temp_corpus_dir
        assert validator.results == []

    def test_validate_all_empty_corpus(self, temp_corpus_dir: Path) -> None:
        """Test validating empty corpus."""
        validator = CorpusValidator(temp_corpus_dir)
        results = validator.validate_all()
        assert len(results) == 0

    def test_validate_all_skips_example_files(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test that example files are skipped during validation."""
        # Create example file
        example_file = temp_corpus_dir / "example_test.yaml"
        with open(example_file, "w") as f:
            yaml.dump(valid_pandoc_metadata, f)

        # Create regular file
        regular_file = temp_corpus_dir / "test-001.yaml"
        with open(regular_file, "w") as f:
            yaml.dump(valid_pandoc_metadata, f)

        validator = CorpusValidator(temp_corpus_dir)
        results = validator.validate_all()

        # Should only validate the regular file
        assert len(results) == 1
        assert results[0].document_id == "test-001"

    def test_validate_yaml_schema_pandoc_format(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test YAML schema validation for Pandoc format."""
        yaml_file = temp_corpus_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_pandoc_metadata, f)

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(document_id="test", yaml_file=yaml_file)

        validator._validate_yaml_schema(valid_pandoc_metadata, result)

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_yaml_schema_docx_format(
        self, temp_corpus_dir: Path, valid_docx_metadata: dict
    ) -> None:
        """Test YAML schema validation for DOCX format."""
        yaml_file = temp_corpus_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_docx_metadata, f)

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(document_id="test", yaml_file=yaml_file)

        validator._validate_yaml_schema(valid_docx_metadata, result)

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_yaml_schema_missing_required_fields(
        self, temp_corpus_dir: Path
    ) -> None:
        """Test schema validation catches missing required fields."""
        incomplete_metadata = {"title": "Test"}

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        validator._validate_yaml_schema(incomplete_metadata, result)

        assert result.passed is False
        assert any("file_paths" in err or "files" in err for err in result.errors)

    def test_validate_yaml_schema_invalid_corpus(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test schema validation catches invalid corpus values."""
        valid_pandoc_metadata["corpus"] = "invalid_corpus"

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        validator._validate_yaml_schema(valid_pandoc_metadata, result)

        assert result.passed is False
        assert any("corpus" in err.lower() for err in result.errors)

    def test_validate_yaml_schema_missing_hash(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test schema validation warns about missing hashes."""
        del valid_pandoc_metadata["pdf_hash"]

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        validator._validate_yaml_schema(valid_pandoc_metadata, result)

        # Should warn but not fail
        assert result.passed is True
        assert len(result.warnings) > 0
        assert any("hash" in warn.lower() for warn in result.warnings)

    def test_validate_file_existence_pandoc(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test file existence validation for Pandoc format."""
        # Create the files
        pdf_path = temp_corpus_dir / "test-001.pdf"
        md_path = temp_corpus_dir / "test-001.md"
        pdf_path.write_text("fake pdf")
        md_path.write_text("# Test")

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        file_paths = validator._validate_file_existence(
            valid_pandoc_metadata, result
        )

        assert result.passed is True
        assert "pdf" in file_paths
        assert "ground_truth" in file_paths
        assert file_paths["pdf"].exists()
        assert file_paths["ground_truth"].exists()

    def test_validate_file_existence_missing_files(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test file existence validation catches missing files."""
        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        _ = validator._validate_file_existence(
            valid_pandoc_metadata, result
        )

        assert result.passed is False
        assert len(result.errors) >= 2  # Missing PDF and ground truth
        assert any("pdf" in err.lower() for err in result.errors)
        assert any("ground truth" in err.lower() for err in result.errors)

    def test_validate_hashes_match(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test hash validation with matching hashes."""
        # Create PDF file
        pdf_path = temp_corpus_dir / "test-001.pdf"
        pdf_content = b"test pdf content"
        pdf_path.write_bytes(pdf_content)

        # Calculate actual hash
        import hashlib

        actual_hash = hashlib.sha256(pdf_content).hexdigest()

        # Update metadata with correct hash
        valid_pandoc_metadata["pdf_hash"] = actual_hash

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        file_paths = {"pdf": pdf_path}
        validator._validate_hashes(valid_pandoc_metadata, file_paths, result)

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_hashes_mismatch(
        self, temp_corpus_dir: Path, valid_pandoc_metadata: dict
    ) -> None:
        """Test hash validation catches mismatched hashes."""
        # Create PDF file
        pdf_path = temp_corpus_dir / "test-001.pdf"
        pdf_path.write_bytes(b"test pdf content")

        # Use wrong hash
        valid_pandoc_metadata["pdf_hash"] = "wrong_hash"

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        file_paths = {"pdf": pdf_path}
        validator._validate_hashes(valid_pandoc_metadata, file_paths, result)

        assert result.passed is False
        assert any("hash mismatch" in err.lower() for err in result.errors)

    def test_validate_markdown_valid(self, temp_corpus_dir: Path) -> None:
        """Test Markdown validation with valid content."""
        md_path = temp_corpus_dir / "test.md"
        md_path.write_text("# Heading\n\nThis is a paragraph.")

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        validator._validate_markdown(md_path, result)

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_markdown_empty(self, temp_corpus_dir: Path) -> None:
        """Test Markdown validation catches empty files."""
        md_path = temp_corpus_dir / "test.md"
        md_path.write_text("")

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        validator._validate_markdown(md_path, result)

        assert result.passed is False
        assert any("empty" in err.lower() for err in result.errors)

    def test_validate_markdown_very_short(self, temp_corpus_dir: Path) -> None:
        """Test Markdown validation warns about very short files."""
        md_path = temp_corpus_dir / "test.md"
        md_path.write_text("hi")

        validator = CorpusValidator(temp_corpus_dir)
        result = ValidationResult(
            document_id="test", yaml_file=Path("test.yaml")
        )

        validator._validate_markdown(md_path, result)

        # Should warn but not fail
        assert result.passed is True
        assert len(result.warnings) > 0

    def test_generate_report_all_passed(self, temp_corpus_dir: Path) -> None:
        """Test report generation when all documents pass."""
        validator = CorpusValidator(temp_corpus_dir)

        # Add some passing results
        result1 = ValidationResult(
            document_id="doc1", yaml_file=Path("doc1.yaml")
        )
        result2 = ValidationResult(
            document_id="doc2", yaml_file=Path("doc2.yaml")
        )
        validator.results = [result1, result2]

        report = validator.generate_report()

        assert "Total Documents: 2" in report
        assert "✅ Passed: 2" in report
        assert "❌ Failed: 0" in report
        assert "ALL DOCUMENTS VALIDATED SUCCESSFULLY" in report

    def test_generate_report_some_failed(self, temp_corpus_dir: Path) -> None:
        """Test report generation when some documents fail."""
        validator = CorpusValidator(temp_corpus_dir)

        # Add passing result
        result1 = ValidationResult(
            document_id="doc1", yaml_file=Path("doc1.yaml")
        )

        # Add failing result
        result2 = ValidationResult(
            document_id="doc2", yaml_file=Path("doc2.yaml")
        )
        result2.add_error("Test error")
        result2.add_warning("Test warning")

        validator.results = [result1, result2]

        report = validator.generate_report()

        assert "Total Documents: 2" in report
        assert "✅ Passed: 1" in report
        assert "❌ Failed: 1" in report
        assert "Test error" in report
        assert "Test warning" in report
