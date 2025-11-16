#!/usr/bin/env python3
"""Build complete SEC EDGAR corpus for PDF-Bench.

This script orchestrates the complete SEC corpus building pipeline:
1. Download HTML filings from SEC EDGAR
2. Download PDF versions (when available)
3. Convert HTML to Markdown (ground truth)
4. Create metadata YAML files
5. Generate corpus metadata
6. Validate corpus integrity

Usage:
    python builders/build_sec_corpus.py [--limit N] [--skip-existing]
"""

import argparse
import hashlib
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List

import yaml

from builders.sec_edgar_client import SECEdgarClient
from builders.sec_html_to_markdown import SECHTMLToMarkdown

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sec_corpus_build.log'),
    ]
)
logger = logging.getLogger(__name__)


def load_targets(targets_file: Path) -> Dict[str, Any]:
    """Load SEC filing targets from YAML file.

    Args:
        targets_file: Path to sec_targets.yaml

    Returns:
        Dictionary with corpus metadata and documents list
    """
    logger.info(f"Loading targets from {targets_file}")
    with open(targets_file, 'r') as f:
        data = yaml.safe_load(f)
    logger.info(f"Loaded {len(data.get('documents', []))} filing targets")
    return data


def ensure_directories(base_dir: Path) -> Dict[str, Path]:
    """Create corpus directory structure.

    Args:
        base_dir: Base directory for SEC corpus

    Returns:
        Dictionary of directory paths
    """
    dirs = {
        'base': base_dir,
        'html': base_dir / 'html',
        'pdfs': base_dir / 'pdfs',
        'ground_truth': base_dir / 'ground_truth',
        'metadata': base_dir / 'metadata',
    }

    for name, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory '{name}': {path}")

    return dirs


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


def download_filing(
    client: SECEdgarClient,
    filing: Dict[str, Any],
    dirs: Dict[str, Path],
    skip_existing: bool = False,
) -> Dict[str, Any]:
    """Download HTML and PDF for a single SEC filing.

    Args:
        client: SEC EDGAR client
        filing: Filing information dictionary
        dirs: Directory paths
        skip_existing: Skip if files already exist

    Returns:
        Dictionary with download results
    """
    filing_id = filing['id']
    cik = filing['cik']
    accession_number = filing['accession_number']
    company_name = filing['company_name']

    logger.info(f"\n{'='*80}")
    logger.info(f"Downloading: {filing_id} - {company_name}")
    logger.info(f"{'='*80}")

    result = {
        'filing_id': filing_id,
        'company_name': company_name,
        'html_downloaded': False,
        'pdf_downloaded': False,
        'errors': [],
    }

    # Define output paths
    html_path = dirs['html'] / f"{filing_id}.html"
    pdf_path = dirs['pdfs'] / f"{filing_id}.pdf"

    # Check if files exist
    if skip_existing and html_path.exists():
        logger.info(f"HTML already exists, skipping download: {html_path}")
        result['html_downloaded'] = True
        result['html_path'] = str(html_path)
    else:
        # Download HTML
        try:
            logger.info("Downloading HTML filing...")
            html_content = client.download_filing_html(cik, accession_number)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Saved HTML: {html_path} ({len(html_content):,} bytes)")
            result['html_downloaded'] = True
            result['html_path'] = str(html_path)
            result['html_size'] = len(html_content)
        except Exception as e:
            error_msg = f"Failed to download HTML: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

    # Download PDF if available
    if skip_existing and pdf_path.exists():
        logger.info(f"PDF already exists, skipping download: {pdf_path}")
        result['pdf_downloaded'] = True
        result['pdf_path'] = str(pdf_path)
        result['pdf_hash'] = sha256_file(pdf_path)
    else:
        try:
            logger.info("Downloading PDF version...")
            pdf_content = client.download_filing_pdf(cik, accession_number)
            if pdf_content:
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                pdf_hash = sha256_file(pdf_path)
                logger.info(f"Saved PDF: {pdf_path} ({len(pdf_content):,} bytes)")
                result['pdf_downloaded'] = True
                result['pdf_path'] = str(pdf_path)
                result['pdf_size'] = len(pdf_content)
                result['pdf_hash'] = pdf_hash
            else:
                logger.info("No PDF version available")
                result['pdf_available'] = False
        except Exception as e:
            logger.warning(f"Failed to download PDF: {e}")
            result['pdf_available'] = False

    return result


