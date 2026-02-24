#!/usr/bin/env python3
"""Build SEC filings corpus from ARS (PDF) + 10-K (HTML) pairs.

Downloads ARS annual report PDFs and converts corresponding 10-K HTML filings
to Markdown ground truth.

Usage:
    python -m builders.build_sec_corpus [--limit N] [--verify-only]
"""

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, Comment

CORPUS_DIR = Path("corpus/sec_filings")
CATALOG_FILE = CORPUS_DIR / "ars_catalog.json"
PDF_DIR = CORPUS_DIR / "pdfs"
GT_DIR = CORPUS_DIR / "ground_truth"
META_DIR = CORPUS_DIR / "metadata"

HEADERS = {"User-Agent": "pdf-bench research@example.com"}
RATE_LIMIT = 0.2  # seconds between requests


def load_catalog() -> list[dict]:
    with open(CATALOG_FILE) as f:
        return json.load(f)


def make_doc_id(entry: dict) -> str:
    """Generate a clean document ID from company name."""
    name = entry["company"].lower()
    # Remove common suffixes
    for suffix in [" inc", " inc.", " corp", " corp.", " co", " co.", " ltd",
                   " plc", " /de", "/de", " group", " & co"]:
        name = name.replace(suffix, "")
    # Clean up
    name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    fy = entry.get("fiscal_year", "2024")
    return f"sec-{name}-{fy}"


