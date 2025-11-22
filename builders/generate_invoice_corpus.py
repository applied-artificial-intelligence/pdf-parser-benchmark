"""Generate comprehensive 100-invoice corpus for PDF-Bench.

This script generates 100 realistic business invoices distributed across:
- 5 geographic regions (US, EU, UK, Canada, APAC)
- 15 industry types
- 3 complexity levels
- 3 quality levels (digital perfect → degraded scans)

Output:
- DOCX source files for ground truth extraction
- PDF files for parser testing
- Markdown ground truth
- YAML metadata
"""

import argparse
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

import yaml
from docx import Document

from builders.invoice.data_generators import InvoiceDataGenerator
from builders.invoice.industry_config import INDUSTRIES
from builders.invoice.tax_calculators import get_tax_calculator
from builders.invoice.templates import get_template

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Distribution matrix: 100 invoices across 5 regions
DISTRIBUTION = {
    "US": {
        "count": 30,
        "industries": ["saas", "manufacturing", "legal", "it_consulting", "construction", "retail"],
        "states": ["CA", "TX", "NY", "FL", "IL"],
    },
    "EU": {
        "count": 20,
        "industries": ["manufacturing", "saas", "architecture", "printing", "freight"],
        "countries": ["DE", "FR", "IT", "ES", "NL"],
    },
    "UK": {
        "count": 15,
        "industries": ["legal", "accounting", "marketing", "property_mgmt"],
    },
    "CA": {
        "count": 20,
        "industries": ["construction", "it_consulting", "medical", "landscaping"],
        "provinces": ["ON", "BC", "AB", "QC"],
    },
    "APAC": {
        "count": 15,
        "industries": ["saas", "manufacturing", "freight", "catering"],
        "countries": ["AU", "SG", "NZ"],
    },
}


# Complexity levels
COMPLEXITY_LEVELS = {
    "simple": {"min_items": 1, "max_items": 3, "weight": 0.3},
    "medium": {"min_items": 4, "max_items": 10, "weight": 0.5},
    "complex": {"min_items": 11, "max_items": 50, "weight": 0.2},
}


# Template styles
TEMPLATE_STYLES = ["enterprise", "small_business", "economy"]


def extract_ground_truth_from_docx(docx_path: Path) -> str:
    """Extract plain text ground truth from DOCX invoice.

    Args:
        docx_path: Path to DOCX file

    Returns:
        Markdown-formatted ground truth text
    """
    doc = Document(docx_path)

    # Extract text from all paragraphs
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            # Detect headings by font size or bold
            is_heading = False
            if para.runs:
                first_run = para.runs[0]
                if first_run.bold and first_run.font.size and first_run.font.size.pt >= 12:
                    is_heading = True

            if is_heading:
                paragraphs.append(f"\n## {text}\n")
            else:
                paragraphs.append(text)

    # Extract text from tables
    for table in doc.tables:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append(" | ".join(cells))

        if rows:
            paragraphs.append("\n")
            # First row as header
            paragraphs.append(rows[0])
            paragraphs.append("---")
            # Remaining rows
            for row in rows[1:]:
                paragraphs.append(row)
            paragraphs.append("")

    return "\n".join(paragraphs)


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> None:
    """Convert DOCX to PDF using LibreOffice headless.

    Args:
        docx_path: Path to input DOCX file
        pdf_path: Path for output PDF file
    """
    output_dir = pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run LibreOffice conversion
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    # LibreOffice outputs with same stem as input, rename if needed
    generated_pdf = output_dir / f"{docx_path.stem}.pdf"
    if generated_pdf != pdf_path and generated_pdf.exists():
        generated_pdf.rename(pdf_path)


