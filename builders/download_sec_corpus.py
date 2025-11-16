#!/usr/bin/env python3
"""Download SEC EDGAR corpus for PDF-Bench.

This script downloads SEC filings specified in corpus/business/sec_targets.yaml
and saves them to the corpus/business/sec/ directory.

Usage:
    python builders/download_sec_corpus.py [--limit N] [--skip-existing]
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

import yaml

try:
    from .sec_edgar_client import SECEdgarClient
except ImportError:
    # For direct script execution
    from sec_edgar_client import SECEdgarClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sec_download.log'),
    ]
)
logger = logging.getLogger(__name__)


def load_targets(targets_file: Path) -> List[Dict[str, Any]]:
    """Load SEC filing targets from YAML file.

    Args:
        targets_file: Path to sec_targets.yaml

    Returns:
        List of filing target dictionaries
    """
    logger.info(f"Loading targets from {targets_file}")
    with open(targets_file, 'r') as f:
        data = yaml.safe_load(f)
    documents = data.get('documents', [])
    logger.info(f"Loaded {len(documents)} filing targets")
    return documents


def ensure_output_dir(output_dir: Path) -> None:
    """Create output directory if it doesn't exist.

    Args:
        output_dir: Path to output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")


def save_html(content: str, output_path: Path) -> None:
    """Save HTML content to file.

    Args:
        content: HTML content string
        output_path: Path to save file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Saved HTML: {output_path} ({len(content)} bytes)")


def save_pdf(content: bytes, output_path: Path) -> None:
    """Save PDF content to file.

    Args:
        content: PDF content bytes
        output_path: Path to save file
    """
    with open(output_path, 'wb') as f:
        f.write(content)
    logger.info(f"Saved PDF: {output_path} ({len(content)} bytes)")


def save_metadata(metadata: Dict[str, Any], output_path: Path) -> None:
    """Save metadata to JSON file.

    Args:
        metadata: Metadata dictionary
        output_path: Path to save file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata: {output_path}")


