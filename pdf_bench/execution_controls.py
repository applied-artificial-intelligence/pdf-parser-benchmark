"""Explicit mechanism controls, separate from parser-quality observations."""

import argparse
import hashlib
import os
import time
from dataclasses import asdict
from pathlib import Path

from reportlab.pdfgen import canvas

from pdf_bench.execution import execute_parser
from pdf_bench.persistence import write_json_atomic
from pdf_bench.systems.base_parser import BaseParser
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter


class DelayedControl(BaseParser):
    """A started, delayed writer tests deadline enforcement, not parser quality."""

    @property
    def name(self) -> str:
        return "delayed-mechanism-control"

    @property
    def version(self) -> str:
        return "1"

    def parse(self, pdf_path: Path, output_dir: Path) -> Path:
        (output_dir / "started").write_text("Parse call started")
        time.sleep(120)
        result = output_dir / "late-output.md"
        result.write_text("Work was not stopped")
        return result


def run_controls(source: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    inputs = output / "inputs"
    inputs.mkdir()
    corrupt = inputs / "truncated.pdf"
    corrupt.write_bytes(source.read_bytes()[:250])
    empty = inputs / "blank.pdf"
    document = canvas.Canvas(str(empty), invariant=1)
    document.showPage()
    document.save()
    rows = []
    for name in ["pypdf", "pdfplumber"]:
        for path, expected in [(corrupt, "parser_failure"), (empty, "success_empty")]:
            attempt = execute_parser(
                PdfsmithAdapter,
                {"backend_name": name, "cache_mode": "bypass"},
                path,
                output / f"{name}-{path.stem}",
                30,
            )
            if attempt.outcome != expected:
                raise ValueError(f"Mechanism control disagrees: {name}/{path.name}: {attempt}")
            row = {
                "control_id": f"{name}-{path.stem}",
                "expected_outcome": expected,
                "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                **asdict(attempt),
            }
            rows.append(row)
    delayed = output / "delayed"
    attempt = execute_parser(DelayedControl, {}, empty, delayed, 5)
    if (
        attempt.outcome != "enforced_timeout"
        or attempt.parse_time_seconds is None
        or not (delayed / "parser-output/started").exists()
        or (delayed / "parser-output/late-output.md").exists()
    ):
        raise ValueError("Delayed control did not establish started and stopped work")
    try:
        os.kill(attempt.worker_pid, 0)
    except ProcessLookupError:
        pass
    else:
        raise ValueError("Timed-out control worker remains alive")
    rows.append(
        {
            "control_id": "delayed-writer",
            "expected_outcome": "enforced_timeout",
            "worker_stopped": True,
            **asdict(attempt),
        }
    )
    for row in rows:
        row["output_path"] = (
            Path(row["output_path"]).relative_to(output.resolve()).as_posix()
            if row["output_path"]
            else None
        )
        row["returned_path"] = (
            Path(row["returned_path"]).relative_to(output.resolve()).as_posix()
            if row["returned_path"]
            else None
        )
    result = {
        "scope": "Mechanism controls only; excluded from primary 200-pair population",
        "attempts": rows,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    write_json_atomic(output / "controls.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(run_controls(args.source, args.output)["scope"])
