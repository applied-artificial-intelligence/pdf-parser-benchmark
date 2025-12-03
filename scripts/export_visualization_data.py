#!/usr/bin/env python3
"""
Export benchmark data to CSV files for visualization.

Generates:
- corpus_breakdown.csv - Document counts by domain
- corpus_breakdown_by_type.csv - Documents by requires_ocr flag
- parser_capabilities.csv - Parser metadata (OCR support, type, etc.)
- parser_overall_scores.csv - Overall performance per parser (text-extraction only)
- parser_overall_scores_ocr.csv - Performance on OCR documents (OCR parsers only)
- parser_domain_scores.csv - Performance by parser × domain (filtered by capability)
- parser_timing.csv - Processing speed per parser
- detailed_results.csv - Full results for custom analysis
"""

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

# =============================================================================
# Parser Capability Definitions
# =============================================================================

PARSER_CAPABILITIES = {
    # Open source - text extraction only (no OCR)
    "pymupdf": {
        "type": "open_source",
        "has_ocr": False,
        "description": "Fast C++ PDF library, text extraction only",
        "note": "Fastest parser, no OCR",
    },
    "pymupdf4llm": {
        "type": "open_source",
        "has_ocr": False,
        "description": "PyMuPDF with LLM-optimized markdown output",
        "note": "Better formatting than pymupdf",
    },
    "pypdf": {
        "type": "open_source",
        "has_ocr": False,
        "description": "Pure Python PDF library",
        "note": "No external dependencies",
    },
    "pypdf2": {
        "type": "open_source",
        "has_ocr": False,
        "description": "Legacy PyPDF fork (deprecated)",
        "note": "Use pypdf instead",
    },
    "pypdfium2": {
        "type": "open_source",
        "has_ocr": False,
        "description": "PDFium bindings (Chrome PDF engine)",
        "note": "Good performance",
    },
    "pdfplumber": {
        "type": "open_source",
        "has_ocr": False,
        "description": "Detailed PDF parsing with table extraction",
        "note": "Good for tables, no OCR",
    },
    "pdfminer": {
        "type": "open_source",
        "has_ocr": False,
        "description": "Pure Python text extraction",
        "note": "Detailed layout analysis",
    },
    "extractous": {
        "type": "open_source",
        "has_ocr": False,
        "description": "Rust-based text extraction",
        "note": "Fast, minimal dependencies",
    },
    "tika": {
        "type": "open_source",
        "has_ocr": False,  # Can use Tesseract but not by default
        "description": "Apache Tika (Java-based)",
        "note": "Requires Java runtime",
    },
    "unstructured": {
        "type": "open_source",
        "has_ocr": False,  # Has OCR option but not default
        "description": "Document processing pipeline",
        "note": "Can enable OCR separately",
    },
    # Open source - with OCR capability
    "docling": {
        "type": "open_source",
        "has_ocr": True,
        "description": "IBM document understanding with OCR",
        "note": "Deep learning based",
    },
    "docling-fast": {
        "type": "open_source",
        "has_ocr": True,
        "description": "Docling with faster/lighter models",
        "note": "Trade-off: speed vs accuracy",
    },
    "marker": {
        "type": "open_source",
        "has_ocr": True,
        "description": "Deep learning PDF to markdown",
        "note": "GPU recommended, has OCR",
    },
    "marker_ollama": {
        "type": "open_source",
        "has_ocr": True,
        "description": "Marker with Ollama LLM post-processing",
        "note": "No accuracy benefit over marker (tested)",
    },
    "kreuzberg": {
        "type": "open_source",
        "has_ocr": True,
        "description": "OCR-capable document parser",
        "note": "Lightweight OCR option",
    },
    # Commercial cloud APIs - all have OCR
    "aws_textract": {
        "type": "commercial",
        "has_ocr": True,
        "description": "Amazon Textract",
        "note": "Pay per page, includes OCR",
    },
    "azure_document_intelligence": {
        "type": "commercial",
        "has_ocr": True,
        "description": "Azure Document Intelligence (Form Recognizer)",
        "note": "Pay per page, includes OCR",
    },
    "google_document_ai": {
        "type": "commercial",
        "has_ocr": True,
        "description": "Google Document AI",
        "note": "Pay per page, includes OCR",
    },
    "databricks": {
        "type": "commercial",
        "has_ocr": True,
        "description": "Databricks Document Understanding",
        "note": "Requires Databricks workspace",
    },
    "landing_ai": {
        "type": "commercial",
        "has_ocr": True,
        "description": "Landing AI Document Intelligence",
        "note": "Visual AI platform",
    },
    # Frontier LLMs - premium tier (highest quality, highest cost)
    "openai_gpt_5_1": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "OpenAI GPT-5.1 vision model",
        "note": "~$0.05/page, best accuracy",
    },
    "gemini_gemini_3_pro_preview": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "Google Gemini 3 Pro Preview",
        "note": "~$0.03/page, strong accuracy",
    },
    "anthropic_claude_sonnet_4_5": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "Anthropic Claude Sonnet 4.5",
        "note": "~$0.04/page, good accuracy",
    },
    # Frontier LLMs - budget tier (LLM quality, lower cost)
    "llamaparse": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "LlamaIndex LlamaParse",
        "note": "$0.003/page, purpose-built for PDF",
    },
    "openai_gpt_4o": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "OpenAI GPT-4o vision model",
        "note": "~$0.02/page, good all-rounder",
    },
    "openai_gpt_4o_mini": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "OpenAI GPT-4o-mini vision model",
        "note": "~$0.005/page, WARNING: destroys structure (13% tree_similarity)",
    },
    "gemini_gemini_2_0_flash": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "Google Gemini 2.0 Flash",
        "note": "~$0.001/page, cheapest LLM option",
    },
    "gemini_gemini_1_5_pro": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "Google Gemini 1.5 Pro",
        "note": "~$0.01/page, previous generation",
    },
    "anthropic_claude_3_5_haiku": {
        "type": "frontier_llm",
        "has_ocr": True,
        "description": "Anthropic Claude 3.5 Haiku",
        "note": "~$0.01/page, budget Anthropic option",
    },
}


