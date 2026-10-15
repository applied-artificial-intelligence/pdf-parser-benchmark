"""Exercise fixed-population bundles through actual uncached parser execution."""

import copy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pdf_bench import invoice_comparison as comparison

UNIT = Path(__file__).resolve().parents[1] / ".workspace/work/2026-10-13-benchmark-rebuild"
QUALIFIED = UNIT / "invoice-reference-evidence/qualified-dc48e90363104d938465629738316513"
PROTOCOL = UNIT / "invoice-task-protocol.json"


def _plan(tmp_path, **options):
    return comparison.freeze_plan(
        QUALIFIED,
        PROTOCOL,
        tmp_path / "plan",
        document_ids=["invoice_001", "invoice_003"],
        **options,
    )


def test_cli_relative_paths_do_not_lose_the_first_produced_attempt(tmp_path):
    _plan(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "pdf_bench.invoice_comparison", "run", "plan", "runs"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    pointer = comparison.read_json(tmp_path / "runs/latest.json")
    summary = comparison.validate_run(tmp_path / "runs" / pointer["bundle"])
    assert summary["pypdf"]["counts"]["planned"] == 2
    assert summary["pdfplumber"]["counts"]["success_content"] == 2


def test_population_is_frozen_before_any_backend_initialization(tmp_path, monkeypatch):
    from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter

    def forbidden(*args, **kwargs):
        raise AssertionError("Population freeze initialized a backend")

    monkeypatch.setattr(PdfsmithAdapter, "_get_backend", forbidden)
    plan_dir = comparison.freeze_plan(QUALIFIED, PROTOCOL, tmp_path / "plan")
    plan = comparison.validate_plan(plan_dir)
    assert plan["scope"] == "primary"
    assert (
        len(plan["planned_pairs"])
        == len({(row["pipeline_id"], row["document_id"]) for row in plan["planned_pairs"]})
        == 200
    )
    assert all(row["eligibility"] == "eligible" for row in plan["documents"])
    assert plan["pipelines"] == [
        {
            "pipeline_id": name,
            "options": {
                "backend_name": name,
                "cache_mode": "bypass",
                **(
                    {"extraction_mode": "plain"}
                    if name == "pypdf"
                    else {
                        "layout": False,
                        "x_tolerance": 3.0,
                        "y_tolerance": 3.0,
                    }
                ),
            },
        }
        for name in ["pypdf", "pdfplumber"]
    ]


def test_actual_run_retains_all_pairs_outputs_stages_and_fixed_scores_after_relocation(tmp_path):
    plan = _plan(tmp_path)
    bundle = comparison.execute_plan(plan, tmp_path / "runs")
    summary = comparison.validate_run(bundle)
    assert summary["pypdf"]["task"]["documents_expected"] == 2
    assert summary["pypdf"]["task"]["document_success"] == 2
    assert summary["pdfplumber"]["task"]["fields_expected"] == 10
    assert summary["pdfplumber"]["task"]["fields_correct"] == 9
    rows = comparison.read_json(bundle / "journal.json")["attempts"]
    assert len(rows) == 4
    assert [row["order"] for row in rows] == list(range(4))
    assert len({row["output_path"] for row in rows}) == 4
    for row in rows:
        assert row["outcome"] == "success_content"
        assert row["parse_time_seconds"] > 0
        assert row["wall_time_seconds"] >= row["parse_time_seconds"]
        assert comparison.digest(bundle / row["output_path"]) == row["output_sha256"]
        assert set(row["stage_identities"]) == {"parse", "prediction", "grade"}
    relocated = tmp_path / "relocated" / bundle.name
    shutil.copytree(bundle, relocated)
    shutil.rmtree(bundle)
    shutil.rmtree(plan)
    assert comparison.validate_run(relocated) == summary


def test_changed_input_or_runtime_rejects_execution_before_attempts(tmp_path, monkeypatch):
    plan = _plan(tmp_path)
    source = plan / "inputs/invoice_001.pdf"
    original = source.read_bytes()
    source.write_bytes(b"corrupt changed input")
    with pytest.raises(ValueError, match="hash/location"):
        comparison.execute_plan(plan, tmp_path / "runs")
    assert not (tmp_path / "runs").exists()
    source.write_bytes(original)
    actual = comparison.runtime_identity
    monkeypatch.setattr(comparison, "runtime_identity", lambda: {**actual(), "python": "different"})
    with pytest.raises(ValueError, match="runtime differs"):
        comparison.execute_plan(plan, tmp_path / "runs")
    assert not (tmp_path / "runs").exists()


def test_real_initialization_failures_keep_all_eligible_inputs_and_zero_task_recovery(tmp_path):
    plan = _plan(tmp_path, pipeline_options={"pypdf": {"extraction_mode": "invalid"}})
    bundle = comparison.execute_plan(plan, tmp_path / "runs")
    summary = comparison.validate_run(bundle)
    failed = summary["pypdf"]
    assert failed["outcome_ids"]["initialization_failure"] == ["invoice_001", "invoice_003"]
    assert failed["task"]["documents_expected"] == 2
    assert failed["task"]["fields_expected"] == 10
    assert failed["task"]["fields_correct"] == failed["task"]["records_matched"] == 0
    assert failed["task"]["record_micro_f1"] == 0
    assert summary["pdfplumber"]["task"]["fields_expected"] == 10
    assert summary["common_content_ids"] == []
    for row in comparison.read_json(bundle / "journal.json")["attempts"][:2]:
        assert row["parse_time_seconds"] is None
        assert row["wall_time_seconds"] > 0
        assert row["output_path"] is None


def test_required_grader_exception_invalidates_aggregate_without_claiming_parse_failure(
    tmp_path,
    monkeypatch,
):
    plan = _plan(tmp_path)

    def broken(prediction, reference):
        raise RuntimeError("Controlled required evaluator failure")

    monkeypatch.setattr(comparison, "grade_invoice", broken)
    bundle = comparison.execute_plan(plan, tmp_path / "runs")
    summary = comparison.validate_run(bundle)
    assert summary["pypdf"]["counts"]["success_content"] == 2
    assert summary["pypdf"]["counts"]["scored"] == 0
    assert summary["pypdf"]["task"]["valid"] is False
    assert summary["pdfplumber"]["task"]["valid"] is False
    grade = comparison.read_json(bundle / "attempts/pypdf--invoice_001/grade.json")
    assert grade["evaluation_error"]["stage"] == "grading"


@pytest.mark.parametrize("target", ["prediction.json", "completion.json", "latest.json"])
def test_real_write_failure_cannot_replace_previous_completed_bundle(tmp_path, monkeypatch, target):
    plan = _plan(tmp_path)
    output = tmp_path / "runs"
    prior = comparison.execute_plan(plan, output)
    pointer_before = (output / "latest.json").read_bytes()
    files_before = {
        p.relative_to(prior).as_posix(): p.read_bytes() for p in prior.rglob("*") if p.is_file()
    }
    writer = comparison.write_json_atomic

    def fail(path, payload):
        if path.name == target:
            raise OSError("Controlled write failure")
        writer(path, payload)

    monkeypatch.setattr(comparison, "write_json_atomic", fail)
    with pytest.raises(OSError, match="Controlled write failure"):
        comparison.execute_plan(plan, output)
    assert (output / "latest.json").read_bytes() == pointer_before
    assert {
        p.relative_to(prior).as_posix(): p.read_bytes() for p in prior.rglob("*") if p.is_file()
    } == files_before
    comparison.validate_run(prior)


def test_deleted_required_prediction_cannot_be_published_even_if_remaining_json_is_valid(
    tmp_path,
    monkeypatch,
):
    plan = _plan(tmp_path)
    output = tmp_path / "runs"
    prior = comparison.execute_plan(plan, output)
    pointer_before = (output / "latest.json").read_bytes()
    writer = comparison.write_json_atomic

    def drop_required(path, payload):
        if path.name == "completion.json":
            victim = path.parent / "attempts/pypdf--invoice_001/prediction.json"
            victim.unlink()
            payload["files"].pop("attempts/pypdf--invoice_001/prediction.json")
        writer(path, payload)

    monkeypatch.setattr(comparison, "write_json_atomic", drop_required)
    with pytest.raises((ValueError, FileNotFoundError)) as error:
        comparison.execute_plan(plan, output)
    assert "prediction.json" in str(error.value) or "missing required artifacts" in str(error.value)
    incomplete = list(output.glob(".incomplete-*"))
    assert len(incomplete) == 1
    assert len(comparison.read_json(incomplete[0] / "journal.json")["attempts"]) == 4
    assert (output / "latest.json").read_bytes() == pointer_before
    comparison.validate_run(prior)


def test_backend_options_input_reference_and_protocol_have_separate_stage_identities(tmp_path):
    plan_dir = _plan(tmp_path)
    plan = comparison.validate_plan(plan_dir)
    bundle = comparison.execute_plan(plan_dir, tmp_path / "runs")
    pair = comparison.read_json(bundle / "journal.json")["attempts"][0]
    raw = pair["output_sha256"]
    prediction = comparison.digest(bundle / "attempts" / pair["pair_id"] / "prediction.json")
    reference = plan["documents"][0]["reference_sha256"]
    baseline = comparison.stage_identities(pair, plan, raw, prediction, reference)
    assert baseline == pair["stage_identities"]
    for field, value in [
        ("runtime_identity", comparison.identity({"changed_backend": True})),
        ("timeout_seconds", 90),
    ]:
        changed = copy.deepcopy(plan)
        changed[field] = value
        assert (
            comparison.stage_identities(pair, changed, raw, prediction, reference)["parse"]
            != baseline["parse"]
        )
    changed = copy.deepcopy(plan)
    changed["documents"][0]["pdf_sha256"] = comparison.identity({"changed_input": True})
    assert (
        comparison.stage_identities(pair, changed, raw, prediction, reference)["parse"]
        != baseline["parse"]
    )
    changed = copy.deepcopy(plan)
    changed["pipelines"][0]["options"]["extraction_mode"] = "layout"
    assert (
        comparison.stage_identities(pair, changed, raw, prediction, reference)["parse"]
        != baseline["parse"]
    )
    changed_reference = comparison.identity({"corrected_reference": True})
    changed = comparison.stage_identities(pair, plan, raw, prediction, changed_reference)
    assert changed["parse"] == baseline["parse"]
    assert changed["prediction"] == baseline["prediction"]
    assert changed["grade"] != baseline["grade"]
    changed_pair = {**pair, "extractor_sha256": comparison.identity({"new_extractor": True})}
    changed = comparison.stage_identities(changed_pair, plan, raw, prediction, reference)
    assert changed["parse"] == baseline["parse"]
    assert changed["prediction"] != baseline["prediction"]
    changed_pair = {**pair, "grader_sha256": comparison.identity({"new_grader": True})}
    changed = comparison.stage_identities(changed_pair, plan, raw, prediction, reference)
    assert changed["parse"] == baseline["parse"]
    assert changed["prediction"] == baseline["prediction"]
    assert changed["grade"] != baseline["grade"]


def test_missing_terminal_pair_is_incomplete_instead_of_a_smaller_success_population(tmp_path):
    plan = _plan(tmp_path)
    bundle = comparison.execute_plan(plan, tmp_path / "runs")
    manifest = comparison.read_json(bundle / "frozen-plan/plan.json")
    rows = comparison.read_json(bundle / "journal.json")["attempts"]
    grades = {
        row["pair_id"]: comparison.read_json(bundle / "attempts" / row["pair_id"] / "grade.json")[
            "grade"
        ]
        for row in rows
    }
    with pytest.raises(ValueError, match="Incomplete execution"):
        comparison.summarize(manifest, rows[:-1], grades)
