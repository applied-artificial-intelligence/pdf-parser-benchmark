"""Complete-record task scoring against separately qualified invoice references."""

import hashlib
import inspect
import json
from collections import Counter
from collections.abc import Callable
from typing import Any, cast

from pdf_bench import invoice_extraction
from pdf_bench.invoice_extraction import REQUIRED_FIELDS, number_value, text_value


def record_key(record: dict, roles: list[str]) -> tuple:
    if set(record) - {"surfaces"} != {*roles, "currency_markers"}:
        return ("invalid", json.dumps(record, sort_keys=True))
    value: Any
    values = []
    for role in roles:
        raw = record[role]
        if role in {"quantity", "unit_price", "line_total"}:
            value, _ = number_value(raw)
            if role != "quantity":
                value = (value, record["currency_markers"].get(role))
        elif role == "description":
            value = text_value(raw).casefold()
        else:
            value = text_value(raw)
        values.append((role, value))
    return tuple(values)


def grade_invoice(prediction: dict, reference: dict) -> dict:
    """A missing eligible field or record is an error, including empty parser output."""
    expected = reference["fields"]
    if set(expected) != set(REQUIRED_FIELDS):
        raise ValueError("Unsupported reference field semantics")
    roles = reference["applicable_record_fields"]
    if set(roles) not in (
        {"description", "quantity", "line_total"},
        {"description", "quantity", "unit_price", "line_total"},
        {"description", "quantity", "unit", "unit_price", "line_total"},
    ):
        raise ValueError("Unsupported reference record semantics")
    actual = prediction["fields"]
    correct = {}
    for key in REQUIRED_FIELDS:
        value = actual.get(key)
        if value is None:
            correct[key] = False
        elif key == "grand_total":
            correct[key] = number_value(value)[0] == number_value(expected[key])[0]
        elif key == "vendor":
            correct[key] = text_value(value).casefold() == text_value(expected[key]).casefold()
        else:
            correct[key] = text_value(value) == text_value(expected[key])
    marker = expected["currency_marker"]
    expected_rows = [
        {
            **row,
            "currency_markers": {
                role: marker for role in roles if role in {"unit_price", "line_total"}
            },
        }
        for row in reference["records"]
    ]
    expected_counts = Counter(record_key(row, roles) for row in expected_rows)
    predicted_counts = Counter(record_key(row, roles) for row in prediction["records"])
    matched = sum((expected_counts & predicted_counts).values())
    expected_count, predicted_count = len(expected_rows), len(prediction["records"])
    return {
        "correct_fields": correct,
        "fields_correct": sum(correct.values()),
        "fields_expected": len(REQUIRED_FIELDS),
        "records_matched": matched,
        "records_expected": expected_count,
        "records_predicted": predicted_count,
        "records_missing": expected_count - matched,
        "records_extra": predicted_count - matched,
        "document_success": (
            all(correct.values())
            and matched == expected_count == predicted_count
            and not prediction["ambiguities"]
        ),
    }


def aggregate_grades(grades: dict[str, dict | None], eligible_ids: list[str]) -> dict:
    """Keep eligible denominators fixed; an evaluation exception invalidates the aggregate."""
    if (
        not eligible_ids
        or len(set(eligible_ids)) != len(eligible_ids)
        or set(grades) != set(eligible_ids)
    ):
        raise ValueError("Grade population mismatch or incomplete execution")
    if any(grade is None for grade in grades.values()):
        return {"valid": False, "reason": "evaluation_failure", "eligible_ids": eligible_ids}
    totals = {
        key: sum(cast(dict, grade)[key] for grade in grades.values())
        for key in [
            "fields_correct",
            "fields_expected",
            "records_matched",
            "records_expected",
            "records_predicted",
            "document_success",
        ]
    }
    matched, expected, predicted = (
        totals["records_matched"],
        totals["records_expected"],
        totals["records_predicted"],
    )
    return {
        "valid": True,
        "eligible_ids": eligible_ids,
        "scored_ids": list(grades),
        **totals,
        "documents_expected": len(eligible_ids),
        "document_task_success_rate": totals["document_success"] / len(eligible_ids),
        "field_micro_accuracy": totals["fields_correct"] / totals["fields_expected"],
        "record_micro_precision": matched / predicted if predicted else None,
        "record_micro_recall": matched / expected if expected else None,
        "record_micro_f1": 2 * matched / (expected + predicted) if expected + predicted else None,
    }


def task_protocol() -> dict:
    return {
        "schema_version": 1,
        "unicode_database_version": invoice_extraction.unicodedata.unidata_version,
        "required_fields": list(REQUIRED_FIELDS),
        "development_ids": [f"invoice_{i:03d}" for i in range(1, 7)],
        "header_aliases": invoice_extraction.ALIASES,
        "normalization": (
            "NFKC and whitespace; vendor/description casefold; exact units, signs and currency "
            "markers; Decimal strings without rounding; printed MM/DD/YYYY or English month dates"
        ),
        "record_matching": (
            "Complete associated records as a multiset; duplicates retain multiplicity"
        ),
        "representation_policy": (
            "Prefer Markdown line-item tables when present, suppressing duplicated linear text. "
            "Reuse headers for Markdown page continuations; concatenate description-only rows. "
            "Otherwise consume linear description-before-values rows under displayed header roles."
        ),
        "limits": (
            "No OCR or semantic repair. Merged FROM/TO text is ambiguous. Within-word wraps, "
            "values followed by description fragments and missing headers may defeat extraction. "
            "This is a configured pipeline test on retained templates, not an unseen test set."
        ),
        "denominators": (
            "Eligible documents and five fields per document stay fixed, including failures, "
            "empty outputs and timeouts as zero recovery. Grader exceptions invalidate aggregates."
        ),
        "extractor_sha256": hashlib.sha256(
            inspect.getsource(invoice_extraction).encode()
        ).hexdigest(),
        "grader_sha256": hashlib.sha256(
            "\n".join(
                inspect.getsource(f)
                for f in cast(
                    list[Callable[..., Any]], [record_key, grade_invoice, aggregate_grades]
                )
            ).encode()
        ).hexdigest(),
    }
