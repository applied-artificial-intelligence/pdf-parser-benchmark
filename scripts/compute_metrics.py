#!/usr/bin/env python3
"""Compute quality metrics for frontier benchmark results."""

import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_bench.metrics import (
    MarkdownASTParser,
    character_error_rate,
    chrf_plus_plus_score,
    edit_similarity,
    element_f1_score,
    teds_score_with_content,
    tree_similarity,
)
from pdf_bench.metrics.markdown_to_html import markdown_table_to_html

# Ground truth location mappings
CORPUS_DIR = Path("corpus")
CACHE_DIR = Path(".cache/parsers")

# Initialize AST parser once
_ast_parser = MarkdownASTParser()


def find_ground_truth(doc_id: str) -> Path | None:
    """Find ground truth file for a document."""
    # Synthetic documents (09_table_simple_grid, etc.)
    if doc_id.startswith(("0", "1", "2", "3")) and "_" in doc_id:
        gt_path = CORPUS_DIR / "synthetic" / f"{doc_id}.md"
        if gt_path.exists():
            return gt_path

    # Arxiv papers (arxiv-2302.00722 -> 2302.00722.md)
    if doc_id.startswith("arxiv-"):
        arxiv_id = doc_id.replace("arxiv-", "")
        for gt_dir in [
            CORPUS_DIR / "academic" / "ground_truth",
            CORPUS_DIR / "academic" / "sample" / "ground_truth",
        ]:
            gt_path = gt_dir / f"{arxiv_id}.md"
            if gt_path.exists():
                return gt_path

    # CUAD documents
    if doc_id.startswith("cuad_"):
        gt_path = CORPUS_DIR / "business" / "cuad" / "ground_truth" / f"{doc_id}.md"
        if gt_path.exists():
            return gt_path

    # Invoices
    if doc_id.startswith("invoice_"):
        gt_path = CORPUS_DIR / "business" / "invoices" / "ground_truth" / f"{doc_id}.md"
        if gt_path.exists():
            return gt_path

    # Resumes
    if doc_id.startswith("resume_"):
        gt_path = CORPUS_DIR / "business" / "hr" / "ground_truth" / f"{doc_id}.md"
        if gt_path.exists():
            return gt_path

    return None


def find_parsed_output(doc_id: str, parser_name: str) -> Path | None:
    """Find parsed markdown output for a document/parser pair."""
    # Parser output is in .cache/parsers/{parser_name}/{doc_id}/*.md
    parser_dir = CACHE_DIR / parser_name / doc_id
    if parser_dir.exists():
        md_files = list(parser_dir.glob("*.md"))
        if md_files:
            return md_files[0]
    return None


def compute_tree_similarity(gt: str, pred: str) -> float:
    """Compute tree similarity metric."""
    try:
        gt_ast = _ast_parser.parse(gt)
        pred_ast = _ast_parser.parse(pred)
        return tree_similarity(gt_ast, pred_ast)
    except Exception:
        return float("nan")


def compute_element_f1(gt: str, pred: str) -> float:
    """Compute element F1 metric."""
    try:
        gt_ast = _ast_parser.parse(gt)
        pred_ast = _ast_parser.parse(pred)
        scores = element_f1_score(gt_ast, pred_ast)
        return scores["overall"]["f1"]
    except Exception:
        return float("nan")


def compute_teds(gt: str, pred: str) -> float:
    """Compute TEDS (Table Edit Distance Similarity) metric."""
    try:
        gt_html = markdown_table_to_html(gt)
        pred_html = markdown_table_to_html(pred)
        if gt_html is None or pred_html is None:
            return float("nan")
        return teds_score_with_content(pred_html, gt_html)
    except Exception:
        return float("nan")


# Max length for expensive O(n³) tree operations (20KB)
MAX_TREE_LENGTH = 20_000


