"""Started timeouts and actual corrupt/empty inputs test accounting, not parser quality."""

from pathlib import Path

from pdf_bench import invoice_comparison as comparison
from pdf_bench.execution import execute_parser
from pdf_bench.execution_controls import DelayedControl, run_controls

UNIT = Path(__file__).resolve().parents[1] / ".workspace/work/2026-10-13-benchmark-rebuild"


def test_real_corrupt_blank_and_started_timeout_controls_stay_outside_primary_population(tmp_path):
    source = UNIT / "invoice-comparison-plan/inputs/invoice_001.pdf"
    result = run_controls(source, tmp_path / "controls")
    assert len(result["attempts"]) == 5
    assert [row["outcome"] for row in result["attempts"]] == [
        "parser_failure",
        "success_empty",
        "parser_failure",
        "success_empty",
        "enforced_timeout",
    ]
    for row in result["attempts"]:
        assert row["parse_time_seconds"] > 0
        if row["outcome"] == "success_empty":
            assert not (tmp_path / "controls" / row["output_path"]).read_text().strip()
        else:
            assert row["output_path"] is None
    assert result["attempts"][-1]["worker_stopped"]


def test_one_controlled_eligible_timeout_cannot_shrink_a_parsers_task_denominator(
    tmp_path,
    monkeypatch,
):
    plan = comparison.freeze_plan(
        UNIT / "invoice-reference-evidence/qualified-dc48e90363104d938465629738316513",
        UNIT / "invoice-task-protocol.json",
        tmp_path / "plan",
        document_ids=["invoice_001", "invoice_003"],
    )

    def controlled(parser_class, options, input_path, directory, timeout_seconds, **kwargs):
        if options["backend_name"] == "pypdf" and input_path.stem == "invoice_001":
            return execute_parser(DelayedControl, {}, input_path, directory, 5, **kwargs)
        return execute_parser(
            parser_class, options, input_path, directory, timeout_seconds, **kwargs
        )

    monkeypatch.setattr(comparison, "execute_parser", controlled)
    bundle = comparison.execute_plan(plan, tmp_path / "runs")
    summary = comparison.validate_run(bundle)
    assert summary["pypdf"]["outcome_ids"]["enforced_timeout"] == ["invoice_001"]
    assert summary["pypdf"]["task"]["valid"]
    assert summary["pypdf"]["task"]["documents_expected"] == 2
    assert summary["pypdf"]["task"]["document_success"] == 1
    assert summary["pypdf"]["task"]["document_task_success_rate"] == 0.5
    assert summary["pypdf"]["task"]["fields_expected"] == 10
    assert summary["pypdf"]["task"]["fields_correct"] == 5
    assert summary["pypdf"]["task"]["record_micro_f1"] < 1
    assert summary["pdfplumber"]["counts"]["success_content"] == 2
    assert summary["common_content_ids"] == ["invoice_003"]
