#!/usr/bin/env python3
"""CLI tool for batch conversion of GOV.UK HTML corpus to Markdown.

This script converts all HTML files in the GOV.UK corpus directory to Markdown format,
preserving document structure while applying normalization rules.

Usage:
    python builders/convert_govuk_corpus.py
    python builders/convert_govuk_corpus.py --dry-run
    python builders/convert_govuk_corpus.py --skip-existing
    python builders/convert_govuk_corpus.py --input-dir corpus/business/govuk
    python builders/convert_govuk_corpus.py --output-dir corpus/business/govuk_markdown

License: Open Government Licence v3.0
See: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
"""

import argparse
import logging
from pathlib import Path

from builders.govuk_html_to_markdown import MarkdownConversionError, html_to_markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT_DIR = Path("corpus/business/govuk")
DEFAULT_OUTPUT_DIR = Path("corpus/business/govuk_markdown")


def convert_file(
    input_path: Path,
    output_path: Path,
    dry_run: bool = False,
    skip_existing: bool = False,
) -> dict[str, str | int | bool]:
    """Convert a single HTML file to Markdown.

    Args:
        input_path: Path to input HTML file
        output_path: Path to output Markdown file
        dry_run: If True, don't write files, just report what would happen
        skip_existing: If True, skip files that already exist

    Returns:
        Dictionary with conversion metadata:
            - input_path: Source file path
            - output_path: Destination file path
            - status: "success", "skipped", or "error"
            - error: Error message if status is "error" (optional)
            - input_size: Size of input file in bytes
            - output_size: Size of output file in bytes (0 for dry-run/error)
    """
    result: dict[str, str | int | bool] = {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "status": "success",
        "input_size": 0,
        "output_size": 0,
    }

    try:
        # Check if input file exists
        if not input_path.exists():
            result["status"] = "error"
            result["error"] = "Input file not found"
            return result

        # Check if output file already exists and skip_existing is True
        if skip_existing and output_path.exists():
            result["status"] = "skipped"
            logger.info(f"Skipping {input_path.name} (already exists)")
            return result

        # Read input HTML
        logger.debug(f"Reading {input_path}")
        html_content = input_path.read_text(encoding="utf-8")
        result["input_size"] = len(html_content)

        # Convert to Markdown
        logger.debug(f"Converting {input_path.name} to Markdown")
        markdown_content = html_to_markdown(html_content)
        result["output_size"] = len(markdown_content)

        # Write output (unless dry-run)
        if not dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown_content, encoding="utf-8")
            logger.info(
                f"Converted {input_path.name} -> {output_path.name} "
                f"({result['input_size']} -> {result['output_size']} bytes)"
            )
        else:
            logger.info(
                f"[DRY RUN] Would convert {input_path.name} -> {output_path.name} "
                f"({result['input_size']} -> {result['output_size']} bytes)"
            )

        return result

    except MarkdownConversionError as e:
        logger.error(f"Conversion error for {input_path.name}: {e}")
        result["status"] = "error"
        result["error"] = str(e)
        return result

    except Exception as e:
        logger.error(f"Unexpected error for {input_path.name}: {e}")
        result["status"] = "error"
        result["error"] = f"Unexpected error: {e}"
        return result


def convert_corpus(
    input_dir: Path,
    output_dir: Path,
    dry_run: bool = False,
    skip_existing: bool = False,
) -> dict[str, int | list[dict[str, str | int | bool]]]:
    """Convert all HTML files in a directory to Markdown.

    Args:
        input_dir: Directory containing HTML files
        output_dir: Directory to write Markdown files
        dry_run: If True, don't write files, just report what would happen
        skip_existing: If True, skip files that already exist

    Returns:
        Dictionary with conversion summary:
            - total: Total number of files processed
            - success: Number of successful conversions
            - skipped: Number of skipped files
            - errors: Number of failed conversions
            - results: List of individual file results
    """
    logger.info(f"Converting GOV.UK corpus: {input_dir} -> {output_dir}")
    logger.info(f"Dry run: {dry_run}, Skip existing: {skip_existing}")

    # Find all HTML files
    html_files = sorted(input_dir.glob("*.html"))
    logger.info(f"Found {len(html_files)} HTML files")

    if not html_files:
        logger.warning(f"No HTML files found in {input_dir}")
        return {
            "total": 0,
            "success": 0,
            "skipped": 0,
            "errors": 0,
            "results": [],
        }

    # Convert each file
    results = []
    success_count = 0
    skipped_count = 0
    error_count = 0

    for i, input_path in enumerate(html_files, 1):
        logger.info(f"[{i}/{len(html_files)}] Processing {input_path.name}")

        # Generate output path (same name, .md extension)
        output_path = output_dir / f"{input_path.stem}.md"

        # Convert file
        result = convert_file(input_path, output_path, dry_run, skip_existing)
        results.append(result)

        # Update counts
        if result["status"] == "success":
            success_count += 1
        elif result["status"] == "skipped":
            skipped_count += 1
        else:
            error_count += 1

    # Print summary
    logger.info("=" * 60)
    logger.info("Conversion Summary:")
    logger.info(f"  Total files:     {len(html_files)}")
    logger.info(f"  Successful:      {success_count}")
    logger.info(f"  Skipped:         {skipped_count}")
    logger.info(f"  Errors:          {error_count}")
    logger.info("=" * 60)

    if error_count > 0:
        logger.warning("Files with errors:")
        for result in results:
            if result["status"] == "error":
                logger.warning(f"  {result['input_path']}: {result.get('error', 'Unknown error')}")

    return {
        "total": len(html_files),
        "success": success_count,
        "skipped": skipped_count,
        "errors": error_count,
        "results": results,
    }


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Convert GOV.UK HTML corpus to Markdown format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Input directory containing HTML files (default: {DEFAULT_INPUT_DIR})",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for Markdown files (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without writing files",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already exist in output directory",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return

    if not args.input_dir.is_dir():
        logger.error(f"Input path is not a directory: {args.input_dir}")
        return

    # Convert corpus
    summary = convert_corpus(
        args.input_dir,
        args.output_dir,
        dry_run=args.dry_run,
        skip_existing=args.skip_existing,
    )

    # Exit with error code if any conversions failed
    errors = summary.get("errors", 0)
    if isinstance(errors, int) and errors > 0:
        exit(1)


if __name__ == "__main__":
    main()
