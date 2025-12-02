"""Benchmark runner that orchestrates parser execution and metric computation."""

import multiprocessing as mp
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pdf_bench.loader import DocumentInfo, LoadedConfig
from pdf_bench.metrics import (
    MarkdownASTParser,
    character_error_rate,
    chrf_plus_plus_score,
    edit_similarity,
    element_f1_score,
    latex_f1_score,
    teds_score_with_content,
    tree_similarity,
)
from pdf_bench.metrics.markdown_to_html import markdown_table_to_html
from pdf_bench.systems import BaseParser

try:
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Wrapper functions for AST-based metrics
# These metrics need parsed AST objects, not raw strings
_ast_parser = MarkdownASTParser()


def _tree_similarity_wrapper(ground_truth: str, prediction: str) -> float:
    """Wrapper for tree_similarity that handles string parsing."""
    try:
        gt_ast = _ast_parser.parse(ground_truth)
        pred_ast = _ast_parser.parse(prediction)
        return tree_similarity(gt_ast, pred_ast)
    except Exception:
        # Return None on parse failure (will be converted to NaN)
        return float("nan")


def _element_f1_wrapper(ground_truth: str, prediction: str) -> float:
    """Wrapper for element_f1_score that handles string parsing and returns F1."""
    try:
        gt_ast = _ast_parser.parse(ground_truth)
        pred_ast = _ast_parser.parse(prediction)
        scores = element_f1_score(gt_ast, pred_ast)
        # element_f1_score returns a dict with 'overall' and 'per_element' keys
        f1_score: float = scores["overall"]["f1"]
        return f1_score
    except Exception:
        return float("nan")


def _teds_wrapper(ground_truth: str, prediction: str) -> float:
    """Wrapper for teds_score_with_content that converts markdown tables to HTML.

    Uses content-aware TEDS that includes cell text in comparison, not just structure.
    This provides more discriminative scores than structure-only TEDS.
    """
    try:
        # Convert markdown tables to HTML
        gt_html = markdown_table_to_html(ground_truth)
        pred_html = markdown_table_to_html(prediction)

        # If no tables found, return NaN
        if gt_html is None or pred_html is None:
            return float("nan")

        return teds_score_with_content(pred_html, gt_html)
    except Exception:
        return float("nan")


# Metric function registry
# All functions must have signature: (ground_truth: str, prediction: str) -> float
METRIC_FUNCTIONS: dict[str, Any] = {
    "edit_similarity": edit_similarity,
    "chrf++": chrf_plus_plus_score,
    "character_error_rate": character_error_rate,
    "tree_similarity": _tree_similarity_wrapper,
    "element_f1": _element_f1_wrapper,
    "teds": _teds_wrapper,  # Use wrapper to convert markdown→HTML
    "latex_f1": latex_f1_score,
}


def _extract_parser_init_args(parser: BaseParser) -> tuple[type[BaseParser], dict[str, Any]]:
    """Extract class and constructor arguments from a parser instance.

    This is needed for multiprocessing: we can't pickle parser instances directly,
    so we need to reconstruct them in worker processes.

    Args:
        parser: Parser instance to extract args from

    Returns:
        Tuple of (parser_class, parser_options_dict)
    """
    parser_class = type(parser)
    parser_options: dict[str, Any] = {}

    # PdfsmithAdapter needs backend_name and kwargs
    if hasattr(parser, "_backend_name"):
        parser_options["backend_name"] = parser._backend_name
        if hasattr(parser, "_kwargs") and parser._kwargs:
            parser_options.update(parser._kwargs)

    # Test parser attributes (MockParser etc.)
    if hasattr(parser, "_name"):
        parser_options["name"] = parser._name
    if hasattr(parser, "_should_fail"):
        parser_options["should_fail"] = parser._should_fail
    if hasattr(parser, "_output_content"):
        parser_options["output_content"] = parser._output_content

    return parser_class, parser_options


@dataclass
class DocumentResult:
    """Results for one document from one parser."""

    document_id: str
    parser_name: str
    success: bool
    metrics: dict[str, float]
    error: str | None = None
    parse_time_seconds: float = 0.0


@dataclass
class BenchmarkResults:
    """Complete results for a benchmark run."""

    benchmark_name: str
    timestamp: str
    results: list[DocumentResult] = field(default_factory=list)
    total_documents: int = 0
    total_parsers: int = 0
    success_count: int = 0
    failure_count: int = 0


