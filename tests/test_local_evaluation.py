import json
import subprocess
import sys
from pathlib import Path

import pytest

from pdf_bench.local_evaluation import (
    FIELDS,
    build_documents,
    grade_fields,
    loaded_config,
    run_comparison,
)
from pdf_bench.persistence import save_results
from pdf_bench.runner import METRIC_FUNCTIONS, BenchmarkRunner


def test_lightweight_pipeline_does_not_load_unused_tika() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-Werror",
            "-c",
            "import sys; from pdf_bench.local_evaluation import FreshLocalParser; "
            "assert 'tika' not in sys.modules",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_bad_metric_produced_by_runner_does_not_truncate_previous_export(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    documents = build_documents(tmp_path / "inputs")[:1]
    config = loaded_config(documents, tmp_path / "outputs")
    config.parser_instances = config.parser_instances[:1]
    good_results = BenchmarkRunner(config, parallel_workers=1).run()
    destination = tmp_path / "results.json"
    save_results(good_results, destination)
    original = destination.read_bytes()
    monkeypatch.setitem(METRIC_FUNCTIONS, "edit_similarity", lambda reference, prediction: object())
    bad_results = BenchmarkRunner(config, parallel_workers=1).run()
    assert bad_results.success_count == 1
    with pytest.raises(TypeError):
        save_results(bad_results, destination)
    assert destination.read_bytes() == original
    assert not list(tmp_path.glob(".results.json.*"))


def test_real_parsers_keep_failures_and_empty_outputs_in_task_denominators(tmp_path: Path) -> None:
    pack = run_comparison(tmp_path / "run")
    assert len(pack["attempts"]) == 8
    assert pack["common_valid_inputs"] == ["inline", "columns", "raster"]
    for parser in pack["summary"].values():
        assert parser["attempted"] == 4
        assert parser["parse_successes"] == 3
        assert parser["parse_failures"] == 1
        assert parser["common_scored_documents"] == 3
    for attempt in pack["attempts"]:
        if attempt["document_id"] == "corrupt":
            assert attempt["status"] == "failed"
            assert attempt["task_metrics"] is None
        if attempt["document_id"] == "raster":
            assert attempt["status"] == "success"
            assert attempt["task_metrics"]["field_accuracy"] == 0
    raw = json.loads((tmp_path / "run/runner-results.json").read_text())
    assert all(row["metrics"].get("teds") is None for row in raw["results"])


def test_field_grader_rejects_values_without_correct_label_associations(tmp_path: Path) -> None:
    documents = build_documents(tmp_path / "inputs")
    config = loaded_config(documents[1:2], tmp_path / "outputs")
    actual = config.parser_instances[0].parse(documents[1].input_path, config.results_dir)
    text = actual.read_text()
    assert all(value in text for value in FIELDS.values())
    assert grade_fields(text, FIELDS)["field_accuracy"] == 0
