"""Repository inventory and status classification for PDF-Bench."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from pdf_bench.config import load_config

STATUS_DRAFT = "draft"
STATUS_VALID_INTERNAL = "valid_internal"
STATUS_PUBLISHABLE = "publishable"
STATUS_ARCHIVE_ONLY = "archive_only"
VALID_STATUSES = {
    STATUS_DRAFT,
    STATUS_VALID_INTERNAL,
    STATUS_PUBLISHABLE,
    STATUS_ARCHIVE_ONLY,
}

OPEN_SOURCE_PARSERS = {
    "pdfsmith-pypdf",
    "pdfsmith-pdfplumber",
    "pdfsmith-pymupdf",
    "pdfsmith-pymupdf4llm",
    "pdfsmith-pdfminer",
    "pdfsmith-pypdfium2",
    "pdfsmith-unstructured",
    "pdfsmith-kreuzberg",
    "pdfsmith-extractous",
    "pdfsmith-docling",
    "pdfsmith-marker",
    "tika",
    "marker_ollama",
}

COMMERCIAL_OR_FRONTIER_PARSERS = {
    "pdfsmith-aws_textract",
    "pdfsmith-azure",
    "pdfsmith-google",
    "pdfsmith-databricks",
    "pdfsmith-llamaparse",
    "pdfsmith-anthropic",
    "pdfsmith-anthropic-haiku",
    "pdfsmith-anthropic-sonnet",
    "pdfsmith-anthropic-opus",
    "pdfsmith-openai",
    "pdfsmith-openai-mini",
    "pdfsmith-openai-4o",
    "pdfsmith-openai-5",
    "pdfsmith-gemini",
    "pdfsmith-gemini-flash",
    "pdfsmith-gemini-pro",
    "landing_ai",
}

INPUT_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".webp", ".bmp"}


@dataclass
class InventoryIssue:
    """Issue found while classifying an artifact."""

    code: str
    message: str
    severity: str = "warning"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class CorpusInventoryRecord:
    """Inventory record for one corpus dataset."""

    corpus_id: str
    path: str
    auto_status: str
    status: str
    status_source: str
    input_count: int
    ground_truth_count: int
    metadata_count: int
    declared_document_count: int | None
    description: str | None
    domain: str | None
    source: str | None
    ground_truth_method: str | None
    features: list[str]
    issues: list[InventoryIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "corpus_id": self.corpus_id,
            "path": self.path,
            "auto_status": self.auto_status,
            "status": self.status,
            "status_source": self.status_source,
            "input_count": self.input_count,
            "ground_truth_count": self.ground_truth_count,
            "metadata_count": self.metadata_count,
            "declared_document_count": self.declared_document_count,
            "description": self.description,
            "domain": self.domain,
            "source": self.source,
            "ground_truth_method": self.ground_truth_method,
            "features": self.features,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class BenchmarkInventoryRecord:
    """Inventory record for one benchmark configuration."""

    name: str
    path: str
    auto_status: str
    status: str
    status_source: str
    parser_count: int
    metric_count: int
    declared_document_count: int | None
    corpus_dir: str | None
    corpus_path_exists: bool
    issues: list[InventoryIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "auto_status": self.auto_status,
            "status": self.status,
            "status_source": self.status_source,
            "parser_count": self.parser_count,
            "metric_count": self.metric_count,
            "declared_document_count": self.declared_document_count,
            "corpus_dir": self.corpus_dir,
            "corpus_path_exists": self.corpus_path_exists,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class ResultInventoryRecord:
    """Inventory record for one result artifact."""

    benchmark_name: str
    path: str
    auto_status: str
    status: str
    status_source: str
    config_file: str | None
    config_exists: bool
    total_documents: int | None
    total_parsers: int | None
    total_results: int | None
    success_count: int | None
    failure_count: int | None
    failure_rate: float | None
    summary_consistent: bool | None
    parser_versions_count: int
    parser_names: list[str]
    failed_parser_counts: dict[str, int]
    parsers_failed_all_tasks: list[str]
    cost_class: str
    recognized_schema: bool
    issues: list[InventoryIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "benchmark_name": self.benchmark_name,
            "path": self.path,
            "auto_status": self.auto_status,
            "status": self.status,
            "status_source": self.status_source,
            "config_file": self.config_file,
            "config_exists": self.config_exists,
            "total_documents": self.total_documents,
            "total_parsers": self.total_parsers,
            "total_results": self.total_results,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "failure_rate": self.failure_rate,
            "summary_consistent": self.summary_consistent,
            "parser_versions_count": self.parser_versions_count,
            "parser_names": self.parser_names,
            "failed_parser_counts": self.failed_parser_counts,
            "parsers_failed_all_tasks": self.parsers_failed_all_tasks,
            "cost_class": self.cost_class,
            "recognized_schema": self.recognized_schema,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass
class InventorySnapshot:
    """Complete repository inventory snapshot."""

    repo_root: str
    generated_at: str
    corpora: list[CorpusInventoryRecord]
    benchmarks: list[BenchmarkInventoryRecord]
    results: list[ResultInventoryRecord]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": self.repo_root,
            "generated_at": self.generated_at,
            "corpora": [record.to_dict() for record in self.corpora],
            "benchmarks": [record.to_dict() for record in self.benchmarks],
            "results": [record.to_dict() for record in self.results],
            "summary": self.summary,
        }


def build_inventory(repo_root: Path) -> InventorySnapshot:
    """Build a repository inventory snapshot."""
    root = repo_root.resolve()
    overrides = _load_inventory_overrides(root)
    corpora = discover_corpora(root, overrides.get("corpora", {}))
    benchmarks = discover_benchmarks(root, overrides.get("benchmarks", {}))
    benchmark_statuses = _build_benchmark_status_map(root, benchmarks)
    results = discover_results(root, benchmark_statuses, overrides.get("results", {}))
    summary = _build_summary(corpora, benchmarks, results)
    return InventorySnapshot(
        repo_root=str(root),
        generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        corpora=corpora,
        benchmarks=benchmarks,
        results=results,
        summary=summary,
    )


def save_inventory(snapshot: InventorySnapshot, output_path: Path) -> None:
    """Save an inventory snapshot to JSON."""
    from pdf_bench.persistence import write_json_atomic

    write_json_atomic(output_path, snapshot.to_dict())


def discover_corpora(
    repo_root: Path, status_overrides: dict[str, Any] | None = None
) -> list[CorpusInventoryRecord]:
    """Discover corpus datasets under the repository."""
    corpus_root = repo_root / "corpus"
    if not corpus_root.exists():
        return []

    candidates: set[Path] = set()
    for metadata_file in corpus_root.rglob("corpus_metadata.yaml"):
        candidates.add(metadata_file.parent)

    for path in corpus_root.rglob("*"):
        if not path.is_dir():
            continue
        child_names = {child.name for child in path.iterdir()}
        if {"pdfs", "ground_truth", "metadata"} & child_names:
            candidates.add(path)

    return [
        _build_corpus_record(repo_root, path, status_overrides or {}) for path in sorted(candidates)
    ]


def discover_benchmarks(
    repo_root: Path, status_overrides: dict[str, Any] | None = None
) -> list[BenchmarkInventoryRecord]:
    """Discover benchmark configuration files under the repository."""
    benchmarks_root = repo_root / "benchmarks"
    if not benchmarks_root.exists():
        return []

    records = []
    for path in sorted(benchmarks_root.rglob("*.yaml")):
        records.append(_build_benchmark_record(repo_root, path, status_overrides or {}))
    return records


def discover_results(
    repo_root: Path,
    benchmark_statuses: dict[str, str] | None = None,
    status_overrides: dict[str, Any] | None = None,
) -> list[ResultInventoryRecord]:
    """Discover result JSON artifacts under the repository."""
    results_root = repo_root / "results"
    if not results_root.exists():
        return []

    records = []
    for path in sorted(results_root.rglob("*.json")):
        records.append(
            _build_result_record(
                repo_root,
                path,
                benchmark_statuses or {},
                status_overrides or {},
            )
        )
    return records


def _build_corpus_record(
    repo_root: Path,
    path: Path,
    status_overrides: dict[str, Any],
) -> CorpusInventoryRecord:
    metadata_path = path / "corpus_metadata.yaml"
    metadata = _load_yaml_file(metadata_path) if metadata_path.exists() else {}
    issues: list[InventoryIssue] = []

    input_stems = _collect_input_stems(path)
    ground_truth_stems = _collect_named_stems(path, "ground_truth", {".md"})
    metadata_stems = _collect_metadata_stems(path)

    input_count = len(input_stems)
    ground_truth_count = len(input_stems & ground_truth_stems)
    metadata_count = len(input_stems & metadata_stems)
    declared_document_count = metadata.get("document_count")

    extra_ground_truth = len(ground_truth_stems - input_stems)
    extra_metadata = len(metadata_stems - input_stems)

    if input_count == 0:
        issues.append(
            InventoryIssue("missing_inputs", "No input documents found", severity="error")
        )
    if ground_truth_count == 0:
        issues.append(
            InventoryIssue("missing_ground_truth", "No ground truth files found", severity="error")
        )
    if metadata_count == 0:
        issues.append(
            InventoryIssue(
                "missing_metadata", "No per-document metadata files found", severity="error"
            )
        )
    if declared_document_count is None:
        issues.append(
            InventoryIssue("missing_declared_count", "corpus_metadata.yaml has no document_count")
        )
    if extra_ground_truth > 0:
        issues.append(
            InventoryIssue(
                "extra_ground_truth",
                f"Found {extra_ground_truth} ground-truth files without matching input documents",
            )
        )
    if extra_metadata > 0:
        issues.append(
            InventoryIssue(
                "extra_metadata",
                f"Found {extra_metadata} metadata files without matching input documents",
            )
        )

    counts = [count for count in [input_count, ground_truth_count, metadata_count] if count > 0]
    if len(set(counts)) > 1:
        issues.append(
            InventoryIssue(
                "count_mismatch",
                "Input/ground-truth/metadata counts differ: "
                f"{input_count}/{ground_truth_count}/{metadata_count}",
                severity="error",
            )
        )

    if isinstance(declared_document_count, int) and counts:
        largest_count = max(counts)
        if declared_document_count != largest_count:
            issues.append(
                InventoryIssue(
                    "declared_count_mismatch",
                    "Declared document_count="
                    f"{declared_document_count} but discovered {largest_count} files",
                )
            )

    auto_status = _classify_corpus_status(input_count, ground_truth_count, metadata_count, issues)
    override_value = _artifact_override_value(repo_root, path, status_overrides)
    status, status_source = _resolve_declared_status(
        override_value, metadata.get("inventory_status"), auto_status, issues
    )

    return CorpusInventoryRecord(
        corpus_id=str(path.relative_to(repo_root)),
        path=str(path),
        auto_status=auto_status,
        status=status,
        status_source=status_source,
        input_count=input_count,
        ground_truth_count=ground_truth_count,
        metadata_count=metadata_count,
        declared_document_count=declared_document_count
        if isinstance(declared_document_count, int)
        else None,
        description=metadata.get("description"),
        domain=metadata.get("domain"),
        source=metadata.get("source"),
        ground_truth_method=metadata.get("ground_truth_method"),
        features=_normalize_string_list(metadata.get("features")),
        issues=issues,
    )


def _build_benchmark_record(
    repo_root: Path,
    path: Path,
    status_overrides: dict[str, Any],
) -> BenchmarkInventoryRecord:
    raw_data = _load_yaml_file(path)
    issues: list[InventoryIssue] = []
    is_archived = "archive" in path.parts

    if not isinstance(raw_data, dict):
        raw_data = {}
        issues.append(
            InventoryIssue(
                "invalid_yaml_shape",
                "Benchmark config must contain a YAML object",
                severity="error",
            )
        )

    if "output" in raw_data:
        issues.append(
            InventoryIssue(
                "unsupported_output_key",
                "Uses legacy 'output' key instead of 'output_config'",
                severity="error",
            )
        )
    if "execution" in raw_data:
        issues.append(
            InventoryIssue(
                "unsupported_execution_key",
                "Uses unsupported 'execution' section",
                severity="error",
            )
        )

    try:
        config = load_config(path)
        load_error = None
    except Exception as exc:
        config = None
        load_error = str(exc)
        issues.append(InventoryIssue("config_load_failed", load_error, severity="error"))

    name = raw_data.get("name") if isinstance(raw_data.get("name"), str) else path.stem
    parser_count = 0
    metric_count = 0
    declared_document_count = None
    corpus_dir = raw_data.get("corpus_dir") if isinstance(raw_data.get("corpus_dir"), str) else None
    corpus_path_exists = False

    if isinstance(raw_data.get("parser_config"), dict):
        parser_count = len(_normalize_string_list(raw_data["parser_config"].get("parsers")))
    if isinstance(raw_data.get("metric_config"), dict):
        metric_count = len(_normalize_string_list(raw_data["metric_config"].get("metrics")))
    if isinstance(raw_data.get("document_filter"), dict):
        max_documents = raw_data["document_filter"].get("max_documents")
        include_doc_ids = raw_data["document_filter"].get("include_doc_ids")
        if isinstance(max_documents, int):
            declared_document_count = max_documents
        elif isinstance(include_doc_ids, list):
            declared_document_count = len(include_doc_ids)

    if config is not None:
        corpus_dir = config.corpus_dir

    if corpus_dir:
        corpus_path_exists = (path.parent / corpus_dir).resolve().exists()
        if not corpus_path_exists:
            issues.append(
                InventoryIssue(
                    "missing_corpus_dir",
                    f"Resolved corpus_dir does not exist: {(path.parent / corpus_dir).resolve()}",
                    severity="error",
                )
            )

    if is_archived:
        auto_status = STATUS_ARCHIVE_ONLY
    else:
        auto_status = STATUS_DRAFT if _has_errors(issues) else STATUS_VALID_INTERNAL
    override_value = _artifact_override_value(repo_root, path, status_overrides)
    status, status_source = _resolve_declared_status(
        override_value, raw_data.get("inventory_status"), auto_status, issues
    )

    return BenchmarkInventoryRecord(
        name=name,
        path=str(path),
        auto_status=auto_status,
        status=status,
        status_source=status_source,
        parser_count=parser_count,
        metric_count=metric_count,
        declared_document_count=declared_document_count,
        corpus_dir=corpus_dir,
        corpus_path_exists=corpus_path_exists,
        issues=issues,
    )


def _build_result_record(
    repo_root: Path,
    path: Path,
    benchmark_statuses: dict[str, str],
    status_overrides: dict[str, Any],
) -> ResultInventoryRecord:
    issues: list[InventoryIssue] = []
    is_checkpoint = ".checkpoint." in path.name or path.name.endswith(".checkpoint.json")
    is_archived = "archive" in path.parts

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        issues.append(InventoryIssue("json_decode_failed", str(exc), severity="error"))
        auto_status = STATUS_ARCHIVE_ONLY if is_archived or is_checkpoint else STATUS_DRAFT
        override_value = _artifact_override_value(repo_root, path, status_overrides)
        status, status_source = _resolve_declared_status(override_value, None, auto_status, issues)
        return ResultInventoryRecord(
            benchmark_name=path.stem,
            path=str(path),
            auto_status=auto_status,
            status=status,
            status_source=status_source,
            config_file=None,
            config_exists=False,
            total_documents=None,
            total_parsers=None,
            total_results=None,
            success_count=None,
            failure_count=None,
            failure_rate=None,
            summary_consistent=None,
            parser_versions_count=0,
            parser_names=[],
            failed_parser_counts={},
            parsers_failed_all_tasks=[],
            cost_class="unknown",
            recognized_schema=False,
            issues=issues,
        )

    recognized_schema = isinstance(data, dict) and {"benchmark", "results", "summary"} <= set(
        data.keys()
    )
    benchmark_data = data.get("benchmark", {}) if isinstance(data, dict) else {}
    summary_data = data.get("summary", {}) if isinstance(data, dict) else {}
    environment_data = data.get("environment", {}) if isinstance(data, dict) else {}
    if not isinstance(benchmark_data, dict):
        benchmark_data = {}
    if not isinstance(summary_data, dict):
        summary_data = {}
    if not isinstance(environment_data, dict):
        environment_data = {}
    raw_results = data.get("results") if isinstance(data, dict) else None

    benchmark_name = (
        benchmark_data.get("name") if isinstance(benchmark_data.get("name"), str) else path.stem
    )
    config_file = (
        benchmark_data.get("config_file")
        if isinstance(benchmark_data.get("config_file"), str)
        else None
    )
    config_exists = _config_path_exists(repo_root, config_file)
    benchmark_config_status = _lookup_benchmark_status(repo_root, config_file, benchmark_statuses)
    parser_versions = environment_data.get("parser_versions", {})
    parser_versions_count = len(parser_versions) if isinstance(parser_versions, dict) else 0
    parser_names = _extract_result_parser_names(raw_results)
    cost_class = _classify_cost_class(parser_names or list(parser_versions.keys()))
    failed_parser_counts, parsers_failed_all_tasks = _collect_failed_parser_counts(raw_results)

    if not recognized_schema:
        issues.append(
            InventoryIssue(
                "unrecognized_result_schema",
                "JSON file does not match the benchmark result schema",
                severity="error",
            )
        )
    if is_checkpoint:
        issues.append(
            InventoryIssue(
                "checkpoint_artifact", "Checkpoint artifact should not be treated as canonical"
            )
        )
    if is_archived:
        issues.append(
            InventoryIssue("archived_result", "Archived artifact kept for reference only")
        )
    if not config_file:
        issues.append(
            InventoryIssue(
                "missing_config_file",
                "Result file does not record benchmark config",
                severity="error",
            )
        )
    elif not config_exists:
        issues.append(
            InventoryIssue(
                "missing_config_path",
                f"Referenced config file not found: {config_file}",
                severity="error",
            )
        )
    elif benchmark_config_status == STATUS_ARCHIVE_ONLY:
        issues.append(
            InventoryIssue(
                "benchmark_config_archive_only",
                f"Referenced benchmark config is marked {STATUS_ARCHIVE_ONLY}",
            )
        )
    elif benchmark_config_status == STATUS_DRAFT:
        issues.append(
            InventoryIssue(
                "benchmark_config_draft",
                "Referenced benchmark config is still draft",
                severity="error",
            )
        )
    if parser_versions_count == 0:
        issues.append(
            InventoryIssue(
                "missing_parser_versions", "No parser versions recorded", severity="error"
            )
        )
    if "git_commit" not in environment_data and "commit_sha" not in environment_data:
        issues.append(InventoryIssue("missing_commit_sha", "No commit SHA recorded for this run"))

    failure_count = summary_data.get("failure_count") if isinstance(summary_data, dict) else None
    total_results = summary_data.get("total_results") if isinstance(summary_data, dict) else None
    summary_consistent = _is_result_summary_consistent(summary_data, raw_results)
    if summary_consistent is False:
        issues.append(
            InventoryIssue(
                "summary_count_mismatch",
                "Result summary counts do not match the recorded result rows",
                severity="error",
            )
        )

    failure_rate = None
    if isinstance(failure_count, int) and isinstance(total_results, int) and total_results > 0:
        failure_rate = failure_count / total_results

    if isinstance(failure_count, int) and failure_count > 0:
        issues.append(
            InventoryIssue(
                "run_failures",
                f"Run contains {failure_count} failed parser/document tasks",
                severity="error",
            )
        )
    if parsers_failed_all_tasks:
        issues.append(
            InventoryIssue(
                "parser_failed_all_tasks",
                "Parser(s) failed every attempted task in this run: "
                + ", ".join(parsers_failed_all_tasks),
            )
        )
    if failure_rate is not None and failure_rate >= 0.2:
        issues.append(
            InventoryIssue(
                "high_failure_rate",
                f"Failure rate is {failure_rate:.1%}, which is too high for a canonical run",
            )
        )

    auto_status = _classify_result_status(
        is_checkpoint=is_checkpoint,
        is_archived=is_archived,
        recognized_schema=recognized_schema,
        config_file=config_file,
        config_exists=config_exists,
        benchmark_config_status=benchmark_config_status,
        parser_versions_count=parser_versions_count,
        failure_count=failure_count,
        failure_rate=failure_rate,
        summary_consistent=summary_consistent,
        parsers_failed_all_tasks=parsers_failed_all_tasks,
    )
    inventory_status = data.get("inventory_status") if isinstance(data, dict) else None
    override_value = _artifact_override_value(repo_root, path, status_overrides)
    status, status_source = _resolve_declared_status(
        override_value, inventory_status, auto_status, issues
    )

    return ResultInventoryRecord(
        benchmark_name=benchmark_name,
        path=str(path),
        auto_status=auto_status,
        status=status,
        status_source=status_source,
        config_file=config_file,
        config_exists=config_exists,
        total_documents=summary_data.get("total_documents")
        if isinstance(summary_data, dict)
        else None,
        total_parsers=summary_data.get("total_parsers") if isinstance(summary_data, dict) else None,
        total_results=summary_data.get("total_results") if isinstance(summary_data, dict) else None,
        success_count=summary_data.get("success_count") if isinstance(summary_data, dict) else None,
        failure_count=failure_count,
        failure_rate=failure_rate,
        summary_consistent=summary_consistent,
        parser_versions_count=parser_versions_count,
        parser_names=parser_names,
        failed_parser_counts=failed_parser_counts,
        parsers_failed_all_tasks=parsers_failed_all_tasks,
        cost_class=cost_class,
        recognized_schema=recognized_schema,
        issues=issues,
    )


def _build_summary(
    corpora: list[CorpusInventoryRecord],
    benchmarks: list[BenchmarkInventoryRecord],
    results: list[ResultInventoryRecord],
) -> dict[str, Any]:
    return {
        "corpora": _status_counts(corpora),
        "benchmarks": _status_counts(benchmarks),
        "results": _status_counts(results),
    }


def _status_counts(records: list[Any]) -> dict[str, int]:
    counts = {"total": len(records)}
    for status in VALID_STATUSES:
        counts[status] = sum(1 for record in records if record.status == status)
    return counts


def _has_errors(issues: list[InventoryIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


def _classify_corpus_status(
    input_count: int,
    ground_truth_count: int,
    metadata_count: int,
    issues: list[InventoryIssue],
) -> str:
    if (
        input_count > 0
        and input_count == ground_truth_count == metadata_count
        and not _has_errors(issues)
    ):
        return STATUS_VALID_INTERNAL
    return STATUS_DRAFT


def _classify_result_status(
    *,
    is_checkpoint: bool,
    is_archived: bool,
    recognized_schema: bool,
    config_file: str | None,
    config_exists: bool,
    benchmark_config_status: str | None,
    parser_versions_count: int,
    failure_count: int | None,
    failure_rate: float | None,
    summary_consistent: bool | None,
    parsers_failed_all_tasks: list[str],
) -> str:
    if is_checkpoint or is_archived:
        return STATUS_ARCHIVE_ONLY
    if not recognized_schema:
        return STATUS_DRAFT
    if not config_file or not config_exists:
        return STATUS_DRAFT
    if benchmark_config_status == STATUS_ARCHIVE_ONLY:
        return STATUS_ARCHIVE_ONLY
    if benchmark_config_status == STATUS_DRAFT:
        return STATUS_DRAFT
    if parser_versions_count == 0:
        return STATUS_DRAFT
    if summary_consistent is False:
        return STATUS_ARCHIVE_ONLY
    if parsers_failed_all_tasks:
        return STATUS_ARCHIVE_ONLY
    if failure_rate is not None and failure_rate >= 0.2:
        return STATUS_ARCHIVE_ONLY
    if isinstance(failure_count, int) and failure_count > 0:
        return STATUS_DRAFT
    return STATUS_VALID_INTERNAL


def _resolve_status_override(
    override_value: Any,
    auto_status: str,
    issues: list[InventoryIssue],
) -> tuple[str, str | None]:
    if override_value is None:
        return auto_status, None
    if isinstance(override_value, str) and override_value in VALID_STATUSES:
        return override_value, "declared"
    issues.append(
        InventoryIssue(
            "invalid_inventory_status",
            f"Ignoring invalid inventory_status value: {override_value!r}",
        )
    )
    return auto_status, None


def _resolve_declared_status(
    file_override_value: Any,
    inline_override_value: Any,
    auto_status: str,
    issues: list[InventoryIssue],
) -> tuple[str, str]:
    status, source = _resolve_status_override(file_override_value, auto_status, issues)
    if source:
        return status, "inventory_overrides"
    status, source = _resolve_status_override(inline_override_value, auto_status, issues)
    if source:
        return status, source
    return auto_status, "auto"


def _collect_input_stems(path: Path) -> set[str]:
    stems = {
        file_path.stem for file_path in path.iterdir() if file_path.suffix.lower() in INPUT_SUFFIXES
    }
    inputs_dir = path / "pdfs"
    if inputs_dir.exists():
        stems |= {
            file_path.stem
            for file_path in inputs_dir.iterdir()
            if file_path.suffix.lower() in INPUT_SUFFIXES
        }
    return stems


def _collect_named_stems(path: Path, subdir_name: str, suffixes: set[str]) -> set[str]:
    stems = {file_path.stem for file_path in path.iterdir() if file_path.suffix.lower() in suffixes}
    target_dir = path / subdir_name
    if target_dir.exists():
        stems |= {
            file_path.stem
            for file_path in target_dir.iterdir()
            if file_path.suffix.lower() in suffixes
        }
    return stems


def _collect_metadata_stems(path: Path) -> set[str]:
    ignored_names = {"targets.yaml", "schema.yaml", "corpus_metadata.yaml"}
    stems = {
        file_path.stem
        for file_path in path.iterdir()
        if file_path.suffix.lower() in {".yaml", ".yml"} and file_path.name not in ignored_names
    }
    target_dir = path / "metadata"
    if target_dir.exists():
        stems |= {
            file_path.stem
            for file_path in target_dir.iterdir()
            if file_path.suffix.lower() in {".yaml", ".yml"} and file_path.name not in ignored_names
        }
    return stems


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _load_yaml_file(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _load_inventory_overrides(repo_root: Path) -> dict[str, dict[str, Any]]:
    path = repo_root / "inventory_overrides.yaml"
    if not path.exists():
        return {"corpora": {}, "benchmarks": {}, "results": {}}

    data = _load_yaml_file(path)
    sections: dict[str, dict[str, Any]] = {}
    for section in ["corpora", "benchmarks", "results"]:
        section_data = data.get(section)
        sections[section] = section_data if isinstance(section_data, dict) else {}
    return sections


def _artifact_override_value(repo_root: Path, path: Path, status_overrides: dict[str, Any]) -> Any:
    try:
        relative_path = str(path.relative_to(repo_root))
    except ValueError:
        relative_path = str(path)
    override_value = status_overrides.get(relative_path)
    if isinstance(override_value, dict):
        return override_value.get("status")
    return override_value


def _extract_result_parser_names(raw_results: Any) -> list[str]:
    if not isinstance(raw_results, list):
        return []
    parser_names = {
        result.get("parser_name")
        for result in raw_results
        if isinstance(result, dict) and isinstance(result.get("parser_name"), str)
    }
    return sorted(parser_names)


def _collect_failed_parser_counts(raw_results: Any) -> tuple[dict[str, int], list[str]]:
    if not isinstance(raw_results, list):
        return {}, []

    parser_totals: dict[str, int] = {}
    failed_counts: dict[str, int] = {}
    for result in raw_results:
        if not isinstance(result, dict):
            continue
        parser_name = result.get("parser_name")
        if not isinstance(parser_name, str):
            continue
        parser_totals[parser_name] = parser_totals.get(parser_name, 0) + 1
        if result.get("success") is False:
            failed_counts[parser_name] = failed_counts.get(parser_name, 0) + 1

    failed_all_tasks = sorted(
        parser_name
        for parser_name, failure_count in failed_counts.items()
        if parser_totals.get(parser_name) == failure_count
    )
    return failed_counts, failed_all_tasks


def _is_result_summary_consistent(summary_data: dict[str, Any], raw_results: Any) -> bool | None:
    if not isinstance(summary_data, dict) or not isinstance(raw_results, list):
        return None

    total_results = summary_data.get("total_results")
    success_count = summary_data.get("success_count")
    failure_count = summary_data.get("failure_count")
    if not all(isinstance(value, int) for value in [total_results, success_count, failure_count]):
        return None

    return (
        success_count + failure_count == total_results == len(raw_results)
        and success_count
        == sum(isinstance(r, dict) and r.get("success") is True for r in raw_results)
        and failure_count
        == sum(isinstance(r, dict) and r.get("success") is False for r in raw_results)
    )


def _classify_cost_class(parser_names: list[str]) -> str:
    if not parser_names:
        return "unknown"
    has_open = any(name in OPEN_SOURCE_PARSERS for name in parser_names)
    has_paid = any(name in COMMERCIAL_OR_FRONTIER_PARSERS for name in parser_names)
    if has_open and has_paid:
        return "mixed"
    if has_paid:
        return "commercial_or_frontier"
    if has_open:
        return "open_source"
    return "unknown"


def _config_path_exists(repo_root: Path, config_file: str | None) -> bool:
    if not config_file:
        return False
    config_path = Path(config_file)
    if config_path.is_absolute():
        return config_path.exists()
    return (repo_root / config_path).exists()


def _build_benchmark_status_map(
    repo_root: Path, benchmarks: list[BenchmarkInventoryRecord]
) -> dict[str, str]:
    status_map: dict[str, str] = {}
    for benchmark in benchmarks:
        path = Path(benchmark.path)
        if path.is_absolute():
            try:
                relative_path = path.relative_to(repo_root)
            except ValueError:
                relative_path = path
        else:
            relative_path = path
        status_map[str(relative_path)] = benchmark.status
        status_map[str((repo_root / relative_path).resolve())] = benchmark.status
    return status_map


def _lookup_benchmark_status(
    repo_root: Path,
    config_file: str | None,
    benchmark_statuses: dict[str, str],
) -> str | None:
    if not config_file:
        return None
    if config_file in benchmark_statuses:
        return benchmark_statuses[config_file]
    config_path = Path(config_file)
    if config_path.is_absolute():
        return benchmark_statuses.get(str(config_path))
    return benchmark_statuses.get(str((repo_root / config_path).resolve()))


REVIEWED_LOCAL_RESULTS = Path(".workspace/work/2026-10-13-local-parser-evaluation")


def retained_result_paths(repo_root: Path) -> list[Path]:
    paths = set((repo_root / "results").rglob("*.json"))
    local = repo_root / REVIEWED_LOCAL_RESULTS
    for run in local.glob("run-*"):
        if run.is_dir():
            paths.update(run.rglob("*.json"))
    return sorted(paths)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _observed_counts(rows: list) -> dict:
    valid = [row for row in rows if isinstance(row, dict)]
    pairs = Counter(
        (
            r.get("document_id") if isinstance(r.get("document_id"), str) else None,
            r.get("parser_name") if isinstance(r.get("parser_name"), str) else None,
        )
        for r in valid
    )
    return {
        "total_rows": len(rows),
        "valid_attempt_rows": len(valid),
        "document_ids": sorted(
            {r["document_id"] for r in valid if isinstance(r.get("document_id"), str)}
        ),
        "parser_names": sorted(
            {r["parser_name"] for r in valid if isinstance(r.get("parser_name"), str)}
        ),
        "success_count": sum(r.get("success") is True for r in valid),
        "failure_count": sum(r.get("success") is False for r in valid),
        "unknown_outcome_count": sum(type(r.get("success")) is not bool for r in valid),
        "duplicate_pairs": [list(pair) for pair, count in pairs.items() if count > 1],
        "planned_pairs": None,
        "missing_planned_pairs": None,
    }


def _historical_metrics(rows: list, counts: dict) -> dict:
    parsers = defaultdict(list)
    for index, row in enumerate(rows):
        if isinstance(row, dict) and isinstance(row.get("parser_name"), str):
            parsers[row["parser_name"]].append((index, row))
    all_metrics = sorted(
        {
            key
            for attempts in parsers.values()
            for _, row in attempts
            for key in (row.get("metrics") if isinstance(row.get("metrics"), dict) else {})
        }
    )
    result = {}
    for metric in all_metrics:
        by_parser = {}
        for parser, attempts in sorted(parsers.items()):
            values = {}
            pointers = {}
            for index, row in attempts:
                value = (row.get("metrics") if isinstance(row.get("metrics"), dict) else {}).get(
                    metric
                )
                if (
                    row.get("success") is True
                    and isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                    and isinstance(row.get("document_id"), str)
                ):
                    values[row["document_id"]] = value
                    pointers[row["document_id"]] = (
                        f"/results/{index}/metrics/{metric.replace('~', '~0').replace('/', '~1')}"
                    )
            by_parser[parser] = {
                "observed_attempt_ids": sorted(
                    {r["document_id"] for _, r in attempts if isinstance(r.get("document_id"), str)}
                ),
                "scored_ids": sorted(values),
                "scored_count": len(values),
                "diagnostic_mean": math.fsum(values[i] for i in sorted(values)) / len(values)
                if values and not counts["duplicate_pairs"]
                else None,
                "values": values,
                "pointers": pointers,
            }
        common = (
            sorted(set.intersection(*(set(p["scored_ids"]) for p in by_parser.values())))
            if by_parser
            else []
        )
        for p in by_parser.values():
            p["common_scored_ids"] = common
            p["common_count"] = len(common)
            p["common_diagnostic_mean"] = (
                sum(p["values"][i] for i in common) / len(common)
                if common and not counts["duplicate_pairs"]
                else None
            )
        result[metric] = {
            "parsers": by_parser,
            "primary_ranking": None,
            "interpretation": (
                "Observed finite successful scores; eligibility and missing planned work remain "
                "unknown. Common-success values are secondary diagnostics."
            ),
        }
    return result


def _current_config_observation(root: Path, recorded: str | None, observed: dict) -> dict:
    if not isinstance(recorded, str):
        return {
            "recorded_path": recorded,
            "available_path": None,
            "historical_equivalence": "unknown",
        }
    candidate = Path(recorded)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        candidate = (root / "benchmarks" / Path(recorded).name).resolve()
    info = {
        "recorded_path": recorded,
        "available_path": None,
        "historical_equivalence": "not established by present-day files",
    }
    if not candidate.is_relative_to(root) or not candidate.is_file():
        return info
    data = candidate.read_bytes()
    rel = candidate.relative_to(root).as_posix()
    observed[rel] = _digest(data)
    try:
        parsed = yaml.safe_load(data)
    except yaml.YAMLError as exc:
        info["error"] = str(exc)
        return info
    return {**info, "available_path": rel, "sha256_now": _digest(data), "contents_now": parsed}


def _current_document_observations(
    root: Path, config: dict, ids: list, observed: dict, indexes: dict
) -> list:
    path = config.get("available_path")
    contents = config.get("contents_now")
    if (
        not path
        or not isinstance(contents, dict)
        or not isinstance(contents.get("corpus_dir"), str)
    ):
        return []
    corpus = ((root / path).parent / contents["corpus_dir"]).resolve()
    if not corpus.is_relative_to(root) or not corpus.is_dir():
        return []
    if corpus not in indexes:
        index = defaultdict(list)
        for candidate in corpus.rglob("*"):
            if (
                candidate.resolve().is_relative_to(root)
                and candidate.is_file()
                and candidate.suffix.lower()
                in INPUT_SUFFIXES
                | {
                    ".md",
                    ".docx",
                    ".yaml",
                }
            ):
                index[candidate.stem].append(candidate)
        indexes[corpus] = index
    records = []
    for doc_id in ids:
        candidates = []
        for candidate in sorted(indexes[corpus].get(doc_id, [])):
            rel = candidate.relative_to(root).as_posix()
            if rel not in observed:
                observed[rel] = _digest(candidate.read_bytes())
            candidates.append({"path": rel, "sha256_now": observed[rel]})
        records.append(
            {
                "document_id": doc_id,
                "current_filename_candidates": candidates,
                "historical_input_reference_identity": "unknown",
                "mapping": (
                    "Matching filenames only; no historical byte equivalence or "
                    "reference qualification implied."
                ),
            }
        )
    return records


def build_run_registry(repo_root: Path) -> dict:
    """Reconcile a frozen discovery boundary without rewriting retained evidence."""
    root = repo_root.resolve()
    paths = retained_result_paths(root)
    frozen = []
    for path in paths:
        try:
            if not path.resolve().is_relative_to(root):
                raise OSError("Retained artifact resolves outside repository")
            frozen.append((path, path.read_bytes(), None))
        except OSError as exc:
            frozen.append((path, None, str(exc)))
    overrides_path = root / "inventory_overrides.yaml"
    observed = {}
    overrides = {}
    if overrides_path.exists():
        data = overrides_path.read_bytes()
        observed["inventory_overrides.yaml"] = _digest(data)
        overrides = yaml.safe_load(data) or {}
    annotations = overrides.get("story", {})
    records, indexes = [], {}
    for path, raw, read_error in frozen:
        rel = path.relative_to(root).as_posix()
        record = {
            "artifact_path": rel,
            "sha256": _digest(raw) if raw is not None else None,
            "retained_snapshot": f"retained/{_digest(raw)}.json" if raw is not None else None,
            "bytes": len(raw) if raw is not None else None,
            "kind": "unrecognized",
            "read_error": read_error,
            "story_annotation": annotations.get(rel),
            "evidence_tier": (annotations.get(rel) or {}).get("evidence_tier", "historical"),
        }
        records.append(record)
        record["interpretation_evidence"] = []
        for evidence_path in (annotations.get(rel) or {}).get("supporting_evidence_paths", []):
            candidate = (root / evidence_path).resolve()
            digest = None
            if candidate.is_relative_to(root) and candidate.is_file():
                digest = _digest(candidate.read_bytes())
                observed[evidence_path] = digest
            record["interpretation_evidence"].append({"path": evidence_path, "sha256_now": digest})
        if raw is None:
            record["kind"] = "unreadable"
            continue
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            record.update(kind="unreadable", read_error=str(exc))
            continue
        if not isinstance(data, dict):
            continue
        benchmark = data.get("benchmark") if isinstance(data.get("benchmark"), dict) else {}
        environment = data.get("environment") if isinstance(data.get("environment"), dict) else {}
        rows = data.get("results")
        record.update(
            original_benchmark=benchmark,
            original_summary=data.get("summary"),
            original_environment=environment,
            original_inventory_status=data.get("inventory_status"),
        )
        if ".checkpoint." in path.name or path.name.endswith(".checkpoint.json"):
            record["kind"] = "checkpoint"
        elif "merged" in path.stem and isinstance(rows, list):
            record["kind"] = "derived_or_merged"
            record["derivation_lineage"] = "Filename indicates a merge; parent identities unknown"
        elif isinstance(rows, list) and benchmark and isinstance(data.get("summary"), dict):
            record["kind"] = "derived_or_merged" if "merged" in path.stem else "run"
        elif isinstance(data.get("attempts"), list):
            record["kind"] = "diagnostic_comparison"
            record["recorded_local_provenance"] = {
                k: data.get(k)
                for k in [
                    "source_revision",
                    "source_is_dirty",
                    "implementation_sha256",
                    "versions",
                    "pdfsmith_declared_version",
                    "cache_policy",
                    "inputs",
                    "output_hashes",
                ]
            }
        elif any(
            k in data for k in ["environment", "versions", "parser_versions", "summary", "corpus"]
        ):
            record["kind"] = "diagnostic"
        record["recorded_provenance"] = {
            "config": benchmark.get("config_file"),
            "run_date": benchmark.get("timestamp") or data.get("executed_at"),
            "generating_revision": environment.get("git_commit")
            or environment.get("commit_sha")
            or data.get("source_revision"),
            "parser_versions": environment.get("parser_versions") or data.get("versions"),
            "backend_options": data.get("backend_options"),
            "cache_policy": data.get("cache_policy"),
            "inputs": data.get("inputs"),
            "reference_method": data.get("reference_method"),
            "reference_hashes": data.get("reference_hashes"),
            "raw_outputs": data.get("raw_outputs") or data.get("output_hashes"),
            "backend_implementation": data.get("implementation_sha256"),
            "metric_definitions": data.get("metric_definitions"),
        }
        record["provenance_unknowns"] = [
            key for key, value in record["recorded_provenance"].items() if value is None
        ]
        record["fresh_latency_comparable"] = False
        config = _current_config_observation(root, benchmark.get("config_file"), observed)
        record["current_config_observation"] = config
        if isinstance(rows, list):
            counts = _observed_counts(rows)
            record["observed"] = counts
            declared = data.get("summary") or {}
            actual = {
                "total_results": counts["total_rows"],
                "total_documents": len(counts["document_ids"]),
                "total_parsers": len(counts["parser_names"]),
                "success_count": counts["success_count"],
                "failure_count": counts["failure_count"],
            }
            record["counter_disagreements"] = {
                k: {"declared": declared.get(k), "observed": v}
                for k, v in actual.items()
                if declared.get(k) != v
            }
            record["metrics"] = _historical_metrics(rows, counts)
            record["current_document_observations"] = _current_document_observations(
                root, config, counts["document_ids"], observed, indexes
            )
    return {
        "schema_version": 1,
        "inventory_implementation_sha256": _digest(Path(__file__).read_bytes()),
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "discovery_scope": ["results/**/*.json", f"{REVIEWED_LOCAL_RESULTS}/run-*/**/*.json"],
        "input_artifacts": [
            {
                "path": p.relative_to(root).as_posix(),
                "sha256": _digest(raw) if raw is not None else None,
            }
            for p, raw, _ in frozen
        ],
        "artifact_count": len(records),
        "artifacts": records,
        "missing_named_tracks": sorted(set(annotations) - {r["artifact_path"] for r in records}),
        "current_observation_files": observed,
        "provenance_coverage": {
            key: {
                "known": sum(
                    r.get("recorded_provenance", {}).get(key) is not None for r in records
                ),
                "artifacts": len(records),
            }
            for key in [
                "config",
                "run_date",
                "generating_revision",
                "parser_versions",
                "backend_options",
                "cache_policy",
                "inputs",
                "reference_method",
                "reference_hashes",
                "raw_outputs",
                "backend_implementation",
                "metric_definitions",
            ]
        },
        "interpretation": (
            "Historical values and current file observations are separate. Unknown provenance "
            "limits a claim, not the usefulness of all retained work. No universal or "
            "unequal-population ranking is generated."
        ),
    }


def publish_registry(repo_root: Path, output_dir: Path) -> dict:
    """Finalize an inspectable bundle before atomically replacing its public pointer."""
    from pdf_bench.persistence import write_json_atomic

    root = repo_root.resolve()
    output = output_dir.resolve()
    if output.is_relative_to(root / "results") or output.is_relative_to(
        root / REVIEWED_LOCAL_RESULTS
    ):
        raise ValueError("Registry exports must be outside retained-result discovery roots")
    registry = build_run_registry(root)
    output.mkdir(parents=True, exist_ok=True)
    identifier = uuid.uuid4().hex
    staging = output / f".incomplete-{identifier}"
    final = output / f"bundle-{identifier}"
    staging.mkdir()
    (staging / "retained").mkdir()
    for record in registry["artifacts"]:
        if record["retained_snapshot"] is not None:
            raw = (root / record["artifact_path"]).read_bytes()
            if _digest(raw) != record["sha256"]:
                raise ValueError("Retained artifact changed before snapshot persistence")
            (staging / record["retained_snapshot"]).write_bytes(raw)
    write_json_atomic(staging / "registry.json", registry)
    story = {
        "registry_sha256": _digest((staging / "registry.json").read_bytes()),
        "tracks": [r for r in registry["artifacts"] if r.get("story_annotation")],
    }
    write_json_atomic(staging / "story.json", story)
    lines = [
        "# Retained benchmark evidence",
        "",
        "Original counters and descriptions remain separate from observed rows "
        "and supported interpretations.",
        "",
        "| Artifact | Kind | Tier | Rows | Success | Failed | Counter disagreements |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for record in registry["artifacts"]:
        c = record.get("observed", {})
        lines.append(
            f"| {record['artifact_path']} | {record['kind']} | {record['evidence_tier']} "
            f"| {c.get('total_rows')} | {c.get('success_count')} | {c.get('failure_count')} "
            f"| {', '.join(record.get('counter_disagreements', {}))} |"
        )
    lines += ["", "## Named track interpretations", ""]
    for record in story["tracks"]:
        annotation = record["story_annotation"]
        lines += [
            f"### {annotation['title']}",
            "",
            annotation["supported_interpretation"],
            "",
            f"Source: `{record['artifact_path']}`, SHA256 `{record['sha256']}`.",
            "",
            "Metric values and exact scored/common document IDs are in registry.json. "
            "All means are diagnostic; no primary ranking is assigned.",
            "",
        ]
        for metric, population in record.get("metrics", {}).items():
            lines += [
                f"#### {metric}",
                "",
                "| Parser | Scored / observed IDs | Mean | Common count | Common mean |",
                "|---|---:|---:|---:|---:|",
            ]
            for parser, scores in population["parsers"].items():
                lines.append(
                    f"| {parser} | {scores['scored_count']} / "
                    f"{len(scores['observed_attempt_ids'])} | {scores['diagnostic_mean']} | "
                    f"{scores['common_count']} | {scores['common_diagnostic_mean']} |"
                )
            lines.append("")
    (staging / "appendix.md").write_text("\n".join(lines))
    for entry in registry["input_artifacts"]:
        if (
            entry["sha256"] is not None
            and _digest((root / entry["path"]).read_bytes()) != entry["sha256"]
        ):
            raise ValueError("Retained artifact changed during registry generation")
    for path, digest in registry["current_observation_files"].items():
        if _digest((root / path).read_bytes()) != digest:
            raise ValueError("Current observation changed during registry generation")
    required = ["registry.json", "story.json", "appendix.md"]
    artifacts = {name: _digest((staging / name).read_bytes()) for name in required}
    artifacts.update(
        {
            record["retained_snapshot"]: record["sha256"]
            for record in registry["artifacts"]
            if record["retained_snapshot"] is not None
        }
    )
    if len(registry["artifacts"]) != len(registry["input_artifacts"]):
        raise ValueError("Incomplete registry coverage")
    write_json_atomic(staging / "manifest.json", {"status": "complete", "artifacts": artifacts})
    os.replace(staging, final)
    _validate_registry_bundle(final, _digest((final / "manifest.json").read_bytes()))
    pointer = {
        "bundle": final.name,
        "manifest_sha256": _digest((final / "manifest.json").read_bytes()),
        "registry_sha256": artifacts["registry.json"],
    }
    write_json_atomic(output / "latest.json", pointer)
    return pointer


def _validate_registry_bundle(bundle: Path, manifest_sha256: str) -> dict:
    raw = (bundle / "manifest.json").read_bytes()
    if _digest(raw) != manifest_sha256:
        raise ValueError("Registry completion manifest hash mismatch")
    manifest = json.loads(raw)
    required = {"registry.json", "story.json", "appendix.md"}
    if manifest.get("status") != "complete" or not required.issubset(manifest.get("artifacts", {})):
        raise ValueError("Registry bundle lacks required completed artifacts")
    for name, digest in manifest["artifacts"].items():
        if not (bundle / name).resolve().is_relative_to(bundle.resolve()):
            raise ValueError("Registry manifest points outside bundle")
        if _digest((bundle / name).read_bytes()) != digest:
            raise ValueError("Registry artifact hash mismatch")
    registry = json.loads((bundle / "registry.json").read_bytes())
    story = json.loads((bundle / "story.json").read_bytes())
    if story["registry_sha256"] != manifest["artifacts"]["registry.json"]:
        raise ValueError("Story points to another registry")
    if registry["artifact_count"] != len(registry["artifacts"]) or len(
        registry["artifacts"]
    ) != len(registry["input_artifacts"]):
        raise ValueError("Registry coverage does not match discovery boundary")
    actual = {(r["artifact_path"], r["sha256"]) for r in registry["artifacts"]}
    expected = {(r["path"], r["sha256"]) for r in registry["input_artifacts"]}
    if actual != expected or len(actual) != len(registry["artifacts"]):
        raise ValueError("Registry artifact membership differs from discovery boundary")
    for record in registry["artifacts"]:
        name = record.get("retained_snapshot")
        if record["sha256"] is not None and manifest["artifacts"].get(name) != record["sha256"]:
            raise ValueError("Registry source snapshot is missing from completion manifest")
    return registry


def load_registry_bundle(output_dir: Path) -> dict:
    pointer = json.loads((output_dir / "latest.json").read_bytes())
    bundle = (output_dir / pointer["bundle"]).resolve()
    if bundle.parent != output_dir.resolve() or not bundle.name.startswith("bundle-"):
        raise ValueError("Invalid registry bundle location")
    registry = _validate_registry_bundle(bundle, pointer["manifest_sha256"])
    if _digest((bundle / "registry.json").read_bytes()) != pointer["registry_sha256"]:
        raise ValueError("Registry pointer hash mismatch")
    return registry