def _worker_run_single(
    parser_name: str,
    parser_class: type[BaseParser],
    parser_options: dict[str, Any],
    doc_id: str,
    pdf_path: Path,
    gt_path: Path,
    results_dir: Path,
    metrics_list: list[str],
) -> DocumentResult:
    """Worker function for parallel execution.

    This function is designed to be called by multiprocessing workers.
    It recreates the parser instance and runs a single benchmark.

    Args:
        parser_name: Name of the parser
        parser_class: Parser class to instantiate
        parser_options: Options to pass to parser constructor
        doc_id: Document ID
        pdf_path: Path to PDF file
        gt_path: Path to ground truth markdown
        results_dir: Directory to save parser output
        metrics_list: List of metric names to compute

    Returns:
        DocumentResult with metrics or error information
    """
    try:
        # Instantiate parser in worker process
        parser = parser_class(**parser_options)

        # Parse PDF to Markdown
        start_time = time.time()
        output_md_path = parser.parse(pdf_path, results_dir)
        parse_time = time.time() - start_time

        # Read generated and ground truth markdown
        generated_md = output_md_path.read_text(encoding="utf-8")
        ground_truth_md = gt_path.read_text(encoding="utf-8")

        # Compute metrics
        metrics = {}
        for metric_name in metrics_list:
            try:
                metric_func = METRIC_FUNCTIONS.get(metric_name)
                if metric_func is None:
                    continue

                score = metric_func(ground_truth_md, generated_md)
                metrics[metric_name] = score

            except Exception:
                metrics[metric_name] = float("nan")

        return DocumentResult(
            document_id=doc_id,
            parser_name=parser_name,
            success=True,
            metrics=metrics,
            parse_time_seconds=parse_time,
        )

    except Exception as e:
        return DocumentResult(
            document_id=doc_id,
            parser_name=parser_name,
            success=False,
            metrics={},
            error=str(e),
        )


