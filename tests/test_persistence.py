"""Tests for persistence module (result saving and loading)."""

import json
import math
from pathlib import Path

import pytest

from pdf_bench.persistence import (
    _deserialize_metrics,
    _serialize_metrics,
    load_results,
    save_results,
)
from pdf_bench.runner import BenchmarkResults, DocumentResult


class TestMetricsSerialization:
    """Test NaN handling in metrics serialization."""

    def test_serialize_metrics_normal_values(self) -> None:
        """Test serialization of normal float values."""
        metrics = {"edit_similarity": 0.85, "chrf++": 82.5, "tree_similarity": 0.78}
        serialized = _serialize_metrics(metrics)

        assert serialized == {
            "edit_similarity": 0.85,
            "chrf++": 82.5,
            "tree_similarity": 0.78,
        }

    def test_serialize_metrics_with_nan(self) -> None:
        """Test serialization of NaN values (should convert to None)."""
        metrics = {
            "edit_similarity": 0.85,
            "chrf++": float("nan"),
            "tree_similarity": 0.78,
        }
        serialized = _serialize_metrics(metrics)

        assert serialized["edit_similarity"] == 0.85
        assert serialized["chrf++"] is None
        assert serialized["tree_similarity"] == 0.78

    def test_deserialize_metrics_normal_values(self) -> None:
        """Test deserialization of normal float values."""
        metrics = {"edit_similarity": 0.85, "chrf++": 82.5, "tree_similarity": 0.78}
        deserialized = _deserialize_metrics(metrics)

        assert deserialized == {
            "edit_similarity": 0.85,
            "chrf++": 82.5,
            "tree_similarity": 0.78,
        }

    def test_deserialize_metrics_with_none(self) -> None:
        """Test deserialization of None values (should convert to NaN)."""
        metrics = {"edit_similarity": 0.85, "chrf++": None, "tree_similarity": 0.78}
        deserialized = _deserialize_metrics(metrics)

        assert deserialized["edit_similarity"] == 0.85
        assert math.isnan(deserialized["chrf++"])
        assert deserialized["tree_similarity"] == 0.78

    def test_round_trip_with_nan(self) -> None:
        """Test that NaN values survive round-trip serialization."""
        original = {
            "metric1": 1.0,
            "metric2": float("nan"),
            "metric3": 3.0,
        }
        serialized = _serialize_metrics(original)
        deserialized = _deserialize_metrics(serialized)

        assert deserialized["metric1"] == 1.0
        assert math.isnan(deserialized["metric2"])
        assert deserialized["metric3"] == 3.0


