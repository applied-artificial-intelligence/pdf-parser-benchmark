import subprocess
import sys
from pathlib import Path

import pytest

from pdf_bench.parsebench_full import validate_journal, validate_population


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
