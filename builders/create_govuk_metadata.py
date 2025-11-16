#!/usr/bin/env python3
"""Generate metadata files for GOV.UK corpus documents.

This script creates individual metadata YAML files for each document in the corpus,
as well as an overall corpus metadata file with aggregate statistics.

Usage:
    python builders/create_govuk_metadata.py
    python builders/create_govuk_metadata.py --dry-run
    python builders/create_govuk_metadata.py --targets corpus/business/gov_uk_targets.yaml

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import argparse
import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_TARGETS = Path("corpus/business/gov_uk_targets.yaml")
DEFAULT_CORPUS_DIR = Path("corpus/business/govuk")


def load_targets(targets_path: Path) -> dict:
    """Load targets YAML file.

    Args:
        targets_path: Path to targets YAML file

    Returns:
        Dictionary with targets data
    """
    logger.info(f"Loading targets from {targets_path}")
    with open(targets_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    logger.info(f"Loaded {len(data.get('documents', []))} documents from targets")
    return data


def get_file_info(file_path: Path) -> dict | None:
    """Get file information (size, hash).

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file info or None if file doesn't exist
    """
    if not file_path.exists():
        return None

    import hashlib

    size = file_path.stat().st_size

    # Calculate SHA256 hash for PDFs
    if file_path.suffix == ".pdf":
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        sha256 = sha256_hash.hexdigest()
    else:
        sha256 = None

    return {"size": size, "sha256": sha256}


def get_pdf_page_count(pdf_path: Path) -> int | None:
    """Get page count from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Page count or None if unavailable
    """
    if not pdf_path.exists():
        return None

    try:
        import pypdf

        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return len(reader.pages)
    except Exception as e:
        logger.warning(f"Could not extract page count from {pdf_path.name}: {e}")
        return None


def create_document_metadata(
    doc: dict, corpus_dir: Path, download_date: str
) -> dict:
    """Create metadata dictionary for a single document.

    Args:
        doc: Document dictionary from targets file
        corpus_dir: Path to corpus directory
        download_date: Download date string (YYYY-MM-DD)

    Returns:
        Metadata dictionary
    """
    doc_id = doc["id"]

    # Get file paths
    html_path = corpus_dir / "html" / f"{doc_id}.html"
    markdown_path = corpus_dir / "ground_truth" / f"{doc_id}.md"
    pdf_path = corpus_dir / "pdfs" / f"{doc_id}.pdf"

    # Get file information
    html_info = get_file_info(html_path)
    markdown_info = get_file_info(markdown_path)
    pdf_info = get_file_info(pdf_path)

    # Get PDF page count
    page_count = get_pdf_page_count(pdf_path) if pdf_info else None

    # Build metadata
    metadata = {
        "id": doc_id,
        "title": doc["title"],
        "source_url": doc["url_html"],
        "publisher": doc["publisher"],
        "publication_date": doc["publication_date"],
        "license": "Open Government Licence v3.0",
        "license_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "download_date": download_date,
        "topics": doc["topics"],
        "complexity": doc["complexity"],
    }

    # Add PDF information if available
    if pdf_info and doc.get("url_pdf"):
        metadata["pdf_url"] = doc["url_pdf"]
        metadata["sha256_pdf"] = pdf_info["sha256"]
        metadata["file_size_pdf"] = pdf_info["size"]
        metadata["page_count"] = page_count if page_count else doc.get("pages")
        metadata["has_pdf"] = True
    else:
        metadata["pdf_url"] = None
        metadata["has_pdf"] = False
        metadata["notes"] = doc.get("notes", "HTML-only document")

    # Add HTML/Markdown sizes
    if html_info:
        metadata["file_size_html"] = html_info["size"]
    if markdown_info:
        metadata["file_size_markdown"] = markdown_info["size"]

    return metadata


def write_document_metadata(
    metadata: dict, output_path: Path, dry_run: bool = False
) -> None:
    """Write document metadata to YAML file.

    Args:
        metadata: Metadata dictionary
        output_path: Path to output YAML file
        dry_run: If True, don't write file
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would write metadata to {output_path.name}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False, width=100)

    logger.info(f"Created metadata file: {output_path.name}")