def convert_to_markdown(
    html_path: Path,
    markdown_path: Path,
    converter: SECHTMLToMarkdown,
    skip_existing: bool = False,
) -> Dict[str, Any]:
    """Convert HTML filing to Markdown ground truth.

    Args:
        html_path: Path to HTML file
        markdown_path: Path to output Markdown file
        converter: SECHTMLToMarkdown instance
        skip_existing: Skip if Markdown already exists

    Returns:
        Dictionary with conversion results
    """
    filing_id = html_path.stem

    result = {
        'filing_id': filing_id,
        'converted': False,
        'errors': [],
    }

    if skip_existing and markdown_path.exists():
        logger.info(f"Markdown already exists, skipping conversion: {markdown_path}")
        result['converted'] = True
        result['markdown_path'] = str(markdown_path)
        return result

    try:
        logger.info(f"Converting to Markdown: {html_path}")

        # Read HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Convert to Markdown
        markdown_content = converter.convert(html_content)

        # Write Markdown
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Saved Markdown: {markdown_path} ({len(markdown_content):,} bytes)")

        result['converted'] = True
        result['markdown_path'] = str(markdown_path)
        result['markdown_size'] = len(markdown_content)

    except Exception as e:
        error_msg = f"Failed to convert {html_path}: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)

    return result


def create_metadata_file(
    filing: Dict[str, Any],
    download_result: Dict[str, Any],
    conversion_result: Dict[str, Any],
    dirs: Dict[str, Path],
) -> Dict[str, Any]:
    """Create metadata YAML file for a filing.

    Args:
        filing: Original filing information from targets
        download_result: Results from download step
        conversion_result: Results from conversion step
        dirs: Directory paths

    Returns:
        Metadata dictionary
    """
    filing_id = filing['id']
    metadata_path = dirs['metadata'] / f"{filing_id}.yaml"

    # Build metadata
    metadata = {
        'id': filing_id,
        'company_name': filing['company_name'],
        'cik': filing['cik'],
        'filing_type': filing['filing_type'],
        'filing_date': filing['filing_date'],
        'accession_number': filing['accession_number'],
        'industry': filing.get('industry', 'Unknown'),
        'fiscal_year': filing.get('fiscal_year'),
        'fiscal_year_end': filing.get('fiscal_year_end'),
        'pages': filing.get('pages'),
        'complexity': filing.get('complexity', 'unknown'),
        'license': 'Public Domain (US Government Works)',
        'source_url': filing.get('url_document', ''),
        'category': 'business',
        'subcategory': 'sec_edgar',
        'document_type': filing.get('filing_type', '10-K/10-Q'),
    }

    # Add file paths and hashes if available
    if download_result.get('pdf_downloaded') and download_result.get('pdf_hash'):
        metadata['pdf_file'] = f"pdfs/{filing_id}.pdf"
        metadata['pdf_hash'] = download_result['pdf_hash']
        metadata['pdf_size'] = download_result.get('pdf_size', 0)

    if download_result.get('html_downloaded'):
        metadata['html_file'] = f"html/{filing_id}.html"
        metadata['html_size'] = download_result.get('html_size', 0)

    if conversion_result.get('converted'):
        metadata['ground_truth_file'] = f"ground_truth/{filing_id}.md"
        metadata['ground_truth_size'] = conversion_result.get('markdown_size', 0)

    # Add additional notes if present
    if 'notes' in filing:
        metadata['notes'] = filing['notes']

    # Write metadata file
    with open(metadata_path, 'w') as f:
        yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Created metadata: {metadata_path}")

    return metadata


