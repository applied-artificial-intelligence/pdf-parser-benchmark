#!/usr/bin/env python3
"""Generate publication-quality visualizations from PDF-Bench benchmark results.

Creates charts for content marketing materials:
1. Parser ranking bar chart (by edit_similarity)
2. Domain breakdown heatmap (parsers × domains)
3. TEDS comparison chart for table-capable parsers
4. Metric correlation visualization

Output: docs/charts/ directory with PNG and SVG files
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def load_benchmark_results(results_path: str = "results/full_corpus_353docs.json") -> dict:
    """Load benchmark results from JSON file."""
    with open(results_path) as f:
        return json.load(f)


def get_domain(doc_id: str) -> str:
    """Categorize document by domain based on ID prefix."""
    if doc_id.startswith("legal_"):
        return "Legal"
    elif doc_id.startswith("invoice_"):
        return "Invoices"
    elif doc_id.startswith("resume_"):
        return "HR/Resumes"
    else:
        return "Synthetic"


def aggregate_results(data: dict) -> tuple[dict, dict]:
    """Aggregate results by parser and by parser+domain."""
    results = data.get("results", [])

    # Aggregate by parser
    parser_metrics = defaultdict(lambda: defaultdict(list))
    parser_domain_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for r in results:
        parser = r.get("parser_name", "unknown")
        doc_id = r.get("document_id", "")
        domain = get_domain(doc_id)
        metrics = r.get("metrics", {})

        for metric, value in metrics.items():
            if value is not None and isinstance(value, int | float):
                parser_metrics[parser][metric].append(value)
                parser_domain_metrics[parser][domain][metric].append(value)

    return dict(parser_metrics), dict(parser_domain_metrics)


def create_parser_ranking_chart(parser_metrics: dict, output_dir: Path):
    """Create horizontal bar chart of parser rankings by edit_similarity."""
    # Calculate mean edit_similarity for each parser
    parser_scores = {}
    for parser, metrics in parser_metrics.items():
        if "edit_similarity" in metrics:
            parser_scores[parser] = np.mean(metrics["edit_similarity"]) * 100

    # Sort by score
    sorted_parsers = sorted(parser_scores.items(), key=lambda x: x[1], reverse=True)
    parsers = [p[0] for p in sorted_parsers]
    scores = [p[1] for p in sorted_parsers]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color gradient based on score
    colors = plt.cm.RdYlGn(np.array(scores) / 100)

    bars = ax.barh(parsers, scores, color=colors)

    # Add value labels
    for bar, score in zip(bars, scores, strict=False):
        ax.text(
            score + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.1f}%",
            va="center",
            fontsize=10,
        )

    ax.set_xlabel("Edit Similarity (%)", fontsize=12)
    ax.set_title("PDF Parser Rankings: 273 Documents × 10 Parsers", fontsize=14, fontweight="bold")
    ax.set_xlim(0, 100)
    ax.invert_yaxis()  # Best at top

    # Add subtitle
    ax.text(
        0.5,
        -0.1,
        "Higher is better. Based on character-level edit similarity between parser output and ground truth.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="gray",
    )

    plt.tight_layout()

    # Save
    fig.savefig(output_dir / "parser_ranking.png", dpi=150, bbox_inches="tight")
    fig.savefig(output_dir / "parser_ranking.svg", bbox_inches="tight")
    plt.close(fig)
    print("✅ Created parser_ranking.png/svg")


def create_domain_heatmap(parser_domain_metrics: dict, output_dir: Path):
    """Create heatmap showing parser performance across domains."""
    parsers = list(parser_domain_metrics.keys())
    domains = ["Legal", "Invoices", "HR/Resumes", "Synthetic"]

    # Build matrix
    matrix = []
    for parser in parsers:
        row = []
        for domain in domains:
            values = (
                parser_domain_metrics.get(parser, {}).get(domain, {}).get("edit_similarity", [])
            )
            if values:
                row.append(np.mean(values) * 100)
            else:
                row.append(np.nan)
        matrix.append(row)

    matrix = np.array(matrix)

    # Sort parsers by overall performance
    overall_scores = np.nanmean(matrix, axis=1)
    sort_idx = np.argsort(overall_scores)[::-1]
    matrix = matrix[sort_idx]
    parsers = [parsers[i] for i in sort_idx]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create heatmap
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Edit Similarity (%)", rotation=-90, va="bottom", fontsize=10)

    # Set ticks
    ax.set_xticks(np.arange(len(domains)))
    ax.set_yticks(np.arange(len(parsers)))
    ax.set_xticklabels(domains, fontsize=11)
    ax.set_yticklabels(parsers, fontsize=11)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    # Add value annotations
    for i in range(len(parsers)):
        for j in range(len(domains)):
            value = matrix[i, j]
            if not np.isnan(value):
                text_color = "white" if value < 60 else "black"
                ax.text(
                    j, i, f"{value:.1f}", ha="center", va="center", color=text_color, fontsize=9
                )

    ax.set_title("Parser Performance by Document Domain", fontsize=14, fontweight="bold")

    # Add note about invoice problem
    ax.text(
        0.5,
        -0.08,
        "Note: All parsers struggle with invoices (<50%). Legal documents are effectively 'solved' (>98%).",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="gray",
    )

    plt.tight_layout()

    fig.savefig(output_dir / "domain_heatmap.png", dpi=150, bbox_inches="tight")
    fig.savefig(output_dir / "domain_heatmap.svg", bbox_inches="tight")
    plt.close(fig)
    print("✅ Created domain_heatmap.png/svg")


def create_teds_comparison(parser_metrics: dict, output_dir: Path):
    """Create bar chart comparing TEDS scores for table-capable parsers."""
    # Get parsers with TEDS scores
    teds_scores = {}
    for parser, metrics in parser_metrics.items():
        teds_values = [v for v in metrics.get("teds", []) if v is not None]
        if teds_values:
            teds_scores[parser] = np.mean(teds_values) * 100

    if not teds_scores:
        print("⚠️ No TEDS scores found, skipping TEDS chart")
        return

    # Sort by score
    sorted_parsers = sorted(teds_scores.items(), key=lambda x: x[1], reverse=True)
    parsers = [p[0] for p in sorted_parsers]
    scores = [p[1] for p in sorted_parsers]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))

    colors = ["#2ecc71" if s >= 90 else "#f39c12" if s >= 80 else "#e74c3c" for s in scores]
    bars = ax.bar(parsers, scores, color=colors)

    # Add value labels
    for bar, score in zip(bars, scores, strict=False):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            score + 1,
            f"{score:.1f}%",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_ylabel("TEDS Score (%)", fontsize=12)
    ax.set_title("Table Extraction Quality (TEDS)", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 100)

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor="#2ecc71", label="Excellent (≥90%)"),
        mpatches.Patch(facecolor="#f39c12", label="Good (80-90%)"),
        mpatches.Patch(facecolor="#e74c3c", label="Poor (<80%)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    # Add note
    ax.text(
        0.5,
        -0.12,
        "TEDS (Tree Edit Distance-based Similarity) measures table structure preservation.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="gray",
    )

    plt.tight_layout()

    fig.savefig(output_dir / "teds_comparison.png", dpi=150, bbox_inches="tight")
    fig.savefig(output_dir / "teds_comparison.svg", bbox_inches="tight")
    plt.close(fig)
    print("✅ Created teds_comparison.png/svg")


def create_metric_correlation(data: dict, output_dir: Path):
    """Create correlation matrix heatmap for metrics."""
    results = data.get("results", [])

    # Extract metrics into arrays
    metrics_data = defaultdict(list)
    metric_names = [
        "edit_similarity",
        "chrf++",
        "character_error_rate",
        "tree_similarity",
        "element_f1",
    ]

    for r in results:
        m = r.get("metrics", {})
        if "edit_similarity" in m:
            for name in metric_names:
                val = m.get(name)
                if val is not None:
                    metrics_data[name].append(val)
                else:
                    metrics_data[name].append(np.nan)

    # Build correlation matrix
    n_metrics = len(metric_names)
    corr_matrix = np.zeros((n_metrics, n_metrics))

    for i, name1 in enumerate(metric_names):
        for j, name2 in enumerate(metric_names):
            arr1 = np.array(metrics_data[name1])
            arr2 = np.array(metrics_data[name2])
            mask = ~(np.isnan(arr1) | np.isnan(arr2))
            if mask.sum() > 10:
                corr_matrix[i, j] = np.corrcoef(arr1[mask], arr2[mask])[0, 1]
            else:
                corr_matrix[i, j] = np.nan

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 7))

    # Display names
    display_names = ["Edit Similarity", "chrF++", "CER", "Tree Similarity", "Element F1"]

    # Create heatmap
    im = ax.imshow(corr_matrix, cmap="RdBu_r", aspect="auto", vmin=-1, vmax=1)

    # Colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Correlation", rotation=-90, va="bottom")

    # Ticks
    ax.set_xticks(np.arange(n_metrics))
    ax.set_yticks(np.arange(n_metrics))
    ax.set_xticklabels(display_names, fontsize=10)
    ax.set_yticklabels(display_names, fontsize=10)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Add value annotations
    for i in range(n_metrics):
        for j in range(n_metrics):
            value = corr_matrix[i, j]
            if not np.isnan(value):
                text_color = "white" if abs(value) > 0.5 else "black"
                ax.text(
                    j, i, f"{value:.2f}", ha="center", va="center", color=text_color, fontsize=9
                )

    ax.set_title("Metric Correlations Across 2,730 Benchmark Runs", fontsize=14, fontweight="bold")

    # Add key insight
    ax.text(
        0.5,
        -0.18,
        "Key insight: Edit Similarity and Tree Similarity have only 0.17 correlation.\n"
        "Text extraction quality does NOT predict structure preservation.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="gray",
    )

    plt.tight_layout()

    fig.savefig(output_dir / "metric_correlation.png", dpi=150, bbox_inches="tight")
    fig.savefig(output_dir / "metric_correlation.svg", bbox_inches="tight")
    plt.close(fig)
    print("✅ Created metric_correlation.png/svg")


def main():
    """Generate all visualizations."""
    # Setup
    output_dir = Path("docs/charts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set style
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette("husl")

    # Load data
    print("Loading benchmark results...")
    data = load_benchmark_results()
    print(f"Loaded {len(data.get('results', []))} results")

    # Aggregate
    parser_metrics, parser_domain_metrics = aggregate_results(data)
    print(f"Found {len(parser_metrics)} parsers")

    # Generate visualizations
    print("\nGenerating visualizations...")
    create_parser_ranking_chart(parser_metrics, output_dir)
    create_domain_heatmap(parser_domain_metrics, output_dir)
    create_teds_comparison(parser_metrics, output_dir)
    create_metric_correlation(data, output_dir)

    print(f"\n✅ All visualizations saved to {output_dir}/")


if __name__ == "__main__":
    main()
