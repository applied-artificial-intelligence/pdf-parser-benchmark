"""Tests for DOCX→PDF pipeline."""

import tempfile
from pathlib import Path

import pytest

from builders.build_docx import DocxBuilder


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def templates_dir():
    """Return path to templates directory."""
    return Path("corpus/synthetic/templates")


@pytest.fixture
def builder(templates_dir, temp_dir):
    """Create DocxBuilder instance."""
    return DocxBuilder(templates_dir, temp_dir)


def test_builder_init(templates_dir, temp_dir):
    """Test DocxBuilder initialization."""
    builder = DocxBuilder(templates_dir, temp_dir)
    assert builder.templates_dir == templates_dir
    assert builder.output_dir == temp_dir
    assert temp_dir.exists()


def test_render_template_simple(builder):
    """Test rendering simple report template."""
    context = {
        "title": "Test Report",
        "author": "Test Author",
        "date": "2025-11-14",
        "report_id": "TST-001",
        "executive_summary": "Test summary",
        "introduction": "Test intro",
        "background": "Test background",
        "methodology": "Test method",
        "findings": "Test findings",
        "observations": ["Obs 1", "Obs 2"],
        "results": "Test results",
        "conclusion": "Test conclusion",
        "recommendations": ["Rec 1", "Rec 2"],
        "references": "Test refs",
    }

    docx_path = builder.render_template("01_simple_report.docx", context, "test_output")

    assert docx_path.exists()
    assert docx_path.name == "test_output.docx"
    assert docx_path.suffix == ".docx"


def test_render_template_not_found(builder):
    """Test rendering with non-existent template."""
    with pytest.raises(FileNotFoundError):
        builder.render_template("nonexistent.docx", {}, "output")


def test_convert_to_pdf(builder):
    """Test PDF conversion."""
    # First render a template
    context = {
        "title": "Test",
        "author": "Author",
        "date": "2025-11-14",
        "report_id": "TST",
        "executive_summary": "Sum",
        "introduction": "Intro",
        "background": "Back",
        "methodology": "Meth",
        "findings": "Find",
        "observations": [],
        "results": "Res",
        "conclusion": "Conc",
        "recommendations": [],
        "references": "Refs",
    }

    docx_path = builder.render_template("01_simple_report.docx", context, "test_pdf")

    # Convert to PDF
    pdf_path = builder.convert_to_pdf(docx_path)

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stem == docx_path.stem


def test_convert_to_pdf_not_found(builder):
    """Test PDF conversion with non-existent DOCX."""
    fake_path = builder.output_dir / "nonexistent.docx"
    with pytest.raises(FileNotFoundError):
        builder.convert_to_pdf(fake_path)


def test_extract_ground_truth(builder):
    """Test ground truth extraction."""
    # Render a template
    context = {
        "title": "GT Test",
        "author": "Author",
        "date": "2025-11-14",
        "report_id": "GT-001",
        "executive_summary": "Summary text",
        "introduction": "Introduction text",
        "background": "Background text",
        "methodology": "Methodology text",
        "findings": "Findings text",
        "observations": ["Observation 1", "Observation 2"],
        "results": "Results text",
        "conclusion": "Conclusion text",
        "recommendations": ["Rec 1", "Rec 2"],
        "references": "References text",
    }

    docx_path = builder.render_template("01_simple_report.docx", context, "test_gt")

    # Extract GT
    gt = builder.extract_ground_truth(docx_path)

    # Verify GT contains expected content
    assert "GT Test" in gt
    assert "# Executive Summary" in gt
    assert "Summary text" in gt
    assert "# Introduction" in gt
    assert "Introduction text" in gt
    assert "# Conclusion" in gt
    assert "Conclusion text" in gt


def test_extract_ground_truth_not_found(builder):
    """Test GT extraction with non-existent DOCX."""
    fake_path = builder.output_dir / "nonexistent.docx"
    with pytest.raises(FileNotFoundError):
        builder.extract_ground_truth(fake_path)


def test_calculate_hash(builder):
    """Test SHA256 hash calculation."""
    # Create a test file
    test_file = builder.output_dir / "test.txt"
    test_file.write_text("test content")

    hash1 = builder.calculate_hash(test_file)

    # Hash should be deterministic
    hash2 = builder.calculate_hash(test_file)
    assert hash1 == hash2

    # Hash should be 64 hex characters (SHA256)
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


def test_calculate_hash_not_found(builder):
    """Test hash calculation with non-existent file."""
    fake_path = builder.output_dir / "nonexistent.txt"
    with pytest.raises(FileNotFoundError):
        builder.calculate_hash(fake_path)


def test_create_metadata(builder):
    """Test metadata YAML creation."""
    yaml_path = builder.create_metadata(
        output_name="test_doc",
        title="Test Document",
        source="template.docx",
        pdf_hash="abc123",
        docx_hash="def456",
        context={"var1": "val1", "var2": "val2"},
    )

    assert yaml_path.exists()
    assert yaml_path.suffix == ".yaml"

    # Read and verify content
    import yaml

    with open(yaml_path) as f:
        metadata = yaml.safe_load(f)

    assert metadata["title"] == "Test Document"
    assert metadata["source"] == "template.docx"
    assert metadata["corpus"] == "synthetic"
    assert metadata["category"] == "docx_generated"
    assert metadata["license"] == "CC0-1.0"
    assert metadata["hashes"]["pdf_sha256"] == "abc123"
    assert metadata["hashes"]["docx_sha256"] == "def456"
    assert metadata["generation"]["context_variables"] == 2


def test_build_document_complete(builder):
    """Test full document build pipeline."""
    context = {
        "title": "Full Pipeline Test",
        "author": "Test Suite",
        "date": "2025-11-14",
        "report_id": "FPT-001",
        "executive_summary": "Full test",
        "introduction": "Intro",
        "background": "Background",
        "methodology": "Method",
        "findings": "Findings",
        "observations": ["A", "B"],
        "results": "Results",
        "conclusion": "Conclusion",
        "recommendations": ["X", "Y"],
        "references": "Refs",
    }

    result = builder.build_document(
        template_name="01_simple_report.docx",
        output_name="full_test",
        title="Full Pipeline Test",
        context=context,
    )

    # Verify all files created
    assert result["docx"].exists()
    assert result["pdf"].exists()
    assert result["ground_truth"].exists()
    assert result["metadata"].exists()

    # Verify file types
    assert result["docx"].suffix == ".docx"
    assert result["pdf"].suffix == ".pdf"
    assert result["ground_truth"].suffix == ".md"
    assert result["metadata"].suffix == ".yaml"

    # Verify metadata content
    import yaml

    with open(result["metadata"]) as f:
        metadata = yaml.safe_load(f)

    assert metadata["title"] == "Full Pipeline Test"
    assert len(metadata["hashes"]["pdf_sha256"]) == 64
    assert len(metadata["hashes"]["docx_sha256"]) == 64
