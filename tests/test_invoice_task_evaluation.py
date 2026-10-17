"""Check actual produced output, complete associations, multiplicity and blind extraction."""

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pdf_bench import invoice_extraction
from pdf_bench.invoice_extraction import extract_invoice
from pdf_bench.invoice_references import extract_reference
from pdf_bench.invoice_task import aggregate_grades, grade_invoice

FIXTURES = Path(__file__).parent / "fixtures"
CONTROL_TEXT = """INVOICE
Example Supplier
Invoice #: INV-X123
Due Date: December 31, 2026
TOTAL: $1,200.50
| Description | Qty | Unit | Rate | Amount |
| --- | --- | --- | --- | --- |
| Item alpha | 2.50 | hour | $100.00 | $250.00 |
| Item beta | 3.00 | box | $316.833 | $950.50 |
"""


@pytest.fixture
def reference():
    return {
        "fields": {
            "invoice_number": "INV-X123",
            "vendor": "Example Supplier",
            "due_date": "2026-12-31",
            "grand_total": "1200.5",
            "currency_marker": "$",
        },
        "applicable_record_fields": ["description", "quantity", "unit", "unit_price", "line_total"],
        "records": [
            {
                "description": "Item alpha",
                "quantity": "2.5",
                "unit": "hour",
                "unit_price": "100",
                "line_total": "250",
            },
            {
                "description": "Item beta",
                "quantity": "3",
                "unit": "box",
                "unit_price": "316.833",
                "line_total": "950.5",
            },
        ],
    }


def test_faithful_supported_representation_and_harmless_formatting_pass(reference):
    prediction = extract_invoice(CONTROL_TEXT)
    assert prediction["field_surfaces"]["grand_total"] == ["$1,200.50"]
    assert prediction["records"][0]["surfaces"]["quantity"] == "2.50"
    grade = grade_invoice(prediction, reference)
    assert grade["document_success"]
    formatted = CONTROL_TEXT.replace("2.50", "2.5000").replace("$1,200.50", "$1200.500")
    formatted = formatted.replace("December 31, 2026", "12/31/2026")
    formatted = formatted.replace("Item alpha", "ITEM  alpha").replace("| Qty |", "| Quantity |")
    assert grade_invoice(extract_invoice(formatted), reference)["document_success"]


def test_independent_literal_predictions_do_not_need_an_extractor_to_grade(reference):
    prediction = {
        "fields": {
            "invoice_number": "INV-X123",
            "vendor": "Example Supplier",
            "due_date": "2026-12-31",
            "grand_total": "1200.50",
            "currency_marker": "$",
        },
        "records": [
            {
                "description": "Item alpha",
                "quantity": "2.50",
                "unit": "hour",
                "unit_price": "100.00",
                "line_total": "250.00",
                "currency_markers": {"unit_price": "$", "line_total": "$"},
            },
            {
                "description": "Item beta",
                "quantity": "3.00",
                "unit": "box",
                "unit_price": "316.833",
                "line_total": "950.50",
                "currency_markers": {"unit_price": "$", "line_total": "$"},
            },
        ],
        "ambiguities": [],
    }
    assert grade_invoice(prediction, reference)["document_success"]
    prediction["records"][0]["quantity"] = "3.00"
    prediction["records"][1]["quantity"] = "2.50"
    assert grade_invoice(prediction, reference)["records_matched"] == 0


def test_real_retained_outputs_expose_pipeline_limitations_without_hiding_rows():
    expected = {
        ("001", "pypdf"): (5, 10, 10, 10),
        ("001", "pdfplumber"): (5, 9, 10, 9),
        ("002", "pypdf"): (5, 8, 8, 8),
        ("002", "pdfplumber"): (5, 8, 8, 8),
        ("003", "pypdf"): (5, 7, 7, 7),
        ("003", "pdfplumber"): (4, 7, 7, 7),
        ("004", "pypdf"): (5, 4, 4, 4),
        ("004", "pdfplumber"): (5, 4, 4, 4),
        ("005", "pypdf"): (5, 5, 5, 5),
        ("005", "pdfplumber"): (5, 5, 5, 5),
        ("006", "pypdf"): (5, 9, 9, 9),
        ("006", "pdfplumber"): (4, 9, 9, 9),
    }
    for (number, backend), counts in expected.items():
        path = FIXTURES / "invoice_parser_outputs" / f"invoice_{number}-{backend}.md"
        prediction = extract_invoice(path.read_text())
        ref = extract_reference(FIXTURES / "invoice_sources/docx" / f"invoice_{number}.docx")
        grade = grade_invoice(prediction, ref)
        assert (
            tuple(
                grade[k]
                for k in [
                    "fields_correct",
                    "records_matched",
                    "records_expected",
                    "records_predicted",
                ]
            )
            == counts
        )


