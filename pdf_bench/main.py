"""Main CLI entry point for PDF-Bench."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from pdf_bench.inventory import build_inventory, save_inventory
from pdf_bench.loader import PARSER_REGISTRY, load_benchmark_config
from pdf_bench.persistence import load_results, save_results
from pdf_bench.report_generator import generate_html_report
from pdf_bench.runner import BenchmarkRunner

app = typer.Typer(
    name="pdfbench",
    help="PDF-Bench: Benchmarking suite for PDF-to-Markdown conversion",
    add_completion=False,
)

console = Console()


def _status_style(status: str) -> str:
    if status == "publishable":
        return "bold green"
    if status == "valid_internal":
        return "green"
    if status == "archive_only":
        return "yellow"
    return "red"


def version_callback(show_version: bool) -> None:
    """Show version and exit."""
    if show_version:
        from pdf_bench import __version__

        typer.echo(f"PDF-Bench version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """PDF-Bench: Benchmarking suite for PDF-to-Markdown conversion."""
    if ctx.invoked_subcommand is None:
        console.print(
            "[bold cyan]PDF-Bench[/bold cyan] - Benchmarking suite for PDF-to-Markdown conversion"
        )
        console.print("\nRun [bold]pdfbench --help[/bold] for usage information.")


@app.command()
def run(
    config_path: Path = typer.Argument(
        ..., help="Path to benchmark configuration YAML file", exists=True
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Path to save results JSON (optional)"
    ),
    workers: int | None = typer.Option(
        None,
        "--workers",
        "-w",
        help="Number of parallel workers (0=auto, 1=sequential, N=parallel)",
    ),
) -> None:
    """
    Run a benchmark using the specified configuration file.

    Example:
        pdfbench run benchmarks/quick_test.yaml -o results/quick_test.json
    """
    try:
        console.print(f"\n[bold cyan]Loading configuration:[/bold cyan] {config_path}")

        # Load configuration
        config = load_benchmark_config(config_path)

        console.print(
            f"[green]✓[/green] Loaded: {config.config.name}\n"
            f"  Documents: {len(config.documents)}\n"
            f"  Parsers: {len(config.parser_instances)}\n"
            f"  Metrics: {len(config.config.metric_config.metrics)}"
        )

        # Determine worker count
        if workers is None:
            workers = config.config.parallel_workers

        # Create runner
        console.print(
            f"\n[bold cyan]Running benchmark...[/bold cyan] "
            f"(workers: {workers if workers > 0 else 'auto'})"
        )
        runner = BenchmarkRunner(config, parallel_workers=workers)

        # Enable checkpointing if output path provided
        checkpoint_path = Path(output).with_suffix(".checkpoint.json") if output else None
        if checkpoint_path:
            console.print(f"[dim]Checkpointing enabled: {checkpoint_path} (every result)[/dim]")

        # Run benchmark with checkpointing - save every result
        results = runner.run(checkpoint_path=checkpoint_path, checkpoint_interval=1)

        # Display summary
        console.print("\n[bold green]✓ Benchmark Complete[/bold green]")
        console.print(
            f"  Total results: {len(results.results)}\n"
            f"  Successful: {results.success_count}\n"
            f"  Failed: {results.failure_count}"
        )

        # Save results if output path provided
        if output:
            console.print(f"\n[bold cyan]Saving results:[/bold cyan] {output}")

            # Get parser versions
            parser_versions = {}
            for parser in config.parser_instances:
                try:
                    parser_versions[parser.name] = parser.version
                except Exception:
                    parser_versions[parser.name] = "unknown"

            save_results(
                results,
                output,
                config_file=str(config_path),
                parser_versions=parser_versions,
            )
            console.print(f"[green]✓[/green] Results saved to {output}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        raise typer.Exit(code=1) from e
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command(name="list")
def list_systems(
    parsers: bool = typer.Option(True, "--parsers/--no-parsers", help="List available parsers"),
    metrics: bool = typer.Option(False, "--metrics", help="List available metrics"),
) -> None:
    """
    List available parsers and metrics.

    Example:
        pdfbench list
        pdfbench list --metrics
    """
    if parsers:
        console.print("\n[bold cyan]Available Parsers:[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Status", style="green")

        for parser_id, parser_class in PARSER_REGISTRY.items():
            try:
                # Try to instantiate to check if available
                _parser = parser_class()
                status = "✓ Available"
                name = parser_class.__name__
            except Exception as e:
                status = f"✗ Error: {str(e)[:30]}"
                name = parser_class.__name__

            table.add_row(parser_id, name, status)

        console.print(table)

    if metrics:
        from pdf_bench.config import VALID_METRICS

        console.print("\n[bold cyan]Available Metrics:[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Category", style="white")

        # Group metrics by category
        categories = {
            "Text": ["edit_distance", "edit_similarity", "character_error_rate", "chrf++"],
            "Structure": ["tree_edit_distance", "tree_similarity", "element_f1"],
            "Table": ["teds", "teds_with_content", "cell_content_f1", "cell_accuracy"],
            "Math": ["latex_f1", "latex_accuracy"],
        }

        for category, metric_list in categories.items():
            for metric in metric_list:
                if metric in VALID_METRICS:
                    table.add_row(metric, category)

        console.print(table)


@app.command()
def report(
    results_path: Path = typer.Argument(
        ..., help="Path to benchmark results JSON file", exists=True
    ),
    output_path: Path | None = typer.Option(
        None, "--output", "-o", help="Path to save HTML report"
    ),
    include_charts: bool = typer.Option(
        False, "--charts", help="Include chart placeholders in report"
    ),
) -> None:
    """
    Generate HTML report from benchmark results.

    Example:
        pdfbench report results/quick_test.json -o reports/quick_test.html
        pdfbench report results/quick_test.json  # Display summary in console
    """
    try:
        console.print(f"\n[bold cyan]Loading results:[/bold cyan] {results_path}")

        # Load results
        results = load_results(results_path)

        console.print(
            f"[green]✓[/green] Loaded: {results.benchmark_name}\n"
            f"  Timestamp: {results.timestamp}\n"
            f"  Results: {len(results.results)}\n"
            f"  Success: {results.success_count}\n"
            f"  Failed: {results.failure_count}"
        )

        if output_path:
            # Generate HTML report
            console.print("\n[bold cyan]Generating HTML report:[/bold cyan]")

            # Try to extract config file from JSON metadata
            import json

            config_file = None
            try:
                with open(results_path, encoding="utf-8") as f:
                    data = json.load(f)
                    config_file = data.get("benchmark", {}).get("config_file")
            except Exception:
                pass

            generate_html_report(
                results,
                output_path,
                config_file=config_file,
                include_charts=include_charts,
            )

            console.print(f"[green]✓[/green] HTML report saved to {output_path}")
            console.print(
                f"  File size: {output_path.stat().st_size:,} bytes\n"
                f"  Open in browser: file://{output_path.absolute()}"
            )
        else:
            # Display summary to console
            console.print("\n[bold cyan]Summary:[/bold cyan]")

            # Group results by parser
            from collections import defaultdict

            from pdf_bench.runner import DocumentResult

            by_parser: dict[str, list[DocumentResult]] = defaultdict(list)
            for result in results.results:
                by_parser[result.parser_name].append(result)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Parser", style="cyan")
            table.add_column("Documents", justify="right")
            table.add_column("Success Rate", justify="right")

            for parser_name, parser_results in sorted(by_parser.items()):
                successes = sum(1 for r in parser_results if r.success)
                total = len(parser_results)
                rate = (successes / total * 100) if total > 0 else 0

                table.add_row(parser_name, str(total), f"{rate:.1f}% ({successes}/{total})")

            console.print(table)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def inventory(
    repo_root: Path = typer.Option(
        Path("."), "--repo-root", help="Repository root to scan", exists=True, file_okay=False
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Optional path to save inventory JSON"
    ),
) -> None:
    """Inventory corpora, benchmark configs, and result artifacts."""
    try:
        snapshot = build_inventory(repo_root)

        console.print(f"\n[bold cyan]Repository inventory:[/bold cyan] {snapshot.repo_root}")
        console.print(f"Generated: {snapshot.generated_at}")

        summary_table = Table(show_header=True, header_style="bold magenta")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Total", justify="right")
        summary_table.add_column("Valid", justify="right")
        summary_table.add_column("Draft", justify="right")
        summary_table.add_column("Archive", justify="right")

        for category in ["corpora", "benchmarks", "results"]:
            counts = snapshot.summary[category]
            summary_table.add_row(
                category,
                str(counts["total"]),
                str(counts["valid_internal"] + counts["publishable"]),
                str(counts["draft"]),
                str(counts["archive_only"]),
            )

        console.print(summary_table)

        if snapshot.corpora:
            corpus_table = Table(show_header=True, header_style="bold magenta")
            corpus_table.add_column("Corpus", style="cyan")
            corpus_table.add_column("Status")
            corpus_table.add_column("Counts", style="white")
            corpus_table.add_column("Issues", justify="right")

            for record in snapshot.corpora:
                corpus_table.add_row(
                    record.corpus_id,
                    f"[{_status_style(record.status)}]{record.status}[/{_status_style(record.status)}]",
                    f"{record.input_count}/{record.ground_truth_count}/{record.metadata_count}",
                    str(len(record.issues)),
                )

            console.print("\n[bold cyan]Corpora[/bold cyan]")
            console.print(corpus_table)

        if snapshot.benchmarks:
            benchmark_table = Table(show_header=True, header_style="bold magenta")
            benchmark_table.add_column("Benchmark", style="cyan")
            benchmark_table.add_column("Status")
            benchmark_table.add_column("Parsers", justify="right")
            benchmark_table.add_column("Metrics", justify="right")
            benchmark_table.add_column("Issues", justify="right")

            for record in snapshot.benchmarks:
                benchmark_table.add_row(
                    record.name,
                    f"[{_status_style(record.status)}]{record.status}[/{_status_style(record.status)}]",
                    str(record.parser_count),
                    str(record.metric_count),
                    str(len(record.issues)),
                )

            console.print("\n[bold cyan]Benchmarks[/bold cyan]")
            console.print(benchmark_table)

        if snapshot.results:
            result_table = Table(show_header=True, header_style="bold magenta")
            result_table.add_column("Result", style="cyan")
            result_table.add_column("Status")
            result_table.add_column("Cost Class", style="white")
            result_table.add_column("Failures", justify="right")
            result_table.add_column("Issues", justify="right")

            for record in snapshot.results:
                failures = record.failure_count if record.failure_count is not None else "-"
                result_table.add_row(
                    Path(record.path).name,
                    f"[{_status_style(record.status)}]{record.status}[/{_status_style(record.status)}]",
                    record.cost_class,
                    str(failures),
                    str(len(record.issues)),
                )

            console.print("\n[bold cyan]Results[/bold cyan]")
            console.print(result_table)

        if output:
            save_inventory(snapshot, output)
            console.print(f"\n[green]✓[/green] Inventory saved to {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()
