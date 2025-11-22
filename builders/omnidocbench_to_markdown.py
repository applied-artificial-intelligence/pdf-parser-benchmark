#!/usr/bin/env python3
"""Convert OmniDocBench JSON annotations to Markdown ground truth.

This script extracts text content from OmniDocBench annotations and converts
them to markdown format suitable for PDF-Bench evaluation.
"""

import json
import os
from pathlib import Path
from typing import Any


# Category type to markdown heading level mapping
HEADING_LEVELS = {
    "title": 1,
    "header": 2,
    "footer": None,  # Skip footers
    "page_number": None,  # Skip page numbers
    "abandon": None,  # Skip abandoned regions
}

# Categories to include in markdown output
TEXT_CATEGORIES = {
    "title",
    "text_block",
    "header",
    "figure_caption",
    "table_caption",
    "equation_caption",
    "reference",
    "figure_footnote",
    "table_footnote",
    "page_footnote",
    "code_txt",
    "equation_explanation",
}

TABLE_CATEGORIES = {"table"}
EQUATION_CATEGORIES = {"equation_isolated"}


def layout_det_to_markdown(det: dict[str, Any]) -> str | None:
    """Convert a single layout detection to markdown text.

    Args:
        det: Layout detection dictionary with category_type, text, etc.

    Returns:
        Markdown string or None if should be skipped.
    """
    category = det.get("category_type", "")
    text = det.get("text", "").strip()

    if not text:
        return None

    # Skip certain categories
    if category in {"footer", "page_number", "abandon", "text_mask", "table_mask"}:
        return None

    # Handle titles/headers
    if category == "title":
        return f"# {text}\n"
    elif category == "header":
        return f"## {text}\n"

    # Handle text blocks
    if category in TEXT_CATEGORIES:
        return f"{text}\n"

    # Handle tables - extract from HTML if available
    if category == "table":
        html = det.get("html", "")
        if html:
            return convert_table_html_to_markdown(html)
        return f"[Table: {text[:100]}...]\n" if len(text) > 100 else f"[Table: {text}]\n"

    # Handle equations - use LaTeX if available
    if category in EQUATION_CATEGORIES:
        latex = det.get("latex", "")
        if latex:
            return f"$${latex}$$\n"
        return f"[Equation: {text}]\n"

    # Default: return text as paragraph
    return f"{text}\n"


def convert_table_html_to_markdown(html: str) -> str:
    """Convert HTML table to markdown table format.

    This is a simplified converter - handles basic tables.
    """
    # Simple regex-based conversion for basic tables
    import re

    # Remove whitespace between tags
    html = re.sub(r">\s+<", "><", html)

    # Extract rows
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
    if not rows:
        return "[Table]\n"

    md_rows = []
    for i, row in enumerate(rows):
        # Extract cells (th or td)
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.IGNORECASE | re.DOTALL)
        # Clean cell content
        cells = [re.sub(r"<[^>]+>", "", cell).strip() for cell in cells]

        if cells:
            md_rows.append("| " + " | ".join(cells) + " |")

            # Add separator after header row
            if i == 0:
                md_rows.append("| " + " | ".join(["---"] * len(cells)) + " |")

    return "\n".join(md_rows) + "\n" if md_rows else "[Table]\n"


def annotation_to_markdown(annotation: dict[str, Any]) -> str:
    """Convert a full OmniDocBench annotation to markdown.

    Args:
        annotation: Full annotation dict with layout_dets, page_info, etc.

    Returns:
        Markdown string representation of the document page.
    """
    layout_dets = annotation.get("layout_dets", [])

    # Sort by reading order if available (handle None values)
    sorted_dets = sorted(layout_dets, key=lambda x: x.get("order") if x.get("order") is not None else float('inf'))

    md_parts = []
    for det in sorted_dets:
        md = layout_det_to_markdown(det)
        if md:
            md_parts.append(md)

    return "\n".join(md_parts)