class TestSaveResults:
    """Test saving benchmark results to JSON."""

    def test_save_basic_results(self, tmp_path: Path) -> None:
        """Test saving basic benchmark results."""
        results = BenchmarkResults(
            benchmark_name="Test Benchmark",
            timestamp="2025-11-16T03:00:00Z",
            results=[
                DocumentResult(
                    document_id="doc1",
                    parser_name="pymupdf",
                    success=True,
                    metrics={"edit_similarity": 0.85, "chrf++": 82.5},
                    parse_time_seconds=0.5,
                )
            ],
            total_documents=1,
            total_parsers=1,
            success_count=1,
            failure_count=0,
        )

        output_file = tmp_path / "results.json"
        save_results(results, output_file)

        assert output_file.exists()

        # Verify JSON structure
        with open(output_file) as f:
            data = json.load(f)

        assert "benchmark" in data
        assert data["benchmark"]["name"] == "Test Benchmark"
        assert data["benchmark"]["timestamp"] == "2025-11-16T03:00:00Z"
        assert "environment" in data
        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 1

    def test_save_with_metadata(self, tmp_path: Path) -> None:
        """Test saving with config file and parser versions."""
        results = BenchmarkResults(
            benchmark_name="Test Benchmark",
            timestamp="2025-11-16T03:00:00Z",
            results=[],
            total_documents=0,
            total_parsers=0,
            success_count=0,
            failure_count=0,
        )

        output_file = tmp_path / "results.json"
        save_results(
            results,
            output_file,
            config_file="benchmarks/test.yaml",
            parser_versions={"pymupdf": "1.24.0", "marker": "1.10.1"},
        )

        with open(output_file) as f:
            data = json.load(f)

        assert data["benchmark"]["config_file"] == "benchmarks/test.yaml"
        assert data["environment"]["parser_versions"] == {
            "pymupdf": "1.24.0",
            "marker": "1.10.1",
        }

    def test_save_with_nan_metrics(self, tmp_path: Path) -> None:
        """Test saving results with NaN metrics."""
        results = BenchmarkResults(
            benchmark_name="Test Benchmark",
            timestamp="2025-11-16T03:00:00Z",
            results=[
                DocumentResult(
                    document_id="doc1",
                    parser_name="pymupdf",
                    success=True,
                    metrics={
                        "edit_similarity": 0.85,
                        "chrf++": float("nan"),
                        "tree_similarity": 0.78,
                    },
                )
            ],
            total_documents=1,
            total_parsers=1,
            success_count=1,
            failure_count=0,
        )

        output_file = tmp_path / "results.json"
        save_results(results, output_file)

        with open(output_file) as f:
            data = json.load(f)

        # NaN should be serialized as None
        metrics = data["results"][0]["metrics"]
        assert metrics["edit_similarity"] == 0.85
        assert metrics["chrf++"] is None
        assert metrics["tree_similarity"] == 0.78

    def test_save_with_failed_results(self, tmp_path: Path) -> None:
        """Test saving results with errors."""
        results = BenchmarkResults(
            benchmark_name="Test Benchmark",
            timestamp="2025-11-16T03:00:00Z",
            results=[
                DocumentResult(
                    document_id="doc1",
                    parser_name="pymupdf",
                    success=False,
                    metrics={},
                    error="Parser failed with error XYZ",
                    parse_time_seconds=0.1,
                )
            ],
            total_documents=1,
            total_parsers=1,
            success_count=0,
            failure_count=1,
        )

        output_file = tmp_path / "results.json"
        save_results(results, output_file)

        with open(output_file) as f:
            data = json.load(f)

        result = data["results"][0]
        assert result["success"] is False
        assert result["error"] == "Parser failed with error XYZ"
        assert result["metrics"] == {}

    def test_save_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that save_results creates parent directories if needed."""
        output_file = tmp_path / "nested" / "dir" / "results.json"
        results = BenchmarkResults(
            benchmark_name="Test",
            timestamp="2025-11-16T03:00:00Z",
            results=[],
            total_documents=0,
            total_parsers=0,
            success_count=0,
            failure_count=0,
        )

        save_results(results, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_save_empty_results(self, tmp_path: Path) -> None:
        """Test saving empty benchmark results."""
        results = BenchmarkResults(
            benchmark_name="Empty Benchmark",
            timestamp="2025-11-16T03:00:00Z",
            results=[],
            total_documents=0,
            total_parsers=0,
            success_count=0,
            failure_count=0,
        )

        output_file = tmp_path / "empty_results.json"
        save_results(results, output_file)

        with open(output_file) as f:
            data = json.load(f)

        assert data["summary"]["total_results"] == 0
        assert len(data["results"]) == 0


class TestLoadResults:
    """Test loading benchmark results from JSON."""

    def test_load_basic_results(self, tmp_path: Path) -> None:
        """Test loading basic benchmark results."""
        # Create a valid JSON file
        data = {
            "benchmark": {
                "name": "Test Benchmark",
                "timestamp": "2025-11-16T03:00:00Z",
                "config_file": None,
            },
            "environment": {
                "python_version": "3.13.5",
                "platform": "Linux",
                "parser_versions": {},
            },
            "results": [
                {
                    "document_id": "doc1",
                    "parser_name": "pymupdf",
                    "success": True,
                    "metrics": {"edit_similarity": 0.85, "chrf++": 82.5},
                    "error": None,
                    "parse_time_seconds": 0.5,
                }
            ],
            "summary": {
                "total_documents": 1,
                "total_parsers": 1,
                "total_results": 1,
                "success_count": 1,
                "failure_count": 0,
            },
        }

        input_file = tmp_path / "results.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        results = load_results(input_file)

        assert results.benchmark_name == "Test Benchmark"
        assert results.timestamp == "2025-11-16T03:00:00Z"
        assert len(results.results) == 1
        assert results.results[0].document_id == "doc1"
        assert results.results[0].parser_name == "pymupdf"
        assert results.results[0].success is True
        assert results.results[0].metrics["edit_similarity"] == 0.85
        assert results.total_documents == 1
        assert results.success_count == 1

    def test_load_with_nan_metrics(self, tmp_path: Path) -> None:
        """Test loading results with NaN metrics (stored as None)."""
        data = {
            "benchmark": {
                "name": "Test Benchmark",
                "timestamp": "2025-11-16T03:00:00Z",
                "config_file": None,
            },
            "environment": {
                "python_version": "3.13.5",
                "platform": "Linux",
                "parser_versions": {},
            },
            "results": [
                {
                    "document_id": "doc1",
                    "parser_name": "pymupdf",
                    "success": True,
                    "metrics": {
                        "edit_similarity": 0.85,
                        "chrf++": None,
                        "tree_similarity": 0.78,
                    },
                    "error": None,
                    "parse_time_seconds": 0.5,
                }
            ],
            "summary": {
                "total_documents": 1,
                "total_parsers": 1,
                "total_results": 1,
                "success_count": 1,
                "failure_count": 0,
            },
        }

        input_file = tmp_path / "results.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        results = load_results(input_file)

        metrics = results.results[0].metrics
        assert metrics["edit_similarity"] == 0.85
        assert math.isnan(metrics["chrf++"])
        assert metrics["tree_similarity"] == 0.78

    def test_load_with_failed_results(self, tmp_path: Path) -> None:
        """Test loading results with errors."""
        data = {
            "benchmark": {
                "name": "Test Benchmark",
                "timestamp": "2025-11-16T03:00:00Z",
                "config_file": None,
            },
            "environment": {
                "python_version": "3.13.5",
                "platform": "Linux",
                "parser_versions": {},
            },
            "results": [
                {
                    "document_id": "doc1",
                    "parser_name": "pymupdf",
                    "success": False,
                    "metrics": {},
                    "error": "Parser failed",
                    "parse_time_seconds": 0.1,
                }
            ],
            "summary": {
                "total_documents": 1,
                "total_parsers": 1,
                "total_results": 1,
                "success_count": 0,
                "failure_count": 1,
            },
        }

        input_file = tmp_path / "results.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        results = load_results(input_file)

        assert results.results[0].success is False
        assert results.results[0].error == "Parser failed"
        assert results.results[0].metrics == {}

    def test_load_missing_file(self, tmp_path: Path) -> None:
        """Test loading from non-existent file."""
        input_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_results(input_file)

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test loading from invalid JSON file."""
        input_file = tmp_path / "invalid.json"
        with open(input_file, "w") as f:
            f.write("not valid json {]")

        with pytest.raises(json.JSONDecodeError):
            load_results(input_file)

    def test_load_missing_required_fields(self, tmp_path: Path) -> None:
        """Test loading from JSON missing required fields."""
        data = {
            "benchmark": {"name": "Test"},
            # Missing timestamp and other fields
        }

        input_file = tmp_path / "incomplete.json"
        with open(input_file, "w") as f:
            json.dump(data, f)

        with pytest.raises(KeyError):
            load_results(input_file)


