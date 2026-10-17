"""Exercise real parser calls and native upstream scoring on selected public inputs."""

import json
import runpy
import shutil
import subprocess
from pathlib import Path

import pytest

from pdf_bench import parsebench_comparison as comparison

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / ".workspace/work/2026-10-13-benchmark-rebuild"
NATIVE = ROOT / "data_exports/parsebench/native-evaluator/bin/python"


@pytest.fixture(scope="module")
def public_runs(tmp_path_factory):
    root = tmp_path_factory.mktemp("native-public-comparison")
    source = UNIT / "parsebench-comparison-plan-v1"
    wanted = {"docs/table/Apple 10-k_page76.pdf", "docs/text/text_simple__agreement.pdf"}
    runtime = runpy.run_path(str(ROOT / "scripts/parsebench_runtime.py"))
    if not NATIVE.exists():
        runtime["install_environment"](
            NATIVE.parent.parent,
            UNIT / "parsebench-runtime-artifacts",
            "3.14.3",
            ["parse_bench-1.0.5-py3-none-any.whl"],
        )
    selection = comparison.read_json(source / "selection.json")
    selection["cases"] = [r for r in selection["cases"] if r["source_path"] in wanted]
    path = root / "selection.json"
    path.write_text(json.dumps(selection))
    sources = runtime["hydrate_sources"](source, root / "sources", wanted)
    source_map = root / "sources.json"
    source_map.write_text(json.dumps(sources))
    manifest = comparison.read_json(UNIT / "parsebench-snapshot.json")
    objects = root / "objects"
    objects.mkdir()
    for group in ["text_content", "table"]:
        name = group + ".jsonl"
        data = (source / "references" / name).read_bytes()
        temporary = objects / "annotation"
        temporary.write_bytes(data)
        hashed = comparison.digest(temporary)
        temporary.rename(objects / hashed)
        manifest["files"][name]["sha256"] = hashed
    snapshot = root / "snapshot.json"
    snapshot.write_text(json.dumps(manifest))
    plan = comparison.freeze(
        path,
        snapshot,
        objects,
        source_map,
        NATIVE,
        ROOT / "pdf_bench/parsebench_native.py",
        root / "plan",
    )
    first = comparison.execute(plan, root / "runs", NATIVE)
    second = comparison.execute(plan, root / "runs", NATIVE)
    return plan, first, second


