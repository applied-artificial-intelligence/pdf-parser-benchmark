#!/usr/bin/env python3
"""Build CUAD contract corpus for PDF-Bench from existing PDF/TXT pairs.

CUAD (Contract Understanding Atticus Dataset) contains real legal contracts
from SEC filings with extracted text that can serve as ground truth.
"""

import shutil
from pathlib import Path

import yaml


def find_matching_pairs(cuad_base: Path) -> list[tuple[Path, Path]]:
    """Find PDF/TXT pairs in CUAD dataset.

    Args:
        cuad_base: Base CUAD_v1 directory

    Returns:
        List of (pdf_path, txt_path) tuples
    """
    pdf_dir = cuad_base / "full_contract_pdf"
    txt_dir = cuad_base / "full_contract_txt"

    # Index all files by stem
    pdfs = {p.stem: p for p in pdf_dir.rglob("*.pdf")}
    txts = {t.stem: t for t in txt_dir.rglob("*.txt")}

    # Find matches
    matches = []
    for name, pdf in pdfs.items():
        if name in txts:
            matches.append((pdf, txts[name]))

    return matches


def txt_to_markdown(txt_path: Path) -> str:
    """Convert plain text to basic markdown.

    The CUAD text files are plain text extracts. We convert them to
    markdown with basic structure preservation.

    Args:
        txt_path: Path to text file

    Returns:
        Markdown string
    """
    with open(txt_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Basic cleanup
    lines = content.split("\n")
    md_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            md_lines.append("")
            continue

        # Detect potential headers (all caps lines, numbered sections)
        if line.isupper() and len(line) > 3 and len(line) < 100:
            md_lines.append(f"## {line.title()}")
        elif line.startswith(("ARTICLE", "SECTION", "EXHIBIT", "SCHEDULE")):
            md_lines.append(f"## {line}")
        elif line[0].isdigit() and "." in line[:5]:
            # Numbered section
            md_lines.append(f"### {line}")
        else:
            md_lines.append(line)

    return "\n".join(md_lines)


def extract_contract_type(filename: str) -> str:
    """Extract contract type from filename.

    Args:
        filename: Contract filename

    Returns:
        Contract type string
    """
    filename_lower = filename.lower()

    contract_types = [
        ("hosting", "Hosting Agreement"),
        ("development", "Development Agreement"),
        ("license", "License Agreement"),
        ("service", "Service Agreement"),
        ("supply", "Supply Agreement"),
        ("distribution", "Distribution Agreement"),
        ("agency", "Agency Agreement"),
        ("joint venture", "Joint Venture Agreement"),
        ("strategic alliance", "Strategic Alliance Agreement"),
        ("endorsement", "Endorsement Agreement"),
        ("outsourcing", "Outsourcing Agreement"),
        ("collaboration", "Collaboration Agreement"),
        ("maintenance", "Maintenance Agreement"),
        ("co-branding", "Co-Branding Agreement"),
        ("non-competition", "Non-Competition Agreement"),
    ]

    for keyword, contract_type in contract_types:
        if keyword in filename_lower:
            return contract_type

    return "Contract"


def build_cuad_corpus(
    cuad_base: str | Path,
    output_dir: str | Path,
    max_docs: int | None = None,
) -> dict[str, int]:
    """Build CUAD corpus for PDF-Bench.

    Args:
        cuad_base: Path to CUAD_v1 directory
        output_dir: Output directory for corpus
        max_docs: Maximum documents to include

    Returns:
        Statistics dictionary
    """
    cuad_base = Path(cuad_base)
    output_dir = Path(output_dir)

    # Create directory structure
    (output_dir / "pdfs").mkdir(parents=True, exist_ok=True)
    (output_dir / "ground_truth").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)

    # Find matching pairs
    pairs = find_matching_pairs(cuad_base)
    print(f"Found {len(pairs)} PDF/TXT pairs")

    if max_docs:
        pairs = pairs[:max_docs]

    stats = {"total": 0, "converted": 0, "errors": 0}

    for i, (pdf_path, txt_path) in enumerate(pairs):
        stats["total"] += 1
        doc_id = f"cuad_{i:03d}"

        try:
            # Copy PDF
            pdf_dest = output_dir / "pdfs" / f"{doc_id}.pdf"
            shutil.copy2(pdf_path, pdf_dest)

            # Convert TXT to markdown
            markdown = txt_to_markdown(txt_path)
            md_dest = output_dir / "ground_truth" / f"{doc_id}.md"
            with open(md_dest, "w", encoding="utf-8") as f:
                f.write(markdown)

            # Create metadata
            contract_type = extract_contract_type(pdf_path.stem)
            metadata = {
                "doc_id": doc_id,
                "original_filename": pdf_path.name,
                "source": "cuad",
                "corpus": "business",
                "domain": "legal",
                "contract_type": contract_type,
                "source_url": f"CUAD_v1/{pdf_path.relative_to(cuad_base)}",
            }

            meta_dest = output_dir / "metadata" / f"{doc_id}.yaml"
            with open(meta_dest, "w") as f:
                yaml.dump(metadata, f, default_flow_style=False)

            stats["converted"] += 1

        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            stats["errors"] += 1

    # Create corpus metadata
    corpus_meta = {
        "name": "CUAD Contracts",
        "description": "Contract Understanding Atticus Dataset - real SEC filing contracts",
        "source": "https://www.atticusprojectai.org/cuad",
        "document_count": stats["converted"],
        "domain": "legal",
        "features": ["contracts", "legal", "sec_filings"],
    }

    with open(output_dir / "corpus_metadata.yaml", "w") as f:
        yaml.dump(corpus_meta, f, default_flow_style=False)

    return stats


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Build CUAD corpus for PDF-Bench")
    parser.add_argument("--cuad", required=True, help="Path to CUAD_v1 directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--max", type=int, help="Maximum documents")

    args = parser.parse_args()

    stats = build_cuad_corpus(
        cuad_base=args.cuad,
        output_dir=args.output,
        max_docs=args.max,
    )

    print("\nBuild complete:")
    print(f"  Total pairs: {stats['total']}")
    print(f"  Converted: {stats['converted']}")
    print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
