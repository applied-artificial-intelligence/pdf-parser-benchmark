#!/usr/bin/env python3
"""Category-weighted analysis for Pareto frontier visualization.

Implements the evaluation methodology:
- 5 categories: synthetic, academic, legal, invoices, resumes
- Equal category weighting (20% each)
- Primary metric: chrf++ (general-purpose)
- Secondary metrics by category
"""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

# Document category mappings (based on actual doc IDs in results)
CATEGORIES = {
    "synthetic": [
        "09_table_simple_grid",
        "10_table_colspan",
        "14_table_financial",
        "15_list_simple_bullets",
        "17_list_nested_2level",
        "19_list_mixed_types",
        "21_column_two_column",
        "24_column_newsletter",
        "27_mixed_business_report",
        "32_mixed_comprehensive",
    ],
    "academic": [
        "arxiv-2302.00722",
        "arxiv-2302.13971",
        "arxiv-2312.00752",
        "arxiv-2401.06244",
        "arxiv-2403.09313",
    ],
    "legal": [
        "cuad_000",
        "cuad_007",
        "cuad_011",
        "cuad_016",
        "cuad_028",
    ],
    "invoices": [
        "invoice_001",
        "invoice_015",
        "invoice_030",
        "invoice_050",
        "invoice_075",
    ],
    "resumes": [
        "resume_001",
        "resume_005",
        "resume_010",
        "resume_020",
        "resume_030",
    ],
}

# Flatten for lookup
DOC_TO_CATEGORY = {}
for cat, docs in CATEGORIES.items():
    for doc in docs:
        DOC_TO_CATEGORY[doc] = cat

# Primary metric for Pareto frontier
PRIMARY_METRIC = "chrf++"

# API pricing per 1M tokens (Dec 2024 estimates)
PRICING = {
    # Premium models
    "anthropic_claude_sonnet_4_5": {"input": 3.0, "output": 15.0},
    "openai_gpt_5_1": {"input": 2.5, "output": 10.0},
    "gemini_gemini_3_pro_preview": {"input": 1.25, "output": 5.0},
    # Budget models
    "anthropic_claude_3_5_haiku": {"input": 0.25, "output": 1.25},
    "openai_gpt_4o_mini": {"input": 0.15, "output": 0.6},
    "gemini_gemini_2_0_flash": {"input": 0.075, "output": 0.30},
    "llamaparse": {"per_page": 0.003},  # $0.003/page
}


def calculate_cost(result: dict, parser_name: str) -> float:
    """Calculate cost in USD for a single parse result."""
    if parser_name not in PRICING:
        return 0.0

    pricing = PRICING[parser_name]

    if "per_page" in pricing:
        # Flat per-page pricing (LlamaParse)
        # Estimate pages from output length if not available
        return pricing["per_page"]  # Approximate 1 page per result

    input_tokens = result.get("input_tokens", 0)
    output_tokens = result.get("output_tokens", 0)

    cost = (
        input_tokens / 1_000_000 * pricing["input"] + output_tokens / 1_000_000 * pricing["output"]
    )
    return cost


def load_results(input_file: Path) -> dict:
    """Load results with metrics."""
    with open(input_file) as f:
        return json.load(f)


def compute_category_scores(results: list[dict]) -> dict:
    """Compute per-parser, per-category average scores."""
    # Structure: {parser: {category: {metric: [values]}}}
    parser_cat_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Also track costs
    parser_costs = defaultdict(list)

    for result in results:
        doc_id = result["document_id"]
        parser = result["parser_name"]
        metrics = result.get("metrics", {})

        if not metrics:
            continue

        category = DOC_TO_CATEGORY.get(doc_id)
        if not category:
            continue

        # Collect metrics
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)) and not math.isnan(value):
                parser_cat_metrics[parser][category][metric_name].append(value)

        # Calculate cost
        cost = calculate_cost(result, parser)
        parser_costs[parser].append(cost)

    # Compute averages
    analysis = {}

    for parser in parser_cat_metrics:
        analysis[parser] = {
            "category_scores": {},
            "overall_score": 0.0,
            "avg_cost": mean(parser_costs[parser]) if parser_costs[parser] else 0.0,
            "total_docs": 0,
        }

        category_primary_scores = []

        for category in CATEGORIES:
            cat_metrics = parser_cat_metrics[parser][category]
            if not cat_metrics:
                continue

            analysis[parser]["category_scores"][category] = {}

            for metric_name, values in cat_metrics.items():
                if values:
                    avg = mean(values)
                    std = stdev(values) if len(values) > 1 else 0.0
                    analysis[parser]["category_scores"][category][metric_name] = {
                        "mean": avg,
                        "std": std,
                        "n": len(values),
                    }

            # Get primary metric for this category
            if PRIMARY_METRIC in cat_metrics and cat_metrics[PRIMARY_METRIC]:
                category_primary_scores.append(mean(cat_metrics[PRIMARY_METRIC]))
                analysis[parser]["total_docs"] += len(cat_metrics[PRIMARY_METRIC])

        # Compute category-weighted overall score (equal weights)
        if category_primary_scores:
            analysis[parser]["overall_score"] = mean(category_primary_scores)

    return analysis


