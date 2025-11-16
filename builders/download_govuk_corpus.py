#!/usr/bin/env python3
"""Download GOV.UK corpus HTML content.

This script reads the GOV.UK targets YAML file and downloads HTML content
from each URL, extracting and saving the main content area.

Usage:
    python builders/download_govuk_corpus.py [--dry-run] [--limit N] [--skip-existing]

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

from scrape_govuk import GovUKScraperError, scrape_and_save

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TARGETS_FILE = PROJECT_ROOT / "corpus" / "business" / "gov_uk_targets.yaml"
OUTPUT_DIR = PROJECT_ROOT / "corpus" / "business" / "govuk"
METADATA_FILE = OUTPUT_DIR / "download_metadata.json"


def load_targets(targets_file: Path) -> dict[str, Any]:
    """Load targets YAML file.

    Args:
        targets_file: Path to targets YAML file

    Returns:
        Parsed YAML data

    Raises:
        FileNotFoundError: If targets file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    logger.info(f"Loading targets from {targets_file}")

    if not targets_file.exists():
        raise FileNotFoundError(f"Targets file not found: {targets_file}")

    with open(targets_file) as f:
        data = yaml.safe_load(f)

    logger.info(f"Loaded {len(data.get('documents', []))} documents from targets file")
    return data


def download_corpus(
    targets_file: Path = TARGETS_FILE,
    output_dir: Path = OUTPUT_DIR,
    dry_run: bool = False,
    limit: int | None = None,
    skip_existing: bool = False,
    max_retries: int = 3,
    rate_limit_delay: float = 1.5,
) -> dict[str, Any]:
    """Download all GOV.UK corpus documents.

    Args:
        targets_file: Path to targets YAML file
        output_dir: Directory where to save HTML files
        dry_run: If True, don't actually download, just show what would be done
        limit: Maximum number of documents to download (for testing)
        skip_existing: If True, skip documents that already exist
        max_retries: Maximum retry attempts per download
        rate_limit_delay: Delay between downloads (seconds)

    Returns:
        Dictionary with download statistics and results:
            - total: Total number of documents
            - processed: Number of documents processed
            - successful: Number of successful downloads
            - failed: Number of failed downloads
            - skipped: Number of skipped (existing) downloads
            - results: List of individual download results
    """
    # Load targets
    targets_data = load_targets(targets_file)
    documents = targets_data.get("documents", [])

    if limit:
        documents = documents[:limit]
        logger.info(f"Limited to first {limit} documents")

    # Create output directory
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

    # Download statistics
    stats = {
        "total": len(documents),
        "processed": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "results": [],
    }

    # Download each document
    for i, doc in enumerate(documents, 1):
        doc_id = doc.get("id", f"unknown_{i}")
        url_html = doc.get("url_html")
        title = doc.get("title", "Untitled")

        logger.info(f"\n[{i}/{len(documents)}] Processing: {doc_id}")
        logger.info(f"  Title: {title}")
        logger.info(f"  URL: {url_html}")

        if not url_html:
            logger.warning(f"  ⚠️  No HTML URL for {doc_id}, skipping")
            stats["skipped"] += 1
            stats["results"].append(
                {
                    "id": doc_id,
                    "title": title,
                    "status": "skipped",
                    "reason": "no_html_url",
                }
            )
            continue

        # Check if file already exists
        output_path = output_dir / f"{doc_id}.html"
        if skip_existing and output_path.exists():
            logger.info(f"  ⏭️  Already exists, skipping")
            stats["skipped"] += 1
            stats["results"].append(
                {
                    "id": doc_id,
                    "title": title,
                    "url": url_html,
                    "output_path": str(output_path),
                    "status": "skipped",
                    "reason": "already_exists",
                }
            )
            continue

        if dry_run:
            logger.info(f"  [DRY RUN] Would download to: {output_path}")
            stats["processed"] += 1
            stats["results"].append(
                {
                    "id": doc_id,
                    "title": title,
                    "url": url_html,
                    "output_path": str(output_path),
                    "status": "dry_run",
                }
            )
            continue

        # Download and save
        try:
            result = scrape_and_save(
                url_html,
                output_path,
                max_retries=max_retries,
                rate_limit_delay=rate_limit_delay,
            )

            result.update(
                {
                    "id": doc_id,
                    "title": title,
                }
            )

            if result["status"] == "success":
                logger.info(
                    f"  ✅ Success! Saved {result['content_size']:,} bytes to {output_path.name}"
                )
                stats["successful"] += 1
            else:
                logger.error(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                stats["failed"] += 1

            stats["processed"] += 1
            stats["results"].append(result)

        except Exception as e:
            logger.error(f"  ❌ Unexpected error: {e}", exc_info=True)
            stats["failed"] += 1
            stats["processed"] += 1
            stats["results"].append(
                {
                    "id": doc_id,
                    "title": title,
                    "url": url_html,
                    "output_path": str(output_path),
                    "status": "error",
                    "error": str(e),
                }
            )

    # Save metadata
    if not dry_run:
        logger.info(f"\nSaving metadata to {METADATA_FILE}")
        with open(METADATA_FILE, "w") as f:
            json.dump(
                {
                    "targets_file": str(targets_file),
                    "output_dir": str(output_dir),
                    "statistics": {
                        k: v for k, v in stats.items() if k != "results"
                    },
                    "downloads": stats["results"],
                },
                f,
                indent=2,
            )

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total documents:     {stats['total']}")
    logger.info(f"Processed:           {stats['processed']}")
    logger.info(f"Successful:          {stats['successful']} ✅")
    logger.info(f"Failed:              {stats['failed']} ❌")
    logger.info(f"Skipped:             {stats['skipped']} ⏭️")
    logger.info("=" * 70)

    if not dry_run and stats["successful"] > 0:
        logger.info(f"\nHTML files saved to: {output_dir}")
        logger.info(f"Metadata saved to: {METADATA_FILE}")

    return stats


def main() -> int:
    """Main entry point for command-line usage.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Download GOV.UK corpus HTML content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )

    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="Limit to first N documents (for testing)",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip documents that have already been downloaded",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        metavar="N",
        help="Maximum retry attempts per download (default: 3)",
    )

    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.5,
        metavar="SECONDS",
        help="Delay between downloads in seconds (default: 1.5)",
    )

    parser.add_argument(
        "--targets",
        type=Path,
        default=TARGETS_FILE,
        help=f"Path to targets YAML file (default: {TARGETS_FILE})",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory for HTML files (default: {OUTPUT_DIR})",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Run download
    try:
        stats = download_corpus(
            targets_file=args.targets,
            output_dir=args.output,
            dry_run=args.dry_run,
            limit=args.limit,
            skip_existing=args.skip_existing,
            max_retries=args.max_retries,
            rate_limit_delay=args.rate_limit,
        )

        # Return error code if there were failures
        if stats["failed"] > 0:
            logger.warning(f"\nCompleted with {stats['failed']} failure(s)")
            return 1

        logger.info("\n✅ All downloads completed successfully!")
        return 0

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Interrupted by user")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
