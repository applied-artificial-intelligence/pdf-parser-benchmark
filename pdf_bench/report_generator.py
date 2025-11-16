"""HTML report generation for PDF-Bench benchmark results."""

import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from pdf_bench.runner import BenchmarkResults, DocumentResult


def generate_html_report(
    results: BenchmarkResults,
    output_path: Path,
    config_file: str | None = None,
    include_charts: bool = False,
) -> None:
    """
    Generate HTML report from benchmark results.

    Args:
        results: Benchmark results to generate report from
        output_path: Path to save HTML report
        config_file: Optional path to config file
        include_charts: Whether to include chart placeholders

    Raises:
        ValueError: If results are empty or invalid
    """
    if not results.results:
        raise ValueError("Cannot generate report from empty results")

    # Prepare template environment
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report.html")

    # Calculate leaderboard (average scores by parser)
    leaderboard = _calculate_leaderboard(results)

    # Calculate metric breakdown (scores by metric)
    metrics = _calculate_metric_breakdown(results)

    # Calculate category breakdown (placeholder for now)
    categories = _calculate_category_breakdown(results)

    # Calculate success rate
    success_rate = (
        (results.success_count / len(results.results) * 100)
        if results.results
        else 0.0
    )

    # Render template
    html_content = template.render(
        benchmark_name=results.benchmark_name,
        timestamp=results.timestamp,
        total_documents=results.total_documents,
        total_parsers=results.total_parsers,
        success_rate=success_rate,
        leaderboard=leaderboard,
        metrics=metrics,
        categories=categories,
        config_file=config_file,
        include_charts=include_charts,
    )

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def _calculate_leaderboard(results: BenchmarkResults) -> list[dict[str, Any]]:
    """Calculate leaderboard rankings by parser."""
    # Group results by parser
    by_parser: dict[str, list[DocumentResult]] = defaultdict(list)
    for result in results.results:
        if result.success:
            by_parser[result.parser_name].append(result)

    # Calculate average scores for each parser
    parser_scores = []
    for parser_name, parser_results in by_parser.items():
        # Collect all metric scores (excluding NaN)
        all_scores = []
        for result in parser_results:
            for score in result.metrics.values():
                if not math.isnan(score):
                    all_scores.append(score)

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        success_count = len(parser_results)

        # Count total results for this parser (including failures)
        total_results = sum(
            1 for r in results.results if r.parser_name == parser_name
        )
        success_rate = success_count / total_results if total_results > 0 else 0.0

        parser_scores.append(
            {
                "parser": parser_name,
                "avg_score": avg_score,
                "success_rate": success_rate,
                "num_documents": total_results,
            }
        )

    # Sort by average score (descending)
    parser_scores.sort(
        key=lambda x: (
            float(x["avg_score"]) if isinstance(x["avg_score"], (int, float)) else 0.0
        ),
        reverse=True,
    )

    # Add ranks
    for rank, entry in enumerate(parser_scores, start=1):
        entry["rank"] = rank

    return parser_scores


def _calculate_metric_breakdown(
    results: BenchmarkResults,
) -> dict[str, list[dict[str, Any]]]:
    """Calculate metric scores by parser for each metric."""
    # Group by metric, then by parser
    metric_data: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for result in results.results:
        if result.success:
            for metric_name, score in result.metrics.items():
                if not math.isnan(score):
                    metric_data[metric_name][result.parser_name].append(score)

    # Calculate averages
    metrics_output = {}
    for metric_name, parser_scores in sorted(metric_data.items()):
        scores_list = []
        for parser_name, scores in sorted(parser_scores.items()):
            avg_score = sum(scores) / len(scores) if scores else None
            scores_list.append({"parser": parser_name, "score": avg_score})

        # Sort by score (descending)
        scores_list.sort(
            key=lambda x: x["score"] if x["score"] is not None else -1, reverse=True
        )
        metrics_output[metric_name] = scores_list

    return metrics_output


def _calculate_category_breakdown(
    results: BenchmarkResults,
) -> dict[str, list[dict[str, Any]]]:
    """Calculate performance by document category (placeholder)."""
    # For now, create a single "All Documents" category
    # Future: Parse document IDs or metadata for real categories

    by_parser: dict[str, list[DocumentResult]] = defaultdict(list)
    for result in results.results:
        by_parser[result.parser_name].append(result)

    category_data = []
    for parser_name, parser_results in sorted(by_parser.items()):
        successes = sum(1 for r in parser_results if r.success)
        failures = len(parser_results) - successes

        # Calculate average score across all metrics
        all_scores = []
        for result in parser_results:
            if result.success:
                for score in result.metrics.values():
                    if not math.isnan(score):
                        all_scores.append(score)

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        category_data.append(
            {
                "parser": parser_name,
                "avg_score": avg_score,
                "successes": successes,
                "failures": failures,
            }
        )

    return {"All Documents": category_data}
