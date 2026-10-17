"""Tests for repository inventory and status classification."""

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from pdf_bench.inventory import (
    STATUS_ARCHIVE_ONLY,
    STATUS_DRAFT,
    STATUS_VALID_INTERNAL,
    build_inventory,
    save_inventory,
)
from pdf_bench.main import app

runner = CliRunner()


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _valid_benchmark_config() -> dict:
    return {
        "name": "Valid Benchmark",
        "description": "Test config",
        "corpus_dir": "../corpus",
        "document_filter": {
            "include_doc_ids": ["doc-001", "doc-002"],
        },
        "parser_config": {
            "parsers": ["pymupdf"],
            "parser_options": {},
        },
        "metric_config": {
            "metrics": ["edit_distance"],
            "aggregate": True,
        },
        "output_config": {
            "results_dir": "results",
        },
        "parallel_workers": 1,
    }


def _result_payload(
    *,
    config_file: str | None,
    parser_versions: dict[str, str],
    failure_count: int,
    parser_name: str = "pdfsmith-pymupdf",
    total_results: int = 1,
    success_count: int | None = None,
    results: list[dict] | None = None,
) -> dict:
    payload_results = results or [
        {
            "document_id": "doc-001",
            "parser_name": parser_name,
            "success": failure_count == 0,
            "metrics": {"edit_similarity": 0.9},
            "error": None if failure_count == 0 else "failed",
            "parse_time_seconds": 0.1,
        }
    ]
    computed_success_count = (
        success_count if success_count is not None else total_results - failure_count
    )
    return {
        "benchmark": {
            "name": "Valid Benchmark",
            "timestamp": "2026-03-20T12:00:00+00:00",
            "config_file": config_file,
        },
        "environment": {
            "python_version": "3.13.0",
            "platform": "Linux",
            "parser_versions": parser_versions,
        },
        "results": payload_results,
        "summary": {
            "total_documents": 2,
            "total_parsers": 1,
            "total_results": total_results,
            "success_count": computed_success_count,
            "failure_count": failure_count,
        },
    }


