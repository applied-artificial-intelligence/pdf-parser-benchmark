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
