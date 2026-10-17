"""Reproduce execution defects through actual adapters and runner dispatch."""

import hashlib
from pathlib import Path

import pytest

from pdf_bench.runner import _extract_parser_init_args, _worker_run_single
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter
from pdf_bench.utils.caching import cache_key, store_cached

SOURCE = Path(__file__).parent / "fixtures/invoice_sources/pdfs/invoice_001.pdf"


def _loaded(tmp_path):
    from pdf_bench.config import (
        BenchmarkConfig,
        DocumentFilter,
        MetricConfig,
        OutputConfig,
        ParserConfig,
    )
    from pdf_bench.loader import DocumentInfo, LoadedConfig
    from pdf_bench.utils.metadata import DocumentMetadata

    source = tmp_path / "invoice.pdf"
    source.write_bytes(SOURCE.read_bytes())
    reference = tmp_path / "reference.md"
    reference.write_text("Invoice INV-98034")
    doc = DocumentInfo(
        "invoice", source, reference, DocumentMetadata("invoice", "synthetic", "invoices")
    )
    config = BenchmarkConfig(
        "Actual execution",
        "Checkpoint controls",
        str(tmp_path),
        DocumentFilter(),
        ParserConfig(["pypdf"]),
        MetricConfig(["edit_similarity"]),
        OutputConfig("outputs"),
    )
    return LoadedConfig(config, [doc], [PdfsmithAdapter("pypdf")], tmp_path / "outputs")


