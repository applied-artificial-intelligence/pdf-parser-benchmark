"""Benchmark runner that orchestrates parser execution and metric computation."""

import hashlib
import inspect
import math
import multiprocessing as mp
import sys
import uuid
from dataclasses import dataclass, field
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any, cast

from pdf_bench.execution import execute_parser
from pdf_bench.loader import IMAGE_CAPABLE_BACKENDS, DocumentInfo, LoadedConfig
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

    # Only use Rich progress bar if we have a real TTY
    # Otherwise it blocks/hangs in background processes and piped output
    RICH_AVAILABLE = sys.stdout.isatty()
except ImportError:
    RICH_AVAILABLE = False


# Wrapper functions for AST-based metrics
# These metrics need parsed AST objects, not raw strings
def _tree_similarity_wrapper(ground_truth: str, prediction: str) -> float:
    """Wrapper for tree_similarity that handles string parsing."""
    try:
        parser = MarkdownASTParser()
        gt_ast = parser.parse(ground_truth)
        pred_ast = parser.parse(prediction)
        return tree_similarity(gt_ast, pred_ast)
    except Exception:
        # Return None on parse failure (will be converted to NaN)
        return float("nan")


def _element_f1_wrapper(ground_truth: str, prediction: str) -> float:
    """Wrapper for element_f1_score that handles string parsing and returns F1."""
    try:
        parser = MarkdownASTParser()
        gt_ast = parser.parse(ground_truth)
        pred_ast = parser.parse(prediction)
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


def _latex_f1_wrapper(ground_truth: str, prediction: str) -> float:
    """Wrapper for latex_f1_score that returns just the F1 score as a float."""
    try:
        scores = latex_f1_score(ground_truth, prediction)
        return scores.f1
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
    "latex_f1": _latex_f1_wrapper,
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
        parser_options["cache_mode"] = cast(Any, parser).cache_mode
        return parser_class, parser_options

    for name, parameter in inspect.signature(parser_class).parameters.items():
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        for attribute in (f"_{name}", name):
            if hasattr(parser, attribute):
                parser_options[name] = getattr(parser, attribute)
                break
        else:
            if parameter.default is inspect.Parameter.empty:
                raise ValueError(f"Cannot reconstruct required parser option: {name}")

    return parser_class, parser_options


@dataclass
class DocumentResult:
    """Results for one document from one parser."""

    document_id: str
    parser_name: str
    success: bool
    metrics: dict[str, float]
    error: str | None = None
    parse_time_seconds: float | None = None
    parse_outcome: str = "unknown"
    wall_time_seconds: float | None = None
    output_path: str | None = None
    output_sha256: str | None = None
    error_type: str | None = None
    metric_outcomes: dict[str, dict[str, str]] = field(default_factory=dict)
    evaluation_errors: dict[str, str] = field(default_factory=dict)