def download_file(url: str, dest: Path) -> bool:
    """Download a file from URL to dest path."""
    if dest.exists() and dest.stat().st_size > 0:
        return True  # Already downloaded
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def html_to_markdown(html_content: str) -> str:
    """Convert SEC filing HTML to clean Markdown ground truth.

    Strips iXBRL tags, CSS, scripts, and navigation elements while preserving
    the document's text structure, tables, and headings.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script, style, and iXBRL processing instructions
    for tag in soup.find_all(["script", "style", "meta", "link", "noscript"]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove hidden elements
    for tag in soup.find_all(style=re.compile(r"display\s*:\s*none", re.I)):
        tag.decompose()

    # Unwrap iXBRL tags (ix:*) - preserve their text content
    for tag in soup.find_all(re.compile(r"^ix:")):
        tag.unwrap()

    lines: list[str] = []

    def process_element(element, depth=0):
        """Recursively process HTML elements to Markdown."""
        if isinstance(element, str):
            text = element.strip()
            if text:
                lines.append(text)
            return

        if not hasattr(element, "name") or element.name is None:
            return

        tag = element.name.lower()

        # Headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            text = element.get_text(strip=True)
            if text:
                lines.append("")
                lines.append(f"{'#' * level} {text}")
                lines.append("")
            return

        # Paragraphs
        if tag == "p":
            text = element.get_text(separator=" ", strip=True)
            if text:
                lines.append("")
                lines.append(text)
            return

        # Line breaks
        if tag == "br":
            lines.append("")
            return

        # Horizontal rules
        if tag == "hr":
            lines.append("")
            lines.append("---")
            lines.append("")
            return

        # Bold
        if tag in ("b", "strong"):
            text = element.get_text(strip=True)
            if text:
                lines.append(f"**{text}**")
            return

        # Italic
        if tag in ("i", "em"):
            text = element.get_text(strip=True)
            if text:
                lines.append(f"*{text}*")
            return

        # Lists
        if tag in ("ul", "ol"):
            lines.append("")
            for i, li in enumerate(element.find_all("li", recursive=False)):
                text = li.get_text(separator=" ", strip=True)
                if text:
                    prefix = f"{i+1}." if tag == "ol" else "-"
                    lines.append(f"{prefix} {text}")
            lines.append("")
            return

        # Tables
        if tag == "table":
            _process_table(element)
            return

        # Divs and spans - recurse
        if tag in ("div", "span", "section", "article", "main", "body",
                    "html", "td", "th", "tr", "thead", "tbody", "tfoot",
                    "font", "a", "center", "blockquote"):
            for child in element.children:
                process_element(child, depth + 1)
            return

        # Default: extract text
        text = element.get_text(separator=" ", strip=True)
        if text and len(text) > 1:
            lines.append(text)

    def _process_table(table_elem):
        """Convert HTML table to Markdown table."""
        rows = []
        for tr in table_elem.find_all("tr"):
            cells = []
            for cell in tr.find_all(["td", "th"]):
                text = cell.get_text(separator=" ", strip=True)
                # Clean up whitespace
                text = re.sub(r"\s+", " ", text)
                cells.append(text)
            if cells and any(c for c in cells):
                rows.append(cells)

        if not rows:
            return

        # Normalize column count
        max_cols = max(len(r) for r in rows)
        for row in rows:
            while len(row) < max_cols:
                row.append("")

        # Skip trivially small tables (likely layout tables)
        if max_cols < 2 and len(rows) < 3:
            # Just output as text
            for row in rows:
                text = " | ".join(c for c in row if c)
                if text:
                    lines.append(text)
            return

        lines.append("")
        # Header row
        lines.append("| " + " | ".join(rows[0]) + " |")
        lines.append("| " + " | ".join("---" for _ in rows[0]) + " |")
        # Data rows
        for row in rows[1:]:
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # Find the main content body
    body = soup.find("body") or soup
    process_element(body)

    # Clean up output
    text = "\n".join(lines)
    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def process_entry(entry: dict, idx: int, total: int) -> dict | None:
    """Process a single ARS+10-K pair. Returns metadata dict or None on failure."""
    doc_id = make_doc_id(entry)
    company = entry["company"]
    print(f"[{idx+1}/{total}] {company} ({doc_id})")

    pdf_path = PDF_DIR / f"{doc_id}.pdf"
    gt_path = GT_DIR / f"{doc_id}.md"
    meta_path = META_DIR / f"{doc_id}.yaml"

    # Skip if already fully processed
    if pdf_path.exists() and gt_path.exists() and meta_path.exists():
        print(f"  Already processed, skipping")
        return {"doc_id": doc_id, "status": "cached"}

    # Download ARS PDF
    print(f"  Downloading ARS PDF...")
    if not download_file(entry["ars_pdf_url"], pdf_path):
        print(f"  FAILED: Could not download ARS PDF")
        return None
    pdf_size = pdf_path.stat().st_size
    print(f"  PDF: {pdf_size / 1024 / 1024:.1f} MB")
    time.sleep(RATE_LIMIT)

    # Download 10-K HTML
    print(f"  Downloading 10-K HTML...")
    html_path = CORPUS_DIR / "html_cache" / f"{doc_id}.htm"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    if not download_file(entry["tenk_html_url"], html_path):
        print(f"  FAILED: Could not download 10-K HTML")
        return None
    time.sleep(RATE_LIMIT)

    # Convert HTML to Markdown ground truth
    print(f"  Converting 10-K HTML to Markdown...")
    html_content = html_path.read_text(errors="replace")
    markdown = html_to_markdown(html_content)

    if len(markdown) < 500:
        print(f"  WARNING: Ground truth is very short ({len(markdown)} chars)")

    gt_path.parent.mkdir(parents=True, exist_ok=True)
    gt_path.write_text(markdown)
    print(f"  Ground truth: {len(markdown):,} chars")

    # Create metadata YAML
    import yaml
    metadata = {
        "doc_id": doc_id,
        "corpus": "business",
        "domain": "sec-edgar",
        "source": "sec_edgar",
        "source_url": entry["ars_pdf_url"],
    }

    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(yaml.dump(metadata, default_flow_style=False, sort_keys=False))

    return {"doc_id": doc_id, "status": "ok", "pdf_mb": pdf_size / 1024 / 1024,
            "gt_chars": len(markdown)}


def verify_catalog(catalog: list[dict]) -> None:
    """Verify all URLs in catalog are accessible."""
    ok = 0
    fail = 0
    for i, entry in enumerate(catalog):
        doc_id = make_doc_id(entry)
        try:
            req = urllib.request.Request(entry["ars_pdf_url"], method="HEAD", headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                size = int(resp.headers.get("Content-Length", 0))
                print(f"[{i+1}/{len(catalog)}] {entry['company']:30s} | {size/1024/1024:6.1f} MB | OK")
                ok += 1
        except Exception as e:
            print(f"[{i+1}/{len(catalog)}] {entry['company']:30s} | FAIL: {e}")
            fail += 1
        time.sleep(RATE_LIMIT)

    print(f"\nVerification: {ok} OK, {fail} failed out of {len(catalog)}")


def main():
    parser = argparse.ArgumentParser(description="Build SEC filings corpus")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of documents to process")
    parser.add_argument("--verify-only", action="store_true", help="Only verify URLs, don't download")
    args = parser.parse_args()

    catalog = load_catalog()
    print(f"Loaded catalog with {len(catalog)} ARS+10-K pairs")

    if args.verify_only:
        verify_catalog(catalog)
        return

    # Create directories
    for d in [PDF_DIR, GT_DIR, META_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    entries = catalog[:args.limit] if args.limit > 0 else catalog
    results = []
    for i, entry in enumerate(entries):
        result = process_entry(entry, i, len(entries))
        if result:
            results.append(result)
        time.sleep(RATE_LIMIT)

    # Summary
    ok = [r for r in results if r["status"] in ("ok", "cached")]
    print(f"\n{'='*60}")
    print(f"Processed {len(ok)}/{len(entries)} documents successfully")
    if ok:
        sizes = [r.get("pdf_mb", 0) for r in ok if r.get("pdf_mb")]
        if sizes:
            print(f"PDF sizes: {min(sizes):.1f} - {max(sizes):.1f} MB (avg {sum(sizes)/len(sizes):.1f} MB)")

    # Write corpus metadata
    corpus_meta = {
        "name": "SEC Filings (ARS Annual Reports)",
        "description": "Annual Report to Stockholders (ARS) PDFs paired with 10-K iXBRL HTML ground truth",
        "document_count": len(ok),
        "domain": "financial",
        "source": "SEC EDGAR",
        "features": ["financial_statements", "tables", "sec_filings", "annual_reports",
                     "multi_column", "charts", "designed_layout"],
        "ground_truth_method": "10-K iXBRL HTML converted to Markdown via BeautifulSoup",
    }
    import yaml
    (CORPUS_DIR / "corpus_metadata.yaml").write_text(
        yaml.dump(corpus_meta, default_flow_style=False, sort_keys=False)
    )


if __name__ == "__main__":
    main()
