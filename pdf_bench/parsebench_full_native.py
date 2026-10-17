"""Evaluate all pinned ParseBench dimensions on retained PDFSmith Markdown."""

import argparse
import contextlib
import hashlib
import json
import os
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pdf_bench.parsebench_native import identity, table_converter
from pdf_bench.persistence import write_json_atomic

METRICS = {
    "text_content": "content_faithfulness",
    "text_formatting": "semantic_formatting",
    "table": "grits_trm_composite",
    "chart": "rule_chart_data_point_pass_rate",
    "layout": "layout_element_rule_pass_rate",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(unit: Path, run: Path) -> dict:
    os.environ["LLAMACLOUD_BENCH_LLM_NORMALIZATION"] = "off"

    def restricted(event: str, args: tuple) -> None:
        if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.fork"}:
            raise PermissionError(
                "Network and parser processes unavailable during native regrading"
            )
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            if Path(os.fsdecode(args[0])).suffix.lower() == ".pdf":
                raise PermissionError("Native regrading cannot read original PDFs")

    sys.addaudithook(restricted)
    from parse_bench.evaluation.evaluators.parse import ParseEvaluator
    from parse_bench.evaluation.runner import _evaluate_single_worker
    from parse_bench.schemas.parse_output import ParseOutput
    from parse_bench.schemas.pipeline_io import InferenceRequest, InferenceResult
    from parse_bench.test_cases.loader import _load_jsonl_dataset

    plan = json.loads((run / "plan.json").read_text())
    protocol_path = unit / "full-native-protocol.json"
    protocol = json.loads(protocol_path.read_text())
    if (
        protocol["harness_sha256"] != digest(Path(__file__))
        or identity() != protocol["native_environment"]
    ):
        raise ValueError("Native harness/environment differs from frozen protocol")
    complete = json.loads((run / "parse-complete.json").read_text())
    if complete["plan_sha256"] != digest(run / "plan.json") or complete["journal_sha256"] != digest(
        run / "journal.json"
    ):
        raise ValueError("Changed completed parse artifacts")
    attempts = json.loads((run / "journal.json").read_text())["attempts"]
    expected_inputs = {r["source_path"]: r["sha256"] for r in plan["inputs"]}
    if len(attempts) != len(expected_inputs) or len({r["source_path"] for r in attempts}) != len(
        attempts
    ):
        raise ValueError("Incomplete or duplicate full-population attempts")
    if {r["source_path"]: r["input_sha256"] for r in attempts} != expected_inputs:
        raise ValueError("Native journal input identities differ from frozen plan")
    by_source = {r["source_path"]: r for r in attempts}
    snapshot = json.loads((unit / "parsebench-snapshot.json").read_text())
    inventory = json.loads((unit / "parsebench-inventory.json").read_text())
    if digest(unit / "parsebench-inventory.json") != plan["inventory_sha256"]:
        raise ValueError("Changed frozen annotation inventory")
    cache = Path("data_exports/parsebench/objects").resolve()
    references = run / "native-references"
    references.mkdir(exist_ok=True)
    for group in METRICS:
        obj = snapshot["files"][group + ".jsonl"]
        data = (cache / obj["sha256"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != obj["sha256"]:
            raise ValueError("Pinned annotation bytes changed")
        (references / (group + ".jsonl")).write_bytes(data)
    cases = _load_jsonl_dataset(references)
    if len(cases) != len(inventory["cases"]):
        raise ValueError("Upstream loader did not preserve every dimension case")
    evaluator = ParseEvaluator(**protocol["options"])
    convert = table_converter()
    rows = []
    sums: dict[str, float] = dict.fromkeys(METRICS, 0.0)
    counts: Counter[str] = Counter()
    for case in cases:
        group = case.group
        source = case.file_path.relative_to(references).as_posix()
        attempt = by_source[source]
        raw = ""
        if attempt["output_path"]:
            output = (run / attempt["output_path"]).resolve()
            if (
                not output.is_relative_to(run.resolve())
                or digest(output) != attempt["output_sha256"]
            ):
                raise ValueError("Retained output changed")
            raw = output.read_text()
        normalized = convert(raw)
        inference = InferenceResult(
            request=InferenceRequest(
                example_id=case.test_id, source_file_path=str(case.file_path), product_type="parse"
            ),
            pipeline_name=plan["backend"],
            product_type="parse",
            raw_output={"markdown": raw},
            output=ParseOutput(
                example_id=case.test_id, pipeline_name=plan["backend"], markdown=normalized
            ),
            started_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
            completed_at=datetime(2000, 1, 1, tzinfo=timezone.utc),
            latency_in_ms=0,
        )
        if group == "layout":
            result = _evaluate_single_worker(
                inference.model_dump(mode="json"),
                case.model_dump(mode="json"),
                "layout_detection",
                True,
                "layout_detection",
            )
            result.pop("evaluated_at", None)
            error = result.get("error") or ""
            if "No layout data" not in error and "not LayoutOutput" not in error:
                raise ValueError(f"Unexpected native grounding result: {error}")
            value = 0.0
            status = "native_unsupported_output_zero_padding"
        else:
            result = evaluator.evaluate(inference, case).model_dump(mode="json")
            result.pop("evaluated_at", None)
            metrics = {m["metric_name"]: m["value"] for m in result["metrics"]}
            name = METRICS[group]
            if name not in metrics:
                raise ValueError(f"Required native metric absent for {group}: {list(metrics)}")
            value = metrics[name]
            status = "native_evaluated"
        rows.append(
            {
                "source_path": source,
                "group": group,
                "parse_outcome": attempt["outcome"],
                "metric": METRICS[group],
                "value": value,
                "status": status,
                "result": result,
            }
        )
        sums[group] += value
        counts[group] += 1
        if len(rows) % 100 == 0:
            print(
                f"Native {plan['backend']}: {len(rows)}/{len(cases)}", file=sys.stderr, flush=True
            )
    expected = plan["dimension_cases"]
    if dict(counts) != expected:
        raise ValueError("Native metric population differs from frozen dimensions")
    result = {
        "backend": plan["backend"],
        "plan_sha256": digest(run / "plan.json"),
        "native_environment": identity(),
        "evaluator_options": protocol["options"],
        "protocol_sha256": digest(protocol_path),
        "normalization": "off",
        "input_count": len(attempts),
        "case_count": len(rows),
        "outcomes": dict(Counter(r["outcome"] for r in attempts)),
        "dimensions": {
            g: {
                "sum": sums[g],
                "count": counts[g],
                "mean": sums[g] / counts[g],
                "metric": METRICS[g],
            }
            for g in counts
        },
    }
    target = run / ("native-grade-" + uuid.uuid4().hex)
    write_json_atomic(target / "details.json", {"cases": rows})
    write_json_atomic(target / "summary.json", result)
    write_json_atomic(
        target / "complete.json",
        {
            "details_sha256": digest(target / "details.json"),
            "summary_sha256": digest(target / "summary.json"),
        },
    )
    write_json_atomic(
        run / "native-latest.json",
        {"bundle": target.name, "complete_sha256": digest(target / "complete.json")},
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    with contextlib.redirect_stdout(sys.stderr):
        result = grade(args.unit.resolve(), args.run.resolve())
    print(json.dumps(result["dimensions"], indent=2))


if __name__ == "__main__":
    main()