class TestRoundTrip:
    """Test round-trip serialization (save then load)."""

    def test_round_trip_basic(self, tmp_path: Path) -> None:
        """Test that results survive round-trip serialization."""
        original = BenchmarkResults(
            benchmark_name="Round Trip Test",
            timestamp="2025-11-16T03:00:00Z",
            results=[
                DocumentResult(
                    document_id="doc1",
                    parser_name="pymupdf",
                    success=True,
                    metrics={"edit_similarity": 0.85, "chrf++": 82.5},
                    parse_time_seconds=0.5,
                ),
                DocumentResult(
                    document_id="doc2",
                    parser_name="marker",
                    success=False,
                    metrics={},
                    error="Parse error",
                    parse_time_seconds=0.1,
                ),
            ],
            total_documents=2,
            total_parsers=2,
            success_count=1,
            failure_count=1,
        )

        output_file = tmp_path / "round_trip.json"
        save_results(original, output_file)
        loaded = load_results(output_file)

        # Compare results
        assert loaded.benchmark_name == original.benchmark_name
        assert loaded.timestamp == original.timestamp
        assert len(loaded.results) == len(original.results)
        assert loaded.total_documents == original.total_documents
        assert loaded.total_parsers == original.total_parsers
        assert loaded.success_count == original.success_count
        assert loaded.failure_count == original.failure_count

        # Compare individual results
        for orig, load in zip(original.results, loaded.results, strict=True):
            assert orig.document_id == load.document_id
            assert orig.parser_name == load.parser_name
            assert orig.success == load.success
            assert orig.metrics == load.metrics
            assert orig.error == load.error
            assert orig.parse_time_seconds == load.parse_time_seconds

    def test_round_trip_with_nan(self, tmp_path: Path) -> None:
        """Test that NaN values survive round-trip."""
        original = BenchmarkResults(
            benchmark_name="NaN Test",
            timestamp="2025-11-16T03:00:00Z",
            results=[
                DocumentResult(
                    document_id="doc1",
                    parser_name="pymupdf",
                    success=True,
                    metrics={
                        "metric1": 1.0,
                        "metric2": float("nan"),
                        "metric3": 3.0,
                    },
                )
            ],
            total_documents=1,
            total_parsers=1,
            success_count=1,
            failure_count=0,
        )

        output_file = tmp_path / "nan_round_trip.json"
        save_results(original, output_file)
        loaded = load_results(output_file)

        metrics = loaded.results[0].metrics
        assert metrics["metric1"] == 1.0
        assert math.isnan(metrics["metric2"])
        assert metrics["metric3"] == 3.0

    def test_round_trip_large_dataset(self, tmp_path: Path) -> None:
        """Test round-trip with many results."""
        results_list = []
        for i in range(100):
            results_list.append(
                DocumentResult(
                    document_id=f"doc{i}",
                    parser_name=f"parser{i % 4}",
                    success=(i % 5 != 0),  # 80% success rate
                    metrics={
                        "metric1": float(i),
                        "metric2": float(i) * 0.5,
                    },
                    error="Error" if (i % 5 == 0) else None,
                    parse_time_seconds=0.1 * i,
                )
            )

        original = BenchmarkResults(
            benchmark_name="Large Dataset",
            timestamp="2025-11-16T03:00:00Z",
            results=results_list,
            total_documents=100,
            total_parsers=4,
            success_count=80,
            failure_count=20,
        )

        output_file = tmp_path / "large_round_trip.json"
        save_results(original, output_file)
        loaded = load_results(output_file)

        assert len(loaded.results) == 100
        assert loaded.success_count == 80
        assert loaded.failure_count == 20

        # Spot check a few results
        assert loaded.results[0].document_id == "doc0"
        assert loaded.results[99].document_id == "doc99"
        assert loaded.results[50].metrics["metric1"] == 50.0
