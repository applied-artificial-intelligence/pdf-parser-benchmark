"""Reproduce execution defects through actual adapters and runner dispatch."""

import hashlib
from pathlib import Path

import pytest

from pdf_bench.runner import _extract_parser_init_args, _worker_run_single
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter
from pdf_bench.utils.caching import cache_key, store_cached

SOURCE = Path(__file__).parent / "fixtures/invoice_sources/pdfs/invoice_001.pdf"


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
