"""
Document metadata schema and utilities for PDF-Bench corpus.

This module defines the structure and validation for document metadata files
that accompany each PDF in the corpus. Metadata is stored in YAML format and
includes information about the document source, content features, and licensing.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Valid corpus and domain values
VALID_CORPORA = ["academic", "business", "synthetic"]
VALID_DOMAINS = {
    "academic": [
        "arxiv",
        # OmniDocBench domains
        "academic",
        "academic_literature",
        "book",
        "colorful_textbook",
        "education",
        "exam_paper",
        "handwritten",
        "magazine",
        "mixed",
        "news",
        "newspaper",
        "note",
        "PPT2PDF",
        "presentation",
        "research_report",
    ],
    "business": [
        "gov-uk",
        "sec-edgar",
        "legal",
        "invoices",
        "hr",
        "legal_contracts",
        "presentations",
    ],
    "synthetic": ["pandoc", "libreoffice", "tables", "lists", "multicolumn", "mixed"],
}

# Valid feature tags
VALID_FEATURES = [
    "tables",
    "math",
    "figures",
    "code",
    "lists",
    "footnotes",
    "multi-column",
    "headers-footers",
]


@dataclass
class DocumentMetadata:
    """
    Metadata for a single document in the PDF-Bench corpus.

    Required Fields:
        doc_id: Unique identifier (e.g., "arxiv_2301_12345")
        corpus: Which corpus it belongs to ("academic", "business", "synthetic")
        domain: Subcategory within corpus (e.g., "arxiv", "gov-uk")

    Optional Fields:
        source_url: URL to download original PDF (optional for OmniDocBench)
        title: Document title
        authors: List of author names
        publication_date: When published (ISO 8601 format: "YYYY-MM-DD")
        page_count: Number of pages
        file_size_bytes: PDF file size in bytes
        features: List of features present (tables, math, images, code, etc.)
        language: Document language (ISO 639-1 code, default "en")
        license: License information (e.g., "CC-BY-4.0", "OGL-v3.0")
        notes: Free-form notes
    """

    # Required fields
    doc_id: str
    corpus: str
    domain: str

    # Optional fields
    source_url: str | None = None  # Made optional for OmniDocBench compatibility
    title: str | None = None
    authors: list[str] = field(default_factory=list)
    publication_date: str | None = None
    page_count: int | None = None
    file_size_bytes: int | None = None
    features: list[str] = field(default_factory=list)
    language: str = "en"
    license: str | None = None
    notes: str | None = None

    def validate(self) -> None:
        """
        Validate metadata against schema rules.

        Raises:
            ValueError: If any validation rule is violated
        """
        errors = []

        # Required fields must not be empty
        if not self.doc_id:
            errors.append("doc_id is required and cannot be empty")
        if not self.corpus:
            errors.append("corpus is required and cannot be empty")
        if not self.domain:
            errors.append("domain is required and cannot be empty")

        # Validate corpus
        if self.corpus and self.corpus not in VALID_CORPORA:
            errors.append(f"corpus must be one of {VALID_CORPORA}, got '{self.corpus}'")

        # Validate domain against corpus
        if self.corpus and self.domain:
            valid_domains = VALID_DOMAINS.get(self.corpus, [])
            if self.domain not in valid_domains:
                errors.append(
                    f"domain '{self.domain}' is not valid for corpus '{self.corpus}'. "
                    f"Valid domains: {valid_domains}"
                )

        # Validate URL format (basic check) - allow generated:// for synthetic data
        if self.source_url and not (
            self.source_url.startswith("http://")
            or self.source_url.startswith("https://")
            or self.source_url.startswith("generated://")
        ):
            errors.append(
                f"source_url must start with http://, https://, or generated://, "
                f"got '{self.source_url}'"
            )

        # Validate numeric fields
        if self.page_count is not None and self.page_count < 1:
            errors.append(f"page_count must be >= 1, got {self.page_count}")

        if self.file_size_bytes is not None and self.file_size_bytes < 0:
            errors.append(f"file_size_bytes must be >= 0, got {self.file_size_bytes}")

        # Note: Feature validation disabled to allow flexible tagging in synthetic corpus
        # for feature in self.features:
        #     if feature not in VALID_FEATURES:
        #         errors.append(f"Unknown feature '{feature}'. Valid features: {VALID_FEATURES}")

        # Validate language code - allow both 2-letter ISO codes and descriptive names
        # (OmniDocBench uses descriptive names like "simplified_chinese", "en")
        # Only flag completely empty/whitespace-only values
        if self.language is not None and not self.language.strip():
            errors.append("language cannot be empty or whitespace-only")

        # Validate publication_date format (basic check)
        if self.publication_date:
            try:
                parts = self.publication_date.split("-")
                if len(parts) != 3:
                    raise ValueError("Must have 3 parts")
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                if not (1900 <= year <= 2100):
                    raise ValueError("Year out of range")
                if not (1 <= month <= 12):
                    raise ValueError("Month out of range")
                if not (1 <= day <= 31):
                    raise ValueError("Day out of range")
            except (ValueError, IndexError):
                errors.append(
                    f"publication_date must be in YYYY-MM-DD format, got '{self.publication_date}'"
                )

        if errors:
            raise ValueError(
                f"Metadata validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {error}" for error in errors)
            )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert metadata to dictionary for YAML serialization.

        Returns:
            Dictionary representation of metadata
        """
        result: dict[str, Any] = {
            "doc_id": self.doc_id,
            "source_url": self.source_url,
            "corpus": self.corpus,
            "domain": self.domain,
        }

        # Add optional fields if present
        if self.title is not None:
            result["title"] = self.title
        if self.authors:
            result["authors"] = self.authors
        if self.publication_date is not None:
            result["publication_date"] = self.publication_date
        if self.page_count is not None:
            result["page_count"] = self.page_count
        if self.file_size_bytes is not None:
            result["file_size_bytes"] = self.file_size_bytes
        if self.features:
            result["features"] = self.features
        if self.language != "en":  # Only include if non-default
            result["language"] = self.language
        if self.license is not None:
            result["license"] = self.license
        if self.notes is not None:
            result["notes"] = self.notes

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        """
        Create metadata instance from dictionary.

        Args:
            data: Dictionary with metadata fields

        Returns:
            DocumentMetadata instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If validation fails
        """
        # Extract required fields
        try:
            doc_id = data["doc_id"]
            corpus = data["corpus"]
            domain = data["domain"]
        except KeyError as e:
            raise KeyError(f"Missing required field: {e}") from e

        # Create instance with optional fields
        metadata = cls(
            doc_id=doc_id,
            corpus=corpus,
            domain=domain,
            source_url=data.get("source_url"),  # Now optional
            title=data.get("title"),
            authors=data.get("authors", []),
            publication_date=data.get("publication_date"),
            page_count=data.get("page_count"),
            file_size_bytes=data.get("file_size_bytes"),
            features=data.get("features", []),
            language=data.get("language", "en"),
            license=data.get("license"),
            notes=data.get("notes"),
        )

        # Validate before returning
        metadata.validate()
        return metadata


def load_metadata(yaml_path: Path) -> DocumentMetadata:
    """
    Load document metadata from YAML file.

    Args:
        yaml_path: Path to YAML metadata file

    Returns:
        DocumentMetadata instance

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
        KeyError: If required fields are missing
        ValueError: If validation fails
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {yaml_path}")

    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML file {yaml_path}: {e}") from e

    if data is None:
        raise ValueError(f"Empty YAML file: {yaml_path}")

    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a dictionary, got {type(data)}")

    return DocumentMetadata.from_dict(data)


def save_metadata(metadata: DocumentMetadata, yaml_path: Path) -> None:
    """
    Save document metadata to YAML file.

    Args:
        metadata: DocumentMetadata instance to save
        yaml_path: Path to save YAML file

    Raises:
        ValueError: If metadata validation fails
        OSError: If file cannot be written
    """
    # Validate before saving
    metadata.validate()

    # Create parent directory if it doesn't exist
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict and save with nice formatting
    data = metadata.to_dict()

    try:
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,  # Preserve field order
                width=100,
            )
    except OSError as e:
        raise OSError(f"Failed to write metadata file {yaml_path}: {e}") from e