def test_actual_backend_transposed_headers_fail_while_value_tokens_remain(monkeypatch):
    from pdfsmith import get_backend

    backend = get_backend("pdfplumber")
    source = FIXTURES / "invoice_sources/pdfs/invoice_002.pdf"
    ref = extract_reference(FIXTURES / "invoice_sources/docx/invoice_002.docx")
    correct = backend.parse(source)
    assert grade_invoice(extract_invoice(correct), ref)["document_success"]
    original = type(backend)._table_to_markdown

    def swapped(self, table):
        table = copy.deepcopy(table)
        if table and table[0] == ["Description", "Qty", "Rate", "Amount"]:
            table[0][2], table[0][3] = table[0][3], table[0][2]
        return original(self, table)

    monkeypatch.setattr(type(backend), "_table_to_markdown", swapped)
    wrong = backend.parse(source)
    assert "$155,552.63" in correct and "$155,552.63" in wrong
    grade = grade_invoice(extract_invoice(wrong), ref)
    assert not grade["document_success"]
    assert grade["records_matched"] == 0
    assert grade["records_missing"] == grade["records_extra"] == 8


def test_wrong_field_associations_fail_even_when_all_value_tokens_survive(reference):
    wrong = CONTROL_TEXT.replace("Due Date: December 31, 2026", "Invoice #: December 31, 2026")
    wrong = wrong.replace("Invoice #: INV-X123", "Due Date: INV-X123")
    grade = grade_invoice(extract_invoice(wrong), reference)
    assert not grade["correct_fields"]["invoice_number"]
    assert not grade["correct_fields"]["due_date"]
    assert not grade["document_success"]


def test_ambiguous_backend_headers_cannot_be_hidden_by_duplicated_plain_text(
    reference, tmp_path, monkeypatch
):
    from pdfsmith import get_backend
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import Table, TableStyle

    source = tmp_path / "invoice.pdf"
    canvas = Canvas(str(source), invariant=1)
    for index, text in enumerate(
        [
            "INVOICE",
            "Example Supplier",
            "Invoice #: INV-X123",
            "Due Date: December 31, 2026",
            "TOTAL: $1,200.50",
        ]
    ):
        canvas.drawString(50, 780 - index * 25, text)
    table = Table(
        [
            ["Description", "Quantity", "Unit", "Unit Price", "Amount"],
            ["Item alpha", "2.50", "hour", "$100.00", "$250.00"],
            ["Item beta", "3.00", "box", "$316.833", "$950.50"],
        ],
        colWidths=[120, 70, 70, 80, 80],
        rowHeights=25,
    )
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, "black")]))
    table.wrapOn(canvas, 500, 100)
    table.drawOn(canvas, 50, 500)
    canvas.save()
    backend = get_backend("pdfplumber")
    correct = backend.parse(source)
    assert grade_invoice(extract_invoice(correct), reference)["document_success"]
    original = type(backend)._table_to_markdown

    def duplicate(self, table):
        table = copy.deepcopy(table)
        if table[0][0] == "Description":
            table[0][3] = "Quantity"
        return original(self, table)

    monkeypatch.setattr(type(backend), "_table_to_markdown", duplicate)
    wrong = backend.parse(source)
    assert "Description Quantity Unit Unit Price Amount" in wrong
    assert not grade_invoice(extract_invoice(wrong), reference)["document_success"]


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("$250.00", "$250.01"),
        ("$250.00", "($250.00)"),
        ("$250.00", "€250.00"),
        ("| hour |", "| day |"),
        ("$316.833", "$316.83"),
    ],
)
def test_amount_sign_currency_unit_or_precision_changes_fail(reference, old, new):
    grade = grade_invoice(extract_invoice(CONTROL_TEXT.replace(old, new)), reference)
    assert not grade["document_success"]
    assert grade["records_matched"] == 1
    assert grade["records_missing"] == grade["records_extra"] == 1


