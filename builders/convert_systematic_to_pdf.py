"""Convert systematic corpus DOCX files to PDF and extract ground truth.

This script:
1. Converts all DOCX files (09-32) to PDF using LibreOffice headless
2. Normalizes PDFs for parser compatibility
3. Extracts ground truth markdown from DOCX structure
4. Creates metadata YAML files with hashes and document info
"""

import hashlib
import subprocess
from pathlib import Path

import yaml
from docx import Document

from builders.pdf_utils import normalize_pdf


def convert_docx_to_pdf(docx_path: Path) -> Path:
    """Convert DOCX to PDF using LibreOffice headless.

    Args:
        docx_path: Path to DOCX file

    Returns:
        Path to generated PDF file

    Raises:
        RuntimeError: If conversion fails
    """
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    cmd = [
        "soffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(docx_path.parent),
        str(docx_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
        print(f"    {result.stdout.strip()}")
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Conversion timeout: {docx_path.name}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Conversion failed: {e.stderr}") from e

    pdf_path = docx_path.with_suffix(".pdf")
    if not pdf_path.exists():
        raise RuntimeError(f"PDF not created: {pdf_path}")

    # Normalize PDF for parser compatibility
    normalize_pdf(pdf_path)

    return pdf_path


def extract_ground_truth(docx_path: Path) -> str:
    """Extract ground truth markdown from DOCX structure.

    Args:
        docx_path: Path to DOCX file

    Returns:
        Ground truth markdown string
    """
    doc = Document(str(docx_path))
    markdown_lines = []

    for element in doc.element.body:
        # Handle paragraphs
        if element.tag.endswith("p"):
            para = None
            for p in doc.paragraphs:
                if p._element == element:
                    para = p
                    break

            if para is None:
                continue

            text = para.text.strip()
            if not text:
                continue

            # Check if heading
            style_name = para.style.name if para.style else ""
            if style_name.startswith("Heading"):
                level = int(style_name.split()[-1])
                markdown_lines.append(f"{'#' * level} {text}")
            # Check if list
            elif style_name.startswith("List"):
                if "Bullet" in style_name:
                    level = 0
                    if "2" in style_name:
                        level = 1
                    elif "3" in style_name:
                        level = 2
                    indent = "  " * level
                    markdown_lines.append(f"{indent}- {text}")
                elif "Number" in style_name:
                    markdown_lines.append(f"1. {text}")
            # Regular paragraph
            else:
                markdown_lines.append(text)

        # Handle tables
        elif element.tag.endswith("tbl"):
            table = None
            for t in doc.tables:
                if t._element == element:
                    table = t
                    break

            if table is None:
                continue

            # Extract table as markdown
            for row_idx, row in enumerate(table.rows):
                cells = [cell.text.strip() for cell in row.cells]
                markdown_lines.append("| " + " | ".join(cells) + " |")

                # Add header separator after first row
                if row_idx == 0:
                    markdown_lines.append("| " + " | ".join(["---"] * len(cells)) + " |")

    return "\n".join(markdown_lines)


def calculate_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of SHA256 hash
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_metadata(
    docx_path: Path,
    pdf_path: Path,
    md_path: Path,
    doc_info: dict,
) -> Path:
    """Create metadata YAML file for document.

    Args:
        docx_path: Path to DOCX source
        pdf_path: Path to PDF file
        md_path: Path to markdown ground truth
        doc_info: Document information (title, category, features)

    Returns:
        Path to created YAML file
    """
    yaml_path = docx_path.with_suffix(".yaml")

    metadata = {
        "doc_id": docx_path.stem,
        "source_url": f"https://github.com/pdf-bench/corpus/synthetic/{docx_path.name}",
        "corpus": "synthetic",
        "domain": doc_info["category"],
        "title": doc_info["title"],
        "authors": ["PDF-Bench Project"],
        "publication_date": "2025-11-18",
        "features": doc_info["features"],
        "license": "MIT",
        "notes": doc_info["notes"],
        "files": {
            "docx": str(docx_path.name),
            "pdf": str(pdf_path.name),
            "ground_truth": str(md_path.name),
        },
        "hashes": {
            "pdf": calculate_hash(pdf_path),
            "ground_truth": calculate_hash(md_path),
        },
    }

    with open(yaml_path, "w") as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)

    return yaml_path


# Document metadata for all 24 documents
DOCUMENT_INFO = {
    "09_table_simple_grid": {
        "title": "Table Test 01: Simple Grid",
        "category": "tables",
        "features": ["tables", "simple_grid"],
        "notes": "Basic 3x4 table with headers. Tests simple table detection.",
    },
    "10_table_colspan": {
        "title": "Table Test 02: Merged Columns",
        "category": "tables",
        "features": ["tables", "merged_cells", "colspan"],
        "notes": "Table with merged cells (colspan). Tests horizontal cell merging.",
    },
    "11_table_wide": {
        "title": "Table Test 03: Wide Table",
        "category": "tables",
        "features": ["tables", "wide_table"],
        "notes": "Wide table with 7 columns. Tests horizontal scrolling and structure.",
    },
    "12_table_multiple": {
        "title": "Table Test 04: Multiple Tables",
        "category": "tables",
        "features": ["tables", "multiple_tables"],
        "notes": "Multiple tables separated by text. Tests table boundary detection.",
    },
    "13_table_complex_headers": {
        "title": "Table Test 05: Complex Structure",
        "category": "tables",
        "features": ["tables", "merged_cells", "rowspan", "colspan", "complex_headers"],
        "notes": "Complex table with multi-level merged headers. Tests advanced structure.",
    },
    "14_table_financial": {
        "title": "Table Test 06: Financial Statement",
        "category": "tables",
        "features": ["tables", "financial", "numeric"],
        "notes": "Financial table with formatted numbers. Tests numeric data extraction.",
    },
    "15_list_simple_bullets": {
        "title": "List Test 01: Simple Bullets",
        "category": "lists",
        "features": ["lists", "bullets"],
        "notes": "Simple bulleted list. Tests basic list detection.",
    },
    "16_list_numbered": {
        "title": "List Test 02: Numbered Steps",
        "category": "lists",
        "features": ["lists", "numbered"],
        "notes": "Numbered procedural list. Tests ordered list detection.",
    },
    "17_list_nested_2level": {
        "title": "List Test 03: Two-Level Nesting",
        "category": "lists",
        "features": ["lists", "bullets", "nested", "depth_2"],
        "notes": "Two-level nested bullets. Tests list nesting detection.",
    },
    "18_list_nested_3level": {
        "title": "List Test 04: Three-Level Nesting",
        "category": "lists",
        "features": ["lists", "bullets", "nested", "depth_3"],
        "notes": "Three-level nested bullets. Tests deep nesting.",
    },
    "19_list_mixed_types": {
        "title": "List Test 05: Mixed List Types",
        "category": "lists",
        "features": ["lists", "bullets", "numbered", "nested", "mixed"],
        "notes": "Mixed numbered and bulleted lists. Tests list type detection.",
    },
    "20_list_with_paragraphs": {
        "title": "List Test 06: Lists with Paragraphs",
        "category": "lists",
        "features": ["lists", "bullets", "paragraphs", "mixed_content"],
        "notes": "Lists interspersed with paragraphs. Tests content separation.",
    },
    "21_column_two_column": {
        "title": "Column Test 01: Two-Column Text",
        "category": "multicolumn",
        "features": ["multicolumn", "columns_2", "reading_order"],
        "notes": "Two-column layout. Tests reading order (down then across).",
    },
    "22_column_three_column": {
        "title": "Column Test 02: Three-Column Layout",
        "category": "multicolumn",
        "features": ["multicolumn", "columns_3", "reading_order"],
        "notes": "Three-column layout. Tests reading order across multiple columns.",
    },
    "23_column_mixed_width": {
        "title": "Column Test 03: Mixed Width Sections",
        "category": "multicolumn",
        "features": ["multicolumn", "columns_2", "full_width", "mixed_sections"],
        "notes": "Mixed full-width and column sections. Tests section transitions.",
    },
    "24_column_newsletter": {
        "title": "Newsletter: Company Updates",
        "category": "multicolumn",
        "features": ["multicolumn", "columns_2", "newsletter", "articles"],
        "notes": "Newsletter-style layout. Tests article separation.",
    },
    "25_column_academic": {
        "title": "Research Paper: Multi-Column Format",
        "category": "multicolumn",
        "features": ["multicolumn", "columns_2", "academic", "abstract", "references"],
        "notes": "Academic paper layout with abstract and references. Tests structure.",
    },
    "26_column_brochure": {
        "title": "Product Brochure: Features Overview",
        "category": "multicolumn",
        "features": ["multicolumn", "columns_3", "marketing", "features"],
        "notes": "Marketing brochure with feature grid. Tests visual layout.",
    },
    "27_mixed_business_report": {
        "title": "Quarterly Business Review",
        "category": "mixed",
        "features": ["tables", "lists", "headings", "mixed_content"],
        "notes": "Business report with tables and lists. Tests real-world complexity.",
    },
    "28_mixed_technical_docs": {
        "title": "API Integration Guide",
        "category": "mixed",
        "features": ["tables", "lists", "code", "technical"],
        "notes": "Technical documentation. Tests structured reference content.",
    },
    "29_mixed_policy_doc": {
        "title": "Employee Handbook: Section 5",
        "category": "mixed",
        "features": ["tables", "lists", "nested", "policy", "hierarchy"],
        "notes": "Policy document with nested lists and tables. Tests hierarchy.",
    },
    "30_mixed_meeting_minutes": {
        "title": "Product Team Meeting Minutes",
        "category": "mixed",
        "features": ["tables", "lists", "headings", "structured"],
        "notes": "Meeting minutes with agenda and action items. Tests structure.",
    },
    "31_mixed_research_summary": {
        "title": "Market Research Summary",
        "category": "mixed",
        "features": ["tables", "lists", "data", "analysis"],
        "notes": "Research summary with data tables. Tests analytical content.",
    },
    "32_mixed_comprehensive": {
        "title": "Annual Report 2025",
        "category": "mixed",
        "features": ["tables", "lists", "nested", "headings", "comprehensive"],
        "notes": "Comprehensive annual report. Tests all features combined.",
    },
}


def main() -> None:
    """Convert all systematic corpus documents to PDF."""
    corpus_dir = Path("corpus/synthetic")

    print("🔄 Systematic Corpus PDF Conversion")
    print("=" * 60)
    print()

    # Find all DOCX files from systematic corpus (09-32)
    docx_files = sorted(
        corpus_dir.glob("[0-9][0-9]_*.docx"),
        key=lambda p: int(p.stem.split("_")[0]),
    )

    print(f"Found {len(docx_files)} DOCX files to convert")
    print()

    success_count = 0
    failed = []

    for docx_path in docx_files:
        doc_id = docx_path.stem
        print(f"📄 {doc_id}")

        try:
            # 1. Convert to PDF
            print("  🔨 Converting to PDF...")
            pdf_path = convert_docx_to_pdf(docx_path)
            print(f"    ✓ {pdf_path.name}")

            # 2. Extract ground truth
            print("  📝 Extracting ground truth...")
            markdown = extract_ground_truth(docx_path)
            md_path = docx_path.with_suffix(".md")
            md_path.write_text(markdown, encoding="utf-8")
            print(f"    ✓ {md_path.name} ({len(markdown)} chars)")

            # 3. Create metadata
            print("  📋 Creating metadata...")
            if doc_id in DOCUMENT_INFO:
                yaml_path = create_metadata(docx_path, pdf_path, md_path, DOCUMENT_INFO[doc_id])
                print(f"    ✓ {yaml_path.name}")
            else:
                print(f"    ⚠️  No metadata template for {doc_id}")

            success_count += 1
            print("  ✅ Complete")

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            failed.append((doc_id, str(e)))

        print()

    print("=" * 60)
    print(f"✅ Successfully converted: {success_count}/{len(docx_files)}")
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for doc_id, error in failed:
            print(f"  - {doc_id}: {error}")
    print()
    print(f"📁 Output: {corpus_dir}")
    print()
    print("Next: Run benchmark with expanded corpus")
    print("  python run_benchmark.py corpus/synthetic")


if __name__ == "__main__":
    main()
