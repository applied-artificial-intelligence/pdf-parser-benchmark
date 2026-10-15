"""Result persistence for PDF-Bench benchmark results."""

import json
import math
import os
import platform
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pdf_bench.runner import BenchmarkResults, DocumentResult


@dataclass
class EnvironmentInfo:
    """System and environment information for reproducibility."""

    python_version: str
    platform: str
    parser_versions: dict[str, str]


def _serialize_metrics(metrics: dict[str, float]) -> dict[str, float | None]:
    """
    Convert metrics dict, handling NaN values by converting to None.

    Args:
        metrics: Dictionary of metric name -> float value (may contain NaN or None)

    Returns:
        Dictionary with NaN values converted to None for JSON serialization
    """
    result: dict[str, float | None] = {}
    for key, value in metrics.items():
        # Handle None values (shouldn't happen but be defensive)
        if value is None:
            result[key] = None
        # Handle NaN values
        elif isinstance(value, float) and not math.isfinite(value):
            result[key] = None
        else:
            result[key] = value
    return result


def write_json_atomic(output_path: Path, payload: dict[str, Any]) -> None:
    """Validate before writing and replace only after a complete temporary-file write."""
    serialized = json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _deserialize_metrics(metrics: dict[str, float | None]) -> dict[str, float]:
    """
    Convert metrics dict, handling None values by converting to NaN.

    Args:
        metrics: Dictionary of metric name -> float | None (from JSON)

    Returns:
        Dictionary with None values converted back to NaN
    """
    return {key: (float("nan") if value is None else value) for key, value in metrics.items()}


def save_results(
    results: BenchmarkResults,
    output_path: Path,
    config_file: str | None = None,
    parser_versions: dict[str, str] | None = None,
) -> None:
    """
    Save benchmark results to JSON file.

    Args:
        results: Benchmark results to save
        output_path: Path to save JSON file
        config_file: Optional path to config file used
        parser_versions: Optional dict of parser name -> version
    """
    # Prepare environment info
    python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    env_info = {
        "python_version": python_ver,
        "platform": platform.platform(),
        "parser_versions": parser_versions or {},
    }

    # Serialize results
    serialized_results = []
    for result in results.results:
        serialized_result = {
            "document_id": result.document_id,
            "parser_name": result.parser_name,
            "success": result.success,
            "metrics": _serialize_metrics(result.metrics),
            "error": result.error,
            "parse_time_seconds": result.parse_time_seconds,
        }
        serialized_results.append(serialized_result)

    # Create complete output structure
    output_data = {
        "benchmark": {
            "name": results.benchmark_name,
            "timestamp": results.timestamp,
            "config_file": config_file,
        },
        "environment": env_info,
        "results": serialized_results,
        "summary": {
            "total_documents": results.total_documents,
            "total_parsers": results.total_parsers,
            "total_results": len(results.results),
            "success_count": results.success_count,
            "failure_count": results.failure_count,
        },
    }

    write_json_atomic(output_path, output_data)


def load_results(input_path: Path) -> BenchmarkResults:
    """
    Load benchmark results from JSON file.

    Args:
        input_path: Path to JSON file

    Returns:
        BenchmarkResults object reconstructed from JSON

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        KeyError: If required fields are missing
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    # Extract benchmark info
    benchmark_info = data["benchmark"]

    # Deserialize results
    document_results = []
    for result_data in data["results"]:
        doc_result = DocumentResult(
            document_id=result_data["document_id"],
            parser_name=result_data["parser_name"],
            success=result_data["success"],
            metrics=_deserialize_metrics(result_data["metrics"]),
            error=result_data.get("error"),
            parse_time_seconds=result_data.get("parse_time_seconds", 0.0),
        )
        document_results.append(doc_result)

    # Extract summary info
    summary = data["summary"]

    # Reconstruct BenchmarkResults
    return BenchmarkResults(
        benchmark_name=benchmark_info["name"],
        timestamp=benchmark_info["timestamp"],
        results=document_results,
        total_documents=summary["total_documents"],
        total_parsers=summary["total_parsers"],
        success_count=summary["success_count"],
        failure_count=summary["failure_count"],
    )
