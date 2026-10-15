"""Actual local parsers and explicitly labeled controls exercise isolated attempt execution."""

import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from pdf_bench.execution import execute_parser
from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter

SOURCE = Path(__file__).parent / "fixtures/invoice_sources/pdfs/invoice_001.pdf"


class ControlledBackend(BaseParser):
    """Mechanism controls only; these outcomes do not measure parser quality."""

    def __init__(self, mode: str = "empty") -> None:
        self.mode = mode
        if mode == "init-error":
            raise RuntimeError("Controlled initialization failure")

    @property
    def name(self) -> str:
        return "controlled-backend"

    @property
    def version(self) -> str:
        return "control"

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        if self.mode == "error":
            raise RuntimeError("Ordinary parsing error containing exceeded")
        if self.mode == "delay":
            (output_dir / "started").write_text("The parse call started")
            time.sleep(20)
            (output_dir / "late-write").write_text("Work was not stopped")
        target = output_dir / "result.md"
        target.write_text(" \n" if self.mode == "empty" else "Controlled content")
        return target


def test_actual_adapter_retains_exact_output_bytes_and_success_content(tmp_path):
    result = execute_parser(
        PdfsmithAdapter,
        {"backend_name": "pypdf", "cache_mode": "bypass"},
        SOURCE,
        tmp_path / "attempt",
        30,
    )
    assert result.outcome == "success_content", result.error
    assert "INV-98034" in result.output_path.read_text()
    assert result.output_sha256 == hashlib.sha256(result.output_path.read_bytes()).hexdigest()
    assert Path(result.returned_path).read_bytes() == result.output_path.read_bytes()
    assert result.parse_time_seconds > 0
    assert result.wall_time_seconds >= result.parse_time_seconds


@pytest.mark.parametrize(
    ("mode", "outcome"),
    [
        ("empty", "success_empty"),
        ("error", "parser_failure"),
        ("init-error", "initialization_failure"),
    ],
)
def test_empty_failure_and_initialization_are_distinct_controls(tmp_path, mode, outcome):
    result = execute_parser(ControlledBackend, {"mode": mode}, SOURCE, tmp_path / mode, 30)
    assert result.outcome == outcome
    if mode == "init-error":
        assert result.parse_time_seconds is None
    else:
        assert result.parse_time_seconds > 0
    if mode == "empty":
        assert result.output_path.read_bytes() == b" \n"
    elif mode == "error":
        assert "exceeded" in result.error
        assert result.error_type == "RuntimeError"


def test_corrupt_pdf_records_started_failure_time_from_actual_pypdf(tmp_path):
    source = tmp_path / "corrupt.pdf"
    source.write_bytes(b"%PDF-1.7\ntruncated upload\n")
    result = execute_parser(
        PdfsmithAdapter,
        {"backend_name": "pypdf", "cache_mode": "bypass"},
        source,
        tmp_path / "attempt",
        30,
    )
    assert result.outcome == "parser_failure"
    assert result.parse_time_seconds > 0
    assert result.output_path is None


def test_enforced_timeout_stops_started_worker_before_any_late_output(tmp_path):
    directory = tmp_path / "delayed"
    result = execute_parser(ControlledBackend, {"mode": "delay"}, SOURCE, directory, 5)
    assert result.outcome == "enforced_timeout"
    assert result.error_type == "EnforcedParseTimeoutError"
    assert (directory / "parser-output/started").exists()
    assert result.parse_time_seconds > 0
    assert not (directory / "parser-output/late-write").exists()
    assert result.output_path is None
    with pytest.raises(ProcessLookupError):
        os.kill(result.worker_pid, 0)


def test_same_stem_different_backend_options_have_exclusive_outputs(tmp_path):
    def call(layout):
        return execute_parser(
            PdfsmithAdapter,
            {"backend_name": "pdfplumber", "cache_mode": "bypass", "layout": layout},
            SOURCE,
            tmp_path / f"layout-{layout}",
            30,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = list(pool.map(call, [False, True]))
    assert first.outcome == second.outcome == "success_content"
    assert first.output_path != second.output_path
    assert first.output_sha256 != second.output_sha256
    before = first.output_path.read_bytes()
    with pytest.raises(FileExistsError):
        call(False)
    assert first.output_path.read_bytes() == before