def create_corpus_metadata(
    targets_data: Dict[str, Any],
    results: List[Dict[str, Any]],
    dirs: Dict[str, Path],
) -> None:
    """Create corpus-level metadata file.

    Args:
        targets_data: Original targets data
        results: List of processing results
        dirs: Directory paths
    """
    corpus_metadata_path = dirs['base'] / 'corpus_metadata.yaml'

    # Count successful downloads/conversions
    html_count = sum(1 for r in results if r.get('download', {}).get('html_downloaded'))
    pdf_count = sum(1 for r in results if r.get('download', {}).get('pdf_downloaded'))
    markdown_count = sum(1 for r in results if r.get('conversion', {}).get('converted'))

    # Calculate total sizes
    total_pdf_size = sum(
        r.get('download', {}).get('pdf_size', 0)
        for r in results
        if r.get('download', {}).get('pdf_downloaded')
    )
    total_markdown_size = sum(
        r.get('conversion', {}).get('markdown_size', 0)
        for r in results
        if r.get('conversion', {}).get('converted')
    )

    corpus_metadata = {
        'corpus_name': 'SEC EDGAR Filings Corpus',
        'description': targets_data.get('description', 'SEC EDGAR filings corpus for PDF-Bench'),
        'license': targets_data.get('license', 'Public Domain (US Government Works)'),
        'source': targets_data.get('source', 'https://www.sec.gov/edgar'),
        'total_documents': len(results),
        'html_documents': html_count,
        'pdf_documents': pdf_count,
        'markdown_ground_truth': markdown_count,
        'total_pdf_size_bytes': total_pdf_size,
        'total_pdf_size_mb': round(total_pdf_size / 1024 / 1024, 2),
        'total_markdown_size_bytes': total_markdown_size,
        'total_markdown_size_kb': round(total_markdown_size / 1024, 2),
        'selection_methodology': targets_data.get('selection_methodology', ''),
        'filing_types': list(set(
            filing.get('filing_type', 'Unknown')
            for filing in targets_data.get('documents', [])
        )),
        'industries': list(set(
            filing.get('industry', 'Unknown')
            for filing in targets_data.get('documents', [])
        )),
    }

    with open(corpus_metadata_path, 'w') as f:
        yaml.dump(corpus_metadata, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Created corpus metadata: {corpus_metadata_path}")
    logger.info(f"  Total documents: {len(results)}")
    logger.info(f"  HTML files: {html_count}")
    logger.info(f"  PDF files: {pdf_count} ({corpus_metadata['total_pdf_size_mb']:.2f} MB)")
    logger.info(f"  Markdown files: {markdown_count} ({corpus_metadata['total_markdown_size_kb']:.2f} KB)")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build complete SEC EDGAR corpus for PDF-Bench"
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of filings to process',
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
        help='Output directory for corpus',
    )
    parser.add_argument(
        '--user-agent',
        default='PDF-Bench/0.1 (research@example.com)',
        help='User-Agent string for SEC requests',
    )

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("SEC EDGAR CORPUS BUILDER")
    logger.info("="*80)

    # Load targets
    try:
        targets_data = load_targets(args.targets)
        filings = targets_data.get('documents', [])
    except Exception as e:
        logger.error(f"Failed to load targets: {e}")
        return 1

    # Limit if requested
    if args.limit:
        filings = filings[:args.limit]
        logger.info(f"Limited to {args.limit} filings")

    # Create directory structure
    dirs = ensure_directories(args.output_dir)

    # Initialize converter
    converter = SECHTMLToMarkdown(
        use_financial_tables=True,
        normalize_currency=True,
        strip_xbrl=True,
        extract_metadata=True,
    )
    logger.info("Initialized SEC HTML→Markdown converter")

    # Process each filing
    results = []

    with SECEdgarClient(user_agent=args.user_agent) as client:
        for i, filing in enumerate(filings, 1):
            logger.info(f"\n{'#'*80}")
            logger.info(f"Processing filing {i}/{len(filings)}")
            logger.info(f"{'#'*80}")

            try:
                # Step 1: Download HTML and PDF
                download_result = download_filing(
                    client,
                    filing,
                    dirs,
                    skip_existing=args.skip_existing,
                )

                # Step 2: Convert HTML to Markdown
                conversion_result = {'converted': False}
                if download_result.get('html_downloaded'):
                    html_path = Path(download_result['html_path'])
                    markdown_path = dirs['ground_truth'] / f"{filing['id']}.md"
                    conversion_result = convert_to_markdown(
                        html_path,
                        markdown_path,
                        converter,
                        skip_existing=args.skip_existing,
                    )

                # Step 3: Create metadata file
                if download_result.get('html_downloaded') or download_result.get('pdf_downloaded'):
                    metadata = create_metadata_file(
                        filing,
                        download_result,
                        conversion_result,
                        dirs,
                    )

                # Record result
                results.append({
                    'filing_id': filing['id'],
                    'download': download_result,
                    'conversion': conversion_result,
                    'success': download_result.get('html_downloaded', False),
                })

            except Exception as e:
                logger.error(f"Unexpected error processing {filing.get('id', 'unknown')}: {e}")
                results.append({
                    'filing_id': filing.get('id', 'unknown'),
                    'error': str(e),
                    'success': False,
                })

    # Create corpus-level metadata
    create_corpus_metadata(targets_data, results, dirs)

    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("BUILD SUMMARY")
    logger.info(f"{'='*80}")

    total = len(results)
    successful = sum(1 for r in results if r.get('success'))
    html_count = sum(1 for r in results if r.get('download', {}).get('html_downloaded'))
    pdf_count = sum(1 for r in results if r.get('download', {}).get('pdf_downloaded'))
    markdown_count = sum(1 for r in results if r.get('conversion', {}).get('converted'))

    logger.info(f"Total filings processed:  {total}")
    logger.info(f"Successfully processed:   {successful}/{total}")
    logger.info(f"HTML files:               {html_count}/{total}")
    logger.info(f"PDF files:                {pdf_count}/{total}")
    logger.info(f"Markdown ground truth:    {markdown_count}/{total}")

    # Save detailed results
    results_path = dirs['base'] / 'build_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nDetailed results saved to: {results_path}")

    logger.info("\nCorpus build complete!")
    logger.info(f"Corpus directory: {dirs['base']}")

    return 0 if successful == total else 1


if __name__ == '__main__':
    sys.exit(main())