# Domains that require OCR (scanned/image-based documents)
OCR_REQUIRED_DOMAINS = {"omnidocbench"}

# Domains with native text (digital PDFs)
TEXT_EXTRACTION_DOMAINS = {
    "synthetic",
    "legal_contracts",
    "invoices",
    "legal_templates",
    "hr",
    "arxiv",
}


def get_parser_info(parser_name: str) -> dict:
    """Get capability info for a parser."""
    return PARSER_CAPABILITIES.get(
        parser_name,
        {
            "type": "unknown",
            "has_ocr": False,
            "description": "Unknown parser",
            "note": "",
        },
    )


def get_domain(doc_id: str) -> str:
    """Categorize document by ID pattern."""
    doc_id_lower = doc_id.lower()

    if doc_id.startswith("syn-") or (
        len(doc_id) > 2 and doc_id[0:2].isdigit() and doc_id[2] == "_"
    ):
        return "synthetic"
    if "cuad" in doc_id_lower:
        return "legal_contracts"
    if "invoice" in doc_id_lower:
        return "invoices"
    if doc_id.startswith("legal-") or ("legal" in doc_id_lower and "cuad" not in doc_id_lower):
        return "legal_templates"
    if doc_id.startswith("hr-") or "resume" in doc_id_lower or "job-" in doc_id_lower:
        return "hr"
    if "arxiv" in doc_id_lower:
        return "arxiv"
    if "omnidoc" in doc_id_lower:
        return "omnidocbench"
    return "other"


def domain_requires_ocr(domain: str) -> bool:
    """Check if a domain requires OCR capability."""
    return domain in OCR_REQUIRED_DOMAINS


def load_all_results(results_dir: Path) -> list[dict]:
    """Load and merge all benchmark result files."""
    all_results = []
    seen = set()

    files = [
        # Core benchmark results
        "full_corpus_353docs.json",
        "comprehensive_278docs_all_parsers.json",
        "cuad_75docs_all_parsers.json",
        "invoices_100docs.json",
        "legal_108docs.json",
        "hr_34docs.json",
        "omnidocbench_english_252.json",
        "omnidocbench_english_ocr.json",
        "arxiv_10docs_fresh.json",
        "marker_comparison_29docs.json",
        # Gap fill results (additional parser coverage)
        "marker_gap_fill.json",
        "pypdf2_gap_fill.json",
        "synthetic_missing_parsers.json",
        # Commercial API results (200 docs each)
        "commercial_200docs.json",
        "invoices_100docs_fresh.json",
        # Frontier LLM results
        "frontier_premium_300p.json",
        "frontier_unified_30docs.json",
        "frontier_premium_300p_old_models.json",
    ]

    for fname in files:
        fpath = results_dir / fname
        if not fpath.exists():
            continue

        with open(fpath) as f:
            data = json.load(f)

        for r in data["results"]:
            key = (r["document_id"], r["parser_name"])
            if key not in seen:
                seen.add(key)
                r["source_file"] = fname
                all_results.append(r)

    return all_results


