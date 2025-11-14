"""
Unit tests for document metadata schema and utilities.
"""

from pathlib import Path

import pytest
import yaml

from pdf_bench.utils.metadata import (
    VALID_CORPORA,
    VALID_DOMAINS,
    VALID_FEATURES,
    DocumentMetadata,
    load_metadata,
    save_metadata,
)


class TestDocumentMetadata:
    """Test DocumentMetadata dataclass and validation."""

    def test_minimal_valid_metadata(self) -> None:
        """Test creating metadata with only required fields."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
        )
        metadata.validate()  # Should not raise

    def test_full_metadata(self) -> None:
        """Test creating metadata with all fields populated."""
        metadata = DocumentMetadata(
            doc_id="arxiv_1706_03762",
            source_url="https://arxiv.org/pdf/1706.03762.pdf",
            corpus="academic",
            domain="arxiv",
            title="Attention Is All You Need",
            authors=["Ashish Vaswani", "Noam Shazeer"],
            publication_date="2017-06-12",
            page_count=15,
            file_size_bytes=2155905,
            features=["tables", "math", "figures"],
            language="en",
            license="arXiv.org perpetual non-exclusive license",
            notes="Seminal transformer paper",
        )
        metadata.validate()  # Should not raise

    def test_missing_doc_id(self) -> None:
        """Test that missing doc_id fails validation."""
        metadata = DocumentMetadata(
            doc_id="",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
        )
        with pytest.raises(ValueError, match="doc_id is required"):
            metadata.validate()

    def test_missing_source_url(self) -> None:
        """Test that missing source_url fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="",
            corpus="academic",
            domain="arxiv",
        )
        with pytest.raises(ValueError, match="source_url is required"):
            metadata.validate()

    def test_invalid_corpus(self) -> None:
        """Test that invalid corpus fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="invalid_corpus",
            domain="arxiv",
        )
        with pytest.raises(ValueError, match="corpus must be one of"):
            metadata.validate()

    def test_invalid_domain_for_corpus(self) -> None:
        """Test that mismatched domain/corpus fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="gov-uk",  # Wrong domain for academic corpus
        )
        with pytest.raises(ValueError, match="domain .* is not valid for corpus"):
            metadata.validate()

    def test_invalid_url_format(self) -> None:
        """Test that invalid URL format fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="ftp://example.com/doc.pdf",  # Not http/https
            corpus="academic",
            domain="arxiv",
        )
        with pytest.raises(ValueError, match="source_url must start with"):
            metadata.validate()

    def test_invalid_page_count(self) -> None:
        """Test that invalid page_count fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            page_count=0,  # Must be >= 1
        )
        with pytest.raises(ValueError, match="page_count must be >= 1"):
            metadata.validate()

    def test_invalid_file_size(self) -> None:
        """Test that negative file_size_bytes fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            file_size_bytes=-100,
        )
        with pytest.raises(ValueError, match="file_size_bytes must be >= 0"):
            metadata.validate()

    def test_invalid_feature(self) -> None:
        """Test that unknown feature fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            features=["tables", "unknown_feature"],
        )
        with pytest.raises(ValueError, match="Unknown feature"):
            metadata.validate()

    def test_invalid_language_code(self) -> None:
        """Test that invalid language code fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            language="eng",  # Should be 2 letters
        )
        with pytest.raises(ValueError, match="language should be 2-letter"):
            metadata.validate()

    def test_invalid_publication_date_format(self) -> None:
        """Test that invalid date format fails validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            publication_date="2023/01/15",  # Wrong format
        )
        with pytest.raises(ValueError, match="publication_date must be in YYYY-MM-DD"):
            metadata.validate()

    def test_invalid_publication_date_values(self) -> None:
        """Test that invalid date values fail validation."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            publication_date="2023-13-01",  # Invalid month
        )
        with pytest.raises(ValueError, match="publication_date must be in YYYY-MM-DD"):
            metadata.validate()

    def test_multiple_validation_errors(self) -> None:
        """Test that multiple validation errors are reported together."""
        metadata = DocumentMetadata(
            doc_id="",
            source_url="ftp://example.com/doc.pdf",
            corpus="invalid",
            domain="invalid",
            page_count=-5,
        )
        with pytest.raises(ValueError, match="5 error"):
            metadata.validate()

    def test_to_dict_minimal(self) -> None:
        """Test converting minimal metadata to dict."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
        )
        data = metadata.to_dict()

        assert data["doc_id"] == "test_001"
        assert data["source_url"] == "https://example.com/doc.pdf"
        assert data["corpus"] == "academic"
        assert data["domain"] == "arxiv"
        assert "title" not in data  # Optional fields excluded if None
        assert "language" not in data  # Default value excluded

    def test_to_dict_full(self) -> None:
        """Test converting full metadata to dict."""
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            title="Test Document",
            authors=["Author One", "Author Two"],
            publication_date="2023-01-15",
            page_count=10,
            file_size_bytes=100000,
            features=["tables", "math"],
            language="fr",
            license="CC-BY-4.0",
            notes="Test notes",
        )
        data = metadata.to_dict()

        assert data["title"] == "Test Document"
        assert data["authors"] == ["Author One", "Author Two"]
        assert data["publication_date"] == "2023-01-15"
        assert data["page_count"] == 10
        assert data["file_size_bytes"] == 100000
        assert data["features"] == ["tables", "math"]
        assert data["language"] == "fr"
        assert data["license"] == "CC-BY-4.0"
        assert data["notes"] == "Test notes"

    def test_from_dict_minimal(self) -> None:
        """Test creating metadata from minimal dict."""
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "academic",
            "domain": "arxiv",
        }
        metadata = DocumentMetadata.from_dict(data)

        assert metadata.doc_id == "test_001"
        assert metadata.source_url == "https://example.com/doc.pdf"
        assert metadata.corpus == "academic"
        assert metadata.domain == "arxiv"
        assert metadata.language == "en"  # Default

    def test_from_dict_full(self) -> None:
        """Test creating metadata from full dict."""
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "academic",
            "domain": "arxiv",
            "title": "Test Document",
            "authors": ["Author One"],
            "publication_date": "2023-01-15",
            "page_count": 10,
            "file_size_bytes": 100000,
            "features": ["tables"],
            "language": "fr",
            "license": "CC-BY-4.0",
            "notes": "Test notes",
        }
        metadata = DocumentMetadata.from_dict(data)

        assert metadata.title == "Test Document"
        assert metadata.authors == ["Author One"]
        assert metadata.language == "fr"

    def test_from_dict_missing_required_field(self) -> None:
        """Test that from_dict fails with missing required field."""
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "academic",
            # Missing domain
        }
        with pytest.raises(KeyError, match="Missing required field"):
            DocumentMetadata.from_dict(data)

    def test_from_dict_validates(self) -> None:
        """Test that from_dict validates the data."""
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "invalid_corpus",
            "domain": "arxiv",
        }
        with pytest.raises(ValueError, match="corpus must be one of"):
            DocumentMetadata.from_dict(data)

    def test_roundtrip_to_dict_from_dict(self) -> None:
        """Test that to_dict/from_dict roundtrip preserves data."""
        original = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            title="Test Document",
            authors=["Author One", "Author Two"],
            publication_date="2023-01-15",
            page_count=10,
            features=["tables", "math"],
        )

        data = original.to_dict()
        reconstructed = DocumentMetadata.from_dict(data)

        assert reconstructed.doc_id == original.doc_id
        assert reconstructed.title == original.title
        assert reconstructed.authors == original.authors
        assert reconstructed.features == original.features