def _compute_metric_results(
    ground_truth: str, prediction: str, metrics_list: list[str]
) -> tuple[dict, dict, dict]:
    metrics, outcomes, errors = {}, {}, {}
    for name in metrics_list:
        function = METRIC_FUNCTIONS.get(name)
        if function is None:
            continue
        try:
            score = function(ground_truth, prediction)
            metrics[name] = score
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                errors[name] = "Metric returned a non-numeric score"
                outcomes[name] = {"status": "error", "reason": errors[name]}
            elif math.isfinite(score):
                outcomes[name] = {"status": "scored"}
            else:
                reason = "metric_returned_non_finite"
                if name == "teds" and (
                    markdown_table_to_html(ground_truth) is None
                    or markdown_table_to_html(prediction) is None
                ):
                    reason = "no_markdown_table_in_reference_or_output"
                outcomes[name] = {"status": "unavailable", "reason": reason}
        except Exception as error:
            metrics[name] = float("nan")
            errors[name] = f"{type(error).__name__}: {error}"
            outcomes[name] = {"status": "error", "reason": errors[name]}
    return metrics, outcomes, errors


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
    input_path: Path,
    gt_path: Path,
    results_dir: Path,
    metrics_list: list[str],
    timeout_seconds: float = 300,
) -> DocumentResult:
    """Worker function for parallel execution.

    This function is designed to be called by multiprocessing workers.
    It recreates the parser instance and runs a single benchmark.

    Args:
        parser_name: Name of the parser
        parser_class: Parser class to instantiate
        parser_options: Options to pass to parser constructor
        doc_id: Document ID
        input_path: Path to input file (PDF or image)
        gt_path: Path to ground truth markdown
        results_dir: Directory to save parser output
        metrics_list: List of metric names to compute

    Returns:
        DocumentResult with metrics or error information
    """
    unknown = set(metrics_list) - set(METRIC_FUNCTIONS)
    if unknown:
        raise ValueError(f"Unknown required metrics: {sorted(unknown)}")
    try:
        attempt = execute_parser(
            parser_class,
            parser_options,
            input_path,
            results_dir / "attempts" / uuid.uuid4().hex,
            timeout_seconds,
        )
    except Exception as error:
        return DocumentResult(
            document_id=doc_id,
            parser_name=parser_name,
            success=False,
            metrics={},
            error=str(error),
            error_type=type(error).__name__,
            parse_outcome="initialization_failure",
        )
    result = DocumentResult(
        document_id=doc_id,
        parser_name=parser_name,
        success=attempt.outcome in {"success_content", "success_empty"},
        metrics={},
        error=attempt.error,
        error_type=attempt.error_type,
        parse_time_seconds=attempt.parse_time_seconds,
        wall_time_seconds=attempt.wall_time_seconds,
        parse_outcome=attempt.outcome,
        output_path=str(attempt.output_path) if attempt.output_path is not None else None,
        output_sha256=attempt.output_sha256,
    )
    if result.success:
        try:
            if attempt.output_path is None:
                raise ValueError("Successful parsing has no retained output")
            raw = attempt.output_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != attempt.output_sha256:
                raise ValueError("Output changed between parsing and metric evaluation")
            generated = raw.decode("utf-8")
            truth = gt_path.read_text(encoding="utf-8")
            result.metrics, result.metric_outcomes, result.evaluation_errors = (
                _compute_metric_results(truth, generated, metrics_list)
            )
        except Exception as error:
            result.evaluation_errors["reference_or_output_read"] = str(error)
    return result


def _parser_supports_document(parser: BaseParser, doc: DocumentInfo) -> bool:
    """Check if a parser can handle a given document type.

    PDFs are supported by all parsers, but images require specific backends.

    Args:
        parser: Parser instance to check
        doc: Document info with input type

    Returns:
        True if parser can handle document, False otherwise
    """
    # PDFs are supported by all parsers
    if doc.input_type == "pdf":
        return True

    # For images, check if parser is image-capable
    # Use parser.name which includes "pdfsmith-" prefix
    return parser.name in IMAGE_CAPABLE_BACKENDS