def generate_invoice(
    invoice_id: int,
    region: str,
    industry_key: str,
    complexity: str,
    template_style: str,
    output_dirs: dict[str, Path],
    generator: InvoiceDataGenerator,
) -> tuple[Path, Path, Path]:
    """Generate a single invoice with DOCX, PDF, ground truth, and metadata.

    Args:
        invoice_id: Invoice number (001-100)
        region: Geographic region (US, EU, UK, CA, APAC)
        industry_key: Industry key from INDUSTRIES dict
        complexity: Complexity level (simple, medium, complex)
        template_style: Template style (enterprise, small_business, economy)
        output_dirs: Dictionary of output directories
        generator: InvoiceDataGenerator instance

    Returns:
        Tuple of (docx_path, pdf_path, ground_truth_path)
    """
    invoice_code = f"invoice_{invoice_id:03d}"

    logger.info(f"Generating {invoice_code}: {region} / {industry_key} / {complexity}")

    # Get industry config
    industry_config = INDUSTRIES[industry_key]

    # Generate invoice data
    vendor = generator.generate_company(industry_config, is_vendor=True)
    customer = generator.generate_company(industry_config, is_vendor=False)

    invoice_number = generator.generate_invoice_number(style="standard")
    invoice_date = generator.generate_invoice_date(days_ago_range=(0, 90))

    payment_terms = industry_config.payment_terms[0]  # Use first payment term
    due_date = generator.generate_due_date(invoice_date, payment_terms)

    # Generate line items based on complexity
    complexity_config = COMPLEXITY_LEVELS[complexity]
    line_items = generator.generate_line_items(
        industry_config,
        count_range=(complexity_config["min_items"], complexity_config["max_items"]),
    )

    # Calculate tax
    subtotal = sum(item.amount for item in line_items)
    tax_calc = get_tax_calculator(region)

    # Get region-specific tax parameters
    tax_params = {}
    if region == "US":
        tax_params["state"] = DISTRIBUTION["US"]["states"][
            invoice_id % len(DISTRIBUTION["US"]["states"])
        ]
    elif region == "EU":
        tax_params["country"] = DISTRIBUTION["EU"]["countries"][
            invoice_id % len(DISTRIBUTION["EU"]["countries"])
        ]
    elif region == "CA":
        tax_params["province"] = DISTRIBUTION["CA"]["provinces"][
            invoice_id % len(DISTRIBUTION["CA"]["provinces"])
        ]
    elif region == "APAC":
        tax_params["country"] = DISTRIBUTION["APAC"]["countries"][
            invoice_id % len(DISTRIBUTION["APAC"]["countries"])
        ]

    tax_result = tax_calc.calculate(subtotal, **tax_params)

    # Generate PO number
    po_number = generator.generate_po_number()

    # Generate notes
    notes = generator.generate_notes(
        industry_config,
        company=vendor.name.split()[0].lower(),
        date=invoice_date.strftime("%Y-%m-%d"),
        po_number=po_number,
        invoice_number=invoice_number,
    )

    # Create invoice using template
    template = get_template(template_style)
    doc = template.create_invoice(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        vendor=vendor,
        customer=customer,
        line_items=line_items,
        tax_result=tax_result,
        payment_terms=payment_terms,
        notes=notes,
        po_number=po_number,
    )

    # Save DOCX
    docx_path = output_dirs["docx"] / f"{invoice_code}.docx"
    doc.save(str(docx_path))
    logger.info(f"  Saved DOCX: {docx_path}")

    # Convert to PDF
    pdf_path = output_dirs["pdfs"] / f"{invoice_code}.pdf"
    convert_docx_to_pdf(docx_path, pdf_path)
    logger.info(f"  Converted to PDF: {pdf_path}")

    # Extract ground truth
    ground_truth_text = extract_ground_truth_from_docx(docx_path)
    ground_truth_path = output_dirs["ground_truth"] / f"{invoice_code}.md"
    ground_truth_path.write_text(ground_truth_text, encoding="utf-8")
    logger.info(f"  Extracted ground truth: {ground_truth_path}")

    # Create metadata
    metadata = {
        "document_id": invoice_code,
        "region": region,
        "industry": industry_key,
        "complexity": complexity,
        "template_style": template_style,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "vendor": {
            "name": vendor.name,
            "country": vendor.country,
        },
        "customer": {
            "name": customer.name,
            "country": customer.country,
        },
        "line_item_count": len(line_items),
        "subtotal": float(tax_result.subtotal),
        "tax_amount": float(tax_result.tax_amount),
        "total": float(tax_result.total),
        "payment_terms": payment_terms,
        "generated_at": datetime.now().isoformat(),
    }

    metadata_path = output_dirs["metadata"] / f"{invoice_code}.yaml"
    with open(metadata_path, "w") as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
    logger.info(f"  Created metadata: {metadata_path}")

    return docx_path, pdf_path, ground_truth_path


