"""Exercise actual retained contradictions and the registry publication path."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from pdf_bench.inventory import build_run_registry, load_registry_bundle, publish_registry

FIXTURES = Path(__file__).parent / "fixtures/retained_results"
ROOT = Path(__file__).parents[1]


@pytest.fixture
def retained_repo(tmp_path):
    (tmp_path / "results").mkdir()
    (tmp_path / "benchmarks").mkdir()
    for file in FIXTURES.iterdir():
        if file.suffix == ".json" and file.name != "origins.json":
            shutil.copyfile(file, tmp_path / "results" / file.name)
        elif file.suffix == ".yaml":
            shutil.copyfile(file, tmp_path / "benchmarks" / file.name)
    shutil.copyfile(ROOT / "inventory_overrides.yaml", tmp_path / "inventory_overrides.yaml")
    return tmp_path


def _record(registry, name):
    return next(r for r in registry["artifacts"] if r["artifact_path"] == "results/" + name)


def test_original_commercial_counters_do_not_override_observed_attempts(retained_repo):
    registry = build_run_registry(retained_repo)
    record = _record(registry, "sec_filings_commercial_5docs.json")
    assert record["original_summary"]["failure_count"] == 13
    assert record["observed"]["failure_count"] == 1
    assert record["observed"]["success_count"] == 14
    assert record["observed"]["total_rows"] == 15
    assert record["counter_disagreements"]["failure_count"] == {"declared": 13, "observed": 1}
    assert record["observed"]["planned_pairs"] is None
    assert record["observed"]["missing_planned_pairs"] is None
    screen = _record(registry, "sec_filings_screen_all.json")
    assert "89" in screen["original_benchmark"]["name"]
    assert len(screen["observed"]["document_ids"]) == 320


def test_unequal_metric_populations_are_explicit_and_do_not_create_primary_ranks(retained_repo):
    record = _record(build_run_registry(retained_repo), "sec_filings_commercial_5docs.json")
    metric = record["metrics"]["edit_similarity"]
    aws = metric["parsers"]["pdfsmith-aws_textract"]
    azure = metric["parsers"]["pdfsmith-azure_document_intelligence"]
    assert metric["primary_ranking"] is None
    assert aws["scored_count"] == 4
    assert len(aws["observed_attempt_ids"]) == 5
    assert azure["scored_count"] == 5
    assert aws["common_scored_ids"] == azure["common_scored_ids"]
    assert aws["common_count"] == 4
    assert "sec-energizer_holdings-2025" not in aws["common_scored_ids"]
    assert aws["diagnostic_mean"] == pytest.approx(0.9015772992171767)
    assert azure["common_diagnostic_mean"] == pytest.approx(0.8997344402644975)
    assert record["fresh_latency_comparable"] is False
    assert "cache_policy" in record["provenance_unknowns"]


def test_current_config_and_story_labels_do_not_certify_historical_truth(retained_repo):
    config_path = retained_repo / "benchmarks/invoices_100docs_fresh.yaml"
    config = yaml.safe_load(config_path.read_text())
    config["corpus_dir"] = "../corpus"
    config_path.write_text(yaml.safe_dump(config))
    current = retained_repo / "corpus/pdfs/invoice_001.pdf"
    current.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "tests/fixtures/sample.pdf", current)
    registry = build_run_registry(retained_repo)
    invoice = _record(registry, "invoices_100docs_fresh.json")
    assert invoice["story_annotation"]["historical_description"]["status"].startswith("tier_1")
    assert invoice["evidence_tier"] == "historical"
    observation = invoice["current_config_observation"]
    assert (
        observation["sha256_now"]
        == hashlib.sha256(
            (retained_repo / "benchmarks/invoices_100docs_fresh.yaml").read_bytes()
        ).hexdigest()
    )
    assert observation["historical_equivalence"] == "not established by present-day files"
    assert all(
        r["historical_input_reference_identity"] == "unknown"
        for r in invoice["current_document_observations"]
    )
    mapped = next(
        r for r in invoice["current_document_observations"] if r["document_id"] == "invoice_001"
    )
    assert mapped["current_filename_candidates"] == [
        {
            "path": "corpus/pdfs/invoice_001.pdf",
            "sha256_now": hashlib.sha256(current.read_bytes()).hexdigest(),
        }
    ]
    assert invoice["recorded_provenance"]["inputs"] is None
    assert registry["missing_named_tracks"]


def test_discovery_keeps_checkpoints_unknown_json_and_truncated_artifacts(retained_repo):
    results = retained_repo / "results"
    shutil.copyfile(
        results / "sec_filings_commercial_5docs.json", results / "commercial.checkpoint.json"
    )
    (results / "truncated.json").write_bytes(b'{"benchmark": ')
    expected = {p.relative_to(retained_repo).as_posix() for p in results.rglob("*.json")}
    local = (
        retained_repo / ".workspace/work/2026-10-13-local-parser-evaluation/run-03/comparison.json"
    )
    local.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "tests/fixtures/local_comparison.json", local)
    expected.add(local.relative_to(retained_repo).as_posix())
    registry = build_run_registry(retained_repo)
    assert {r["artifact_path"] for r in registry["artifacts"]} == expected
    assert registry["artifact_count"] == len(expected)
    assert _record(registry, "commercial.checkpoint.json")["kind"] == "checkpoint"
    assert _record(registry, "truncated.json")["kind"] == "unreadable"
    assert _record(registry, "pareto_analysis.json")["kind"] in {"unrecognized", "diagnostic"}
    assert _record(registry, "truncated.json")["read_error"]


def test_actual_generator_publishes_complete_bundle_without_changing_retained_bytes(retained_repo):
    before = {p: p.read_bytes() for p in (retained_repo / "results").rglob("*.json")}
    output = retained_repo / "exports"
    command = [
        sys.executable,
        str(ROOT / "scripts/build_internal_benchmark_story.py"),
        "--repo-root",
        str(retained_repo),
        "--output-dir",
        str(output),
    ]
    subprocess.run(command, check=True, capture_output=True)
    registry = load_registry_bundle(output)
    assert registry["artifact_count"] == len(before)
    assert {p: p.read_bytes() for p in before} == before
    pointer = json.loads((output / "latest.json").read_text())
    appendix = (output / pointer["bundle"] / "appendix.md").read_text()
    assert "Scored / observed IDs" in appendix
    assert "sec_filings_commercial_5docs.json" in appendix
    assert "no primary ranking" in appendix
    for p, data in before.items():
        assert _record(registry, p.name)["sha256"] == hashlib.sha256(data).hexdigest()
        snapshot = _record(registry, p.name)["retained_snapshot"]
        assert (output / pointer["bundle"] / snapshot).read_bytes() == data


def test_failed_generation_preserves_previous_completed_bundle(retained_repo, monkeypatch):
    output = retained_repo / "exports"
    publish_registry(retained_repo, output)
    before_pointer = (output / "latest.json").read_bytes()
    pointer = json.loads(before_pointer)
    before = {
        p.relative_to(output): p.read_bytes()
        for p in (output / pointer["bundle"]).rglob("*")
        if p.is_file()
    }
    original = Path.write_text

    def fail_appendix(path, *args, **kwargs):
        if path.name == "appendix.md":
            raise OSError("Injected filesystem write failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_appendix)
    with pytest.raises(OSError, match="Injected filesystem"):
        publish_registry(retained_repo, output)
    assert (output / "latest.json").read_bytes() == before_pointer
    assert {
        p.relative_to(output): p.read_bytes()
        for p in (output / pointer["bundle"]).rglob("*")
        if p.is_file()
    } == before
    assert load_registry_bundle(output)["artifact_count"] == 4


def test_reader_rejects_missing_or_tampered_completed_artifact(retained_repo):
    output = retained_repo / "exports"
    pointer = publish_registry(retained_repo, output)
    appendix = output / pointer["bundle"] / "appendix.md"
    appendix.write_text(appendix.read_text() + "\nchanged")
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        load_registry_bundle(output)


def test_failed_pointer_replacement_keeps_previous_verified_bundle(retained_repo, monkeypatch):
    import os

    output = retained_repo / "exports"
    publish_registry(retained_repo, output)
    before = (output / "latest.json").read_bytes()
    replace = os.replace

    def fail_pointer(source, target):
        if Path(target).name == "latest.json":
            raise OSError("Injected pointer replacement failure")
        return replace(source, target)

    monkeypatch.setattr(os, "replace", fail_pointer)
    with pytest.raises(OSError, match="pointer replacement"):
        publish_registry(retained_repo, output)
    assert (output / "latest.json").read_bytes() == before
    assert load_registry_bundle(output)["artifact_count"] == 4


def test_rows_from_actual_runner_with_repeated_document_ids_are_ambiguous(tmp_path, monkeypatch):
    from pdf_bench.config import (
        BenchmarkConfig,
        DocumentFilter,
        MetricConfig,
        OutputConfig,
        ParserConfig,
    )
    from pdf_bench.loader import DocumentInfo, LoadedConfig
    from pdf_bench.persistence import save_results
    from pdf_bench.runner import BenchmarkRunner
    from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter
    from pdf_bench.utils.metadata import DocumentMetadata

    monkeypatch.chdir(tmp_path)
    doc = DocumentInfo(
        "duplicate",
        ROOT / "tests/fixtures/sample.pdf",
        ROOT / "tests/fixtures/sample_ground_truth.md",
        DocumentMetadata("duplicate", "synthetic", "pandoc"),
    )
    config = BenchmarkConfig(
        "Repeated metadata ID",
        "Actual duplicate-input producing path",
        str(tmp_path),
        DocumentFilter(),
        ParserConfig(["pypdf"]),
        MetricConfig(["edit_similarity"]),
        OutputConfig("outputs"),
    )
    loaded = LoadedConfig(config, [doc, doc], [PdfsmithAdapter("pypdf")], tmp_path / "outputs")
    loaded.results_dir.mkdir()
    runner = BenchmarkRunner(loaded, parallel_workers=1)
    results = runner.run()
    target = tmp_path / "results/duplicates.json"
    save_results(results, target)
    record = _record(build_run_registry(tmp_path), "duplicates.json")
    assert record["observed"]["total_rows"] == 2
    assert record["observed"]["duplicate_pairs"] == [["duplicate", "pdfsmith-pypdf"]]
    assert (
        record["metrics"]["edit_similarity"]["parsers"]["pdfsmith-pypdf"]["diagnostic_mean"] is None
    )
    config.metric_config.metrics = ["teds"]
    loaded.documents = [doc]
    results = BenchmarkRunner(loaded, parallel_workers=1).run()
    assert results.results[0].success is True
    save_results(results, tmp_path / "results/no-table.json")
    no_table = _record(build_run_registry(tmp_path), "no-table.json")
    metric = no_table["metrics"]["teds"]["parsers"]["pdfsmith-pypdf"]
    assert metric["scored_count"] == 0
    assert metric["diagnostic_mean"] is None