def test_duplicate_multiplicity_and_extra_rows_are_penalized(reference):
    expected = copy.deepcopy(reference)
    expected["records"].append(copy.deepcopy(expected["records"][0]))
    prediction = extract_invoice(CONTROL_TEXT)
    missing = grade_invoice(prediction, expected)
    assert missing["records_missing"] == 1
    assert not missing["document_success"]
    prediction["records"].append(copy.deepcopy(prediction["records"][0]))
    assert grade_invoice(prediction, expected)["document_success"]
    prediction["records"].append(copy.deepcopy(prediction["records"][0]))
    extra = grade_invoice(prediction, expected)
    assert extra["records_extra"] == 1 and not extra["document_success"]


def test_row_reordering_preserves_records_but_column_value_swaps_do_not(reference):
    prediction = extract_invoice(CONTROL_TEXT)
    prediction["records"].reverse()
    assert grade_invoice(prediction, reference)["document_success"]
    for row in prediction["records"]:
        row["unit_price"], row["line_total"] = row["line_total"], row["unit_price"]
    grade = grade_invoice(prediction, reference)
    assert grade["records_matched"] == 0 and not grade["document_success"]


def test_missing_failed_empty_and_all_failed_outputs_keep_fixed_denominators(reference):
    empty = grade_invoice(extract_invoice(" \n"), reference)
    assert empty["fields_correct"] == empty["records_matched"] == 0
    assert empty["records_expected"] == 2 and empty["records_predicted"] == 0
    correct = grade_invoice(extract_invoice(CONTROL_TEXT), reference)
    summary = aggregate_grades({"a": correct, "b": empty}, ["a", "b"])
    assert summary["document_task_success_rate"] == summary["field_micro_accuracy"] == 0.5
    assert summary["fields_expected"] == 10 and summary["records_expected"] == 4
    assert summary["record_micro_f1"] == pytest.approx(2 / 3)
    all_failed = aggregate_grades({"a": empty, "b": empty}, ["a", "b"])
    assert all_failed["record_micro_precision"] is None
    assert all_failed["record_micro_recall"] == all_failed["document_task_success_rate"] == 0
    with pytest.raises(ValueError, match="population"):
        aggregate_grades({"a": correct}, ["a", "b"])
    assert aggregate_grades({"a": None}, ["a"])["valid"] is False


def test_extractor_subprocess_has_no_access_to_answers_and_predictions_depend_on_output(tmp_path):
    expected_prediction = extract_invoice(CONTROL_TEXT)
    allowed = tmp_path / "available"
    allowed.mkdir()
    script = allowed / "extract.py"
    shutil.copyfile(invoice_extraction.__file__, script)
    source = allowed / "parser-output.txt"
    source.write_text(CONTROL_TEXT)
    denied = tmp_path / "answers"
    denied.mkdir()
    gold = denied / "gold.json"
    gold.write_text(json.dumps({"secret_answer": "Not a prediction input", "rows": 999}))
    harness = """
import os, runpy, sys
from pathlib import Path
root, forbidden, script, source, target = map(Path, sys.argv[1:])
stdlib = Path(sys.base_prefix).resolve()
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).resolve()
        if not path.is_relative_to(root) and not path.is_relative_to(stdlib):
            raise PermissionError('Answer files unavailable')
    if event.startswith(('socket.', 'subprocess.', 'os.system')):
        raise PermissionError('No network or subprocesses')
sys.addaudithook(audit)
try:
    forbidden.read_bytes()
except PermissionError:
    pass
else:
    raise AssertionError('Answers are accessible')
sys.argv = [str(script), str(source), str(target)]
runpy.run_path(str(script), run_name='__main__')
"""

    def run(name):
        target = allowed / name
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                "-c",
                harness,
                str(allowed),
                str(gold),
                str(script),
                str(source),
                str(target),
            ],
            cwd=allowed,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        return target.read_bytes()

    before = run("prediction-1.json")
    assert json.loads(before) == expected_prediction
    gold.write_text(json.dumps({"entirely_different_labels": ["wrong"] * 1000, "rows": 0}))
    assert run("prediction-2.json") == before
    source.write_text("")
    blank = run("prediction-empty.json")
    assert blank != before
    assert json.loads(blank)["records"] == []
    source.write_text(CONTROL_TEXT.replace("$1,200.50", "$99.01"))
    changed = run("prediction-changed.json")
    assert changed != before
    assert json.loads(changed)["fields"]["grand_total"] == "99.01"
