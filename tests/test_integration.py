"""End-to-End Integration Tests for PDF-Bench.

This module tests the complete benchmark workflow:
1. Load configuration
2. Run benchmark
3. Save results to JSON
4. Load results back
5. Generate HTML report

These tests verify that all components work together correctly.
"""

import json
from pathlib import Path

import pytest

from pdf_bench.loader import load_benchmark_config
from pdf_bench.persistence import load_results, save_results
from pdf_bench.report_generator import generate_html_report
from pdf_bench.runner import BenchmarkRunner


class TestQuickBenchmarkWorkflow:
    """Test complete workflow with quick_test.yaml (fast execution)."""

    def test_complete_workflow(self, tmp_path: Path) -> None:
        """Test full workflow: config → run → save → load → report."""
        # Step 1: Load configuration
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("quick_test.yaml not found")

        config = load_benchmark_config(config_path)

        # Verify config loaded correctly
        assert config.config.name == "Quick Test Benchmark"
        assert len(config.parser_instances) >= 1  # At least one parser
        assert len(config.documents) >= 1  # At least one document

        # Step 2: Run benchmark
        runner = BenchmarkRunner(config, parallel_workers=1)
        results = runner.run()

        # Verify results structure
        assert results.benchmark_name == "Quick Test Benchmark"
        assert results.timestamp is not None
        assert len(results.results) > 0
        assert results.total_documents == len(config.documents)
        assert results.total_parsers == len(config.parser_instances)

        # Verify at least some results succeeded
        assert results.success_count > 0

        # Verify each result has expected structure
        for result in results.results:
            assert result.document_id is not None
            assert result.parser_name is not None
            assert isinstance(result.success, bool)
            assert isinstance(result.metrics, dict)
            assert result.parse_time_seconds >= 0

            # If successful, should have metrics
            if result.success:
                assert len(result.metrics) > 0

        # Step 3: Save results to JSON
        results_path = tmp_path / "quick_test_results.json"
        save_results(
            results,
            results_path,
            config_file=str(config_path),
            parser_versions={parser.name: parser.version for parser in config.parser_instances},
        )

        # Verify JSON file was created
        assert results_path.exists()
        assert results_path.stat().st_size > 0

        # Verify JSON is valid
        with open(results_path, encoding="utf-8") as f:
            data = json.load(f)

        # Verify JSON structure
        assert "benchmark" in data
        assert data["benchmark"]["name"] == "Quick Test Benchmark"
        assert data["benchmark"]["config_file"] == str(config_path)

        assert "environment" in data
        assert "python_version" in data["environment"]
        assert "platform" in data["environment"]
        assert "parser_versions" in data["environment"]

        assert "results" in data
        assert len(data["results"]) == len(results.results)

        assert "summary" in data
        assert data["summary"]["total_documents"] == results.total_documents
        assert data["summary"]["total_parsers"] == results.total_parsers
        assert data["summary"]["success_count"] == results.success_count

        # Step 4: Load results back
        loaded_results = load_results(results_path)

        # Verify round-trip equality
        assert loaded_results.benchmark_name == results.benchmark_name
        assert loaded_results.timestamp == results.timestamp
        assert len(loaded_results.results) == len(results.results)
        assert loaded_results.total_documents == results.total_documents
        assert loaded_results.total_parsers == results.total_parsers
        assert loaded_results.success_count == results.success_count
        assert loaded_results.failure_count == results.failure_count

        # Verify individual results match
        for original, loaded in zip(results.results, loaded_results.results, strict=True):
            assert loaded.document_id == original.document_id
            assert loaded.parser_name == original.parser_name
            assert loaded.success == original.success
            assert loaded.error == original.error

            # Verify metrics match (including NaN handling)
            assert set(loaded.metrics.keys()) == set(original.metrics.keys())
            for metric_name in original.metrics:
                orig_val = original.metrics[metric_name]
                loaded_val = loaded.metrics[metric_name]

                # Handle NaN comparison
                import math

                if math.isnan(orig_val):
                    assert math.isnan(loaded_val)
                else:
                    assert loaded_val == orig_val

        # Step 5: Generate HTML report
        report_path = tmp_path / "quick_test_report.html"
        generate_html_report(loaded_results, report_path, config_file=str(config_path))

        # Verify HTML report was created
        assert report_path.exists()
        assert report_path.stat().st_size > 0

        # Verify HTML contains expected sections
        html_content = report_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html_content
        assert "Quick Test Benchmark" in html_content
        assert "Leaderboard" in html_content
        assert "Metric Breakdown" in html_content

        # Verify report contains parser names
        for parser in config.parser_instances:
            assert parser.name in html_content

    def test_workflow_with_parallel_execution(self, tmp_path: Path) -> None:
        """Test workflow with parallel execution enabled."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("quick_test.yaml not found")

        config = load_benchmark_config(config_path)

        # Run with 2 parallel workers
        runner = BenchmarkRunner(config, parallel_workers=2)
        results = runner.run()

        # Verify results structure (same as sequential)
        assert results.benchmark_name == "Quick Test Benchmark"
        assert len(results.results) > 0

        # Save and verify
        results_path = tmp_path / "parallel_results.json"
        save_results(results, results_path)
        assert results_path.exists()

        # Load back and verify
        loaded_results = load_results(results_path)
        assert len(loaded_results.results) == len(results.results)

    def test_workflow_with_charts_enabled(self, tmp_path: Path) -> None:
        """Test report generation with chart placeholders."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("quick_test.yaml not found")

        config = load_benchmark_config(config_path)
        runner = BenchmarkRunner(config, parallel_workers=1)
        results = runner.run()

        # Generate report with charts enabled
        report_path = tmp_path / "report_with_charts.html"
        generate_html_report(
            results, report_path, config_file=str(config_path), include_charts=True
        )

        # Verify HTML was created
        assert report_path.exists()

        # Charts section should be present (even if placeholder)
        html_content = report_path.read_text(encoding="utf-8")
        assert "chart" in html_content.lower() or "visualization" in html_content.lower()


