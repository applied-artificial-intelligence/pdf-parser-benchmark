"""Prepare source-bound failure differences for review; never infer a cause automatically."""

import argparse
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

from pdf_bench.invoice_comparison import digest, read_json, validate_run
from pdf_bench.invoice_task import record_key
from pdf_bench.persistence import write_json_atomic


def build(bundle: Path, output: Path, review: Path | None = None) -> dict:
    validate_run(bundle)
    plan = read_json(bundle / "frozen-plan/plan.json")
    journal = read_json(bundle / "journal.json")["attempts"]
    documents = {row["document_id"]: row for row in plan["documents"]}
    failed = {}
    for row in journal:
        grade = read_json(bundle / f"attempts/{row['pair_id']}/grade.json")["grade"]
        if grade is None:
            raise ValueError("Cannot audit quality with unresolved evaluator failures")
        if not grade["document_success"]:
            failed[row["pair_id"]] = (row, grade)
    entries = []
    for pair_id, (row, grade) in sorted(failed.items()):
        doc_id = row["document_id"]
        prediction = read_json(bundle / f"attempts/{pair_id}/prediction.json")
        reference = read_json(bundle / f"frozen-plan/references/{doc_id}.json")
        roles = reference["applicable_record_fields"]
        expected_records = [
            {
                **record,
                "currency_markers": {
                    role: reference["fields"]["currency_marker"]
                    for role in roles
                    if role in {"unit_price", "line_total"}
                },
            }
            for record in reference["records"]
        ]
        expected_counts = Counter(record_key(record, roles) for record in expected_records)
        predicted_counts = Counter(record_key(record, roles) for record in prediction["records"])

        def unmatched(records, remaining, match_roles):
            result = []
            for record in records:
                key = record_key(record, match_roles)
                if remaining[key]:
                    result.append(record)
                    remaining[key] -= 1
            return result

        missing = unmatched(expected_records, expected_counts - predicted_counts, roles)
        extra = unmatched(prediction["records"], predicted_counts - expected_counts, roles)
        raw = (bundle / row["output_path"]).read_text() if row["output_path"] else ""
        field_differences = {
            key: {
                "expected": reference["fields"][key],
                "predicted": prediction["fields"].get(key),
                "surfaces": prediction["field_surfaces"].get(key),
            }
            for key, correct in grade["correct_fields"].items()
            if not correct
        }
        cues = [
            record["description"].split()[0][:6].casefold()
            for record in missing + extra
            if record.get("description", "").split()
        ]
        cues += [
            value["expected"].split()[0][:6].casefold()
            for value in field_differences.values()
            if value["expected"]
        ]
        lines = raw.splitlines()
        indexes = {
            nearby
            for i, line in enumerate(lines)
            if any(cue in unicodedata.normalize("NFKC", line).casefold() for cue in cues)
            for nearby in range(max(0, i - 1), min(len(lines), i + 2))
        }
        excerpts = [{"line": i + 1, "text": lines[i]} for i in sorted(indexes)]
        peer = "pdfplumber" if row["pipeline_id"] == "pypdf" else "pypdf"
        entries.append(
            {
                "pair_id": pair_id,
                "document_id": doc_id,
                "pipeline_id": row["pipeline_id"],
                "template_style": documents[doc_id]["template_style"],
                "complexity": documents[doc_id]["complexity"],
                "shared_document_failure": f"{peer}--{doc_id}" in failed,
                "input_sha256": documents[doc_id]["pdf_sha256"],
                "reference_sha256": documents[doc_id]["reference_sha256"],
                "raw_sha256": row["output_sha256"],
                "raw_path": row["output_path"],
                "grade": grade,
                "field_differences": field_differences,
                "missing_records": missing,
                "extra_records": extra,
                "raw_excerpts": excerpts,
                "review_status": "unreviewed",
                "cause": None,
                "review_note": None,
            }
        )
    result = {
        "completion_sha256": digest(bundle / "completion.json"),
        "scope": "All failed task pairs and all parser-disagreement documents; candidate "
        "differences are not causal judgments",
        "failed_pair_count": len(entries),
        "failed_document_count": len({row["document_id"] for row in entries}),
        "entries": entries,
    }
    if review is not None:
        decisions = read_json(review)
        candidate_sha256 = hashlib.sha256(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            ).encode()
        ).hexdigest()
        if decisions["candidate_sha256"] != candidate_sha256:
            raise ValueError("Review belongs to different candidate evidence")
        notes = decisions["decisions"]
        keys = [row["pair_id"] for row in notes]
        if len(set(keys)) != len(keys) or set(keys) != set(failed):
            raise ValueError("Review is incomplete or has duplicate/foreign failed pairs")
        allowed = {
            "reference_gap",
            "lost_or_misassociated_parser_content",
            "unsupported_extractor_representation",
            "evaluation_defect",
            "unknown",
        }
        counts = Counter()
        lookup = {row["pair_id"]: row for row in notes}
        for entry in entries:
            decision = lookup[entry["pair_id"]]
            causes = decision["causes"]
            if not causes or not set(causes) <= allowed or not decision["note"].strip():
                raise ValueError("Review lacks an explicit supported cause and observation")
            entry.update(review_status="reviewed", cause=causes, review_note=decision["note"])
            counts.update(set(causes))
        result.update(
            scope="Coding-agent review of all failed task pairs, using prior source/PDF "
            "qualification and retained raw output; not independent human adjudication",
            reviewed_failure_pairs=len(entries),
            cause_pair_counts={name: counts[name] for name in sorted(allowed)},
            shared_failure_document_ids=sorted(
                {entry["document_id"] for entry in entries if entry["shared_document_failure"]}
            ),
            parser_disagreement_document_ids=sorted(
                {entry["document_id"] for entry in entries if not entry["shared_document_failure"]}
            ),
            review={
                "method": decisions["method"],
                "candidate_sha256": candidate_sha256,
                "decisions_sha256": digest(review),
                "source_visual_rechecks": decisions.get("source_visual_rechecks", []),
            },
        )
    write_json_atomic(output, result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            {
                key: value
                for key, value in build(args.bundle, args.output, args.review).items()
                if key != "entries"
            }
        )
    )