def print_summary(analysis: dict):
    """Print human-readable summary."""
    print("\n" + "=" * 80)
    print("CATEGORY-WEIGHTED EVALUATION RESULTS")
    print("=" * 80)
    print(f"Primary Metric: {PRIMARY_METRIC}")
    print(f"Categories: {', '.join(CATEGORIES.keys())} (equal 20% weight each)")
    print()

    # Sort by overall score
    sorted_parsers = sorted(analysis.items(), key=lambda x: x[1]["overall_score"], reverse=True)

    # Overall ranking
    print(f"OVERALL RANKING (category-weighted {PRIMARY_METRIC})")
    print("-" * 60)
    print(f"{'Rank':<6}{'Parser':<35}{'Score':>10}{'Cost/doc':>12}")
    print("-" * 60)

    for rank, (parser, data) in enumerate(sorted_parsers, 1):
        cost_str = f"${data['avg_cost']:.4f}" if data["avg_cost"] > 0 else "N/A"
        print(f"{rank:<6}{parser:<35}{data['overall_score']:>10.3f}{cost_str:>12}")

    print()

    # Per-category breakdown
    print("\nPER-CATEGORY BREAKDOWN")
    print("-" * 80)

    for category in CATEGORIES:
        print(f"\n{category.upper()} ({len(CATEGORIES[category])} docs):")
        cat_scores = []

        for parser, data in sorted_parsers:
            if category in data["category_scores"]:
                cat_data = data["category_scores"][category]
                if PRIMARY_METRIC in cat_data:
                    pm = cat_data[PRIMARY_METRIC]
                    cat_scores.append((parser, pm["mean"], pm.get("std", 0), pm["n"]))

        cat_scores.sort(key=lambda x: x[1], reverse=True)

        for parser, score, std, n in cat_scores[:7]:
            short_parser = parser[:30]
            print(f"  {short_parser:<32} {score:.3f} +/- {std:.3f} (n={n})")

    print()


def export_pareto_data(analysis: dict, output_file: Path):
    """Export data for Pareto frontier visualization."""
    pareto_data = {
        "methodology": {
            "version": "category_weighted_v1",
            "primary_metric": PRIMARY_METRIC,
            "categories": list(CATEGORIES.keys()),
            "category_weights": "equal (20% each)",
            "cost_basis": "per_document_average",
        },
        "dataset_composition": {
            cat: {"docs": docs, "n": len(docs)} for cat, docs in CATEGORIES.items()
        },
        "parsers": {},
    }

    for parser, data in analysis.items():
        pareto_data["parsers"][parser] = {
            "overall_quality": data["overall_score"],
            "avg_cost_per_doc": data["avg_cost"],
            "total_docs_evaluated": data["total_docs"],
            "category_scores": data["category_scores"],
        }

    with open(output_file, "w") as f:
        json.dump(pareto_data, f, indent=2)

    print(f"\nPareto data exported to: {output_file}")


def main():
    """Run category-weighted analysis."""
    input_file = Path("results/frontier_with_metrics.json")
    output_file = Path("results/pareto_analysis.json")

    if not input_file.exists():
        print(f"Error: {input_file} not found. Run compute_metrics.py first.")
        sys.exit(1)

    print(f"Loading results from {input_file}...")
    data = load_results(input_file)
    results = data.get("results", [])

    # Filter to docs with all 7 parsers
    from collections import Counter

    doc_counts = Counter(r["document_id"] for r in results)
    full_coverage = {d for d, c in doc_counts.items() if c == 7}
    results = [r for r in results if r["document_id"] in full_coverage]

    print(f"Analyzing {len(results)} results ({len(full_coverage)} docs with all 7 parsers)")

    analysis = compute_category_scores(results)
    print_summary(analysis)
    export_pareto_data(analysis, output_file)

    # Also print Pareto-relevant data
    print("\nPARETO FRONTIER DATA (cost vs quality)")
    print("-" * 60)
    print(f"{'Parser':<35}{'Quality':>10}{'Cost/doc':>12}")
    print("-" * 60)

    for parser, data in sorted(analysis.items(), key=lambda x: x[1]["avg_cost"]):
        cost_str = f"${data['avg_cost']:.5f}" if data["avg_cost"] > 0 else "N/A"
        print(f"{parser:<35}{data['overall_score']:>10.3f}{cost_str:>12}")


if __name__ == "__main__":
    main()
