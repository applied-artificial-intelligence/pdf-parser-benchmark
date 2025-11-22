"""Legal contract corpus builder.

Generates 100 realistic legal contracts across 5 types:
- 30 SaaS Agreements
- 30 Employment Agreements
- 20 Non-Disclosure Agreements
- 10 Consulting Agreements
- 10 Service Agreements

Each contract includes:
- DOCX source document
- PDF conversion (normalized for parser compatibility)
- Markdown ground truth
- YAML metadata with contract details and quality tags

Usage:
    python build_legal_corpus.py              # Generate full corpus (100 contracts)
    python build_legal_corpus.py --test       # Generate test corpus (10 contracts)
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builders.legal.contract_templates import get_template  # noqa: E402
from builders.legal.data_generators import LegalDataGenerator  # noqa: E402
from builders.pdf_utils import normalize_pdf  # noqa: E402


class LegalCorpusBuilder:
    """Builds the legal contract corpus."""

    def __init__(self, base_dir: Path, test_mode: bool = False):
        """Initialize corpus builder.

        Args:
            base_dir: Base directory for corpus (e.g., corpus/business/legal)
            test_mode: If True, generate test corpus (10 contracts)
        """
        self.base_dir = base_dir
        self.test_mode = test_mode
        self.generator = LegalDataGenerator(seed=42 if test_mode else 0)

        # Contract distribution
        if test_mode:
            self.distribution = {
                "saas": 2,
                "employment": 2,
                "nda": 2,
                "consulting": 2,
                "service": 2,
            }
        else:
            self.distribution = {
                "saas": 30,
                "employment": 30,
                "nda": 20,
                "consulting": 10,
                "service": 10,
            }

        # Set up directories
        self.docx_dir = base_dir / "docx"
        self.pdf_dir = base_dir / "pdfs"
        self.ground_truth_dir = base_dir / "ground_truth"
        self.metadata_dir = base_dir / "metadata"

        self._create_directories()

    def _create_directories(self) -> None:
        """Create output directories."""
        for directory in [self.docx_dir, self.pdf_dir, self.ground_truth_dir, self.metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _docx_to_pdf(self, docx_path: Path, pdf_path: Path) -> bool:
        """Convert DOCX to PDF using LibreOffice.

        Args:
            docx_path: Path to DOCX file
            pdf_path: Path to output PDF file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use LibreOffice headless for conversion
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(pdf_path.parent),
                    str(docx_path),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )
            # Normalize PDF for parser compatibility
            normalize_pdf(pdf_path)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Warning: PDF conversion failed for {docx_path.name}: {e}")
            return False

    def _extract_ground_truth(self, doc_path: Path) -> str:
        """Extract ground truth markdown from DOCX.

        Args:
            doc_path: Path to DOCX file

        Returns:
            Markdown content
        """
        from docx import Document

        doc = Document(str(doc_path))
        lines = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                lines.append("")  # Preserve blank lines
                continue

            # Check if this is a heading
            style_name = para.style.name if para.style else ""
            if style_name.startswith("Heading"):
                # Extract heading level
                if style_name == "Heading 1":
                    lines.append(f"# {text}")
                elif style_name == "Heading 2":
                    lines.append(f"## {text}")
                elif style_name == "Heading 3":
                    lines.append(f"### {text}")
                else:
                    lines.append(text)
            else:
                # Regular paragraph
                lines.append(text)

        return "\n".join(lines)

    def _generate_metadata(
        self, contract_id: str, contract_type: str, variables: dict[str, object]
    ) -> dict[str, object]:
        """Generate metadata for a contract.

        Args:
            contract_id: Contract identifier (e.g., "legal_saas_001")
            contract_type: Contract type
            variables: Variables used to generate contract

        Returns:
            Metadata dictionary
        """
        # Extract key information from variables
        metadata: dict[str, object] = {
            "id": contract_id,
            "contract_type": contract_type,
            "generated_at": datetime.now().isoformat(),
            "source": "synthetic",
            "category": "business",
            "subcategory": "legal",
        }

        # Add contract-specific metadata
        if contract_type == "saas":
            metadata.update(
                {
                    "provider": variables["provider"],
                    "customer": variables["customer"],
                    "platform_name": variables.get("platform_name", ""),
                    "annual_value": str(int(str(variables.get("monthly_fee", 0) or 0)) * 12),
                    "jurisdiction": variables.get("jurisdiction", ""),
                }
            )
        elif contract_type == "employment":
            metadata.update(
                {
                    "employer": variables["company"],
                    "employee": variables["employee"],
                    "position": variables.get("position_title", ""),
                    "annual_salary": variables.get("annual_salary", ""),
                    "jurisdiction": variables.get("jurisdiction", ""),
                }
            )
        elif contract_type == "nda":
            metadata.update(
                {
                    "disclosing_party": variables["disclosing_party"],
                    "receiving_party": variables["receiving_party"],
                    "purpose": variables.get("purpose", ""),
                    "jurisdiction": variables.get("jurisdiction", ""),
                }
            )
        elif contract_type == "consulting":
            metadata.update(
                {
                    "client": variables["client"],
                    "consultant": variables["consultant"],
                    "hourly_rate": variables.get("hourly_rate", 0),
                    "jurisdiction": variables.get("jurisdiction", ""),
                }
            )
        elif contract_type == "service":
            metadata.update(
                {
                    "service_provider": variables["service_provider"],
                    "customer": variables["customer"],
                    "service_description": variables.get("service_description", ""),
                    "jurisdiction": variables.get("jurisdiction", ""),
                }
            )

        # Quality tags for benchmarking
        metadata["quality_tags"] = [
            "legal_numbering",  # Uses 5-level legal numbering
            "defined_terms",  # Contains defined terms
            "signature_blocks",  # Has signature blocks
            "recitals",  # Contains WHEREAS clauses
            "multi_section",  # Multiple numbered sections
        ]

        # Complexity indicators
        metadata["complexity"] = {
            "has_subsections": True,
            "has_numbered_lists": True,
            "has_legal_language": True,
            "multi_page": True,
        }

        return metadata

    def generate_contract(self, contract_type: str, contract_num: int) -> bool:
        """Generate a single contract.

        Args:
            contract_type: Type of contract (saas, employment, nda, consulting, service)
            contract_num: Contract number within type

        Returns:
            True if successful, False otherwise
        """
        # Generate ID
        type_abbr = {
            "saas": "saas",
            "employment": "emp",
            "nda": "nda",
            "consulting": "cons",
            "service": "svc",
        }
        contract_id = f"legal_{type_abbr[contract_type]}_{contract_num:03d}"

        print(f"Generating {contract_id}...")

        try:
            # Generate contract data
            variables = self.generator.generate_contract_variables(contract_type)

            # Generate DOCX using template
            template = get_template(contract_type)
            doc = template.generate(variables)
            if doc is None:
                raise RuntimeError(f"Failed to generate document for {contract_id}")

            # Save DOCX
            docx_path = self.docx_dir / f"{contract_id}.docx"
            doc.save(str(docx_path))
            print(f"  ✓ Created DOCX: {docx_path.name}")

            # Convert to PDF
            pdf_path = self.pdf_dir / f"{contract_id}.pdf"
            if self._docx_to_pdf(docx_path, pdf_path):
                print(f"  ✓ Converted to PDF: {pdf_path.name}")
            else:
                print("  ⚠ PDF conversion failed (continuing anyway)")

            # Extract ground truth
            ground_truth = self._extract_ground_truth(docx_path)
            gt_path = self.ground_truth_dir / f"{contract_id}.md"
            gt_path.write_text(ground_truth, encoding="utf-8")
            print(f"  ✓ Extracted ground truth: {gt_path.name}")

            # Generate metadata
            metadata = self._generate_metadata(contract_id, contract_type, variables)
            metadata_path = self.metadata_dir / f"{contract_id}.yaml"
            with open(metadata_path, "w") as f:
                yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
            print(f"  ✓ Generated metadata: {metadata_path.name}")

            return True

        except Exception as e:
            print(f"  ✗ Error generating {contract_id}: {e}")
            import traceback

            traceback.print_exc()
            return False

    def build_corpus(self) -> dict[str, int]:
        """Build the complete corpus.

        Returns:
            Dictionary with success/failure counts
        """
        print(f"\n{'=' * 60}")
        print("Legal Corpus Builder")
        print(f"Mode: {'TEST' if self.test_mode else 'FULL'}")
        print(f"Output: {self.base_dir}")
        print(f"{'=' * 60}\n")

        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
        }

        # Generate contracts by type
        global_num = 1
        for contract_type, count in self.distribution.items():
            print(f"\n📄 Generating {count} {contract_type.upper()} contracts...")

            for _i in range(1, count + 1):
                if self.generate_contract(contract_type, global_num):
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                stats["total"] += 1
                global_num += 1

        # Print summary
        print(f"\n{'=' * 60}")
        print("Corpus Generation Complete")
        print(f"{'=' * 60}")
        print(f"Total contracts: {stats['total']}")
        print(f"Successful: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print("\nOutput directories:")
        print(f"  - DOCX: {self.docx_dir}")
        print(f"  - PDF: {self.pdf_dir}")
        print(f"  - Ground Truth: {self.ground_truth_dir}")
        print(f"  - Metadata: {self.metadata_dir}")

        return stats


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build legal contract corpus")
    parser.add_argument(
        "--test", action="store_true", help="Generate test corpus (10 contracts instead of 100)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("corpus/business/legal"),
        help="Output directory for corpus (default: corpus/business/legal)",
    )
    args = parser.parse_args()

    # Build corpus
    builder = LegalCorpusBuilder(base_dir=args.output_dir, test_mode=args.test)

    stats = builder.build_corpus()

    # Exit with error code if any failed
    sys.exit(0 if stats["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
