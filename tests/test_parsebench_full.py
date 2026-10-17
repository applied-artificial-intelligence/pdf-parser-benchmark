import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pdf_bench.parsebench_full import interleaved_inputs, validate_journal, validate_population
from pdf_bench.parsebench_roster import local_roster


def test_offline_native_result_writer_does_not_require_parser_dependencies(tmp_path):
    script = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
def block(event, args):
    if event == "import" and args[0] == "pdf_bench.runner":
        raise ModuleNotFoundError("The parsing runner is absent from the native runtime")
sys.addaudithook(block)
from pdf_bench.persistence import write_json_atomic
write_json_atomic(Path(sys.argv[2]), {"native": True})
assert "pdf_bench.runner" not in sys.modules
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            script,
            str(Path(__file__).resolve().parents[1]),
            str(tmp_path / "result.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "result.json").read_text().strip().endswith("}")


def test_readiness_inventory_never_initializes_a_paid_backend(monkeypatch):
    from pdfsmith.backends.registry import BACKEND_REGISTRY

    def forbidden():
        raise AssertionError("Paid backend initialization would require approval")

    for info in BACKEND_REGISTRY.values():
        if info.weight == "commercial":
            monkeypatch.setattr(info, "loader", forbidden)
    rows = local_roster()
    paid = [r for r in rows if r["paid"]]
    assert paid
    assert all("initialization_error" not in row for row in paid)


def test_a_shared_text_input_remains_two_dimension_cases_without_duplicate_parsing():
    inventory = {
        "cases": [
            {"source_path": "docs/text/a.pdf", "group": "text_content"},
            {"source_path": "docs/text/a.pdf", "group": "text_formatting"},
        ]
    }
    coverage = {"inputs": [{"source_path": "docs/text/a.pdf"}]}
    validate_population(coverage, inventory)
    coverage["inputs"].append({"source_path": "docs/text/a.pdf"})
    with pytest.raises(ValueError, match="population"):
        validate_population(coverage, inventory)


def test_slow_parser_execution_order_covers_dimensions_before_exhausting_one_group():
    rows = [
        {"source_path": f"docs/{group}/{index}.pdf", "groups": [group]}
        for group in ["chart", "layout", "table", "text_content"]
        for index in range(3)
    ]
    rows[-1]["groups"].append("text_formatting")
    ordered = interleaved_inputs(rows)
    assert len({r["source_path"] for r in ordered}) == 12
    assert {r["groups"][0] for r in ordered[:4]} == {"chart", "layout", "table", "text_content"}


def test_failed_parse_cannot_disappear_from_full_population_denominator():
    plan = {
        "inputs": [
            {"source_path": "a.pdf", "sha256": "a"},
            {"source_path": "b.pdf", "sha256": "b"},
        ]
    }
    rows = [
        {"source_path": "a.pdf", "input_sha256": "a", "outcome": "success_content"},
        {"source_path": "b.pdf", "input_sha256": "b", "outcome": "parser_failure"},
    ]
    validate_journal(plan, rows)
    with pytest.raises(ValueError, match="Incomplete"):
        validate_journal(plan, rows[:1])
    rows[1]["input_sha256"] = "other"
    with pytest.raises(ValueError, match="identity"):
        validate_journal(plan, rows)


