#!/usr/bin/env python3
"""CLI tool for batch conversion of SEC EDGAR filings HTML to Markdown.

This script processes SEC filing HTML files and converts them to Markdown format
using the SEC HTML to Markdown converter. It's designed for corpus preparation.

Usage:
    python builders/convert_sec_corpus.py \\
        --input corpus/business/sec/html/ \\
        --output corpus/business/sec/ground_truth/ \\
        --dry-run \\
        --skip-existing

The script:
- Recursively processes all .html files in input directory
- Converts using financial table extraction
- Preserves directory structure in output
- Logs conversion statistics and errors
"""

import argparse
import logging
import sys
from pathlib import Path

from builders.sec_html_to_markdown import SECHTMLToMarkdown, SECMarkdownConversionError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup_argparser() -> argparse.ArgumentParser:
    """Create argument parser for CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Convert SEC EDGAR filing HTML files to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all files in directory
  python builders/convert_sec_corpus.py \\
      --input corpus/business/sec/html/ \\
      --output corpus/business/sec/ground_truth/

  # Dry run to see what would be converted
  python builders/convert_sec_corpus.py \\
      --input corpus/business/sec/html/ \\
      --output corpus/business/sec/ground_truth/ \\
      --dry-run

  # Skip already converted files
  python builders/convert_sec_corpus.py \\
      --input corpus/business/sec/html/ \\
      --output corpus/business/sec/ground_truth/ \\
      --skip-existing

  # Disable financial table extraction (use simple HTML)
  python builders/convert_sec_corpus.py \\
      --input corpus/business/sec/html/ \\
      --output corpus/business/sec/ground_truth/ \\
      --no-financial-tables

  # Verbose logging
  python builders/convert_sec_corpus.py \\
      --input corpus/business/sec/html/ \\
      --output corpus/business/sec/ground_truth/ \\
      --verbose
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Input directory containing SEC filing HTML files",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Output directory for Markdown files",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without actually converting",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already have corresponding Markdown output",
    )

    parser.add_argument(
        "--no-financial-tables",
        action="store_true",
        help="Disable financial table extraction (use simple HTML preservation)",
    )

    parser.add_argument(
        "--no-normalize-currency",
        action="store_true",
        help="Disable currency normalization in tables",
    )

    parser.add_argument(
        "--no-strip-xbrl",
        action="store_true",
        help="Keep XBRL tags in table HTML",
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Don't extract filing metadata",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.html",
        help="Glob pattern for HTML files (default: **/*.html)",
    )

    return parser


def convert_file(
    input_path: Path,
    output_path: Path,
    converter: SECHTMLToMarkdown,
    dry_run: bool = False,
) -> bool:
    """Convert single HTML file to Markdown.

    Args:
        input_path: Path to input HTML file
        output_path: Path to output Markdown file
        converter: SECHTMLToMarkdown instance
        dry_run: If True, don't actually write file

    Returns:
        True if conversion successful, False otherwise
    """
    try:
        logger.info(f"Converting: {input_path}")

        # Read HTML
        with open(input_path, encoding="utf-8") as f:
            html = f.read()

        # Convert to Markdown
        markdown = converter.convert(html)

        if dry_run:
            logger.info(f"Would write to: {output_path} ({len(markdown)} bytes)")
        else:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write Markdown
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)

            logger.info(f"Wrote: {output_path} ({len(markdown)} bytes)")

        return True

    except SECMarkdownConversionError as e:
        logger.error(f"Conversion failed for {input_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error converting {input_path}: {e}")
        return False


def get_output_path(input_path: Path, input_dir: Path, output_dir: Path) -> Path:
    """Calculate output path preserving directory structure.

    Args:
        input_path: Path to input file
        input_dir: Root input directory
        output_dir: Root output directory

    Returns:
        Path for output file
    """
    # Get relative path from input_dir
    rel_path = input_path.relative_to(input_dir)

    # Change extension to .md
    rel_path = rel_path.with_suffix(".md")

    # Combine with output_dir
    return output_dir / rel_path


def main() -> int:
    """Main entry point for CLI.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = setup_argparser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input directory
    if not args.input.exists():
        logger.error(f"Input directory does not exist: {args.input}")
        return 1

    if not args.input.is_dir():
        logger.error(f"Input path is not a directory: {args.input}")
        return 1

    # Create converter
    converter = SECHTMLToMarkdown(
        use_financial_tables=not args.no_financial_tables,
        normalize_currency=not args.no_normalize_currency,
        strip_xbrl=not args.no_strip_xbrl,
        extract_metadata=not args.no_metadata,
    )

    logger.info("Converter settings:")
    logger.info(f"  Financial tables: {not args.no_financial_tables}")
    logger.info(f"  Normalize currency: {not args.no_normalize_currency}")
    logger.info(f"  Strip XBRL: {not args.no_strip_xbrl}")
    logger.info(f"  Extract metadata: {not args.no_metadata}")

    # Find all HTML files
    html_files = list(args.input.glob(args.pattern))

    if not html_files:
        logger.warning(f"No HTML files found in {args.input} matching {args.pattern}")
        return 0

    logger.info(f"Found {len(html_files)} HTML files to process")

    # Convert files
    success_count = 0
    skip_count = 0
    error_count = 0

    for input_path in html_files:
        # Calculate output path
        output_path = get_output_path(input_path, args.input, args.output)

        # Skip if output exists and skip_existing is True
        if args.skip_existing and output_path.exists():
            logger.info(f"Skipping (already exists): {input_path}")
            skip_count += 1
            continue

        # Convert file
        if convert_file(input_path, output_path, converter, dry_run=args.dry_run):
            success_count += 1
        else:
            error_count += 1

    # Print summary
    logger.info("=" * 60)
    logger.info("Conversion Summary:")
    logger.info(f"  Total files: {len(html_files)}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Skipped: {skip_count}")
    logger.info(f"  Errors: {error_count}")

    if args.dry_run:
        logger.info("  (Dry run - no files written)")

    # Return error code if any conversions failed
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