def generate_corpus(output_base: Path, count: int = 100) -> None:
    """Generate full invoice corpus.

    Args:
        output_base: Base output directory
        count: Number of invoices to generate (default: 100)
    """
    # Create output directories
    output_dirs = {
        "docx": output_base / "docx",
        "pdfs": output_base / "pdfs",
        "ground_truth": output_base / "ground_truth",
        "metadata": output_base / "metadata",
    }

    for dir_path in output_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating {count} invoices...")
    logger.info(f"Output directory: {output_base}")

    # Generate invoices according to distribution
    invoice_id = 1
    stats = {
        "total": 0,
        "by_region": {},
        "by_industry": {},
        "by_complexity": {},
    }

    for region, config in DISTRIBUTION.items():
        region_count = config["count"]
        industries = config["industries"]

        logger.info(f"\n{'=' * 60}")
        logger.info(f"Region: {region} ({region_count} invoices)")
        logger.info(f"{'=' * 60}")

        # Create generator for this region
        generator = InvoiceDataGenerator(region=region, seed=42 + invoice_id)

        for i in range(region_count):
            # Select industry (round-robin)
            industry_key = industries[i % len(industries)]

            # Select complexity (weighted random)
            complexity_rand = (i * 17) % 100  # Pseudo-random but deterministic
            if complexity_rand < 30:
                complexity = "simple"
            elif complexity_rand < 80:
                complexity = "medium"
            else:
                complexity = "complex"

            # Select template style (round-robin)
            template_style = TEMPLATE_STYLES[i % len(TEMPLATE_STYLES)]

            # Generate invoice
            try:
                generate_invoice(
                    invoice_id=invoice_id,
                    region=region,
                    industry_key=industry_key,
                    complexity=complexity,
                    template_style=template_style,
                    output_dirs=output_dirs,
                    generator=generator,
                )

                # Update stats
                stats["total"] += 1
                stats["by_region"][region] = stats["by_region"].get(region, 0) + 1
                stats["by_industry"][industry_key] = stats["by_industry"].get(industry_key, 0) + 1
                stats["by_complexity"][complexity] = stats["by_complexity"].get(complexity, 0) + 1

                invoice_id += 1

            except Exception as e:
                logger.error(f"Failed to generate invoice {invoice_id}: {e}", exc_info=True)

            if invoice_id > count:
                break

        if invoice_id > count:
            break

    # Write summary
    summary_path = output_base / "corpus_summary.json"
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_invoices": stats["total"],
        "distribution": stats,
    }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"\n{'=' * 60}")
    logger.info("Corpus Generation Complete!")
    logger.info(f"{'=' * 60}")
    logger.info(f"Total invoices: {stats['total']}")
    logger.info(f"By region: {stats['by_region']}")
    logger.info(f"By industry: {stats['by_industry']}")
    logger.info(f"By complexity: {stats['by_complexity']}")
    logger.info(f"Summary saved to: {summary_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate realistic invoice corpus for PDF-Bench")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("corpus/business/invoices"),
        help="Output directory (default: corpus/business/invoices)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of invoices to generate (default: 100)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Generate only 5 test invoices for validation",
    )

    args = parser.parse_args()

    if args.test:
        logger.info("TEST MODE: Generating 5 invoices for validation")
        args.count = 5

    generate_corpus(output_base=args.output, count=args.count)


if __name__ == "__main__":
    main()
