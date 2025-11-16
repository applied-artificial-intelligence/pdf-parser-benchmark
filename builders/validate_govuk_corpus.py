#!/usr/bin/env python3
"""Validation script for GOV.UK corpus.

This script validates the integrity of the GOV.UK corpus by checking:
- File existence (HTML, Markdown, PDF, metadata)
- File integrity (SHA256 hashes for PDFs)
- Metadata completeness
- License information
- File sizes and non-empty content

Usage:
    python builders/validate_govuk_corpus.py
    python builders/validate_govuk_corpus.py --corpus-dir corpus/business/govuk
    python builders/validate_govuk_corpus.py --verbose

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import argparse
import hashlib
import logging
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_CORPUS_DIR = Path("corpus/business/govuk")


class ValidationError:
    """Represents a validation error."""

    def __init__(self, doc_id: str, severity: str, message: str):
        """Initialize validation error.

        Args:
            doc_id: Document ID
            severity: Error severity (error, warning, info)
            message: Error message
        """
        self.doc_id = doc_id
        self.severity = severity
        self.message = message

    def __str__(self):
        return f"[{self.severity.upper()}] {self.doc_id}: {self.message}"


class CorpusValidator:
    """Validates GOV.UK corpus integrity."""

    def __init__(self, corpus_dir: Path):
        """Initialize validator.

        Args:
            corpus_dir: Path to corpus directory
        """
        self.corpus_dir = corpus_dir
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []
        self.info: list[ValidationError] = []

    def add_error(self, doc_id: str, message: str) -> None:
        """Add an error."""
        self.errors.append(ValidationError(doc_id, "error", message))
        logger.error(f"{doc_id}: {message}")

    def add_warning(self, doc_id: str, message: str) -> None:
        """Add a warning."""
        self.warnings.append(ValidationError(doc_id, "warning", message))
        logger.warning(f"{doc_id}: {message}")

    def add_info(self, doc_id: str, message: str) -> None:
        """Add an info message."""
        self.info.append(ValidationError(doc_id, "info", message))
        logger.debug(f"{doc_id}: {message}")

    def validate_file_exists(self, file_path: Path, doc_id: str, file_type: str) -> bool:
        """Validate that a file exists.

        Args:
            file_path: Path to file
            doc_id: Document ID
            file_type: Type of file (for error message)

        Returns:
            True if file exists, False otherwise
        """
        if not file_path.exists():
            self.add_error(doc_id, f"{file_type} file not found: {file_path.name}")
            return False
        return True

    def validate_file_not_empty(self, file_path: Path, doc_id: str, file_type: str) -> bool:
        """Validate that a file is not empty.

        Args:
            file_path: Path to file
            doc_id: Document ID
            file_type: Type of file

        Returns:
            True if file is not empty, False otherwise
        """
        if file_path.exists():
            size = file_path.stat().st_size
            if size == 0:
                self.add_error(doc_id, f"{file_type} file is empty")
                return False
            if size < 100:  # Very small files might be incomplete
                self.add_warning(doc_id, f"{file_type} file is very small ({size} bytes)")
        return True

    def validate_pdf_hash(self, pdf_path: Path, expected_hash: str, doc_id: str) -> bool:
        """Validate PDF file hash.

        Args:
            pdf_path: Path to PDF file
            expected_hash: Expected SHA256 hash
            doc_id: Document ID

        Returns:
            True if hash matches, False otherwise
        """
        if not pdf_path.exists():
            return False

        # Calculate actual hash
        sha256_hash = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        actual_hash = sha256_hash.hexdigest()

        if actual_hash != expected_hash:
            self.add_error(
                doc_id,
                f"PDF hash mismatch: expected {expected_hash[:16]}..., got {actual_hash[:16]}...",
            )
            return False

        return True

    def validate_metadata_completeness(self, metadata: dict, doc_id: str) -> bool:
        """Validate metadata completeness.

        Args:
            metadata: Metadata dictionary
            doc_id: Document ID

        Returns:
            True if metadata is complete, False otherwise
        """
        required_fields = [
            "id",
            "title",
            "source_url",
            "publisher",
            "license",
            "license_url",
            "download_date",
            "topics",
            "complexity",
        ]

        all_present = True
        for field in required_fields:
            if field not in metadata:
                self.add_error(doc_id, f"Missing required metadata field: {field}")
                all_present = False

        # Validate license
        if metadata.get("license") != "Open Government Licence v3.0":
            self.add_error(doc_id, f"Invalid license: {metadata.get('license')}")
            all_present = False

        # Validate topics list
        if not isinstance(metadata.get("topics"), list) or not metadata.get("topics"):
            self.add_warning(doc_id, "Topics field is empty or not a list")

        return all_present

    def validate_document(self, doc_id: str) -> bool:
        """Validate a single document.

        Args:
            doc_id: Document ID

        Returns:
            True if document is valid, False otherwise
        """
        logger.info(f"Validating {doc_id}...")

        # Define paths
        html_path = self.corpus_dir / "html" / f"{doc_id}.html"
        markdown_path = self.corpus_dir / "ground_truth" / f"{doc_id}.md"
        pdf_path = self.corpus_dir / "pdfs" / f"{doc_id}.pdf"
        metadata_path = self.corpus_dir / "metadata" / f"{doc_id}.yaml"

        all_valid = True

        # Validate metadata exists
        if not self.validate_file_exists(metadata_path, doc_id, "Metadata"):
            return False

        # Load metadata
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        # Validate metadata completeness
        if not self.validate_metadata_completeness(metadata, doc_id):
            all_valid = False

        # Validate HTML exists and is not empty
        if not self.validate_file_exists(html_path, doc_id, "HTML"):
            all_valid = False
        else:
            if not self.validate_file_not_empty(html_path, doc_id, "HTML"):
                all_valid = False

        # Validate Markdown exists and is not empty
        if not self.validate_file_exists(markdown_path, doc_id, "Markdown"):
            all_valid = False
        else:
            if not self.validate_file_not_empty(markdown_path, doc_id, "Markdown"):
                all_valid = False

        # Validate PDF (if expected)
        if metadata.get("has_pdf"):
            if not self.validate_file_exists(pdf_path, doc_id, "PDF"):
                all_valid = False
            else:
                if not self.validate_file_not_empty(pdf_path, doc_id, "PDF"):
                    all_valid = False

                # Validate PDF hash
                expected_hash = metadata.get("sha256_pdf")
                if expected_hash:
                    if not self.validate_pdf_hash(pdf_path, expected_hash, doc_id):
                        all_valid = False
                else:
                    self.add_warning(doc_id, "PDF hash not found in metadata")
        else:
            # Document should be HTML-only
            if pdf_path.exists():
                self.add_warning(doc_id, "PDF exists but metadata says HTML-only")
            else:
                self.add_info(doc_id, "HTML-only document (no PDF)")

        return all_valid

    def validate_corpus_metadata(self) -> bool:
        """Validate corpus metadata file.

        Returns:
            True if corpus metadata is valid, False otherwise
        """
        logger.info("Validating corpus metadata...")

        corpus_metadata_path = self.corpus_dir / "corpus_metadata.yaml"

        if not corpus_metadata_path.exists():
            self.add_error("corpus", "Corpus metadata file not found")
            return False

        # Load corpus metadata
        with open(corpus_metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        # Validate required fields
        required_fields = [
            "corpus_name",
            "corpus_id",
            "version",
            "created_date",
            "license",
            "license_url",
            "statistics",
            "documents",
        ]

        all_valid = True
        for field in required_fields:
            if field not in metadata:
                self.add_error("corpus", f"Missing required field: {field}")
                all_valid = False

        # Validate license
        if metadata.get("license") != "Open Government Licence v3.0":
            self.add_error("corpus", f"Invalid license: {metadata.get('license')}")
            all_valid = False

        # Validate statistics
        stats = metadata.get("statistics", {})
        if stats.get("total_documents", 0) == 0:
            self.add_error("corpus", "No documents in corpus statistics")
            all_valid = False

        return all_valid

    def validate_all(self) -> dict:
        """Validate entire corpus.

        Returns:
            Validation summary dictionary
        """
        logger.info("=" * 60)
        logger.info("STARTING CORPUS VALIDATION")
        logger.info("=" * 60)

        # Validate corpus metadata
        corpus_valid = self.validate_corpus_metadata()

        # Load corpus metadata to get document list
        corpus_metadata_path = self.corpus_dir / "corpus_metadata.yaml"
        if corpus_metadata_path.exists():
            with open(corpus_metadata_path, "r", encoding="utf-8") as f:
                corpus_metadata = yaml.safe_load(f)
            document_ids = corpus_metadata.get("documents", [])
        else:
            # If corpus metadata doesn't exist, try to find documents from metadata dir
            metadata_dir = self.corpus_dir / "metadata"
            if metadata_dir.exists():
                document_ids = [
                    p.stem for p in sorted(metadata_dir.glob("*.yaml"))
                    if p.stem != "corpus_metadata"
                ]
            else:
                logger.error("Cannot find documents to validate")
                return self.get_summary()

        logger.info(f"\nValidating {len(document_ids)} documents...\n")

        # Validate each document
        valid_count = 0
        for doc_id in document_ids:
            if self.validate_document(doc_id):
                valid_count += 1

        # Print summary
        summary = self.get_summary()
        summary["corpus_valid"] = corpus_valid
        summary["documents_validated"] = len(document_ids)
        summary["documents_valid"] = valid_count

        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Corpus metadata:      {'✅ VALID' if corpus_valid else '❌ INVALID'}")
        logger.info(f"Documents validated:  {summary['documents_validated']}")
        logger.info(f"Documents valid:      {summary['documents_valid']}")
        logger.info(f"Documents invalid:    {summary['documents_validated'] - summary['documents_valid']}")
        logger.info(f"Errors:               {summary['error_count']}")
        logger.info(f"Warnings:             {summary['warning_count']}")
        logger.info(f"Info messages:        {summary['info_count']}")
        logger.info("=" * 60)

        if summary["error_count"] == 0:
            logger.info("\n✅ CORPUS VALIDATION PASSED")
        else:
            logger.error("\n❌ CORPUS VALIDATION FAILED")
            logger.error("\nErrors found:")
            for error in self.errors:
                logger.error(f"  {error}")

        if summary["warning_count"] > 0:
            logger.warning("\nWarnings:")
            for warning in self.warnings:
                logger.warning(f"  {warning}")

        return summary

    def get_summary(self) -> dict:
        """Get validation summary.

        Returns:
            Dictionary with validation summary
        """
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info),
            "errors": [str(e) for e in self.errors],
            "warnings": [str(w) for w in self.warnings],
            "info": [str(i) for i in self.info],
        }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate GOV.UK corpus integrity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=DEFAULT_CORPUS_DIR,
        help=f"Path to corpus directory (default: {DEFAULT_CORPUS_DIR})",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate corpus directory exists
    if not args.corpus_dir.exists():
        logger.error(f"Corpus directory does not exist: {args.corpus_dir}")
        exit(1)

    # Create validator and run validation
    validator = CorpusValidator(args.corpus_dir)
    summary = validator.validate_all()

    # Exit with error code if validation failed
    if summary["error_count"] > 0:
        exit(1)


if __name__ == "__main__":
    main()