def create_corpus_metadata(
    targets_data: dict, document_metadata_list: list[dict], download_date: str
) -> dict:
    """Create overall corpus metadata.

    Args:
        targets_data: Targets YAML data
        document_metadata_list: List of individual document metadata
        download_date: Download date string

    Returns:
        Corpus metadata dictionary
    """
    # Count documents by status
    total_docs = len(document_metadata_list)
    docs_with_pdf = sum(1 for m in document_metadata_list if m.get("has_pdf", False))
    docs_html_only = total_docs - docs_with_pdf

    # Calculate total pages
    total_pages = sum(
        m.get("page_count", 0) for m in document_metadata_list if m.get("page_count")
    )

    # Calculate total sizes
    total_pdf_size = sum(
        m.get("file_size_pdf", 0) for m in document_metadata_list if m.get("file_size_pdf")
    )
    total_markdown_size = sum(
        m.get("file_size_markdown", 0) for m in document_metadata_list if m.get("file_size_markdown")
    )

    # Count complexity distribution
    complexity_counts = Counter(m["complexity"] for m in document_metadata_list)

    # Collect all unique topics
    all_topics = set()
    for m in document_metadata_list:
        all_topics.update(m.get("topics", []))

    # Collect publishers
    publishers = sorted(set(m["publisher"] for m in document_metadata_list))

    metadata = {
        "corpus_name": "GOV.UK Publications Corpus",
        "corpus_id": "govuk_v1",
        "version": "1.0",
        "created_date": download_date,
        "description": targets_data.get(
            "description", "UK government publications covering diverse topics"
        ),
        "license": "Open Government Licence v3.0",
        "license_url": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "source": targets_data.get("source", "https://www.gov.uk/"),
        "statistics": {
            "total_documents": total_docs,
            "documents_with_pdf": docs_with_pdf,
            "documents_html_only": docs_html_only,
            "total_pages": total_pages,
            "total_pdf_size_bytes": total_pdf_size,
            "total_markdown_size_bytes": total_markdown_size,
        },
        "complexity_distribution": dict(complexity_counts),
        "topics": sorted(all_topics),
        "publishers": publishers,
        "documents": [m["id"] for m in document_metadata_list],
    }

    return metadata


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate metadata files for GOV.UK corpus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--targets",
        type=Path,
        default=DEFAULT_TARGETS,
        help=f"Path to targets YAML file (default: {DEFAULT_TARGETS})",
    )

    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=DEFAULT_CORPUS_DIR,
        help=f"Path to corpus directory (default: {DEFAULT_CORPUS_DIR})",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files",
    )

    args = parser.parse_args()

    # Load targets
    targets_data = load_targets(args.targets)
    documents = targets_data.get("documents", [])

    if not documents:
        logger.error("No documents found in targets file")
        return

    # Current date
    download_date = datetime.now().strftime("%Y-%m-%d")

    # Create metadata directory
    metadata_dir = args.corpus_dir / "metadata"
    if not args.dry_run:
        metadata_dir.mkdir(parents=True, exist_ok=True)

    # Generate metadata for each document
    document_metadata_list = []
    success_count = 0
    skipped_count = 0

    logger.info(f"Generating metadata for {len(documents)} documents...")

    for i, doc in enumerate(documents, 1):
        doc_id = doc["id"]
        logger.info(f"[{i}/{len(documents)}] Processing {doc_id}")

        # Check if document has any files
        html_path = args.corpus_dir / "html" / f"{doc_id}.html"
        markdown_path = args.corpus_dir / "ground_truth" / f"{doc_id}.md"

        if not html_path.exists() and not markdown_path.exists():
            logger.warning(f"  Skipping {doc_id} (no files found)")
            skipped_count += 1
            continue

        # Create metadata
        metadata = create_document_metadata(doc, args.corpus_dir, download_date)
        document_metadata_list.append(metadata)

        # Write individual metadata file
        output_path = metadata_dir / f"{doc_id}.yaml"
        write_document_metadata(metadata, output_path, args.dry_run)
        success_count += 1

    # Create overall corpus metadata
    logger.info("\nCreating corpus metadata...")
    corpus_metadata = create_corpus_metadata(
        targets_data, document_metadata_list, download_date
    )

    corpus_metadata_path = args.corpus_dir / "corpus_metadata.yaml"
    if not args.dry_run:
        with open(corpus_metadata_path, "w", encoding="utf-8") as f:
            yaml.dump(
                corpus_metadata, f, default_flow_style=False, sort_keys=False, width=100
            )
        logger.info(f"Created corpus metadata: {corpus_metadata_path}")
    else:
        logger.info(f"[DRY RUN] Would write corpus metadata to {corpus_metadata_path}")

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("METADATA GENERATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total documents in targets: {len(documents)}")
    logger.info(f"Metadata files created:     {success_count}")
    logger.info(f"Skipped (no files):         {skipped_count}")
    logger.info("=" * 60)
    logger.info(f"\nCorpus Statistics:")
    logger.info(f"  Documents:        {corpus_metadata['statistics']['total_documents']}")
    logger.info(f"  With PDF:         {corpus_metadata['statistics']['documents_with_pdf']}")
    logger.info(f"  HTML-only:        {corpus_metadata['statistics']['documents_html_only']}")
    logger.info(f"  Total pages:      {corpus_metadata['statistics']['total_pages']}")
    logger.info(f"  PDF size:         {corpus_metadata['statistics']['total_pdf_size_bytes']:,} bytes")
    logger.info(f"  Markdown size:    {corpus_metadata['statistics']['total_markdown_size_bytes']:,} bytes")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
