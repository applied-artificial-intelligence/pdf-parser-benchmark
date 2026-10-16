"""Tests for benchmark runner."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pdf_bench.config import (
    BenchmarkConfig,
    DocumentFilter,
    MetricConfig,
    OutputConfig,
    ParserConfig,
)
from pdf_bench.loader import DocumentInfo, LoadedConfig
from pdf_bench.runner import BenchmarkResults, BenchmarkRunner, DocumentResult
from pdf_bench.systems import BaseParser
from pdf_bench.utils.metadata import DocumentMetadata


class MockParser(BaseParser):
    """Mock parser for testing."""

    def __init__(
        self,
        name: str,
        should_fail: bool = False,
        output_content: str = "# Test Output",
    ) -> None:
        self._name = name
        self._should_fail = should_fail
        self._output_content = output_content

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "1.0.0"

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        """Mock parse that writes test content."""
        if self._should_fail:
            raise RuntimeError(f"Parser {self._name} failed")

        # Write mock output
        output_path = output_dir / f"{pdf_path.stem}_{self._name}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._output_content, encoding="utf-8")
        return output_path


@pytest.fixture
def sample_metadata() -> DocumentMetadata:
    """Sample document metadata."""
    return DocumentMetadata(
        doc_id="test-doc-001",
        source_url="https://example.com/test.pdf",
        corpus="synthetic",
        domain="pandoc",
        title="Test Document",
        features=["text"],
    )


@pytest.fixture
def sample_document(tmp_path: Path, sample_metadata: DocumentMetadata) -> DocumentInfo:
    """Create a sample document with PDF and ground truth."""
    # Create dummy PDF
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy pdf", encoding="utf-8")

    # Create ground truth markdown
    gt_path = tmp_path / "test.md"
    gt_content = "# Test Document\n\nThis is a test."
    gt_path.write_text(gt_content, encoding="utf-8")

    return DocumentInfo(
        doc_id="test-doc-001",
        input_path=pdf_path,
        ground_truth_path=gt_path,
        metadata=sample_metadata,
    )


@pytest.fixture
def sample_config(tmp_path: Path, sample_document: DocumentInfo) -> LoadedConfig:
    """Create a sample loaded configuration."""
    config = BenchmarkConfig(
        name="Test Benchmark",
        description="Test configuration",
        corpus_dir=str(tmp_path),
        document_filter=DocumentFilter(),
        parser_config=ParserConfig(parsers=[]),
        metric_config=MetricConfig(metrics=["edit_similarity", "chrf++"]),
        output_config=OutputConfig(results_dir="results"),
    )

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    return LoadedConfig(
        config=config,
        documents=[sample_document],
        parser_instances=[MockParser("mock_parser")],
        results_dir=results_dir,
    )


class TestDocumentResult:
    """Tests for DocumentResult dataclass."""

    def test_successful_result(self) -> None:
        """Test creating a successful result."""
        result = DocumentResult(
            document_id="doc-001",
            parser_name="test_parser",
            success=True,
            metrics={"edit_similarity": 0.95},
            parse_time_seconds=1.5,
        )

        assert result.document_id == "doc-001"
        assert result.parser_name == "test_parser"
        assert result.success is True
        assert result.metrics["edit_similarity"] == 0.95
        assert result.parse_time_seconds == 1.5
        assert result.error is None

    def test_failed_result(self) -> None:
        """Test creating a failed result."""
        result = DocumentResult(
            document_id="doc-001",
            parser_name="test_parser",
            success=False,
            metrics={},
            error="Parser crashed",
        )

        assert result.success is False
        assert result.metrics == {}
        assert result.error == "Parser crashed"


class TestBenchmarkResults:
    """Tests for BenchmarkResults dataclass."""

    def test_empty_results(self) -> None:
        """Test creating empty results."""
        results = BenchmarkResults(
            benchmark_name="Test",
            timestamp="2025-01-01T00:00:00Z",
        )

        assert results.benchmark_name == "Test"
        assert results.timestamp == "2025-01-01T00:00:00Z"
        assert results.results == []
        assert results.total_documents == 0
        assert results.total_parsers == 0
        assert results.success_count == 0
        assert results.failure_count == 0

    def test_results_with_data(self) -> None:
        """Test results with data."""
        doc_result = DocumentResult(
            document_id="doc-001",
            parser_name="test",
            success=True,
            metrics={"edit_similarity": 0.95},
        )

        results = BenchmarkResults(
            benchmark_name="Test",
            timestamp="2025-01-01T00:00:00Z",
            results=[doc_result],
            total_documents=5,
            total_parsers=3,
            success_count=14,
            failure_count=1,
        )

        assert len(results.results) == 1
        assert results.total_documents == 5
        assert results.total_parsers == 3
        assert results.success_count == 14
        assert results.failure_count == 1


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner."""

    def test_init(self, sample_config: LoadedConfig) -> None:
        """Test runner initialization."""
        runner = BenchmarkRunner(sample_config)
        assert runner.config == sample_config

    def test_run_single_success(self, sample_config: LoadedConfig) -> None:
        """Test successful single parser/document run."""
        runner = BenchmarkRunner(sample_config)
        parser = sample_config.parser_instances[0]
        doc = sample_config.documents[0]

        result = runner._run_single(parser, doc)

        assert result.success is True
        assert result.document_id == doc.doc_id
        assert result.parser_name == parser.name
        assert result.error is None
        assert result.parse_time_seconds > 0
        assert "edit_similarity" in result.metrics
        assert "chrf++" in result.metrics

    def test_run_single_parser_failure(self, sample_config: LoadedConfig) -> None:
        """Test handling of parser failure."""
        # Create failing parser
        failing_parser = MockParser("failing_parser", should_fail=True)
        sample_config.parser_instances = [failing_parser]

        runner = BenchmarkRunner(sample_config)
        doc = sample_config.documents[0]

        result = runner._run_single(failing_parser, doc)

        assert result.success is False
        assert result.error is not None
        assert "failed" in result.error.lower()
        assert result.metrics == {}

    def test_run_single_metric_computation(self, sample_config: LoadedConfig) -> None:
        """Test metric computation for different outputs."""
        # Create parser that outputs identical content to ground truth
        gt_content = sample_config.documents[0].ground_truth_path.read_text()
        identical_parser = MockParser("identical", output_content=gt_content)
        sample_config.parser_instances = [identical_parser]

        runner = BenchmarkRunner(sample_config)
        doc = sample_config.documents[0]

        result = runner._run_single(identical_parser, doc)

        assert result.success is True
        # Identical content should have high similarity
        assert result.metrics["edit_similarity"] == pytest.approx(1.0)

    def test_run_complete_benchmark(self, sample_config: LoadedConfig) -> None:
        """Test running complete benchmark."""
        runner = BenchmarkRunner(sample_config)
        results = runner.run()

        assert results.benchmark_name == sample_config.config.name
        assert results.timestamp is not None
        assert results.total_documents == len(sample_config.documents)
        assert results.total_parsers == len(sample_config.parser_instances)
        assert len(results.results) == (results.total_documents * results.total_parsers)
        assert results.success_count + results.failure_count == len(results.results)

    def test_run_multiple_parsers_and_documents(
        self, tmp_path: Path, sample_metadata: DocumentMetadata
    ) -> None:
        """Test running with multiple parsers and documents."""
        # Create multiple documents
        docs = []
        for i in range(3):
            pdf_path = tmp_path / f"test_{i}.pdf"
            pdf_path.write_text(f"dummy pdf {i}", encoding="utf-8")

            gt_path = tmp_path / f"test_{i}.md"
            gt_path.write_text(f"# Test {i}\n\nContent {i}", encoding="utf-8")

            docs.append(
                DocumentInfo(
                    doc_id=f"test-doc-{i:03d}",
                    input_path=pdf_path,
                    ground_truth_path=gt_path,
                    metadata=sample_metadata,
                )
            )

        # Create multiple parsers
        parsers = [
            MockParser("parser_1", output_content="# Test\n\nParser 1 output"),
            MockParser("parser_2", output_content="# Test\n\nParser 2 output"),
        ]

        config = LoadedConfig(
            config=BenchmarkConfig(
                name="Multi Test",
                description="Multiple parsers and documents",
                corpus_dir=str(tmp_path),
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=[]),
                metric_config=MetricConfig(metrics=["edit_similarity"]),
                output_config=OutputConfig(results_dir="results"),
            ),
            documents=docs,
            parser_instances=parsers,
            results_dir=tmp_path / "results",
        )

        runner = BenchmarkRunner(config)
        results = runner.run()

        # Should have 3 documents * 2 parsers = 6 results
        assert len(results.results) == 6
        assert results.total_documents == 3
        assert results.total_parsers == 2

        # Verify all combinations present
        doc_parser_combos = {(r.document_id, r.parser_name) for r in results.results}
        assert len(doc_parser_combos) == 6  # All unique

    def test_run_with_mixed_success_failure(
        self, tmp_path: Path, sample_document: DocumentInfo
    ) -> None:
        """Test running with some parsers succeeding and some failing."""
        parsers = [
            MockParser("success_1", should_fail=False),
            MockParser("failure_1", should_fail=True),
            MockParser("success_2", should_fail=False),
        ]

        config = LoadedConfig(
            config=BenchmarkConfig(
                name="Mixed Test",
                description="Mixed success/failure",
                corpus_dir=str(tmp_path),
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=[]),
                metric_config=MetricConfig(metrics=["edit_similarity"]),
                output_config=OutputConfig(results_dir="results"),
            ),
            documents=[sample_document],
            parser_instances=parsers,
            results_dir=tmp_path / "results",
        )

        runner = BenchmarkRunner(config)
        results = runner.run()

        assert len(results.results) == 3
        assert results.success_count == 2
        assert results.failure_count == 1

        # Check individual results
        for result in results.results:
            if "failure" in result.parser_name:
                assert result.success is False
                assert result.error is not None
            else:
                assert result.success is True
                assert result.error is None

    def test_compute_metrics_all_configured(self, sample_config: LoadedConfig) -> None:
        """Test computing all configured metrics."""
        runner = BenchmarkRunner(sample_config)

        gt = "# Test\n\nSome content"
        pred = "# Test\n\nSome content"

        metrics = runner._compute_metrics(gt, pred)

        # Should have all configured metrics
        assert "edit_similarity" in metrics
        assert "chrf++" in metrics

        # Identical strings should have high scores
        assert metrics["edit_similarity"] == pytest.approx(1.0)

    def test_compute_metrics_unknown_metric_skipped(self, sample_config: LoadedConfig) -> None:
        """Test that unknown metrics are skipped gracefully."""
        # Add unknown metric to config
        sample_config.config.metric_config.metrics.append("unknown_metric_xyz")

        runner = BenchmarkRunner(sample_config)
        gt = "# Test"
        pred = "# Test"

        metrics = runner._compute_metrics(gt, pred)

        # Should compute known metrics
        assert "edit_similarity" in metrics
        assert "chrf++" in metrics

        # Unknown metric should not be present (skipped)
        assert "unknown_metric_xyz" not in metrics

    def test_element_f1_does_not_mark_valid_markdown_as_missing(
        self, sample_config: LoadedConfig
    ) -> None:
        # Configure element_f1 metric
        sample_config.config.metric_config.metrics = ["element_f1"]

        runner = BenchmarkRunner(sample_config)
        gt = "# Heading\n\nParagraph"
        pred = "# Heading\n\nParagraph"

        metrics = runner._compute_metrics(gt, pred)

        assert "element_f1" in metrics
        assert metrics["element_f1"] == pytest.approx(1.0)
        missing_heading = runner._compute_metrics(gt, "Paragraph")
        assert missing_heading["element_f1"] < metrics["element_f1"]

    def test_compute_metrics_failure_handled(self, sample_config: LoadedConfig) -> None:
        """Test that metric computation failures are handled gracefully."""
        runner = BenchmarkRunner(sample_config)

        # Patch the metric function in the METRIC_FUNCTIONS dict
        with patch.dict(
            "pdf_bench.runner.METRIC_FUNCTIONS",
            {"edit_similarity": Mock(side_effect=RuntimeError("Metric error"))},
        ):
            metrics = runner._compute_metrics("gt", "pred")

            # Should mark failed metric as NaN
            assert "edit_similarity" in metrics
            assert str(metrics["edit_similarity"]) == "nan"

    def test_results_directory_created(self, sample_config: LoadedConfig) -> None:
        """Test that parser outputs are written to results directory."""
        runner = BenchmarkRunner(sample_config)
        runner.run()

        # Check that output files were created in results directory
        assert sample_config.results_dir.exists()
        assert any(sample_config.results_dir.iterdir())  # Has files

    def test_parse_time_recorded(self, sample_config: LoadedConfig) -> None:
        """Test that parse time is recorded."""
        runner = BenchmarkRunner(sample_config)
        results = runner.run()

        # All successful results should have parse time > 0
        for result in results.results:
            if result.success:
                assert result.parse_time_seconds >= 0