def _create_sample_repo(repo_root: Path) -> None:
    corpus_dir = repo_root / "corpus" / "sample"
    _write_yaml(
        corpus_dir / "corpus_metadata.yaml",
        {
            "name": "Sample Corpus",
            "description": "Sample",
            "document_count": 2,
            "domain": "business",
            "source": "synthetic",
            "ground_truth_method": "manual",
            "features": ["tables"],
        },
    )
    for doc_id in ["doc-001", "doc-002"]:
        _write_text(corpus_dir / "pdfs" / f"{doc_id}.pdf", "pdf")
        _write_text(corpus_dir / "ground_truth" / f"{doc_id}.md", "# Ground truth")
        _write_yaml(
            corpus_dir / "metadata" / f"{doc_id}.yaml",
            {
                "doc_id": doc_id,
                "corpus": "business",
                "domain": "sample",
            },
        )
    _write_text(corpus_dir / "ground_truth" / "doc-001_aux.md", "# Auxiliary")
    _write_yaml(
        corpus_dir / "metadata" / "doc-001_aux.yaml",
        {
            "doc_id": "doc-001_aux",
            "corpus": "business",
            "domain": "sample",
        },
    )

    _write_yaml(repo_root / "benchmarks" / "valid.yaml", _valid_benchmark_config())

    legacy_config = _valid_benchmark_config()
    legacy_config["name"] = "Legacy Benchmark"
    legacy_config["output"] = {"format": "json"}
    _write_yaml(repo_root / "benchmarks" / "legacy.yaml", legacy_config)

    archived_config = _valid_benchmark_config()
    archived_config["name"] = "Archived Benchmark"
    archived_config["inventory_status"] = "archive_only"
    _write_yaml(repo_root / "benchmarks" / "archived.yaml", archived_config)

    archived_path_config = _valid_benchmark_config()
    archived_path_config["name"] = "Archived Path Benchmark"
    _write_yaml(repo_root / "benchmarks" / "archive" / "path_archived.yaml", archived_path_config)

    _write_json(
        repo_root / "results" / "valid.json",
        _result_payload(
            config_file="benchmarks/valid.yaml",
            parser_versions={"pdfsmith-pymupdf": "0.3.0"},
            failure_count=0,
        ),
    )
    _write_json(
        repo_root / "results" / "valid.checkpoint.json",
        _result_payload(
            config_file="benchmarks/valid.yaml",
            parser_versions={"pdfsmith-pymupdf": "0.3.0"},
            failure_count=0,
        ),
    )
    _write_json(
        repo_root / "results" / "archive" / "old.json",
        _result_payload(
            config_file="benchmarks/valid.yaml",
            parser_versions={"pdfsmith-pymupdf": "0.3.0"},
            failure_count=0,
        ),
    )
    _write_json(
        repo_root / "results" / "missing_versions.json",
        _result_payload(
            config_file="benchmarks/valid.yaml",
            parser_versions={},
            failure_count=0,
        ),
    )
    _write_json(
        repo_root / "results" / "archived_config_result.json",
        _result_payload(
            config_file="benchmarks/archived.yaml",
            parser_versions={"pdfsmith-pymupdf": "0.3.0"},
            failure_count=0,
        ),
    )
    _write_json(
        repo_root / "results" / "summary_mismatch.json",
        _result_payload(
            config_file="benchmarks/valid.yaml",
            parser_versions={"pdfsmith-pymupdf": "0.3.0"},
            failure_count=1,
            total_results=1,
            success_count=1,
            results=[
                {
                    "document_id": "doc-001",
                    "parser_name": "pdfsmith-pymupdf",
                    "success": False,
                    "metrics": {},
                    "error": "failed",
                    "parse_time_seconds": 0.1,
                }
            ],
        ),
    )
    _write_json(
        repo_root / "results" / "parser_failed_all_tasks.json",
        {
            "benchmark": {
                "name": "Valid Benchmark",
                "timestamp": "2026-03-20T12:00:00+00:00",
                "config_file": "benchmarks/valid.yaml",
            },
            "environment": {
                "python_version": "3.13.0",
                "platform": "Linux",
                "parser_versions": {"pdfsmith-pymupdf": "0.3.0"},
            },
            "results": [
                {
                    "document_id": "doc-001",
                    "parser_name": "pdfsmith-pymupdf",
                    "success": False,
                    "metrics": {},
                    "error": "failed",
                    "parse_time_seconds": 0.1,
                },
                {
                    "document_id": "doc-002",
                    "parser_name": "pdfsmith-pymupdf",
                    "success": False,
                    "metrics": {},
                    "error": "failed",
                    "parse_time_seconds": 0.1,
                },
            ],
            "summary": {
                "total_documents": 2,
                "total_parsers": 1,
                "total_results": 2,
                "success_count": 0,
                "failure_count": 2,
            },
        },
    )


