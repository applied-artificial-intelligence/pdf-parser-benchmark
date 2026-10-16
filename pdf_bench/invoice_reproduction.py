"""Reproduction and representation controls for the fixed invoice comparison."""

from pathlib import Path

from pdf_bench.invoice_comparison import digest, read_json, validate_plan, validate_run
from pdf_bench.invoice_extraction import extract_invoice
from pdf_bench.invoice_task import aggregate_grades, grade_invoice


def compare_runs(first: Path, second: Path) -> dict:
    """Require deterministic observations; fresh call durations are not equality targets."""
    summaries = [validate_run(directory) for directory in [first, second]]
    if digest(first / "frozen-plan/plan.json") != digest(second / "frozen-plan/plan.json"):
        raise ValueError("Fresh executions did not use the identical frozen plan")
    if summaries[0] != summaries[1]:
        raise ValueError("Fresh executions have different outcomes or task aggregates")
    journals = [read_json(directory / "journal.json")["attempts"] for directory in [first, second]]
    compared = []
    for left, right in zip(*journals, strict=True):
        for key in ["pair_id", "outcome", "output_sha256", "stage_identities"]:
            if left[key] != right[key]:
                raise ValueError(f"Fresh execution mismatch: {left['pair_id']} / {key}")
        for name in ["prediction.json", "grade.json"]:
            relative = f"attempts/{left['pair_id']}/{name}"
            if read_json(first / relative) != read_json(second / relative):
                raise ValueError(f"Fresh semantic artifact mismatch: {relative}")
        compared.append(left["pair_id"])
    return {
        "first_completion_sha256": digest(first / "completion.json"),
        "second_completion_sha256": digest(second / "completion.json"),
        "identical_plan_sha256": digest(first / "frozen-plan/plan.json"),
        "matching_pairs": compared,
        "comparison": "Exact raw bytes, normalized predictions, outcomes, stage identities and "
        "task aggregates; individual durations are observed, not required equal",
    }


def faithful_representation_controls(plan_directory: Path) -> dict:
    """Test a declared supported format; this does not establish a ceiling on real PDFs."""
    plan = validate_plan(plan_directory)
    names = {
        "description": "Description",
        "quantity": "Qty",
        "unit": "Unit",
        "unit_price": "Rate",
        "line_total": "Amount",
    }
    rows = []
    for document in plan["documents"]:
        doc_id = document["document_id"]
        reference = read_json(plan_directory / "references" / f"{doc_id}.json")
        fields = reference["fields"]
        roles = reference["applicable_record_fields"]
        lines = [
            "INVOICE",
            fields["vendor"],
            f"Invoice #: {fields['invoice_number']}",
            f"Due Date: {fields['due_date']}",
            f"TOTAL: {fields['currency_marker']}{fields['grand_total']}",
            "| " + " | ".join(names[role] for role in roles) + " |",
            "| " + " | ".join("---" for _ in roles) + " |",
        ]
        for record in reference["records"]:
            cells = [
                fields["currency_marker"] + record[role]
                if role in {"unit_price", "line_total"}
                else record[role]
                for role in roles
            ]
            if any("|" in cell or "\n" in cell for cell in cells):
                raise ValueError("Reference lies outside the supported faithful control format")
            lines.append("| " + " | ".join(cells) + " |")
        text = "\n".join(lines) + "\n"
        prediction = extract_invoice(text)
        grade = grade_invoice(prediction, reference)
        rows.append(
            {
                "document_id": doc_id,
                "representation": text,
                "prediction": prediction,
                "grade": grade,
            }
        )
    return {
        "scope": "Reference-derived faithful Markdown representation control, not parser output, "
        "a universal extractor ceiling, or evidence of PDF layout recovery",
        "plan_sha256": digest(plan_directory / "plan.json"),
        "documents": rows,
        "aggregate": aggregate_grades(
            {row["document_id"]: row["grade"] for row in rows}, [row["document_id"] for row in rows]
        ),
    }


def summarize_cells(bundle: Path) -> dict:
    validate_run(bundle)
    plan = read_json(bundle / "frozen-plan/plan.json")
    cells: dict = {}
    for pipeline in plan["pipelines"]:
        name = pipeline["pipeline_id"]
        groups: dict[str, list[str]] = {}
        for document in plan["documents"]:
            cell = f"{document['template_style']}/{document['complexity']}"
            groups.setdefault(cell, []).append(document["document_id"])
        cells[name] = {}
        for cell, ids in groups.items():
            grades = {
                doc_id: read_json(bundle / f"attempts/{name}--{doc_id}/grade.json")["grade"]
                for doc_id in ids
            }
            cells[name][cell] = aggregate_grades(grades, ids)
    return cells