@pytest.fixture
def resumable_run(tmp_path):
    import fitz

    from pdf_bench.parsebench_roster import runtime_identity
    from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter

    source = tmp_path / "sources"
    source.mkdir()
    with fitz.open() as document:
        document.new_page().insert_text((72, 72), "A real resumable parser input")
        document.save(source / "valid.pdf")
    (source / "corrupt.pdf").write_bytes(b"%PDF-broken")
    target = tmp_path / "run"
    target.mkdir()
    adapter = PdfsmithAdapter("pypdf", cache_mode="bypass")
    plan = {
        "backend": "pypdf",
        "runtime": runtime_identity(),
        "options": adapter._get_backend().effective_options,
        "input_root": str(source),
        "timeout_seconds": 15,
        "inputs": [
            {"source_path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(source.iterdir())
        ],
    }
    (target / "plan.json").write_text(json.dumps(plan))
    return target


def test_real_parser_resume_preserves_failures_interrupted_files_and_rejects_changed_output(
    resumable_run,
):
    from pdf_bench.parsebench_full import resume, retained_attempts

    target = resumable_run
    interrupted = target / "attempts" / "interrupted"
    interrupted.mkdir(parents=True)
    (interrupted / "raw.md").write_text("Interrupted raw evidence")
    deadline = datetime.now(timezone.utc) + timedelta(hours=1)
    resume(target, 2, deadline)
    plan = json.loads((target / "plan.json").read_text())
    rows = retained_attempts(target, plan)
    assert rows["valid.pdf"]["outcome"] == "success_content"
    assert rows["corrupt.pdf"]["outcome"] == "parser_failure"
    assert "real resumable" in (target / rows["valid.pdf"]["output_path"]).read_text()
    assert (interrupted / "raw.md").read_text() == "Interrupted raw evidence"
    before = {p: p.read_bytes() for p in (target / "attempts").rglob("*") if p.is_file()}
    resume(target, 2, deadline)
    assert {p: p.read_bytes() for p in (target / "attempts").rglob("*") if p.is_file()} == before
    output = target / rows["valid.pdf"]["output_path"]
    output.write_text("Modified retained parser bytes")
    sessions = set((target / "resumptions").iterdir())
    with pytest.raises(ValueError, match="output bytes"):
        resume(target, 2, deadline)
    assert set((target / "resumptions").iterdir()) == sessions


def test_cutoff_does_not_admit_calls_that_cannot_finish(resumable_run):
    from pdf_bench.parsebench_full import resume

    resume(resumable_run, 2, datetime.now(timezone.utc) + timedelta(seconds=70))
    assert not (resumable_run / "attempts").exists()
    assert not (resumable_run / "parse-complete.json").exists()


def test_overnight_queue_runs_real_calls_and_resumes_without_repeating_attempts(
    resumable_run, monkeypatch
):
    import os

    from pdf_bench import parsebench_overnight as overnight

    target = resumable_run
    unit = target.parent
    evidence = unit / "full-comparison-evidence"
    evidence.mkdir()
    target.rename(evidence / "pypdf")
    target = evidence / "pypdf"
    plan = json.loads((target / "plan.json").read_text())
    (unit / "sample.json").write_text(json.dumps([r["source_path"] for r in plan["inputs"]]))
    config = {
        "max_calls": 2,
        "cpus": sorted(os.sched_getaffinity(0)),
        "nice": os.getpriority(os.PRIO_PROCESS, 0),
        "sample": "sample.json",
        "jobs": [
            {
                "backend": "pypdf",
                "run": "pypdf",
                "python": sys.executable,
                "workers": 2,
                "priority": 0,
                "plan_sha256": hashlib.sha256((target / "plan.json").read_bytes()).hexdigest(),
            }
        ],
    }
    policy = unit / "policy.json"
    policy.write_text(json.dumps(config))
    monkeypatch.setattr(
        overnight, "window_end", lambda _: datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        monkeypatch.setenv(name, "2")
    overnight.run_queue(policy)
    assert json.loads((unit / "overnight-status.json").read_text())["state"] == "parse_complete"
    assert len(list((target / "attempts").glob("*/attempt.json"))) == 2
    assert (target / "timing-pilot" / "parse-complete.json").exists()
    assert (target / "timing-pilot-w2" / "parse-complete.json").exists()
    before = {p: p.read_bytes() for p in target.rglob("attempt.json")}
    overnight.run_queue(policy)
    assert {p: p.read_bytes() for p in target.rglob("attempt.json")} == before
