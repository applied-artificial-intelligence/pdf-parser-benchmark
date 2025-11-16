#!/usr/bin/env python3
"""Validate SEC EDGAR corpus integrity.

This script validates the SEC corpus by checking:
- Directory structure
- File existence
- Metadata correctness
- SHA256 hashes for PDFs
- Ground truth Markdown files
- Completeness

Usage:
    python builders/validate_sec_corpus.py
"""

import hashlib
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)


def sha256_file(file_path: Path) -> str:
    """Calculate SHA256 hash of file.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def validate_directory_structure(corpus_dir: Path) -> bool:
    """Validate corpus directory structure exists.

    Args:
        corpus_dir: Path to corpus directory

    Returns:
        True if valid, False otherwise
    """
    logger.info("Validating directory structure...")

    required_dirs = ['html', 'pdfs', 'ground_truth', 'metadata']
    all_exist = True

    for dir_name in required_dirs:
        dir_path = corpus_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            logger.info(f"  ✓ {dir_name}/")
        else:
            logger.error(f"  ✗ {dir_name}/ - MISSING")
            all_exist = False

    return all_exist


def load_corpus_metadata(corpus_dir: Path) -> Dict[str, Any]:
    """Load corpus-level metadata.

    Args:
        corpus_dir: Path to corpus directory

    Returns:
        Dictionary of corpus metadata
    """
    metadata_path = corpus_dir / 'corpus_metadata.yaml'

    if not metadata_path.exists():
        logger.error(f"Corpus metadata not found: {metadata_path}")
        return {}

    with open(metadata_path, 'r') as f:
        metadata = yaml.safe_load(f)

    logger.info(f"\nCorpus Metadata:")
    logger.info(f"  Name: {metadata.get('corpus_name')}")
    logger.info(f"  Total documents: {metadata.get('total_documents')}")
    logger.info(f"  HTML documents: {metadata.get('html_documents')}")
    logger.info(f"  PDF documents: {metadata.get('pdf_documents')}")
    logger.info(f"  Markdown ground truth: {metadata.get('markdown_ground_truth')}")

    return metadata


def validate_filing(
    filing_id: str,
    corpus_dir: Path,
) -> Dict[str, Any]:
    """Validate a single filing's files and metadata.

    Args:
        filing_id: Filing ID (e.g., "sec_001")
        corpus_dir: Path to corpus directory

    Returns:
        Dictionary with validation results
    """
    result = {
        'filing_id': filing_id,
        'metadata_valid': False,
        'html_exists': False,
        'pdf_exists': False,
        'pdf_hash_valid': None,
        'markdown_exists': False,
        'errors': [],
    }

    # Check metadata file
    metadata_path = corpus_dir / 'metadata' / f"{filing_id}.yaml"
    if not metadata_path.exists():
        result['errors'].append(f"Metadata file missing: {metadata_path}")
        return result

    # Load metadata
    try:
        with open(metadata_path, 'r') as f:
            metadata = yaml.safe_load(f)
        result['metadata_valid'] = True
    except Exception as e:
        result['errors'].append(f"Failed to load metadata: {e}")
        return result

    # Check HTML file
    html_path = corpus_dir / 'html' / f"{filing_id}.html"
    if html_path.exists():
        result['html_exists'] = True
        result['html_size'] = html_path.stat().st_size
    else:
        result['errors'].append(f"HTML file missing: {html_path}")

    # Check PDF file (if metadata says it should exist)
    if 'pdf_file' in metadata:
        pdf_path = corpus_dir / metadata['pdf_file']
        if pdf_path.exists():
            result['pdf_exists'] = True
            result['pdf_size'] = pdf_path.stat().st_size

            # Verify hash if provided
            if 'pdf_hash' in metadata:
                actual_hash = sha256_file(pdf_path)
                expected_hash = metadata['pdf_hash']
                if actual_hash == expected_hash:
                    result['pdf_hash_valid'] = True
                else:
                    result['pdf_hash_valid'] = False
                    result['errors'].append(
                        f"PDF hash mismatch: expected {expected_hash}, got {actual_hash}"
                    )
        else:
            result['errors'].append(f"PDF file missing: {pdf_path}")
    else:
        # PDF not expected for this filing
        result['pdf_exists'] = False

    # Check Markdown ground truth
    markdown_path = corpus_dir / 'ground_truth' / f"{filing_id}.md"
    if markdown_path.exists():
        result['markdown_exists'] = True
        result['markdown_size'] = markdown_path.stat().st_size
    else:
        result['errors'].append(f"Markdown file missing: {markdown_path}")

    return result


def main() -> int:
    """Main entry point."""
    corpus_dir = Path('corpus/business/sec')

    logger.info("="*80)
    logger.info("SEC EDGAR CORPUS VALIDATION")
    logger.info("="*80)
    logger.info(f"Corpus directory: {corpus_dir}\n")

    # Check if corpus directory exists
    if not corpus_dir.exists():
        logger.error(f"Corpus directory does not exist: {corpus_dir}")
        return 1

    # Validate directory structure
    if not validate_directory_structure(corpus_dir):
        logger.error("\nDirectory structure validation FAILED")
        return 1

    logger.info("  ✓ Directory structure valid\n")

    # Load corpus metadata
    corpus_metadata = load_corpus_metadata(corpus_dir)
    if not corpus_metadata:
        logger.error("\nFailed to load corpus metadata")
        return 1

    # Get list of all metadata files
    metadata_dir = corpus_dir / 'metadata'
    metadata_files = list(metadata_dir.glob('*.yaml'))

    # Exclude corpus_metadata.yaml
    metadata_files = [
        f for f in metadata_files
        if f.name != 'corpus_metadata.yaml'
    ]

    filing_ids = [f.stem for f in metadata_files]
    filing_ids.sort()

    logger.info(f"\nValidating {len(filing_ids)} filings...\n")

    # Validate each filing
    results = []
    for filing_id in filing_ids:
        result = validate_filing(filing_id, corpus_dir)
        results.append(result)

        # Print result
        status = "✓" if not result['errors'] else "✗"
        logger.info(f"{status} {filing_id}")

        if result['errors']:
            for error in result['errors']:
                logger.error(f"    - {error}")

    # Summary
    logger.info("\n" + "="*80)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*80)

    total = len(results)
    valid = sum(1 for r in results if not r['errors'])
    metadata_count = sum(1 for r in results if r['metadata_valid'])
    html_count = sum(1 for r in results if r['html_exists'])
    pdf_count = sum(1 for r in results if r['pdf_exists'])
    markdown_count = sum(1 for r in results if r['markdown_exists'])

    # PDF hash validation (only for filings with PDFs)
    pdfs_with_hash = [r for r in results if r['pdf_exists'] and r['pdf_hash_valid'] is not None]
    pdf_hash_valid_count = sum(1 for r in pdfs_with_hash if r['pdf_hash_valid'])

    logger.info(f"Total filings:             {total}")
    logger.info(f"Valid filings:             {valid}/{total}")
    logger.info(f"Metadata files:            {metadata_count}/{total}")
    logger.info(f"HTML files:                {html_count}/{total}")
    logger.info(f"PDF files:                 {pdf_count}/{total}")
    if pdfs_with_hash:
        logger.info(f"PDF hashes valid:          {pdf_hash_valid_count}/{len(pdfs_with_hash)}")
    logger.info(f"Markdown ground truth:     {markdown_count}/{total}")

    # File size totals
    total_html_size = sum(r.get('html_size', 0) for r in results)
    total_pdf_size = sum(r.get('pdf_size', 0) for r in results)
    total_markdown_size = sum(r.get('markdown_size', 0) for r in results)

    logger.info(f"\nTotal HTML size:           {total_html_size:,} bytes ({total_html_size/1024:.2f} KB)")
    logger.info(f"Total PDF size:            {total_pdf_size:,} bytes ({total_pdf_size/1024/1024:.2f} MB)")
    logger.info(f"Total Markdown size:       {total_markdown_size:,} bytes ({total_markdown_size/1024:.2f} KB)")

    # Final verdict
    logger.info("\n" + "="*80)
    if valid == total and metadata_count == total and html_count == total and markdown_count == total:
        if pdfs_with_hash and pdf_hash_valid_count != len(pdfs_with_hash):
            logger.warning("VALIDATION PASSED (with PDF hash warnings)")
            return 0
        else:
            logger.info("✓ VALIDATION PASSED - All files present and valid")
            return 0
    else:
        logger.error("✗ VALIDATION FAILED - See errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