class BenchmarkRunner:
    """Orchestrates benchmark execution across parsers and documents."""

    def __init__(self, config: LoadedConfig, parallel_workers: int | None = None) -> None:
        """Initialize runner with loaded configuration.

        Args:
            config: LoadedConfig with instantiated parsers and resolved paths
            parallel_workers: Number of parallel workers to use.
                0 or None = auto-detect CPU count
                1 = sequential execution (no multiprocessing)
                N > 1 = use N parallel workers
        """
        self.config = config

        # Determine worker count
        if parallel_workers is None:
            # Use config value if available, otherwise default to auto
            parallel_workers = getattr(config.config, "parallel_workers", 0)

        if parallel_workers == 0:
            # Auto-detect: use CPU count, capped at reasonable max
            self.workers = min(mp.cpu_count(), 8)
        else:
            self.workers = max(1, parallel_workers)

    def run(
        self, checkpoint_path: Path | None = None, checkpoint_interval: int = 20
    ) -> BenchmarkResults:
        """Execute complete benchmark with incremental checkpointing.

        Uses parallel execution if workers > 1, otherwise sequential.
        Saves checkpoints every checkpoint_interval results to allow resumption on failure.

        Args:
            checkpoint_path: Optional path to save/load checkpoints. If None, no checkpointing.
            checkpoint_interval: Number of results between checkpoints (default: 20)

        Returns:
            BenchmarkResults with all parser/document combinations
        """
        import datetime

        results = BenchmarkResults(
            benchmark_name=self.config.config.name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            total_documents=len(self.config.documents),
            total_parsers=len(self.config.parser_instances),
        )

        # Build list of all tasks
        tasks = []
        for parser in self.config.parser_instances:
            for doc in self.config.documents:
                tasks.append((parser, doc))

        # Load existing checkpoint if available
        completed_tasks = set()
        if checkpoint_path and checkpoint_path.exists():
            try:
                from pdf_bench.persistence import load_results

                checkpoint_results = load_results(checkpoint_path)
                results.results = checkpoint_results.results
                results.success_count = checkpoint_results.success_count
                results.failure_count = checkpoint_results.failure_count

                # Build set of completed (parser, doc_id) pairs
                for result in results.results:
                    completed_tasks.add((result.parser_name, result.document_id))

                print(f"✓ Loaded checkpoint: {len(completed_tasks)} tasks already complete")
            except Exception as e:
                print(f"⚠ Could not load checkpoint: {e}, starting fresh")

        # Filter out already-completed tasks
        remaining_tasks = []
        for parser, doc in tasks:
            if (parser.name, doc.doc_id) not in completed_tasks:
                remaining_tasks.append((parser, doc))

        if not remaining_tasks:
            print("✓ All tasks already complete!")
            return results

        print(f"→ Running {len(remaining_tasks)} tasks ({len(completed_tasks)} already done)")

        # Execute tasks (parallel or sequential)
        if self.workers == 1:
            # Sequential execution with checkpointing
            task_results = self._run_sequential_with_checkpoints(
                remaining_tasks, results, checkpoint_path, checkpoint_interval
            )
        else:
            # Parallel execution with checkpointing
            task_results = self._run_parallel_with_checkpoints(
                remaining_tasks, results, checkpoint_path, checkpoint_interval
            )

        # Collect results (may already be in results from checkpointing)
        if task_results:
            for result in task_results:
                results.results.append(result)
                if result.success:
                    results.success_count += 1
                else:
                    results.failure_count += 1

        return results

    def _run_sequential(self, tasks: list[tuple[BaseParser, DocumentInfo]]) -> list[DocumentResult]:
        """Execute tasks sequentially with optional progress bar.

        Args:
            tasks: List of (parser, document) tuples to execute

        Returns:
            List of DocumentResults
        """
        results = []

        if RICH_AVAILABLE:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task_id = progress.add_task(f"Running {self.config.config.name}", total=len(tasks))

                for parser, doc in tasks:
                    result = self._run_single(parser, doc)
                    results.append(result)
                    progress.update(task_id, advance=1)
        else:
            # No progress bar, just iterate
            for parser, doc in tasks:
                result = self._run_single(parser, doc)
                results.append(result)

        return results

    def _run_sequential_with_checkpoints(
        self,
        tasks: list[tuple[BaseParser, DocumentInfo]],
        results: BenchmarkResults,
        checkpoint_path: Path | None,
        checkpoint_interval: int,
    ) -> list[DocumentResult]:
        """Execute tasks sequentially with periodic checkpointing.

        Args:
            tasks: List of (parser, document) tuples to execute
            results: BenchmarkResults object to update
            checkpoint_path: Path to save checkpoints
            checkpoint_interval: Number of results between checkpoints

        Returns:
            Empty list (results are added directly to results object)
        """
        from pdf_bench.persistence import save_results

        task_results = []
        checkpoint_counter = 0

        if RICH_AVAILABLE:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task_id = progress.add_task(f"Running {self.config.config.name}", total=len(tasks))

                for parser, doc in tasks:
                    result = self._run_single(parser, doc)
                    task_results.append(result)
                    results.results.append(result)

                    if result.success:
                        results.success_count += 1
                    else:
                        results.failure_count += 1

                    checkpoint_counter += 1

                    # Save checkpoint periodically
                    if checkpoint_path and checkpoint_counter >= checkpoint_interval:
                        save_results(results, checkpoint_path)
                        checkpoint_counter = 0

                    progress.update(task_id, advance=1)
        else:
            # No progress bar, just iterate
            for i, (parser, doc) in enumerate(tasks):
                result = self._run_single(parser, doc)
                task_results.append(result)
                results.results.append(result)

                if result.success:
                    results.success_count += 1
                else:
                    results.failure_count += 1

                checkpoint_counter += 1

                # Save checkpoint periodically
                if checkpoint_path and checkpoint_counter >= checkpoint_interval:
                    save_results(results, checkpoint_path)
                    checkpoint_counter = 0
                    print(f"✓ Checkpoint saved ({i + 1}/{len(tasks)} tasks complete)")

        # Final checkpoint
        if checkpoint_path:
            save_results(results, checkpoint_path)

        return []  # Results already added to results object

    def _run_parallel_with_checkpoints(
        self,
        tasks: list[tuple[BaseParser, DocumentInfo]],
        results: BenchmarkResults,
        checkpoint_path: Path | None,
        checkpoint_interval: int,
    ) -> list[DocumentResult]:
        """Execute tasks in parallel with periodic checkpointing.

        Args:
            tasks: List of (parser, document) tuples to execute
            results: BenchmarkResults object to update
            checkpoint_path: Path to save checkpoints
            checkpoint_interval: Number of results between checkpoints

        Returns:
            Empty list (results are added directly to results object)
        """
        from pdf_bench.persistence import save_results

        # Prepare task arguments for worker function
        worker_args = []
        for parser, doc in tasks:
            parser_class, parser_options = _extract_parser_init_args(parser)

            worker_args.append(
                (
                    parser.name,
                    parser_class,
                    parser_options,
                    doc.doc_id,
                    doc.pdf_path,
                    doc.ground_truth_path,
                    self.config.results_dir,
                    self.config.config.metric_config.metrics,
                )
            )

        # Execute in parallel with progress tracking and checkpointing
        checkpoint_counter = 0

        if RICH_AVAILABLE:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task_id = progress.add_task(
                    f"Running {self.config.config.name} ({self.workers} workers)",
                    total=len(tasks),
                )

                with mp.Pool(processes=self.workers) as pool:
                    for result in pool.starmap(_worker_run_single, worker_args):
                        results.results.append(result)

                        if result.success:
                            results.success_count += 1
                        else:
                            results.failure_count += 1

                        checkpoint_counter += 1

                        # Save checkpoint periodically
                        if checkpoint_path and checkpoint_counter >= checkpoint_interval:
                            save_results(results, checkpoint_path)
                            checkpoint_counter = 0

                        progress.update(task_id, advance=1)
        else:
            # No progress bar, just use pool
            with mp.Pool(processes=self.workers) as pool:
                for i, result in enumerate(pool.starmap(_worker_run_single, worker_args)):
                    results.results.append(result)

                    if result.success:
                        results.success_count += 1
                    else:
                        results.failure_count += 1

                    checkpoint_counter += 1

                    # Save checkpoint periodically
                    if checkpoint_path and checkpoint_counter >= checkpoint_interval:
                        save_results(results, checkpoint_path)
                        checkpoint_counter = 0
                        print(f"✓ Checkpoint saved ({i + 1}/{len(tasks)} tasks complete)")

        # Final checkpoint
        if checkpoint_path:
            save_results(results, checkpoint_path)

        return []  # Results already added to results object

    def _run_parallel(self, tasks: list[tuple[BaseParser, DocumentInfo]]) -> list[DocumentResult]:
        """Execute tasks in parallel using multiprocessing.

        Args:
            tasks: List of (parser, document) tuples to execute

        Returns:
            List of DocumentResults
        """
        # Prepare task arguments for worker function
        worker_args = []
        for parser, doc in tasks:
            parser_class, parser_options = _extract_parser_init_args(parser)

            worker_args.append(
                (
                    parser.name,
                    parser_class,
                    parser_options,
                    doc.doc_id,
                    doc.pdf_path,
                    doc.ground_truth_path,
                    self.config.results_dir,
                    self.config.config.metric_config.metrics,
                )
            )

        # Execute in parallel with progress tracking
        results = []

        if RICH_AVAILABLE:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task_id = progress.add_task(
                    f"Running {self.config.config.name} ({self.workers} workers)",
                    total=len(tasks),
                )

                with mp.Pool(processes=self.workers) as pool:
                    for result in pool.starmap(_worker_run_single, worker_args):
                        results.append(result)
                        progress.update(task_id, advance=1)
        else:
            # No progress bar, just use pool
            with mp.Pool(processes=self.workers) as pool:
                results = pool.starmap(_worker_run_single, worker_args)

        return results

    def _run_single(self, parser: BaseParser, doc: DocumentInfo) -> DocumentResult:
        """Run one parser on one document.

        Args:
            parser: Parser instance to use
            doc: Document to process

        Returns:
            DocumentResult with metrics or error information
        """
        try:
            # 1. Parse PDF to Markdown
            start_time = time.time()
            output_md_path = parser.parse(doc.pdf_path, self.config.results_dir)
            parse_time = time.time() - start_time

            # 2. Read generated and ground truth markdown
            generated_md = output_md_path.read_text(encoding="utf-8")
            ground_truth_md = doc.ground_truth_path.read_text(encoding="utf-8")

            # 3. Compute configured metrics
            metrics = self._compute_metrics(ground_truth_md, generated_md)

            return DocumentResult(
                document_id=doc.doc_id,
                parser_name=parser.name,
                success=True,
                metrics=metrics,
                parse_time_seconds=parse_time,
            )

        except Exception as e:
            # Handle any parser or metric computation failures
            return DocumentResult(
                document_id=doc.doc_id,
                parser_name=parser.name,
                success=False,
                metrics={},
                error=str(e),
            )

    def _compute_metrics(self, ground_truth: str, prediction: str) -> dict[str, float]:
        """Compute all configured metrics.

        Args:
            ground_truth: Ground truth markdown content
            prediction: Parser-generated markdown content

        Returns:
            Dictionary of metric names to scores
        """
        metrics = {}

        for metric_name in self.config.config.metric_config.metrics:
            try:
                metric_func = METRIC_FUNCTIONS.get(metric_name)
                if metric_func is None:
                    # Skip unknown metrics gracefully
                    continue

                # Call metric function
                score = metric_func(ground_truth, prediction)

                # All wrappers return floats directly
                metrics[metric_name] = score

            except Exception:
                # Mark metric as N/A on failure rather than failing entire benchmark
                metrics[metric_name] = float("nan")

        return metrics
