"""Benchmark runner that orchestrates parser execution and metric computation."""

import time
from dataclasses import dataclass, field
from typing import Any

from pdf_bench.loader import DocumentInfo, LoadedConfig
from pdf_bench.metrics import (
    chrf_plus_plus_score,
    edit_similarity,
    element_f1_score,
    latex_f1_score,
    teds_score,
    tree_similarity,
)
from pdf_bench.systems import BaseParser

# Metric function registry
METRIC_FUNCTIONS: dict[str, Any] = {
    "edit_similarity": edit_similarity,
    "chrf++": chrf_plus_plus_score,
    "tree_similarity": tree_similarity,
    "element_f1": element_f1_score,
    "teds": teds_score,
    "latex_f1": latex_f1_score,
}


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


class BenchmarkRunner:
    """Orchestrates benchmark execution across parsers and documents."""

    def __init__(self, config: LoadedConfig) -> None:
        """Initialize runner with loaded configuration.

        Args:
            config: LoadedConfig with instantiated parsers and resolved paths
        """
        self.config = config

    def run(self) -> BenchmarkResults:
        """Execute complete benchmark.

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

        # For each parser
        for parser in self.config.parser_instances:
            # For each document
            for doc in self.config.documents:
                result = self._run_single(parser, doc)
                results.results.append(result)

                if result.success:
                    results.success_count += 1
                else:
                    results.failure_count += 1

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

    def _compute_metrics(
        self, ground_truth: str, prediction: str
    ) -> dict[str, float]:
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

                # Handle element_f1 which returns ElementScores
                if metric_name == "element_f1":
                    metrics[f"{metric_name}_precision"] = score.precision
                    metrics[f"{metric_name}_recall"] = score.recall
                    metrics[f"{metric_name}_f1"] = score.f1
                else:
                    metrics[metric_name] = score

            except Exception:
                # Mark metric as N/A on failure rather than failing entire benchmark
                metrics[metric_name] = float("nan")

        return metrics
