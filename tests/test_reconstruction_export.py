"""Reproduce real parser artifacts with frozen inputs and isolated offline grading."""

import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pdf_bench import invoice_comparison as comparison
from pdf_bench.invoice_reproduction import (
    compare_runs,
    faithful_representation_controls,
    summarize_cells,
)

UNIT = Path(__file__).resolve().parents[1] / ".workspace/work/2026-10-13-benchmark-rebuild"


@pytest.fixture(scope="module")
def fresh_pair(tmp_path_factory):
    root = tmp_path_factory.mktemp("fresh-invoice-executions")
    plan = comparison.freeze_plan(
        UNIT / "invoice-reference-evidence/qualified-dc48e90363104d938465629738316513",
        UNIT / "invoice-task-protocol.json",
        root / "plan",
        document_ids=[f"invoice_{number:03d}" for number in range(1, 7)],
    )
    first = comparison.execute_plan(plan, root / "runs")
    second = comparison.execute_plan(plan, root / "runs")
    return plan, first, second


def test_two_fresh_actual_runs_match_retained_predictions_and_task_scores(fresh_pair):
    _, first, second = fresh_pair
    result = compare_runs(first, second)
    assert len(result["matching_pairs"]) == 12
    assert result["first_completion_sha256"] != result["second_completion_sha256"]
    assert set(result["matching_pairs"]) == {
        f"{name}--invoice_{number:03d}"
        for name in ["pypdf", "pdfplumber"]
        for number in range(1, 7)
    }


def test_reference_derived_format_control_is_separate_from_actual_parser_quality(fresh_pair):
    plan, first, _ = fresh_pair
    control = faithful_representation_controls(plan)
    assert control["aggregate"]["document_success"] == 6
    assert control["aggregate"]["record_micro_f1"] == 1
    actual = comparison.validate_run(first)
    assert actual["pdfplumber"]["task"]["document_success"] < 6
    cells = summarize_cells(first)
    assert len(cells["pypdf"]) == len(cells["pdfplumber"]) == 6
    assert sum(cell["documents_expected"] for cell in cells["pdfplumber"].values()) == 6


def test_hundred_invoice_fills_remain_six_source_cells_in_reporting():
    bundle = UNIT / "invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c"
    cells = summarize_cells(bundle)
    expected_cells = {
        "enterprise/simple",
        "enterprise/medium",
        "small_business/simple",
        "small_business/medium",
        "economy/medium",
        "economy/complex",
    }
    for name in ["pypdf", "pdfplumber"]:
        assert set(cells[name]) == expected_cells
        assert sum(row["documents_expected"] for row in cells[name].values()) == 100
        assert sum(row["fields_expected"] for row in cells[name].values()) == 500
        assert sum(row["records_expected"] for row in cells[name].values()) == 696
        assert sorted(doc_id for row in cells[name].values() for doc_id in row["eligible_ids"]) == [
            f"invoice_{number:03d}" for number in range(1, 101)
        ]


def _offline(bundle):
    return subprocess.run(
        [sys.executable, "-I", "-S", str(bundle / "frozen-plan/offline-regrade.py"), str(bundle)],
        cwd=bundle,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def test_relocated_offline_regrade_needs_no_input_pdfs_parser_imports_or_original_paths(
    fresh_pair,
    tmp_path,
):
    _, first, _ = fresh_pair
    relocated = tmp_path / "evidence"
    shutil.copytree(first, relocated)
    shutil.rmtree(relocated / "frozen-plan/inputs")
    for directory in (relocated / "attempts").glob("*/parser-output"):
        shutil.rmtree(directory)
    result = _offline(relocated)
    assert result.returncode == 0, result.stderr
    regraded = json.loads(result.stdout)
    assert regraded["pairs_regraded"] == 12
    summary = comparison.validate_run(first)
    assert regraded["task_aggregates"] == {
        name: summary[name]["task"] for name in ["pypdf", "pdfplumber"]
    }


def test_offline_regrade_rejects_changed_prediction_bytes_instead_of_reusing_scores(
    fresh_pair,
    tmp_path,
):
    _, first, _ = fresh_pair
    relocated = tmp_path / "evidence"
    shutil.copytree(first, relocated)
    prediction_path = relocated / "attempts/pypdf--invoice_001/prediction.json"
    prediction = json.loads(prediction_path.read_bytes())
    prediction["fields"]["grand_total"] = "0"
    prediction_path.write_text(json.dumps(prediction))
    result = _offline(relocated)
    assert result.returncode != 0
    assert "Frozen artifact changed or is missing" in result.stderr


def test_reproduction_rejects_a_different_frozen_backend_configuration(fresh_pair, tmp_path):
    _, first, _ = fresh_pair
    plan = comparison.freeze_plan(
        UNIT / "invoice-reference-evidence/qualified-dc48e90363104d938465629738316513",
        UNIT / "invoice-task-protocol.json",
        tmp_path / "different-plan",
        document_ids=[f"invoice_{number:03d}" for number in range(1, 7)],
        pipeline_options={"pypdf": {"extraction_mode": "layout"}},
    )
    different = comparison.execute_plan(plan, tmp_path / "different-runs")
    with pytest.raises(ValueError, match="identical frozen plan"):
        compare_runs(first, different)


def test_partial_failure_review_cannot_replace_a_complete_source_bound_audit(fresh_pair, tmp_path):
    _, first, _ = fresh_pair
    script = Path(__file__).resolve().parents[1] / "scripts/build_invoice_failure_audit.py"
    build = runpy.run_path(str(script))["build"]
    candidate_path = tmp_path / "candidates.json"
    candidates = build(first, candidate_path)
    assert candidates["failed_pair_count"] == 3
    assert all(row["review_status"] == "unreviewed" for row in candidates["entries"])
    review = {
        "method": "Mechanism-test annotations of the known six development outputs",
        "candidate_sha256": comparison.digest(candidate_path),
        "decisions": [
            {
                "pair_id": "pdfplumber--invoice_001",
                "causes": ["unsupported_extractor_representation"],
                "note": "Known final-row continuation is outside the selected Markdown table.",
            },
            {
                "pair_id": "pdfplumber--invoice_003",
                "causes": ["lost_or_misassociated_parser_content"],
                "note": "Known FROM/TO column flattening prevents vendor assignment.",
            },
            {
                "pair_id": "pdfplumber--invoice_006",
                "causes": ["lost_or_misassociated_parser_content"],
                "note": "Known FROM/TO column flattening prevents vendor assignment.",
            },
        ],
    }
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(review))
    final = tmp_path / "audit.json"
    completed = build(first, final, review_path)
    assert completed["reviewed_failure_pairs"] == 3
    previous = final.read_bytes()
    review["decisions"].pop()
    review_path.write_text(json.dumps(review))
    with pytest.raises(ValueError, match="Review is incomplete"):
        build(first, final, review_path)
    assert final.read_bytes() == previous