class TestInventory:
    """Tests for repository inventory scanning."""

    def test_build_inventory_classifies_artifacts(self, tmp_path: Path) -> None:
        """Inventory should classify corpora, configs, and result artifacts."""
        _create_sample_repo(tmp_path)

        snapshot = build_inventory(tmp_path)

        assert snapshot.summary["corpora"]["valid_internal"] == 1
        assert snapshot.summary["benchmarks"]["valid_internal"] == 1
        assert snapshot.summary["benchmarks"]["draft"] == 1
        assert snapshot.summary["benchmarks"]["archive_only"] == 2
        assert snapshot.summary["results"]["valid_internal"] == 1
        assert snapshot.summary["results"]["draft"] == 1
        assert snapshot.summary["results"]["archive_only"] == 5

        corpus = snapshot.corpora[0]
        assert corpus.status == STATUS_VALID_INTERNAL
        assert corpus.input_count == 2
        assert corpus.ground_truth_count == 2
        assert corpus.metadata_count == 2
        assert {issue.code for issue in corpus.issues} == {"extra_ground_truth", "extra_metadata"}

        legacy_benchmark = next(
            record for record in snapshot.benchmarks if Path(record.path).name == "legacy.yaml"
        )
        assert legacy_benchmark.status == STATUS_DRAFT
        assert {issue.code for issue in legacy_benchmark.issues} == {"unsupported_output_key"}

        archived_path_benchmark = next(
            record
            for record in snapshot.benchmarks
            if Path(record.path).name == "path_archived.yaml"
        )
        assert archived_path_benchmark.status == STATUS_ARCHIVE_ONLY

        valid_result = next(
            record for record in snapshot.results if Path(record.path).name == "valid.json"
        )
        assert valid_result.status == STATUS_VALID_INTERNAL
        assert valid_result.cost_class == "open_source"

        missing_versions_result = next(
            record
            for record in snapshot.results
            if Path(record.path).name == "missing_versions.json"
        )
        assert missing_versions_result.status == STATUS_DRAFT
        assert {issue.code for issue in missing_versions_result.issues} >= {
            "missing_parser_versions",
            "missing_commit_sha",
        }

        checkpoint_result = next(
            record
            for record in snapshot.results
            if Path(record.path).name == "valid.checkpoint.json"
        )
        assert checkpoint_result.status == STATUS_ARCHIVE_ONLY

        archived_config_result = next(
            record
            for record in snapshot.results
            if Path(record.path).name == "archived_config_result.json"
        )
        assert archived_config_result.status == STATUS_ARCHIVE_ONLY

        summary_mismatch_result = next(
            record
            for record in snapshot.results
            if Path(record.path).name == "summary_mismatch.json"
        )
        assert summary_mismatch_result.status == STATUS_ARCHIVE_ONLY
        assert summary_mismatch_result.summary_consistent is False
        assert {issue.code for issue in summary_mismatch_result.issues} >= {
            "summary_count_mismatch",
            "high_failure_rate",
        }

        parser_failed_all_tasks_result = next(
            record
            for record in snapshot.results
            if Path(record.path).name == "parser_failed_all_tasks.json"
        )
        assert parser_failed_all_tasks_result.status == STATUS_ARCHIVE_ONLY
        assert parser_failed_all_tasks_result.failed_parser_counts == {"pdfsmith-pymupdf": 2}
        assert parser_failed_all_tasks_result.parsers_failed_all_tasks == ["pdfsmith-pymupdf"]

    def test_save_inventory_writes_json(self, tmp_path: Path) -> None:
        """Inventory snapshots should be serializable to JSON."""
        _create_sample_repo(tmp_path)
        snapshot = build_inventory(tmp_path)

        output_path = tmp_path / "artifacts" / "inventory.json"
        save_inventory(snapshot, output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text(encoding="utf-8"))
        assert data["summary"]["results"]["total"] == 7
        assert data["corpora"][0]["status"] == STATUS_VALID_INTERNAL

    def test_inventory_overrides_file_can_override_status(self, tmp_path: Path) -> None:
        """Repo-level inventory overrides should win over auto and inline status."""
        _create_sample_repo(tmp_path)
        _write_yaml(
            tmp_path / "inventory_overrides.yaml",
            {
                "results": {
                    "results/valid.json": {
                        "status": STATUS_ARCHIVE_ONLY,
                        "note": "Historical snapshot",
                    }
                },
                "benchmarks": {
                    "benchmarks/valid.yaml": STATUS_ARCHIVE_ONLY,
                },
            },
        )

        snapshot = build_inventory(tmp_path)

        overridden_result = next(
            record for record in snapshot.results if Path(record.path).name == "valid.json"
        )
        assert overridden_result.status == STATUS_ARCHIVE_ONLY
        assert overridden_result.status_source == "inventory_overrides"

        overridden_benchmark = next(
            record for record in snapshot.benchmarks if Path(record.path).name == "valid.yaml"
        )
        assert overridden_benchmark.status == STATUS_ARCHIVE_ONLY
        assert overridden_benchmark.status_source == "inventory_overrides"


class TestInventoryCli:
    """Tests for the inventory CLI command."""

    def test_inventory_command_saves_snapshot(self, tmp_path: Path) -> None:
        """CLI should scan the repo and save inventory JSON."""
        _create_sample_repo(tmp_path)
        output_path = tmp_path / "inventory.json"

        result = runner.invoke(
            app,
            ["inventory", "--repo-root", str(tmp_path), "--output", str(output_path)],
        )

        assert result.exit_code == 0
        assert "Repository inventory:" in result.stdout
        assert "Inventory saved to" in result.stdout
        assert output_path.exists()

        data = json.loads(output_path.read_text(encoding="utf-8"))
        assert data["summary"]["benchmarks"]["draft"] == 1