def test_explicit_bypass_reads_and_writes_no_adapter_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    adapter = PdfsmithAdapter("pypdf", cache_mode="bypass")
    poison = tmp_path / "poison.md"
    poison.write_text("Wrong cached invoice")
    key = cache_key(SOURCE, adapter.name, adapter.version)
    store_cached(key, poison, Path(".cache"))
    before = {
        p.relative_to(tmp_path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (tmp_path / ".cache").rglob("*")
        if p.is_file()
    }
    output = adapter.parse(SOURCE, tmp_path / "outputs")
    assert "INV-98034" in output.read_text()
    after = {
        p.relative_to(tmp_path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (tmp_path / ".cache").rglob("*")
        if p.is_file()
    }
    assert after == before
    assert output.is_relative_to(tmp_path / "outputs")


def test_changed_real_backend_option_cannot_reuse_default_cached_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = PdfsmithAdapter("pdfplumber", layout=False).parse(SOURCE, tmp_path / "a").read_bytes()
    second = PdfsmithAdapter("pdfplumber", layout=True).parse(SOURCE, tmp_path / "b").read_bytes()
    assert first != second
    assert not (tmp_path / ".cache").exists()


def test_unsafe_cache_reuse_is_explicitly_disabled():
    with pytest.raises(ValueError, match="reuse is disabled"):
        PdfsmithAdapter("pypdf", cache_mode="reuse")


def test_real_worker_reconstructs_adapter_without_forwarding_display_name(tmp_path):
    parser = PdfsmithAdapter("pypdf", cache_mode="bypass")
    parser_class, options = _extract_parser_init_args(parser)
    reference = tmp_path / "reference.md"
    reference.write_text("Invoice INV-98034")
    result = _worker_run_single(
        parser.name,
        parser_class,
        options,
        "invoice_001",
        SOURCE,
        reference,
        tmp_path / "output",
        ["edit_similarity"],
    )
    assert result.success, result.error
    assert "name" not in options


@pytest.mark.parametrize("change", ["input", "reference", "none"])
def test_checkpoint_resume_is_disabled_before_import_or_overwrite(tmp_path, change):
    from pdf_bench.persistence import load_results
    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    checkpoint = tmp_path / "checkpoint.json"
    first = BenchmarkRunner(loaded, parallel_workers=1).run(checkpoint_path=checkpoint)
    assert first.success_count == 1
    before = checkpoint.read_bytes()
    if change == "input":
        loaded.documents[0].input_path.write_bytes(b"corrupt changed PDF")
    elif change == "reference":
        loaded.documents[0].ground_truth_path.write_text("Changed reference under the same ID")
    with pytest.raises(ValueError, match="resumption is disabled"):
        BenchmarkRunner(loaded, parallel_workers=1).run(checkpoint_path=checkpoint)
    assert checkpoint.read_bytes() == before
    assert load_results(checkpoint).success_count == 1


def test_duplicate_planned_pairs_fail_before_backend_execution(tmp_path):
    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    loaded.documents.append(loaded.documents[0])
    with pytest.raises(ValueError, match="unique"):
        BenchmarkRunner(loaded, parallel_workers=1).run()
    assert not loaded.results_dir.exists()


def test_unknown_required_metric_fails_before_backend_execution(tmp_path):
    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    loaded.config.metric_config.metrics.append("typo_metric")
    with pytest.raises(ValueError, match="Unknown required metrics"):
        BenchmarkRunner(loaded, parallel_workers=1).run()
    assert not loaded.results_dir.exists()


def test_runner_persists_actual_output_identity_and_started_failure_duration(tmp_path):
    import json

    from pdf_bench.loader import DocumentInfo
    from pdf_bench.persistence import save_results
    from pdf_bench.runner import BenchmarkRunner
    from pdf_bench.utils.metadata import DocumentMetadata

    loaded = _loaded(tmp_path)
    corrupt = tmp_path / "corrupt.pdf"
    corrupt.write_bytes(b"%PDF-1.7\ntruncated upload\n")
    loaded.documents.append(
        DocumentInfo(
            "corrupt-control",
            corrupt,
            loaded.documents[0].ground_truth_path,
            DocumentMetadata("corrupt-control", "synthetic", "invoices"),
        )
    )
    results = BenchmarkRunner(loaded, parallel_workers=2).run()
    good, failed = sorted(results.results, key=lambda r: not r.success)
    assert good.parse_outcome == "success_content"
    output = Path(good.output_path)
    assert "INV-98034" in output.read_text()
    assert good.output_sha256 == hashlib.sha256(output.read_bytes()).hexdigest()
    assert failed.parse_outcome == "parser_failure"
    assert failed.parse_time_seconds > 0
    assert failed.output_sha256 is None
    target = tmp_path / "results.json"
    save_results(results, target)
    raw = json.loads(target.read_text())
    rows = {r["document_id"]: r for r in raw["results"]}
    assert rows["invoice"]["output_sha256"] == good.output_sha256
    assert rows["corrupt-control"]["parse_outcome"] == "parser_failure"
    assert rows["corrupt-control"]["parse_time_seconds"] > 0


def test_metric_exception_is_evaluation_failure_after_successful_real_parse(tmp_path, monkeypatch):
    from pdf_bench.runner import METRIC_FUNCTIONS, BenchmarkRunner

    loaded = _loaded(tmp_path)

    def bad_metric(reference, prediction):
        raise RuntimeError("Actual metric failure control")

    monkeypatch.setitem(METRIC_FUNCTIONS, "edit_similarity", bad_metric)
    result = BenchmarkRunner(loaded, parallel_workers=1).run().results[0]
    assert result.success and result.parse_outcome == "success_content"
    assert result.metric_outcomes["edit_similarity"]["status"] == "error"
    assert "Actual metric failure" in result.evaluation_errors["edit_similarity"]
    assert result.error is None


def test_parallel_actual_parsers_of_same_stem_retain_distinct_returned_bytes(tmp_path):
    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    loaded.parser_instances.append(PdfsmithAdapter("pdfplumber", cache_mode="bypass"))
    results = BenchmarkRunner(loaded, parallel_workers=2).run()
    assert all(r.success for r in results.results)
    by_name = {r.parser_name: r for r in results.results}
    first, second = by_name["pdfsmith-pypdf"], by_name["pdfsmith-pdfplumber"]
    assert first.output_path != second.output_path
    assert first.output_sha256 != second.output_sha256
    assert "INV-98034" in Path(first.output_path).read_text()
    assert "| Description |" in Path(second.output_path).read_text()
    for row in results.results:
        assert hashlib.sha256(Path(row.output_path).read_bytes()).hexdigest() == row.output_sha256


def test_actual_blank_pdf_is_success_empty_with_retained_empty_bytes(tmp_path):
    from reportlab.pdfgen.canvas import Canvas

    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    canvas = Canvas(str(loaded.documents[0].input_path), invariant=1)
    canvas.showPage()
    canvas.save()
    loaded.documents[0].ground_truth_path.write_text("")
    result = BenchmarkRunner(loaded, parallel_workers=1).run().results[0]
    assert result.success and result.parse_outcome == "success_empty"
    assert Path(result.output_path).read_bytes() == b""
    assert result.output_sha256 == hashlib.sha256(b"").hexdigest()


def test_incompatible_input_keeps_its_planned_pair_visible(tmp_path):
    from PIL import Image

    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    image = tmp_path / "scan.png"
    Image.new("RGB", (20, 20), "white").save(image)
    loaded.documents[0].input_path = image
    loaded.documents[0].input_type = "image"
    results = BenchmarkRunner(loaded, parallel_workers=1).run()
    assert len(results.results) == 1
    result = results.results[0]
    assert result.parse_outcome == "incompatible"
    assert not result.success and result.parse_time_seconds is None
    assert results.failure_count == 1


@pytest.mark.parametrize(
    "name",
    [
        "legacy_duplicate_run.json",
        "retained_results/sec_filings_commercial_5docs.json",
    ],
)
def test_duplicate_foreign_and_wrong_counter_checkpoints_are_never_imported(tmp_path, name):
    import shutil

    from pdf_bench.persistence import load_results
    from pdf_bench.runner import BenchmarkRunner

    loaded = _loaded(tmp_path)
    checkpoint = tmp_path / "checkpoint.json"
    shutil.copyfile(Path(__file__).parent / "fixtures" / name, checkpoint)
    assert load_results(checkpoint).results
    before = checkpoint.read_bytes()
    with pytest.raises(ValueError, match="resumption is disabled"):
        BenchmarkRunner(loaded, parallel_workers=1).run(checkpoint_path=checkpoint)
    assert checkpoint.read_bytes() == before
    assert not loaded.results_dir.exists()