class TestMVPBenchmarkWorkflow:
    """Test complete workflow with mvp_all.yaml (comprehensive but slower)."""

    @pytest.mark.slow
    def test_complete_mvp_workflow(self, tmp_path: Path) -> None:
        """Test full workflow with mvp_all.yaml configuration.

        This test is marked as slow and may take several minutes to complete.
        It tests all parsers on all documents with all metrics.
        """
        config_path = Path("benchmarks/mvp_all.yaml")
        if not config_path.exists():
            pytest.skip("mvp_all.yaml not found")

        # Load configuration
        config = load_benchmark_config(config_path)

        # Run benchmark (may take a while)
        runner = BenchmarkRunner(config, parallel_workers=2)
        results = runner.run()

        # Verify comprehensive results
        assert results.benchmark_name is not None
        assert len(results.results) > 0

        # Should have multiple parsers × multiple documents
        expected_results = len(config.parser_instances) * len(config.documents)
        assert len(results.results) == expected_results

        # Save results
        results_path = tmp_path / "mvp_results.json"
        save_results(results, results_path, config_file=str(config_path))

        # Verify JSON is valid and complete
        with open(results_path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["results"]) == expected_results

        # Load back and verify
        loaded_results = load_results(results_path)
        assert len(loaded_results.results) == expected_results

        # Generate HTML report
        report_path = tmp_path / "mvp_report.html"
        generate_html_report(loaded_results, report_path)

        # Verify report is comprehensive
        assert report_path.exists()
        html_size = report_path.stat().st_size
        assert html_size > 10_000  # Should be substantial HTML