def compute_all_metrics(ground_truth: str, prediction: str) -> dict:
    """Compute all metrics for a ground truth / prediction pair."""
    metrics = {}

    # Text similarity metrics (cheap, always run)
    try:
        metrics["edit_similarity"] = edit_similarity(ground_truth, prediction)
    except Exception:
        metrics["edit_similarity"] = float("nan")

    try:
        metrics["chrf++"] = chrf_plus_plus_score(ground_truth, prediction)
    except Exception:
        metrics["chrf++"] = float("nan")

    try:
        metrics["character_error_rate"] = character_error_rate(ground_truth, prediction)
    except Exception:
        metrics["character_error_rate"] = float("nan")

    # Structure metrics - skip for very long documents (O(n³) complexity)
    max_len = max(len(ground_truth), len(prediction))
    if max_len <= MAX_TREE_LENGTH:
        metrics["tree_similarity"] = compute_tree_similarity(ground_truth, prediction)
        metrics["element_f1"] = compute_element_f1(ground_truth, prediction)
    else:
        metrics["tree_similarity"] = float("nan")
        metrics["element_f1"] = float("nan")
        metrics["_skipped_tree"] = True

    # TEDS for tables (usually bounded by table size, not doc size)
    metrics["teds"] = compute_teds(ground_truth, prediction)

    return metrics


def main():
    """Compute metrics for all results in frontier_merged.json."""
    input_file = Path("results/frontier_merged.json")
    output_file = Path("results/frontier_with_metrics.json")

    print(f"Loading results from {input_file}...")
    with open(input_file) as f:
        data = json.load(f)

    results = data["results"]
    print(f"Found {len(results)} results")

    # Filter to docs with all 7 parsers for fair comparison
    from collections import Counter

    doc_counts = Counter(r["document_id"] for r in results)
    full_coverage_docs = {d for d, c in doc_counts.items() if c == 7}
    print(f"Documents with all 7 parsers: {len(full_coverage_docs)}")

    # Compute metrics for each result
    computed = 0
    skipped_no_gt = 0
    skipped_no_output = 0
    errors = 0

    start_time = time.time()

    for i, result in enumerate(results):
        doc_id = result["document_id"]
        parser_name = result["parser_name"]

        # Only process docs with full coverage
        if doc_id not in full_coverage_docs:
            continue

        # Skip unsuccessful parses
        if not result.get("success", False):
            continue

        # Find ground truth
        gt_path = find_ground_truth(doc_id)
        if gt_path is None:
            skipped_no_gt += 1
            continue

        # Find parsed output
        output_path = find_parsed_output(doc_id, parser_name)
        if output_path is None:
            skipped_no_output += 1
            continue

        # Read files
        try:
            ground_truth = gt_path.read_text(encoding="utf-8")
            prediction = output_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  Error reading files for {doc_id}/{parser_name}: {e}")
            errors += 1
            continue

        # Compute metrics
        try:
            metrics = compute_all_metrics(ground_truth, prediction)
            result["metrics"] = metrics
            computed += 1

            # Progress output
            if computed % 10 == 0:
                elapsed = time.time() - start_time
                rate = computed / elapsed
                print(f"  {computed} computed ({rate:.1f}/s)...", flush=True)

        except Exception as e:
            print(f"  Error computing metrics for {doc_id}/{parser_name}: {e}")
            errors += 1

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.1f}s:")
    print(f"  - Computed: {computed}")
    print(f"  - Skipped (no ground truth): {skipped_no_gt}")
    print(f"  - Skipped (no parser output): {skipped_no_output}")
    print(f"  - Errors: {errors}")

    # Save results
    data["metrics_computed"] = True
    data["metrics_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nSaved to {output_file}")

    # Print summary stats
    print("\n=== Metric Summary (docs with all 7 parsers) ===")
    from collections import defaultdict

    parser_metrics = defaultdict(list)

    for result in results:
        if result["document_id"] not in full_coverage_docs:
            continue
        if not result.get("metrics"):
            continue

        parser = result["parser_name"]
        metrics = result["metrics"]

        for metric_name, value in metrics.items():
            if not (value != value):  # Skip NaN values
                parser_metrics[(parser, metric_name)].append(value)

    # Print averages by parser
    parsers = sorted(set(p for p, _ in parser_metrics.keys()))
    metric_names = ["edit_similarity", "chrf++", "tree_similarity", "element_f1"]

    print(f"\n{'Parser':<35}", end="")
    for m in metric_names:
        print(f"{m:>15}", end="")
    print()
    print("-" * (35 + 15 * len(metric_names)))

    for parser in parsers:
        print(f"{parser:<35}", end="")
        for metric in metric_names:
            values = parser_metrics.get((parser, metric), [])
            if values:
                avg = sum(values) / len(values)
                print(f"{avg:>15.3f}", end="")
            else:
                print(f"{'N/A':>15}", end="")
        print()


if __name__ == "__main__":
    main()
