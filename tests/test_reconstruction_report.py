"""Verify report claims against actual retained evidence and preserve prior exports."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from pdf_bench import reconstruction_report as report

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / ".workspace/work/2026-10-13-benchmark-rebuild"


@pytest.fixture
def report_inputs(tmp_path):
    root = Path(tempfile.mkdtemp(prefix="report-test-", dir=ROOT / "data_exports"))
    for p in UNIT.iterdir():
        if p.is_file() and (
            p.suffix == ".json" or p.name in {"technical-report.template.md", "replay-protocol.txt"}
        ):
            shutil.copyfile(p, root / p.name)
    shutil.copytree(UNIT / "retained-evidence", root / "retained-evidence")
    for checkpoint in ["invoice-run-checkpoint.json", "parsebench-run-checkpoint.json"]:
        name = json.loads((root / checkpoint).read_bytes())["primary_bundle"]
        shutil.copytree(UNIT / name, root / name)
    try:
        yield root, tmp_path / "reports"
    finally:
        shutil.rmtree(root)


def test_exported_numerators_and_denominators_recompute_from_actual_grades(report_inputs):
    unit, output = report_inputs
    bundle = report.publish_report(ROOT, unit, output)
    exported = report.validate_export(ROOT, bundle)
    claims = {r["id"]: r for r in exported["claims"]}
    primary = (
        unit / json.loads((unit / "invoice-run-checkpoint.json").read_bytes())["primary_bundle"]
    )
    for pipeline in ["pypdf", "pdfplumber"]:
        grades = [
            json.loads(p.read_bytes())["grade"]
            for p in (primary / "attempts").glob(f"{pipeline}--*/grade.json")
        ]
        claim = claims[f"invoice-{pipeline}-document_success"]
        assert claim["value"] == sum(r["document_success"] for r in grades)
        assert claim["denominator"]["value"] == len(grades) == 100
        assert claims[f"invoice-{pipeline}-records_matched"]["value"] == sum(
            r["records_matched"] for r in grades
        )
    assert claims["invoice-pypdf-document_success"]["value"] == 84
    assert claims["invoice-pdfplumber-document_success"]["value"] == 55
    assert len([c for c in claims.values() if c["id"].startswith("cell-")]) == 12


def test_public_claims_keep_their_own_metric_population_and_plan_context(report_inputs):
    unit, output = report_inputs
    bundle = report.publish_report(ROOT, unit, output)
    exported = report.validate_export(ROOT, bundle)
    public_plan = (
        unit
        / json.loads((unit / "parsebench-run-checkpoint.json").read_bytes())["primary_bundle"]
        / "frozen-plan/plan.json"
    )
    for claim in exported["claims"]:
        if claim["id"].startswith("public-"):
            context = exported["contexts"][claim["context"]]
            assert context["plan"]["sha256"] == report.digest(public_plan)
            assert "qualified_public_subset" == claim["tier"]
    assert (
        exported["contexts"]["public"]["plan"]["sha256"]
        != exported["contexts"]["invoice"]["plan"]["sha256"]
    )


def test_changed_actual_raw_output_cannot_replace_a_valid_report_pointer(report_inputs):
    unit, output = report_inputs
    report.publish_report(ROOT, unit, output)
    previous = (output / "latest.json").read_bytes()
    primary = (
        unit / json.loads((unit / "invoice-run-checkpoint.json").read_bytes())["primary_bundle"]
    )
    outputs = sorted((primary / "attempts").glob("pypdf--*/retained-output.md"))
    shutil.copyfile(outputs[1], outputs[0])
    with pytest.raises(ValueError, match="Artifact hash/location mismatch"):
        report.publish_report(ROOT, unit, output)
    assert (output / "latest.json").read_bytes() == previous


def test_incomplete_real_failure_review_cannot_silently_drop_a_hard_pair(report_inputs):
    unit, output = report_inputs
    report.publish_report(ROOT, unit, output)
    previous = (output / "latest.json").read_bytes()
    path = unit / "invoice-failure-audit.json"
    audit = json.loads(path.read_bytes())
    audit["entries"].pop()
    path.write_text(json.dumps(audit))
    with pytest.raises(ValueError, match="failure audit is incomplete"):
        report.publish_report(ROOT, unit, output)
    assert (output / "latest.json").read_bytes() == previous


def test_unmeasured_operating_cost_and_current_historical_backends_remain_unknown(report_inputs):
    unit, output = report_inputs
    bundle = report.publish_report(ROOT, unit, output)
    exported = report.validate_export(ROOT, bundle)
    assert exported["contexts"]["invoice"]["api_charges"] == 0
    assert exported["contexts"]["invoice"]["total_operating_cost"] is None
    assert all(r["current_backend_identity"] is None for r in exported["historical_tracks"])


def test_historical_tracks_cannot_be_promoted_to_new_qualified_results(report_inputs):
    unit, output = report_inputs
    bundle = report.publish_report(ROOT, unit, output)
    exported = report.validate_export(ROOT, bundle)
    registry = report.load_registry_bundle(unit / "retained-evidence")
    actual = {
        r["story_annotation"]["family"]: r["evidence_tier"]
        for r in registry["artifacts"]
        if r.get("story_annotation")
    }
    assert {r["family"]: r["evidence_tier"] for r in exported["historical_tracks"]} == actual
    assert (
        next(r for r in exported["historical_tracks"] if r["family"] == "invoices_source_first")[
            "evidence_tier"
        ]
        == "historical"
    )


def test_actual_performance_selected_population_reverses_record_ordering(report_inputs):
    unit, output = report_inputs
    bundle = report.publish_report(ROOT, unit, output)
    bias = json.loads((bundle / "selection-bias.json").read_bytes())
    assert bias["full"]["pypdf"]["record_micro_f1"] < bias["full"]["pdfplumber"]["record_micro_f1"]
    assert (
        bias["selected"]["pypdf"]["record_micro_f1"]
        > bias["selected"]["pdfplumber"]["record_micro_f1"]
    )
    assert len(bias["selected_ids"]) == 84
    assert bias["selected"]["pypdf"]["document_success"] == 84
    assert bias["selected"]["pdfplumber"]["document_success"] == 48


def test_changed_claim_value_is_rejected_by_the_consumer_against_original_source(report_inputs):
    unit, output = report_inputs
    bundle = report.publish_report(ROOT, unit, output)
    claims_path = bundle / "claims.json"
    payload = json.loads(claims_path.read_bytes())
    payload["claims"][0]["value"] = 0
    claims_path.write_text(json.dumps(payload))
    manifest = json.loads((bundle / "manifest.json").read_bytes())
    manifest["files"]["claims.json"] = report.digest(claims_path)
    (bundle / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="claim differs from its source"):
        report.validate_export(ROOT, bundle)