class BenchmarkRunner:
    """Orchestrates benchmark execution across parsers and documents."""

    def __init__(
        self,
        config: LoadedConfig,
        parallel_workers: int | None = None,
        timeout_seconds: float = 300,
    ) -> None:
        """Initialize runner with loaded configuration.

        Args:
            config: LoadedConfig with instantiated parsers and resolved paths
            parallel_workers: Number of parallel workers to use.
                0 or None = auto-detect CPU count
                1 = sequential execution (no multiprocessing)
                N > 1 = use N parallel workers
        """
        self.config = config
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Timeout must be positive and finite")
        self.timeout_seconds = timeout_seconds

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
        Saves readable snapshots every checkpoint_interval results. Resumption is disabled
        until snapshots carry verified execution identity.

        Args:
            checkpoint_path: Fresh snapshot destination. Existing files cannot be resumed.
            checkpoint_interval: Number of results between checkpoints (default: 20)

        Returns:
            BenchmarkResults with all parser/document combinations
        """
        import datetime

        unknown = set(self.config.config.metric_config.metrics) - set(METRIC_FUNCTIONS)
        if unknown:
            raise ValueError(f"Unknown required metrics: {sorted(unknown)}")
        pairs = [
            (parser.name, doc.doc_id)
            for parser in self.config.parser_instances
            for doc in self.config.documents
        ]
        if len(set(pairs)) != len(pairs):
            raise ValueError("Planned input/parser pairs must be unique")
        if checkpoint_path is not None and checkpoint_path.exists():
            raise ValueError(
                "Checkpoint resumption is disabled: snapshots lack full execution identity. "
                "Use a fresh output location; snapshots remain readable with load_results."
            )

        results = BenchmarkResults(
            benchmark_name=self.config.config.name,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            total_documents=len(self.config.documents),
            total_parsers=len(self.config.parser_instances),
        )

        # Build list of all tasks, filtering incompatible parser/document pairs
        tasks = []
        skipped_image_tasks = 0
        for parser in self.config.parser_instances:
            for doc in self.config.documents:
                if _parser_supports_document(parser, doc):
                    tasks.append((parser, doc))
                else:
                    skipped_image_tasks += 1
                    results.results.append(
                        DocumentResult(
                            document_id=doc.doc_id,
                            parser_name=parser.name,
                            success=False,
                            metrics={},
                            parse_outcome="incompatible",
                            error=f"Parser does not support input type {doc.input_type}",
                        )
                    )
                    results.failure_count += 1

        if skipped_image_tasks > 0:
            print(f"→ Recorded {skipped_image_tasks} incompatible input/parser pairs")

        if not tasks:
            return results

        print(f"→ Running {len(tasks)} tasks")

        # Execute tasks (parallel or sequential)
        if self.workers == 1:
            # Sequential execution with checkpointing
            task_results = self._run_sequential_with_checkpoints(
                tasks, results, checkpoint_path, checkpoint_interval
            )
        else:
            # Parallel execution with checkpointing
            task_results = self._run_parallel_with_checkpoints(
                tasks, results, checkpoint_path, checkpoint_interval
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
            # No progress bar, just iterate with text output
            for i, (parser, doc) in enumerate(tasks):
                print(
                    f"[{i + 1}/{len(tasks)}] {parser.name} / {doc.doc_id}...", end=" ", flush=True
                )
                result = self._run_single(parser, doc)
                task_results.append(result)
                results.results.append(result)

                if result.success:
                    results.success_count += 1
                    print(f"SUCCESS ({result.parse_time_seconds:.1f}s)", flush=True)
                else:
                    results.failure_count += 1
                    print(f"FAILED: {result.error}", flush=True)

                checkpoint_counter += 1

                # Save checkpoint periodically
                if checkpoint_path and checkpoint_counter >= checkpoint_interval:
                    save_results(results, checkpoint_path)
                    checkpoint_counter = 0
                    print(
                        f"  -> Checkpoint saved ({i + 1}/{len(tasks)} tasks complete)", flush=True
                    )

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
                    doc.input_path,
                    doc.ground_truth_path,
                    self.config.results_dir,
                    self.config.config.metric_config.metrics,
                    self.timeout_seconds,
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

                with ThreadPool(processes=self.workers) as pool:
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
            with ThreadPool(processes=self.workers) as pool:
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
                    doc.input_path,
                    doc.ground_truth_path,
                    self.config.results_dir,
                    self.config.config.metric_config.metrics,
                    self.timeout_seconds,
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

                with ThreadPool(processes=self.workers) as pool:
                    for result in pool.starmap(_worker_run_single, worker_args):
                        results.append(result)
                        progress.update(task_id, advance=1)
        else:
            # No progress bar, just use pool
            with ThreadPool(processes=self.workers) as pool:
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
        parser_class, options = _extract_parser_init_args(parser)
        return _worker_run_single(
            parser.name,
            parser_class,
            options,
            doc.doc_id,
            doc.input_path,
            doc.ground_truth_path,
            self.config.results_dir,
            self.config.config.metric_config.metrics,
            self.timeout_seconds,
        )

    def _compute_metrics(self, ground_truth: str, prediction: str) -> dict[str, float]:
        """Compute all configured metrics.

        Args:
            ground_truth: Ground truth markdown content
            prediction: Parser-generated markdown content

        Returns:
            Dictionary of metric names to scores
        """
        return _compute_metric_results(
            ground_truth, prediction, self.config.config.metric_config.metrics
        )[0]