class TestLoadMetadata:
    """Test load_metadata function."""

    def test_load_valid_metadata(self, tmp_path: Path) -> None:
        """Test loading valid metadata from YAML file."""
        yaml_path = tmp_path / "test.yaml"
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "academic",
            "domain": "arxiv",
            "title": "Test Document",
        }

        with open(yaml_path, "w") as f:
            yaml.dump(data, f)

        metadata = load_metadata(yaml_path)

        assert metadata.doc_id == "test_001"
        assert metadata.title == "Test Document"

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test that loading nonexistent file raises FileNotFoundError."""
        yaml_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError, match="Metadata file not found"):
            load_metadata(yaml_path)

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        """Test that loading invalid YAML raises YAMLError."""
        yaml_path = tmp_path / "invalid.yaml"

        with open(yaml_path, "w") as f:
            f.write("invalid: yaml: content: ][")

        with pytest.raises(yaml.YAMLError, match="Failed to parse YAML"):
            load_metadata(yaml_path)

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        """Test that loading empty YAML raises ValueError."""
        yaml_path = tmp_path / "empty.yaml"

        with open(yaml_path, "w") as f:
            f.write("")

        with pytest.raises(ValueError, match="Empty YAML file"):
            load_metadata(yaml_path)

    def test_load_non_dict_yaml(self, tmp_path: Path) -> None:
        """Test that loading non-dict YAML raises ValueError."""
        yaml_path = tmp_path / "list.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump(["item1", "item2"], f)

        with pytest.raises(ValueError, match="must contain a dictionary"):
            load_metadata(yaml_path)

    def test_load_missing_required_field(self, tmp_path: Path) -> None:
        """Test that loading YAML with missing field raises KeyError."""
        yaml_path = tmp_path / "missing_field.yaml"
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "academic",
            # Missing domain
        }

        with open(yaml_path, "w") as f:
            yaml.dump(data, f)

        with pytest.raises(KeyError, match="Missing required field"):
            load_metadata(yaml_path)

    def test_load_invalid_metadata(self, tmp_path: Path) -> None:
        """Test that loading invalid metadata raises ValueError."""
        yaml_path = tmp_path / "invalid.yaml"
        data = {
            "doc_id": "test_001",
            "source_url": "https://example.com/doc.pdf",
            "corpus": "invalid_corpus",
            "domain": "arxiv",
        }

        with open(yaml_path, "w") as f:
            yaml.dump(data, f)

        with pytest.raises(ValueError, match="corpus must be one of"):
            load_metadata(yaml_path)


class TestSaveMetadata:
    """Test save_metadata function."""

    def test_save_valid_metadata(self, tmp_path: Path) -> None:
        """Test saving valid metadata to YAML file."""
        yaml_path = tmp_path / "test.yaml"
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            title="Test Document",
        )

        save_metadata(metadata, yaml_path)

        assert yaml_path.exists()

        # Verify content
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        assert data["doc_id"] == "test_001"
        assert data["title"] == "Test Document"

    def test_save_creates_parent_directory(self, tmp_path: Path) -> None:
        """Test that save_metadata creates parent directories."""
        yaml_path = tmp_path / "subdir" / "test.yaml"
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
        )

        save_metadata(metadata, yaml_path)

        assert yaml_path.exists()
        assert yaml_path.parent.exists()

    def test_save_validates_metadata(self, tmp_path: Path) -> None:
        """Test that save_metadata validates before saving."""
        yaml_path = tmp_path / "test.yaml"
        metadata = DocumentMetadata(
            doc_id="test_001",
            source_url="ftp://invalid.com/doc.pdf",  # Invalid URL
            corpus="academic",
            domain="arxiv",
        )

        with pytest.raises(ValueError, match="source_url must start with"):
            save_metadata(metadata, yaml_path)

        # File should not be created
        assert not yaml_path.exists()

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        """Test that save/load roundtrip preserves data."""
        yaml_path = tmp_path / "test.yaml"
        original = DocumentMetadata(
            doc_id="test_001",
            source_url="https://example.com/doc.pdf",
            corpus="academic",
            domain="arxiv",
            title="Test Document",
            authors=["Author One", "Author Two"],
            publication_date="2023-01-15",
            page_count=10,
            file_size_bytes=100000,
            features=["tables", "math"],
            language="en",
            license="CC-BY-4.0",
            notes="Test notes",
        )

        save_metadata(original, yaml_path)
        loaded = load_metadata(yaml_path)

        assert loaded.doc_id == original.doc_id
        assert loaded.source_url == original.source_url
        assert loaded.title == original.title
        assert loaded.authors == original.authors
        assert loaded.publication_date == original.publication_date
        assert loaded.page_count == original.page_count
        assert loaded.file_size_bytes == original.file_size_bytes
        assert loaded.features == original.features
        assert loaded.language == original.language
        assert loaded.license == original.license
        assert loaded.notes == original.notes


class TestExampleMetadataFiles:
    """Test that example metadata files are valid."""

    @pytest.fixture
    def corpus_dir(self) -> Path:
        """Get path to corpus directory."""
        return Path(__file__).parent.parent.parent / "corpus"

    def test_example_arxiv_metadata(self, corpus_dir: Path) -> None:
        """Test that example arXiv metadata file is valid."""
        yaml_path = corpus_dir / "academic" / "example_arxiv.yaml"

        if yaml_path.exists():
            metadata = load_metadata(yaml_path)
            assert metadata.corpus == "academic"
            assert metadata.domain == "arxiv"
            metadata.validate()  # Should not raise

    def test_example_govuk_metadata(self, corpus_dir: Path) -> None:
        """Test that example GOV.UK metadata file is valid."""
        yaml_path = corpus_dir / "business" / "example_govuk.yaml"

        if yaml_path.exists():
            metadata = load_metadata(yaml_path)
            assert metadata.corpus == "business"
            assert metadata.domain == "gov-uk"
            metadata.validate()  # Should not raise

    def test_example_synthetic_metadata(self, corpus_dir: Path) -> None:
        """Test that example synthetic metadata file is valid."""
        yaml_path = corpus_dir / "synthetic" / "example_pandoc.yaml"

        if yaml_path.exists():
            metadata = load_metadata(yaml_path)
            assert metadata.corpus == "synthetic"
            assert metadata.domain == "pandoc"
            metadata.validate()  # Should not raise


class TestConstants:
    """Test that module constants are correctly defined."""

    def test_valid_corpora(self) -> None:
        """Test VALID_CORPORA constant."""
        assert "academic" in VALID_CORPORA
        assert "business" in VALID_CORPORA
        assert "synthetic" in VALID_CORPORA

    def test_valid_domains(self) -> None:
        """Test VALID_DOMAINS constant."""
        assert "arxiv" in VALID_DOMAINS["academic"]
        assert "gov-uk" in VALID_DOMAINS["business"]
        assert "sec-edgar" in VALID_DOMAINS["business"]
        assert "pandoc" in VALID_DOMAINS["synthetic"]
        assert "libreoffice" in VALID_DOMAINS["synthetic"]

    def test_valid_features(self) -> None:
        """Test VALID_FEATURES constant."""
        expected_features = [
            "tables",
            "math",
            "figures",
            "code",
            "lists",
            "footnotes",
            "multi-column",
            "headers-footers",
        ]
        for feature in expected_features:
            assert feature in VALID_FEATURES