class TestParallelExecution:
    """Tests for parallel execution functionality."""

    def test_init_with_default_workers(self, sample_config: LoadedConfig) -> None:
        """Test runner initialization with default (auto) workers."""
        runner = BenchmarkRunner(sample_config)
        # Should auto-detect CPU count, capped at 8
        assert runner.workers >= 1
        assert runner.workers <= 8

    def test_init_with_sequential(self, sample_config: LoadedConfig) -> None:
        """Test runner initialization for sequential execution."""
        runner = BenchmarkRunner(sample_config, parallel_workers=1)
        assert runner.workers == 1

    def test_init_with_specific_workers(self, sample_config: LoadedConfig) -> None:
        """Test runner initialization with specific worker count."""
        runner = BenchmarkRunner(sample_config, parallel_workers=4)
        assert runner.workers == 4

    def test_init_with_zero_workers(self, sample_config: LoadedConfig) -> None:
        """Test runner initialization with 0 (auto) workers."""
        runner = BenchmarkRunner(sample_config, parallel_workers=0)
        assert runner.workers >= 1

    def test_sequential_execution_with_progress(self, sample_config: LoadedConfig) -> None:
        """Test sequential execution (should work same as before)."""
        runner = BenchmarkRunner(sample_config, parallel_workers=1)
        results = runner.run()

        # Should have same number of results
        assert len(results.results) == (
            len(sample_config.documents) * len(sample_config.parser_instances)
        )
        assert results.success_count + results.failure_count == len(results.results)

    def test_parallel_execution(self, tmp_path: Path, sample_metadata: DocumentMetadata) -> None:
        """Test parallel execution with multiple workers."""
        # Create multiple documents for testing parallel execution
        docs = []
        for i in range(4):
            pdf_path = tmp_path / f"test_{i}.pdf"
            pdf_path.write_text(f"dummy pdf {i}", encoding="utf-8")

            gt_path = tmp_path / f"test_{i}.md"
            gt_path.write_text(f"# Test {i}\n\nContent {i}", encoding="utf-8")

            docs.append(
                DocumentInfo(
                    doc_id=f"test-doc-{i:03d}",
                    input_path=pdf_path,
                    ground_truth_path=gt_path,
                    metadata=sample_metadata,
                )
            )

        # Create config with multiple documents
        config = LoadedConfig(
            config=BenchmarkConfig(
                name="Parallel Test",
                description="Test parallel execution",
                corpus_dir=str(tmp_path),
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=[]),
                metric_config=MetricConfig(metrics=["edit_similarity"]),
                output_config=OutputConfig(results_dir="results"),
            ),
            documents=docs,
            parser_instances=[MockParser("parser_1")],
            results_dir=tmp_path / "results",
        )

        # Run with 2 workers
        runner = BenchmarkRunner(config, parallel_workers=2)
        results = runner.run()

        # Should have 4 results (4 docs × 1 parser)
        assert len(results.results) == 4
        assert results.success_count == 4
        assert results.failure_count == 0

        # All results should have metrics
        for result in results.results:
            assert result.success
            assert "edit_similarity" in result.metrics

    def test_parallel_execution_with_failures(
        self, tmp_path: Path, sample_metadata: DocumentMetadata
    ) -> None:
        """Test parallel execution handles failures correctly."""
        # Create documents
        docs = []
        for i in range(3):
            pdf_path = tmp_path / f"test_{i}.pdf"
            pdf_path.write_text(f"dummy pdf {i}", encoding="utf-8")

            gt_path = tmp_path / f"test_{i}.md"
            gt_path.write_text(f"# Test {i}", encoding="utf-8")

            docs.append(
                DocumentInfo(
                    doc_id=f"test-doc-{i:03d}",
                    input_path=pdf_path,
                    ground_truth_path=gt_path,
                    metadata=sample_metadata,
                )
            )

        # Mix of successful and failing parsers
        parsers = [
            MockParser("success", should_fail=False),
            MockParser("failure", should_fail=True),
        ]

        config = LoadedConfig(
            config=BenchmarkConfig(
                name="Failure Test",
                description="Test failure handling",
                corpus_dir=str(tmp_path),
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=[]),
                metric_config=MetricConfig(metrics=["edit_similarity"]),
                output_config=OutputConfig(results_dir="results"),
            ),
            documents=docs,
            parser_instances=parsers,
            results_dir=tmp_path / "results",
        )

        # Run with parallel workers
        runner = BenchmarkRunner(config, parallel_workers=2)
        results = runner.run()

        # Should have 6 results (3 docs × 2 parsers)
        assert len(results.results) == 6

        # Should have mix of successes and failures
        assert results.success_count == 3  # success parser on 3 docs
        assert results.failure_count == 3  # failure parser on 3 docs

        # Check that failures have error messages
        for result in results.results:
            if not result.success:
                assert result.error is not None
                assert "failed" in result.error.lower()