def independent_native(bundle):
    result = subprocess.run(
        [str(NATIVE), "-I", str(bundle / "frozen-plan/native-worker.py"), str(bundle)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_real_outputs_use_the_actual_upstream_evaluator_in_both_dimensions(public_runs):
    _, first, _ = public_runs
    saved = comparison.read_json(first / "native-results.json")
    assert independent_native(first) == saved
    summary = comparison.validate_run(first)
    for pipeline in ["pypdf", "pdfplumber"]:
        for group in ["text_content", "table"]:
            assert summary[pipeline][group]["valid"]
            assert summary[pipeline][group]["planned_count"] == 1
            assert summary[pipeline][group]["scored_count"] == 1
    assert summary["pdfplumber"]["table"]["mean"] > 0


def test_two_fresh_public_runs_preserve_identical_pairs_outputs_and_native_scores(public_runs):
    plan, first, second = public_runs
    left = comparison.read_json(first / "journal.json")["attempts"]
    right = comparison.read_json(second / "journal.json")["attempts"]
    assert len(left) == len(right) == 4
    assert [r["pair_id"] for r in left] == comparison.read_json(plan / "plan.json")["planned_pairs"]
    assert [r["order_index"] for r in left] == list(range(4))
    assert [r["output_sha256"] for r in left] == [r["output_sha256"] for r in right]
    assert comparison.read_json(first / "native-results.json") == comparison.read_json(
        second / "native-results.json"
    )
    assert len(comparison.compare_runs(first, second)["matching_pairs"]) == 4


def test_missing_upstream_metric_invalidates_instead_of_shrinking_denominator(
    public_runs, monkeypatch, tmp_path
):
    plan, _, _ = public_runs
    genuine = comparison.native_grade

    def drop_produced_metric(bundle, python):
        native = genuine(bundle, python)
        group = native["pairs"][0]["group"]
        primary = comparison.METRICS[group]
        native["pairs"][0]["result"]["metrics"] = [
            m for m in native["pairs"][0]["result"]["metrics"] if m["metric_name"] != primary
        ]
        return native

    monkeypatch.setattr(comparison, "native_grade", drop_produced_metric)
    run = comparison.execute(plan, tmp_path / "runs", NATIVE)
    first = comparison.read_json(run / "journal.json")["attempts"][0]
    result = comparison.validate_run(run)[first["pipeline_id"]][first["group"]]
    assert result["planned_count"] == 1
    assert result["scored_count"] == 0
    assert result["unavailable_pairs"] == [first["pair_id"]]
    assert result["valid"] is False
    assert result["mean"] is None


def test_changed_source_is_rejected_before_real_backend_initialization(public_runs, tmp_path):
    plan, _, _ = public_runs
    changed = tmp_path / "changed"
    shutil.copytree(plan, changed)
    case = comparison.read_json(changed / "plan.json")["cases"][0]
    alternative = next(
        p for p in (plan / "inputs").glob("*.pdf") if p.name != Path(case["input"]).name
    )
    shutil.copyfile(alternative, changed / case["input"])
    output = tmp_path / "runs"
    with pytest.raises(ValueError, match="artifact changed or missing"):
        comparison.execute(changed, output, NATIVE)
    assert not output.exists()


def test_changed_qualification_source_cannot_freeze_a_different_public_input(public_runs, tmp_path):
    source, _, _ = public_runs
    original = comparison.read_json(source / "plan.json")
    selection = comparison.read_json(source / "selection.json")
    selection["cases"] = selection["cases"][:1]
    p = tmp_path / "selection.json"
    p.write_text(json.dumps(selection))
    source_map = tmp_path / "sources.json"
    source_map.write_text(
        json.dumps(
            {selection["cases"][0]["source_path"]: str(source / original["cases"][1]["input"])}
        )
    )
    with pytest.raises(ValueError, match="differs from visual qualification"):
        comparison.freeze(
            p,
            source.parent / "snapshot.json",
            source.parent / "objects",
            source_map,
            NATIVE,
            ROOT / "pdf_bench/parsebench_native.py",
            tmp_path / "plan",
        )
    assert not (tmp_path / "plan").exists()


def test_relocated_native_regrade_uses_retained_output_without_pdfs_or_parser_calls(
    public_runs, tmp_path
):
    _, first, _ = public_runs
    relocated = tmp_path / "relocated"
    shutil.copytree(first, relocated)
    shutil.rmtree(relocated / "frozen-plan/inputs")
    assert comparison.validate_run(relocated, inputs=False) == comparison.validate_run(first)
    assert independent_native(relocated) == comparison.read_json(first / "native-results.json")
    assert comparison.regrade_run(relocated, NATIVE)["pairs_regraded"] == 4


def test_native_regrade_rejects_output_replaced_by_another_real_parser_output(
    public_runs, tmp_path
):
    _, first, _ = public_runs
    changed = tmp_path / "changed"
    shutil.copytree(first, changed)
    attempts = comparison.read_json(changed / "journal.json")["attempts"]
    shutil.copyfile(changed / attempts[-1]["output_path"], changed / attempts[0]["output_path"])
    with pytest.raises(ValueError, match="Retained public parser output changed"):
        comparison.native_grade(changed, NATIVE)


def test_regrade_cannot_relabel_upstream_scores_with_a_different_protocol(
    public_runs, monkeypatch, tmp_path
):
    plan, _, _ = public_runs
    genuine = comparison.native_grade

    def wrong_protocol(bundle, python):
        result = genuine(bundle, python)
        result["protocol"]["normalization"] = "judge"
        return result

    monkeypatch.setattr(comparison, "native_grade", wrong_protocol)
    output = tmp_path / "runs"
    with pytest.raises(ValueError, match="protocol differs"):
        comparison.execute(plan, output, NATIVE)
    assert not (output / "latest.json").exists()


def test_newly_wrong_native_grade_cannot_reuse_a_previous_verified_score(public_runs, monkeypatch):
    _, first, _ = public_runs
    genuine = comparison.native_grade

    def wrong_grade(bundle, python):
        result = genuine(bundle, python)
        result["pairs"][0]["result"]["metrics"][0]["value"] += 0.25
        return result

    monkeypatch.setattr(comparison, "native_grade", wrong_grade)
    with pytest.raises(ValueError, match="regrade differs"):
        comparison.regrade_run(first, NATIVE)
