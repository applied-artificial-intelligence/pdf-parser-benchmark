#!/usr/bin/env python3
"""
Corpus validation script for PDF-Bench synthetic corpus.

Validates all documents in the synthetic corpus by checking:
1. YAML schema compliance
2. File existence verification
3. SHA256 hash verification
4. Markdown syntax validation
5. PDF parseability testing

Generates a comprehensive validation report.
"""

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Add parent directory to path to import pdf_bench modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_bench.systems.pymupdf import PyMuPDFParser


@dataclass
class ValidationResult:
    """Result of validating a single document."""

    document_id: str
    yaml_file: Path
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message and mark as failed."""
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)


class CorpusValidator:
    """Validator for PDF-Bench corpus documents."""

    def __init__(self, corpus_dir: Path):
        """
        Initialize corpus validator.

        Args:
            corpus_dir: Path to corpus directory (e.g., corpus/synthetic)
        """
        self.corpus_dir = corpus_dir
        self.results: list[ValidationResult] = []

    def validate_all(self) -> list[ValidationResult]:
        """
        Validate all documents in the corpus.

        Returns:
            List of validation results, one per document
        """
        # Find all YAML metadata files (excluding example files)
        yaml_files = sorted(self.corpus_dir.glob("*.yaml"))
        yaml_files = [
            f for f in yaml_files if not f.name.startswith("example_")
        ]

        print(f"Found {len(yaml_files)} documents to validate")
        print()

        for yaml_file in yaml_files:
            result = self.validate_document(yaml_file)
            self.results.append(result)

        return self.results

    def validate_document(self, yaml_file: Path) -> ValidationResult:
        """
        Validate a single document.

        Args:
            yaml_file: Path to YAML metadata file

        Returns:
            ValidationResult with status and any errors/warnings
        """
        doc_id = yaml_file.stem
        result = ValidationResult(document_id=doc_id, yaml_file=yaml_file)

        print(f"Validating {doc_id}...")

        # 1. Load and validate YAML
        try:
            with open(yaml_file, encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"YAML parsing error: {e}")
            return result
        except Exception as e:
            result.add_error(f"Error reading YAML file: {e}")
            return result

        if not isinstance(metadata, dict):
            result.add_error("YAML root must be a dictionary")
            return result

        # 2. Validate YAML schema
        self._validate_yaml_schema(metadata, result)

        # 3. Validate file existence
        file_paths = self._validate_file_existence(metadata, result)

        # 4. Validate hashes
        if file_paths:
            self._validate_hashes(metadata, file_paths, result)

        # 5. Validate Markdown syntax
        if file_paths.get("ground_truth"):
            self._validate_markdown(file_paths["ground_truth"], result)

        # 6. Test PDF parseability
        if file_paths.get("pdf"):
            self._validate_pdf_parseability(file_paths["pdf"], result)

        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  {status}")
        print()

        return result

    def _validate_yaml_schema(
        self, metadata: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate YAML schema compliance."""
        # Check for required fields based on document type
        if "file_paths" in metadata:
            # Pandoc-generated document format
            required_fields = [
                "document_id",
                "source_type",
                "category",
                "title",
                "file_paths",
            ]
            for field in required_fields:
                if field not in metadata:
                    result.add_error(f"Missing required field: {field}")

            # Validate file_paths structure
            if "file_paths" in metadata:
                file_paths = metadata["file_paths"]
                if not isinstance(file_paths, dict):
                    result.add_error("file_paths must be a dictionary")
                else:
                    for required_path in ["ground_truth", "pdf"]:
                        if required_path not in file_paths:
                            result.add_error(
                                f"Missing required file path: {required_path}"
                            )

        elif "files" in metadata:
            # DOCX-generated document format
            required_fields = ["title", "corpus", "category", "files"]
            for field in required_fields:
                if field not in metadata:
                    result.add_error(f"Missing required field: {field}")

            # Validate files structure
            if "files" in metadata:
                files = metadata["files"]
                if not isinstance(files, dict):
                    result.add_error("files must be a dictionary")
                else:
                    for required_file in ["pdf", "ground_truth"]:
                        if required_file not in files:
                            result.add_error(
                                f"Missing required file: {required_file}"
                            )

        else:
            result.add_error(
                "Metadata must contain either 'file_paths' or 'files' field"
            )

        # Validate corpus/category values
        valid_corpora = ["synthetic", "academic", "business"]
        if "corpus" in metadata and metadata["corpus"] not in valid_corpora:
            result.add_error(
                f"Invalid corpus: {metadata['corpus']}, "
                f"must be one of {valid_corpora}"
            )

        # Validate hash presence
        has_hash = False
        if "pdf_hash" in metadata:
            has_hash = True
        elif "hashes" in metadata and isinstance(metadata["hashes"], dict):
            if "pdf_sha256" in metadata["hashes"]:
                has_hash = True

        if not has_hash:
            result.add_warning(
                "No PDF hash found (pdf_hash or hashes.pdf_sha256)"
            )

    def _validate_file_existence(
        self, metadata: dict[str, Any], result: ValidationResult
    ) -> dict[str, Path]:
        """
        Validate that all referenced files exist.

        Returns:
            Dictionary mapping file types to their resolved paths
        """
        file_paths = {}

        # Extract file paths based on format
        if "file_paths" in metadata:
            # Pandoc format
            paths_dict = metadata["file_paths"]
            pdf_path = paths_dict.get("pdf")
            gt_path = paths_dict.get("ground_truth")
        elif "files" in metadata:
            # DOCX format
            files_dict = metadata["files"]
            pdf_path = files_dict.get("pdf")
            gt_path = files_dict.get("ground_truth")
            docx_path = files_dict.get("docx")

            # Check DOCX file
            if docx_path:
                full_path = self.corpus_dir / docx_path
                if not full_path.exists():
                    result.add_error(f"DOCX file not found: {docx_path}")
                else:
                    file_paths["docx"] = full_path
        else:
            return file_paths

        # Check PDF file
        if pdf_path:
            # Handle both absolute and relative paths
            if pdf_path.startswith("corpus/"):
                # Absolute path from project root
                full_path = Path(pdf_path)
            else:
                # Relative path from corpus directory
                full_path = self.corpus_dir / pdf_path

            if not full_path.exists():
                result.add_error(f"PDF file not found: {pdf_path}")
            else:
                file_paths["pdf"] = full_path
        else:
            result.add_error("No PDF path specified in metadata")

        # Check ground truth file
        if gt_path:
            if gt_path.startswith("corpus/"):
                full_path = Path(gt_path)
            else:
                full_path = self.corpus_dir / gt_path

            if not full_path.exists():
                result.add_error(f"Ground truth file not found: {gt_path}")
            else:
                file_paths["ground_truth"] = full_path
        else:
            result.add_error("No ground truth path specified in metadata")

        return file_paths

    def _validate_hashes(
        self,
        metadata: dict[str, Any],
        file_paths: dict[str, Path],
        result: ValidationResult,
    ) -> None:
        """Validate SHA256 hashes match actual file contents."""
        # Get expected hash from metadata
        expected_hash = None
        if "pdf_hash" in metadata:
            expected_hash = metadata["pdf_hash"]
        elif "hashes" in metadata and isinstance(metadata["hashes"], dict):
            expected_hash = metadata["hashes"].get("pdf_sha256")

        if not expected_hash:
            # Already warned in schema validation
            return

        # Calculate actual hash
        pdf_path = file_paths.get("pdf")
        if not pdf_path:
            # Already reported as error in file existence check
            return

        try:
            actual_hash = self._calculate_sha256(pdf_path)
        except Exception as e:
            result.add_error(f"Error calculating hash: {e}")
            return

        # Compare hashes
        if actual_hash != expected_hash:
            result.add_error(
                f"PDF hash mismatch:\n"
                f"  Expected: {expected_hash}\n"
                f"  Actual:   {actual_hash}"
            )

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _validate_markdown(self, md_path: Path, result: ValidationResult) -> None:
        """
        Validate Markdown syntax.

        Basic validation to ensure file is readable and contains reasonable content.
        """
        try:
            with open(md_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            result.add_error(f"Error reading Markdown file: {e}")
            return

        # Basic sanity checks
        if not content.strip():
            result.add_error("Ground truth Markdown file is empty")
            return

        if len(content) < 50:
            result.add_warning(
                f"Ground truth is very short ({len(content)} chars)"
            )

        # Check for common Markdown elements (at least some should be present)
        # Note: Some ground truth may have headings without # syntax
        # (e.g., Pandoc output or plain text headers)
        has_markdown_headings = "#" in content
        has_paragraphs = len(content.split("\n\n")) > 1
        # Check for lines that look like headings (short lines followed by content)
        lines = content.split("\n")
        has_heading_like_lines = any(
            len(line.strip()) < 60 and line.strip() and i < len(lines) - 1
            for i, line in enumerate(lines)
        )

        # Only warn if there's truly no structure
        if not has_markdown_headings and not has_paragraphs and not has_heading_like_lines:
            result.add_warning(
                "Ground truth contains minimal structure"
            )

    def _validate_pdf_parseability(
        self, pdf_path: Path, result: ValidationResult
    ) -> None:
        """Test that PDF can be parsed with PyMuPDFParser."""
        import tempfile

        try:
            parser = PyMuPDFParser()

            # Use a temporary directory for output
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = parser.parse(pdf_path, Path(temp_dir))

                # Check that output file was created
                if not output_path.exists():
                    result.add_error("PDF parsing did not create output file")
                    return

                # Read and check the extracted text
                with open(output_path, encoding="utf-8") as f:
                    extracted_text = f.read()

                if not extracted_text.strip():
                    result.add_error("PDF parsed but extracted no text")
                elif len(extracted_text) < 50:
                    result.add_warning(
                        f"PDF extracted very little text ({len(extracted_text)} chars)"
                    )

        except Exception as e:
            result.add_error(f"PDF parsing failed: {e}")

    def generate_report(self) -> str:
        """
        Generate validation report.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("PDF-BENCH CORPUS VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        lines.append(f"Total Documents: {total}")
        lines.append(f"✅ Passed: {passed}")
        lines.append(f"❌ Failed: {failed}")
        lines.append("")

        if failed == 0:
            lines.append("🎉 ALL DOCUMENTS VALIDATED SUCCESSFULLY!")
            lines.append("")

        # Detailed results
        lines.append("=" * 80)
        lines.append("DETAILED RESULTS")
        lines.append("=" * 80)
        lines.append("")

        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"{status}  {result.document_id}")
            lines.append("-" * 80)

            if result.errors:
                lines.append("  ERRORS:")
                for error in result.errors:
                    lines.append(f"    • {error}")

            if result.warnings:
                lines.append("  WARNINGS:")
                for warning in result.warnings:
                    lines.append(f"    ⚠ {warning}")

            if not result.errors and not result.warnings:
                lines.append("  All checks passed ✓")

            lines.append("")

        return "\n".join(lines)


def main() -> int:
    """
    Main entry point for validation script.

    Returns:
        Exit code: 0 if all documents passed, 1 if any failed
    """
    # Determine corpus directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    corpus_dir = project_root / "corpus" / "synthetic"

    if not corpus_dir.exists():
        print(f"ERROR: Corpus directory not found: {corpus_dir}")
        return 1

    print("=" * 80)
    print("PDF-BENCH CORPUS VALIDATION")
    print("=" * 80)
    print(f"Corpus directory: {corpus_dir}")
    print()

    # Run validation
    validator = CorpusValidator(corpus_dir)
    results = validator.validate_all()

    # Generate and print report
    report = validator.generate_report()
    print(report)

    # Save report to file
    report_file = project_root / "TASK-017-validation-report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to: {report_file}")

    # Return exit code
    failed_count = sum(1 for r in results if not r.passed)
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