def get_metadata(annotation: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata from annotation for YAML frontmatter.

    Args:
        annotation: Full annotation dictionary.

    Returns:
        Metadata dictionary.
    """
    page_info = annotation.get("page_info", {})
    page_attr = page_info.get("page_attribute", {})

    return {
        "doc_id": Path(page_info.get("image_path", "")).stem,
        "source": "omnidocbench",
        "corpus": "academic",
        "domain": page_attr.get("data_source", "unknown"),
        "language": page_attr.get("language", "unknown"),
        "layout": page_attr.get("layout", "unknown"),
        "width": page_info.get("width"),
        "height": page_info.get("height"),
        "page_no": page_info.get("page_no"),
    }


def convert_omnidocbench(
    json_path: str | Path,
    output_dir: str | Path,
    filter_sources: list[str] | None = None,
    max_docs: int | None = None,
    require_image: bool = True,
    images_dir: str | Path | None = None,
) -> dict[str, int]:
    """Convert OmniDocBench annotations to markdown files.

    Args:
        json_path: Path to OmniDocBench.json
        output_dir: Directory to write markdown files
        filter_sources: Only include documents from these sources (e.g., ["newspaper", "academic_literature"])
        max_docs: Maximum number of documents to convert
        require_image: Only convert if corresponding image exists
        images_dir: Directory containing images (for filtering)

    Returns:
        Statistics dictionary with counts.
    """
    json_path = Path(json_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (output_dir / "ground_truth").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)

    with open(json_path) as f:
        data = json.load(f)

    # Get available images if filtering
    available_images = set()
    if images_dir:
        images_dir = Path(images_dir)
        if images_dir.exists():
            available_images = set(os.listdir(images_dir))

    stats = {"total": 0, "converted": 0, "skipped_source": 0, "skipped_no_image": 0}

    for annotation in data:
        stats["total"] += 1

        page_info = annotation.get("page_info", {})
        page_attr = page_info.get("page_attribute", {})
        source = page_attr.get("data_source", "unknown")
        image_path = page_info.get("image_path", "")

        # Filter by source
        if filter_sources and source not in filter_sources:
            stats["skipped_source"] += 1
            continue

        # Filter by image availability
        if require_image and images_dir and image_path not in available_images:
            stats["skipped_no_image"] += 1
            continue

        # Check max docs
        if max_docs and stats["converted"] >= max_docs:
            break

        # Convert to markdown
        md_content = annotation_to_markdown(annotation)
        metadata = get_metadata(annotation)

        # Generate filename from image path
        doc_id = metadata["doc_id"]
        if not doc_id:
            doc_id = f"omnidoc_{stats['converted']:04d}"

        # Write markdown
        md_path = output_dir / "ground_truth" / f"{doc_id}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Write metadata YAML
        meta_path = output_dir / "metadata" / f"{doc_id}.yaml"
        import yaml
        with open(meta_path, "w", encoding="utf-8") as f:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)

        stats["converted"] += 1

    return stats


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Convert OmniDocBench to Markdown")
    parser.add_argument("--json", required=True, help="Path to OmniDocBench.json")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--images", help="Images directory (for filtering)")
    parser.add_argument("--sources", nargs="+", help="Filter to specific data sources")
    parser.add_argument("--max", type=int, help="Maximum documents to convert")
    parser.add_argument("--no-require-image", action="store_true", help="Don't require image to exist")

    args = parser.parse_args()

    stats = convert_omnidocbench(
        json_path=args.json,
        output_dir=args.output,
        filter_sources=args.sources,
        max_docs=args.max,
        require_image=not args.no_require_image,
        images_dir=args.images,
    )

    print(f"Conversion complete:")
    print(f"  Total annotations: {stats['total']}")
    print(f"  Converted: {stats['converted']}")
    print(f"  Skipped (source filter): {stats['skipped_source']}")
    print(f"  Skipped (no image): {stats['skipped_no_image']}")


if __name__ == "__main__":
    main()