class TestErrorHandling:
    """Test error handling in integration workflow."""

    def test_save_and_load_with_failures(self, tmp_path: Path) -> None:
        """Test that failed parser runs are properly persisted and loaded."""
        from pdf_bench.runner import BenchmarkResults, DocumentResult

        # Create results with both successes and failures
        results = BenchmarkResults(
            benchmark_name="Test Benchmark",
            timestamp="2025-01-01T00:00:00Z",
            total_documents=2,
            total_parsers=1,
            success_count=1,
            failure_count=1,
        )

        # Add successful result
        results.results.append(
            DocumentResult(
                document_id="doc1",
                parser_name="test_parser",
                success=True,
                metrics={"metric1": 0.95, "metric2": 0.87},
                parse_time_seconds=1.5,
            )
        )

        # Add failed result
        results.results.append(
            DocumentResult(
                document_id="doc2",
                parser_name="test_parser",
                success=False,
                metrics={},
                error="Test error message",
                parse_time_seconds=0.0,
            )
        )

        # Save and load
        results_path = tmp_path / "mixed_results.json"
        save_results(results, results_path)

        loaded_results = load_results(results_path)

        # Verify both results loaded correctly
        assert len(loaded_results.results) == 2
        assert loaded_results.success_count == 1
        assert loaded_results.failure_count == 1

        # Verify failed result preserved error message
        failed_result = [r for r in loaded_results.results if not r.success][0]
        assert failed_result.error == "Test error message"

    def test_report_generation_with_empty_results(self, tmp_path: Path) -> None:
        """Test that report generation fails gracefully on empty results."""
        from pdf_bench.runner import BenchmarkResults

        # Create empty results
        results = BenchmarkResults(
            benchmark_name="Empty Benchmark",
            timestamp="2025-01-01T00:00:00Z",
            total_documents=0,
            total_parsers=0,
        )

        # Should raise ValueError
        report_path = tmp_path / "empty_report.html"
        with pytest.raises(ValueError, match="empty results"):
            generate_html_report(results, report_path)

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test loading from invalid JSON file."""
        # Create invalid JSON file
        invalid_path = tmp_path / "invalid.json"
        invalid_path.write_text("not valid json{]", encoding="utf-8")

        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            load_results(invalid_path)

    def test_load_missing_file(self, tmp_path: Path) -> None:
        """Test loading from non-existent file."""
        missing_path = tmp_path / "missing.json"

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            load_results(missing_path)


class TestNaNHandling:
    """Test that NaN values are properly handled throughout workflow."""

    def test_nan_in_metrics_roundtrip(self, tmp_path: Path) -> None:
        """Test that NaN metric values survive save/load roundtrip."""
        from pdf_bench.runner import BenchmarkResults, DocumentResult

        # Create results with NaN metrics
        results = BenchmarkResults(
            benchmark_name="NaN Test",
            timestamp="2025-01-01T00:00:00Z",
            total_documents=1,
            total_parsers=1,
            success_count=1,
            failure_count=0,
        )

        results.results.append(
            DocumentResult(
                document_id="doc1",
                parser_name="test_parser",
                success=True,
                metrics={
                    "normal_metric": 0.95,
                    "nan_metric": float("nan"),
                    "another_normal": 0.87,
                },
                parse_time_seconds=1.0,
            )
        )

        # Save to JSON
        results_path = tmp_path / "nan_results.json"
        save_results(results, results_path)

        # Verify JSON has null instead of NaN
        with open(results_path, encoding="utf-8") as f:
            data = json.load(f)

        metrics = data["results"][0]["metrics"]
        assert metrics["normal_metric"] == 0.95
        assert metrics["nan_metric"] is None  # NaN → null
        assert metrics["another_normal"] == 0.87

        # Load back
        loaded_results = load_results(results_path)

        # Verify NaN restored
        import math

        loaded_metrics = loaded_results.results[0].metrics
        assert loaded_metrics["normal_metric"] == 0.95
        assert math.isnan(loaded_metrics["nan_metric"])  # null → NaN
        assert loaded_metrics["another_normal"] == 0.87


# Test fixtures
@pytest.fixture
def sample_benchmark_dir(tmp_path: Path) -> Path:
    """Create a minimal benchmark directory structure for testing."""
    # Create corpus directory
    corpus_dir = tmp_path / "corpus" / "synthetic"
    corpus_dir.mkdir(parents=True)

    # Create a simple PDF and ground truth (placeholder)
    # Note: These would need to be real files for actual execution
    pdf_path = corpus_dir / "test.pdf"
    gt_path = corpus_dir / "test.md"

    # For unit tests, we can just create empty files
    # Integration tests use real corpus
    pdf_path.touch()
    gt_path.write_text("# Test Document\n\nTest content.", encoding="utf-8")

    return tmp_path