def download_filing(
    client: SECEdgarClient,
    filing: Dict[str, Any],
    output_dir: Path,
    skip_existing: bool = False,
) -> Dict[str, Any]:
    """Download a single SEC filing.

    Args:
        client: SEC EDGAR client
        filing: Filing information dictionary
        output_dir: Output directory
        skip_existing: Skip if files already exist

    Returns:
        Dictionary with download results
    """
    filing_id = filing['id']
    cik = filing['cik']
    accession_number = filing['accession_number']
    company_name = filing['company_name']

    logger.info(f"\n{'='*80}")
    logger.info(f"Processing: {filing_id} - {company_name}")
    logger.info(f"CIK: {cik}, Accession: {accession_number}")
    logger.info(f"{'='*80}")

    result: Dict[str, Any] = {
        'filing_id': filing_id,
        'company_name': company_name,
        'cik': cik,
        'accession_number': accession_number,
        'html_downloaded': False,
        'pdf_downloaded': False,
        'metadata_saved': False,
        'errors': [],
    }

    # Define output paths
    html_path = output_dir / f"{filing_id}.html"
    pdf_path = output_dir / f"{filing_id}.pdf"
    metadata_path = output_dir / f"{filing_id}_metadata.json"

    # Check if files already exist
    if skip_existing:
        if html_path.exists():
            logger.info(f"HTML file already exists, skipping: {html_path}")
            result['html_downloaded'] = True
            result['html_skipped'] = True

        if pdf_path.exists():
            logger.info(f"PDF file already exists, skipping: {pdf_path}")
            result['pdf_downloaded'] = True
            result['pdf_skipped'] = True

        if metadata_path.exists():
            logger.info(f"Metadata file already exists, skipping: {metadata_path}")
            result['metadata_saved'] = True
            result['metadata_skipped'] = True

        if all([html_path.exists(), metadata_path.exists()]):
            logger.info("All files exist, skipping this filing")
            return result

    # Download HTML
    if not result.get('html_skipped'):
        try:
            logger.info("Downloading HTML filing...")
            html_content = client.download_filing_html(cik, accession_number)
            save_html(html_content, html_path)
            result['html_downloaded'] = True
            result['html_size'] = len(html_content)
        except Exception as e:
            error_msg = f"Failed to download HTML: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

    # Download PDF (if available)
    if not result.get('pdf_skipped'):
        try:
            logger.info("Checking for PDF version...")
            pdf_content = client.download_filing_pdf(cik, accession_number)
            if pdf_content:
                save_pdf(pdf_content, pdf_path)
                result['pdf_downloaded'] = True
                result['pdf_size'] = len(pdf_content)
            else:
                logger.info("No PDF version available")
                result['pdf_available'] = False
        except Exception as e:
            error_msg = f"Failed to download PDF: {e}"
            logger.warning(error_msg)
            result['errors'].append(error_msg)
            result['pdf_available'] = False

    # Get metadata
    if not result.get('metadata_skipped'):
        try:
            logger.info("Fetching filing metadata...")
            metadata = client.get_filing_metadata(cik, accession_number)
            # Add original filing info to metadata
            metadata['original_target'] = filing
            save_metadata(metadata, metadata_path)
            result['metadata_saved'] = True
        except Exception as e:
            error_msg = f"Failed to fetch metadata: {e}"
            logger.warning(error_msg)
            result['errors'].append(error_msg)

    logger.info(f"Completed: {filing_id}")
    logger.info(f"  HTML: {'✓' if result['html_downloaded'] else '✗'}")
    logger.info(f"  PDF:  {'✓' if result['pdf_downloaded'] else '✗'}")
    logger.info(f"  Meta: {'✓' if result['metadata_saved'] else '✗'}")

    return result


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download SEC EDGAR corpus for PDF-Bench"
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of filings to download',
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip files that already exist',
    )
    parser.add_argument(
        '--targets',
        type=Path,
        default=Path('corpus/business/sec_targets.yaml'),
        help='Path to targets YAML file',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('corpus/business/sec'),
        help='Output directory for downloaded files',
    )
    parser.add_argument(
        '--user-agent',
        default='PDF-Bench/0.1 (research@pdf-bench.org)',
        help='User-Agent string for SEC requests',
    )

    args = parser.parse_args()

    # Load targets
    try:
        targets = load_targets(args.targets)
    except Exception as e:
        logger.error(f"Failed to load targets: {e}")
        return 1

    # Limit if requested
    if args.limit:
        targets = targets[:args.limit]
        logger.info(f"Limited to {args.limit} filings")

    # Create output directory
    ensure_output_dir(args.output_dir)

    # Initialize SEC client
    logger.info(f"Initializing SEC EDGAR client with User-Agent: {args.user_agent}")
    with SECEdgarClient(user_agent=args.user_agent) as client:
        results = []

        # Download each filing
        for i, filing in enumerate(targets, 1):
            logger.info(f"\n{'#'*80}")
            logger.info(f"Filing {i}/{len(targets)}")
            logger.info(f"{'#'*80}")

            try:
                result = download_filing(
                    client,
                    filing,
                    args.output_dir,
                    skip_existing=args.skip_existing,
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Unexpected error processing {filing.get('id', 'unknown')}: {e}")
                results.append({
                    'filing_id': filing.get('id', 'unknown'),
                    'error': str(e),
                })

    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("DOWNLOAD SUMMARY")
    logger.info(f"{'='*80}")

    total = len(results)
    html_success = sum(1 for r in results if r.get('html_downloaded'))
    pdf_success = sum(1 for r in results if r.get('pdf_downloaded'))
    metadata_success = sum(1 for r in results if r.get('metadata_saved'))
    errors = sum(1 for r in results if r.get('errors'))

    logger.info(f"Total filings processed: {total}")
    logger.info(f"HTML downloads:         {html_success}/{total}")
    logger.info(f"PDF downloads:          {pdf_success}/{total}")
    logger.info(f"Metadata saved:         {metadata_success}/{total}")
    logger.info(f"Filings with errors:    {errors}/{total}")

    # Save summary
    summary_path = args.output_dir / 'download_summary.json'
    summary = {
        'total': total,
        'html_success': html_success,
        'pdf_success': pdf_success,
        'metadata_success': metadata_success,
        'errors': errors,
        'results': results,
    }
    save_metadata(summary, summary_path)

    logger.info(f"\nDownload complete! Summary saved to {summary_path}")

    return 0 if html_success == total else 1


if __name__ == '__main__':
    sys.exit(main())