def export_parser_capabilities(output_path: Path):
    """Export parser capability metadata."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["parser", "type", "has_ocr", "description", "note"])

        for parser, info in sorted(PARSER_CAPABILITIES.items()):
            writer.writerow(
                [
                    parser,
                    info["type"],
                    "yes" if info["has_ocr"] else "no",
                    info["description"],
                    info["note"],
                ]
            )

    print(f"Exported: {output_path}")


def export_corpus_breakdown(results: list[dict], output_path: Path):
    """Export document counts by domain."""
    doc_domains = {}
    for r in results:
        doc_id = r["document_id"]
        if doc_id not in doc_domains:
            doc_domains[doc_id] = get_domain(doc_id)

    domain_counts = defaultdict(int)
    for domain in doc_domains.values():
        domain_counts[domain] += 1

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "document_count", "requires_ocr"])
        for domain in sorted(domain_counts.keys()):
            writer.writerow(
                [domain, domain_counts[domain], "yes" if domain_requires_ocr(domain) else "no"]
            )
        writer.writerow(["TOTAL", sum(domain_counts.values()), ""])

    print(f"Exported: {output_path}")
    return domain_counts


def export_corpus_by_type(results: list[dict], output_path: Path):
    """Export corpus breakdown by OCR requirement."""
    doc_domains = {}
    for r in results:
        doc_id = r["document_id"]
        if doc_id not in doc_domains:
            doc_domains[doc_id] = get_domain(doc_id)

    ocr_count = sum(1 for d in doc_domains.values() if domain_requires_ocr(d))
    text_count = len(doc_domains) - ocr_count

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["document_type", "document_count", "description"])
        writer.writerow(["text_extraction", text_count, "Digital PDFs with embedded text"])
        writer.writerow(["ocr_required", ocr_count, "Scanned/image-based documents"])
        writer.writerow(["TOTAL", len(doc_domains), ""])

    print(f"Exported: {output_path}")


def filter_results_by_capability(
    results: list[dict], ocr_docs: bool, ocr_parsers: bool
) -> list[dict]:
    """
    Filter results by document and parser capability match.

    Args:
        results: All benchmark results
        ocr_docs: If True, include only OCR-required docs; if False, exclude them
        ocr_parsers: If True, include only OCR-capable parsers; if False, include all
    """
    filtered = []
    for r in results:
        domain = get_domain(r["document_id"])
        doc_needs_ocr = domain_requires_ocr(domain)
        parser_info = get_parser_info(r["parser_name"])
        parser_has_ocr = parser_info.get("has_ocr", False)

        # Filter by document type
        if ocr_docs and not doc_needs_ocr:
            continue
        if not ocr_docs and doc_needs_ocr:
            continue

        # Filter by parser capability
        if ocr_parsers and not parser_has_ocr:
            continue

        filtered.append(r)

    return filtered


def export_parser_overall_scores(results: list[dict], output_path: Path, title: str = ""):
    """Export overall performance scores per parser."""
    parser_metrics = defaultdict(lambda: defaultdict(list))
    parser_success = defaultdict(lambda: {"success": 0, "total": 0})
    parser_times = defaultdict(list)

    for r in results:
        parser = r["parser_name"]
        parser_success[parser]["total"] += 1

        if r["success"]:
            parser_success[parser]["success"] += 1
            if r.get("parse_time_seconds"):
                parser_times[parser].append(r["parse_time_seconds"])

            if r.get("metrics"):
                for metric, value in r["metrics"].items():
                    if value is not None:
                        parser_metrics[parser][metric].append(value)

    metrics_list = [
        "edit_similarity",
        "chrf++",
        "character_error_rate",
        "tree_similarity",
        "element_f1",
        "teds",
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)

        # Add parser capability columns
        header = ["parser", "type", "has_ocr", "success_rate", "doc_count", "avg_parse_time_ms"] + [
            f"avg_{m}" for m in metrics_list
        ]
        writer.writerow(header)

        for parser in sorted(parser_metrics.keys()):
            parser_info = get_parser_info(parser)
            success_rate = (
                parser_success[parser]["success"] / parser_success[parser]["total"]
                if parser_success[parser]["total"] > 0
                else 0
            )
            doc_count = parser_success[parser]["total"]
            avg_time = (
                statistics.mean(parser_times[parser]) * 1000 if parser_times[parser] else None
            )

            row = [
                parser,
                parser_info.get("type", "unknown"),
                "yes" if parser_info.get("has_ocr") else "no",
                f"{success_rate:.3f}",
                doc_count,
                f"{avg_time:.2f}" if avg_time else "",
            ]

            for metric in metrics_list:
                values = parser_metrics[parser].get(metric, [])
                avg = statistics.mean(values) if values else None
                row.append(f"{avg:.4f}" if avg else "")

            writer.writerow(row)

    print(f"Exported: {output_path} {title}")


def export_parser_domain_scores(
    results: list[dict], output_path: Path, include_ocr_domains: bool = False
):
    """Export parser performance broken down by document domain."""
    scores = defaultdict(lambda: defaultdict(list))

    for r in results:
        if not r["success"] or not r.get("metrics"):
            continue

        parser = r["parser_name"]
        domain = get_domain(r["document_id"])

        # Skip OCR domains if not included
        if not include_ocr_domains and domain_requires_ocr(domain):
            continue

        edit_sim = r["metrics"].get("edit_similarity")

        if edit_sim is not None:
            scores[parser][domain].append(edit_sim)

    all_domains = sorted(set(d for p in scores.values() for d in p.keys()))

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["parser", "type", "has_ocr"] + all_domains + ["overall"])

        for parser in sorted(scores.keys()):
            parser_info = get_parser_info(parser)
            row = [
                parser,
                parser_info.get("type", "unknown"),
                "yes" if parser_info.get("has_ocr") else "no",
            ]
            all_scores = []
            for domain in all_domains:
                domain_scores = scores[parser].get(domain, [])
                if domain_scores:
                    avg = statistics.mean(domain_scores)
                    row.append(f"{avg:.4f}")
                    all_scores.extend(domain_scores)
                else:
                    row.append("")

            overall = statistics.mean(all_scores) if all_scores else None
            row.append(f"{overall:.4f}" if overall else "")
            writer.writerow(row)

    print(f"Exported: {output_path}")


def export_parser_timing(results: list[dict], output_path: Path):
    """Export detailed timing statistics per parser."""
    parser_times = defaultdict(list)

    for r in results:
        if r["success"] and r.get("parse_time_seconds"):
            parser_times[r["parser_name"]].append(r["parse_time_seconds"])

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "parser",
                "type",
                "has_ocr",
                "doc_count",
                "mean_ms",
                "median_ms",
                "min_ms",
                "max_ms",
                "std_ms",
            ]
        )

        for parser in sorted(parser_times.keys()):
            parser_info = get_parser_info(parser)
            times = parser_times[parser]
            times_ms = [t * 1000 for t in times]

            writer.writerow(
                [
                    parser,
                    parser_info.get("type", "unknown"),
                    "yes" if parser_info.get("has_ocr") else "no",
                    len(times),
                    f"{statistics.mean(times_ms):.2f}",
                    f"{statistics.median(times_ms):.2f}",
                    f"{min(times_ms):.2f}",
                    f"{max(times_ms):.2f}",
                    f"{statistics.stdev(times_ms):.2f}" if len(times) > 1 else "0.00",
                ]
            )

    print(f"Exported: {output_path}")


def export_detailed_results(results: list[dict], output_path: Path):
    """Export full results for custom analysis."""
    metrics_list = [
        "edit_similarity",
        "chrf++",
        "character_error_rate",
        "tree_similarity",
        "element_f1",
        "teds",
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "document_id",
                "domain",
                "requires_ocr",
                "parser",
                "parser_type",
                "parser_has_ocr",
                "success",
                "parse_time_ms",
            ]
            + metrics_list
        )

        for r in results:
            domain = get_domain(r["document_id"])
            parser_info = get_parser_info(r["parser_name"])
            parse_time = (
                r.get("parse_time_seconds", 0) * 1000 if r.get("parse_time_seconds") else ""
            )

            row = [
                r["document_id"],
                domain,
                "yes" if domain_requires_ocr(domain) else "no",
                r["parser_name"],
                parser_info.get("type", "unknown"),
                "yes" if parser_info.get("has_ocr") else "no",
                "1" if r["success"] else "0",
                f"{parse_time:.2f}" if parse_time else "",
            ]

            for metric in metrics_list:
                val = r.get("metrics", {}).get(metric) if r["success"] else None
                row.append(f"{val:.4f}" if val is not None else "")

            writer.writerow(row)

    print(f"Exported: {output_path}")


def export_structure_leaderboard(results: list[dict], output_path: Path):
    """Export structure recovery scores (tree_similarity, element_f1)."""
    parser_scores = defaultdict(lambda: {"tree": [], "element": [], "count": 0})

    for r in results:
        if not r["success"] or not r.get("metrics"):
            continue

        parser = r["parser_name"]
        tree = r["metrics"].get("tree_similarity")
        elem = r["metrics"].get("element_f1")

        if tree is not None:
            parser_scores[parser]["tree"].append(tree)
        if elem is not None:
            parser_scores[parser]["element"].append(elem)
        parser_scores[parser]["count"] += 1

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "parser",
                "type",
                "has_ocr",
                "doc_count",
                "avg_tree_similarity",
                "avg_element_f1",
                "structure_score",
            ]
        )

        rows = []
        for parser, scores in parser_scores.items():
            if not scores["tree"] and not scores["element"]:
                continue

            parser_info = get_parser_info(parser)
            avg_tree = statistics.mean(scores["tree"]) if scores["tree"] else None
            avg_elem = statistics.mean(scores["element"]) if scores["element"] else None

            # Combined structure score (average of both if available)
            if avg_tree and avg_elem:
                struct_score = (avg_tree + avg_elem) / 2
            elif avg_tree:
                struct_score = avg_tree
            elif avg_elem:
                struct_score = avg_elem
            else:
                struct_score = None

            rows.append(
                [
                    parser,
                    parser_info.get("type", "unknown"),
                    "yes" if parser_info.get("has_ocr") else "no",
                    scores["count"],
                    f"{avg_tree:.4f}" if avg_tree else "",
                    f"{avg_elem:.4f}" if avg_elem else "",
                    f"{struct_score:.4f}" if struct_score else "",
                ]
            )

        # Sort by structure_score descending
        rows.sort(key=lambda x: float(x[6]) if x[6] else 0, reverse=True)
        for row in rows:
            writer.writerow(row)

    print(f"Exported: {output_path}")


def export_table_leaderboard(results: list[dict], output_path: Path):
    """Export table extraction scores (TEDS metric)."""
    parser_scores = defaultdict(lambda: {"teds": [], "count": 0})

    for r in results:
        if not r["success"] or not r.get("metrics"):
            continue

        parser = r["parser_name"]
        teds = r["metrics"].get("teds")

        if teds is not None:
            parser_scores[parser]["teds"].append(teds)
            parser_scores[parser]["count"] += 1

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["parser", "type", "has_ocr", "docs_with_tables", "avg_teds", "min_teds", "max_teds"]
        )

        rows = []
        for parser, scores in parser_scores.items():
            if not scores["teds"]:
                continue

            parser_info = get_parser_info(parser)
            teds_values = scores["teds"]

            rows.append(
                [
                    parser,
                    parser_info.get("type", "unknown"),
                    "yes" if parser_info.get("has_ocr") else "no",
                    scores["count"],
                    f"{statistics.mean(teds_values):.4f}",
                    f"{min(teds_values):.4f}",
                    f"{max(teds_values):.4f}",
                ]
            )

        # Sort by avg_teds descending
        rows.sort(key=lambda x: float(x[4]) if x[4] else 0, reverse=True)
        for row in rows:
            writer.writerow(row)

    print(f"Exported: {output_path}")


def export_speed_leaderboard(results: list[dict], output_path: Path):
    """Export speed rankings (median parse time)."""
    parser_times = defaultdict(list)

    for r in results:
        if r["success"] and r.get("parse_time_seconds"):
            parser_times[r["parser_name"]].append(r["parse_time_seconds"])

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "rank",
                "parser",
                "type",
                "has_ocr",
                "median_ms",
                "mean_ms",
                "doc_count",
                "speed_category",
            ]
        )

        rows = []
        for parser, times in parser_times.items():
            parser_info = get_parser_info(parser)
            times_ms = [t * 1000 for t in times]
            median = statistics.median(times_ms)

            # Categorize speed
            if median < 10:
                category = "very_fast"
            elif median < 100:
                category = "fast"
            elif median < 1000:
                category = "medium"
            elif median < 10000:
                category = "slow"
            else:
                category = "very_slow"

            rows.append(
                [
                    parser,
                    parser_info.get("type", "unknown"),
                    "yes" if parser_info.get("has_ocr") else "no",
                    median,
                    statistics.mean(times_ms),
                    len(times),
                    category,
                ]
            )

        # Sort by median time ascending (fastest first)
        rows.sort(key=lambda x: x[3])

        for rank, row in enumerate(rows, 1):
            writer.writerow(
                [rank] + [row[0], row[1], row[2], f"{row[3]:.2f}", f"{row[4]:.2f}", row[5], row[6]]
            )

    print(f"Exported: {output_path}")


def main():
    results_dir = Path("results")
    output_dir = Path("data_exports")
    output_dir.mkdir(exist_ok=True)

    print("Loading benchmark results...")
    results = load_all_results(results_dir)
    print(f"Loaded {len(results)} result records")

    # 1. Parser capabilities reference
    export_parser_capabilities(output_dir / "parser_capabilities.csv")

    # 2. Corpus breakdown
    export_corpus_breakdown(results, output_dir / "corpus_breakdown.csv")
    export_corpus_by_type(results, output_dir / "corpus_by_type.csv")

    # 3. Text extraction benchmarks (exclude OCR-required docs)
    #    This is the FAIR comparison for all parsers
    text_results = filter_results_by_capability(results, ocr_docs=False, ocr_parsers=False)
    print(f"\nText extraction results: {len(text_results)} records")
    export_parser_overall_scores(
        text_results,
        output_dir / "parser_scores_text_extraction.csv",
        "(text extraction - fair comparison)",
    )
    export_parser_domain_scores(
        text_results, output_dir / "parser_domain_scores_text.csv", include_ocr_domains=False
    )

    # 4. OCR benchmarks (only OCR docs, only OCR-capable parsers)
    #    This is ONLY meaningful for OCR-capable parsers
    ocr_results = filter_results_by_capability(results, ocr_docs=True, ocr_parsers=True)
    print(f"OCR results: {len(ocr_results)} records")
    if ocr_results:
        export_parser_overall_scores(
            ocr_results, output_dir / "parser_scores_ocr.csv", "(OCR documents - OCR parsers only)"
        )

    # 5. Capability-specific leaderboards
    print("\nCapability-specific leaderboards:")
    export_structure_leaderboard(text_results, output_dir / "leaderboard_structure.csv")
    export_table_leaderboard(text_results, output_dir / "leaderboard_tables.csv")
    export_speed_leaderboard(results, output_dir / "leaderboard_speed.csv")

    # 6. Full results (all data, with capability flags for filtering)
    export_parser_timing(results, output_dir / "parser_timing.csv")
    export_detailed_results(results, output_dir / "detailed_results.csv")

    print(f"\nAll exports complete! Files in: {output_dir}/")
    print("\n=== EXPORT SUMMARY ===")
    print("Main comparisons:")
    print("  - parser_scores_text_extraction.csv  (fair comparison on digital PDFs)")
    print("  - parser_scores_ocr.csv              (OCR comparison on scanned PDFs)")
    print("\nCapability-specific leaderboards:")
    print("  - leaderboard_structure.csv          (tree_similarity + element_f1)")
    print("  - leaderboard_tables.csv             (TEDS score)")
    print("  - leaderboard_speed.csv              (ranked by median parse time)")
    print("\nReference data:")
    print("  - parser_capabilities_detailed.csv   (full feature matrix)")
    print("  - detailed_results.csv               (all 5,900+ individual results)")


if __name__ == "__main__":
    main()
