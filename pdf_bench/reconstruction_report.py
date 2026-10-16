"""Publish a source-linked report/export from qualified runs and retained history."""

import shutil
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from typing import Any

from pdf_bench.inventory import load_registry_bundle
from pdf_bench.invoice_comparison import digest, read_json, validate_run
from pdf_bench.invoice_reproduction import summarize_cells
from pdf_bench.invoice_task import aggregate_grades
from pdf_bench.parsebench_comparison import validate_run as validate_public
from pdf_bench.persistence import write_json_atomic


def pointer(value: Any, path: str) -> Any:
    for part in path.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def bounded(root: Path, name: str) -> Path:
    p = (root / name).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError("Report evidence path escapes its work unit")
    return p


def collect(repo: Path, unit: Path) -> dict:
    """Validate source bundles before creating claims or output directories."""
    repo, unit = repo.resolve(), unit.resolve()
    sources, claims = {}, []

    def source(p: Path) -> dict:
        relative = p.resolve().relative_to(repo).as_posix()
        record = {"path": relative, "sha256": digest(p)}
        sources[relative] = record
        return record

    def claim(
        name: str,
        path: Path,
        at: str,
        tier: str,
        interpretation: str,
        denominator: str | None = None,
        context: str | None = None,
    ) -> Any:
        value = pointer(read_json(path), at)
        if value is None:
            raise ValueError(f"Required report measurement is unavailable: {name}")
        row = {
            "id": name,
            "value": value,
            "evidence": {**source(path), "pointer": at},
            "tier": tier,
            "supported_interpretation": interpretation,
            "context": context,
        }
        if at.endswith("/mean"):
            row["statistic"] = "unweighted_case_mean"
        if denominator:
            row["denominator"] = {
                "value": pointer(read_json(path), denominator),
                "evidence": {**source(path), "pointer": denominator},
            }
        claims.append(row)
        return value

    invoice_check = read_json(unit / "invoice-run-checkpoint.json")
    public_check = read_json(unit / "parsebench-run-checkpoint.json")
    invoice = bounded(unit, invoice_check["primary_bundle"])
    public = bounded(unit, public_check["primary_bundle"])
    invoice_result = validate_run(invoice)
    public_result = validate_public(public, inputs=False)
    if (
        digest(invoice / "completion.json")
        != read_json(unit / "invoice-reproduction-v3.json")["first_completion_sha256"]
    ):
        raise ValueError("Invoice report refers to a different reproduced run")
    if digest(public / "completion.json") != public_check["primary_completion_sha256"]:
        raise ValueError("Public report refers to a different qualified run")
    registry = load_registry_bundle(unit / "retained-evidence")
    registry_pointer = read_json(unit / "retained-evidence/latest.json")
    historical = bounded(unit / "retained-evidence", registry_pointer["bundle"])
    registry_path = historical / "registry.json"
    audit_path = unit / "invoice-failure-audit.json"
    audit = read_json(audit_path)
    attempts = read_json(invoice / "journal.json")["attempts"]
    failed = {
        r["pair_id"]
        for r in attempts
        if not read_json(invoice / "attempts" / r["pair_id"] / "grade.json")["grade"][
            "document_success"
        ]
    }
    if (
        audit["completion_sha256"] != digest(invoice / "completion.json")
        or {r["pair_id"] for r in audit["entries"]} != failed
        or audit["reviewed_failure_pairs"] != len(failed)
        or len(audit["entries"]) != len(failed)
    ):
        raise ValueError("Report failure audit is incomplete or belongs to another run")
    by_pair = {r["pair_id"]: r for r in attempts}
    for row in audit["entries"]:
        actual = by_pair[row["pair_id"]]
        grade = read_json(invoice / "attempts" / row["pair_id"] / "grade.json")["grade"]
        if (
            row["review_status"] != "reviewed"
            or row["raw_sha256"] != actual["output_sha256"]
            or row["grade"] != grade
        ):
            raise ValueError("Report failure review differs from actual output/grade")
    cells = summarize_cells(invoice)
    plan = read_json(invoice / "frozen-plan/plan.json")
    ids = [r["document_id"] for r in plan["documents"]]
    qualification = read_json(unit / "invoice-reference-checkpoint.json")
    qualification_manifest = bounded(repo, qualification["bundle"]) / "manifest.json"
    qualified = read_json(qualification_manifest)
    if (
        digest(qualification_manifest) != plan["reference_manifest_sha256"]
        or qualification["manifest_sha256"] != plan["reference_manifest_sha256"]
        or qualification["documents"] != len(ids)
        or qualification["line_items"]
        != sum(
            len(read_json(invoice / "frozen-plan/references" / f"{doc_id}.json")["records"])
            for doc_id in ids
        )
        or qualification["physical_pages"]
        != sum(r["mechanical"]["pages"] for r in qualified["documents"])
        or qualification["source_layout_cells"]
        != dict(Counter(f"{r['template_style']}/{r['complexity']}" for r in plan["documents"]))
    ):
        raise ValueError("Report qualification population differs from scored inputs")
    source(qualification_manifest)
    if read_json(unit / "invoice-cell-results-v3.json") != cells:
        raise ValueError("Retained source-cell results differ from actual run")
    source(unit / "invoice-cell-results-v3.json")
    grades = {
        name: {
            doc_id: read_json(invoice / f"attempts/{name}--{doc_id}/grade.json")["grade"]
            for doc_id in ids
        }
        for name in invoice_result
        if name != "common_content_ids"
    }
    selected_ids = [doc_id for doc_id in ids if grades["pypdf"][doc_id]["document_success"]]
    selection_bias = {
        "scope": "Diagnostic performance-selected counterfactual, never the primary population",
        "source_completion": source(invoice / "completion.json"),
        "selection_rule": (
            "Keep only inputs where the configured pypdf pipeline meets the complete-invoice task"
        ),
        "selected_ids": selected_ids,
        "full": {name: aggregate_grades(values, ids) for name, values in grades.items()},
        "selected": {
            name: aggregate_grades(
                {doc_id: values[doc_id] for doc_id in selected_ids}, selected_ids
            )
            for name, values in grades.items()
        },
        "historical_limit": (
            "Other parsers were not executed on all SEC-screen exclusions; no "
            "equivalent historical counterfactual is established."
        ),
    }
    interpretation = (
        "Configured parser plus frozen extractor on source-qualified "
        "synthetic invoices; not real-vendor or universal parser performance"
    )
    summary = invoice / "summary.json"
    for name in plan["pipelines"]:
        pipeline = name["pipeline_id"]
        base = f"/{pipeline}/task/"
        for field, denominator in [
            ("document_success", "documents_expected"),
            ("fields_correct", "fields_expected"),
            ("records_matched", "records_expected"),
            ("record_micro_f1", None),
            ("records_predicted", None),
        ]:
            claim(
                f"invoice-{pipeline}-{field}",
                summary,
                base + field,
                "strong_within_declared_task",
                interpretation,
                base + denominator if denominator else None,
                "invoice",
            )
    for pipeline, groups in public_result.items():
        for group in groups:
            claim(
                f"public-{pipeline}-{group}",
                public / "summary.json",
                f"/{pipeline}/{group}/mean",
                "qualified_public_subset",
                (
                    "Pinned native per-case metric mean on the fixed relevant subset; no "
                    "full-leaderboard equivalence"
                ),
                denominator=f"/{pipeline}/{group}/planned_count",
                context="public",
            )
    for name in ["documents", "physical_pages", "line_items"]:
        claim(
            "qualified-" + name,
            unit / "invoice-reference-checkpoint.json",
            "/" + name,
            "source_qualified",
            "Source-derived facts and coding-agent visual page qualification",
            context="invoice",
        )
    for cell in cells["pypdf"]:
        escaped = cell.replace("/", "~1")
        for pipeline in ["pypdf", "pdfplumber"]:
            claim(
                f"cell-{pipeline}-{cell}",
                unit / "invoice-cell-results-v3.json",
                f"/{pipeline}/{escaped}/document_success",
                "source_qualified_six_cells",
                "Synthetic source template/complexity cell; not a real-vendor layout sample",
                f"/{pipeline}/{escaped}/documents_expected",
                "invoice",
            )
    claim(
        "retained-artifact-count",
        registry_path,
        "/artifact_count",
        "historical",
        "Retained artifact count, not a count of independent experiments",
    )
    for name in ["failed_pair_count", "failed_document_count", "reviewed_failure_pairs"]:
        claim(
            "audit-" + name,
            audit_path,
            "/" + name,
            "qualified_task_audit",
            "Coding-agent inspection, not independent human adjudication",
            context="invoice",
        )
    for name in [
        "group_cases",
        "annotation_rows",
        "unique_input_paths",
        "unique_source_content_ids",
    ]:
        claim(
            "parsebench-inventory-" + name,
            unit / "parsebench-inventory.json",
            "/totals/" + name,
            "pinned_inventory",
            (
                "Paths, group cases and content identities differ from independently "
                "verified original-document counts"
            ),
        )
    supporting_names = [
        "invoice-reference-checkpoint.json",
        "invoice-hardware-observation.json",
        "invoice-reproduction-v3.json",
        "invoice-relocated-reproduction-v3.json",
        "invoice-offline-regrade-v3.json",
        "invoice-replay-instructions-check.json",
        "invoice-faithful-format-control-v3.json",
        "parsebench-comparison-qualified-selection.json",
        "parsebench-relocated-reproduction-v2.json",
        "parsebench-reproduction-v2.json",
        "parsebench-execution-observation.json",
        "extractbench-contract-assessment.json",
        "editorial-context.json",
    ]
    for name in supporting_names:
        source(unit / name)
    for path in [
        unit / "invoice-run-checkpoint.json",
        unit / "parsebench-run-checkpoint.json",
        invoice / "journal.json",
        public / "journal.json",
        invoice / "frozen-plan/plan.json",
        public / "frozen-plan/plan.json",
        public / "native-results.json",
        invoice / "completion.json",
        public / "completion.json",
        historical / "manifest.json",
        unit / "technical-report.template.md",
        Path(__file__),
    ]:
        source(path)
    for proof, count in [
        ("invoice-offline-regrade-v3.json", 200),
        ("parsebench-relocated-reproduction-v2.json", 100),
    ]:
        evidence = read_json(unit / proof)
        observed = (
            evidence["pairs_regraded"]
            if "pairs_regraded" in evidence
            else evidence["offline_regrade"]["pairs_regraded"]
        )
        if observed != count:
            raise ValueError("Report replay evidence is incomplete")
    environment = read_json(invoice / "frozen-plan/environment.json")
    public_plan = read_json(public / "frozen-plan/plan.json")
    contexts = {
        "invoice": {
            "completion": source(invoice / "completion.json"),
            "plan": source(invoice / "frozen-plan/plan.json"),
            "observed_at": read_json(invoice / "completion.json")["completed_at"],
            "task": source(invoice / "frozen-plan/task-protocol.json"),
            "environment": source(invoice / "frozen-plan/environment.json"),
            "python": environment["python"],
            "backend_versions": environment["backend_dependencies"],
            "pdfsmith_distribution": environment["pdfsmith_distribution"],
            "pdfsmith_source_version": environment["pdfsmith_source_version"],
            "pipelines": plan["pipelines"],
            "boundaries": (
                "Sequential isolated calls; cache bypass; parse/read/retention "
                "duration after initialization; wall duration includes startup; "
                "hardware observed, no speed winner"
            ),
            "api_charges": 0,
            "total_operating_cost": None,
            "cost_unknown_reason": "No monetized hardware/energy/labor allocation was measured",
        },
        "public": {
            "completion": source(public / "completion.json"),
            "plan": source(public / "frozen-plan/plan.json"),
            "observed_at": read_json(unit / "parsebench-execution-observation.json")["observed_at"],
            "executed_at": None,
            "upstream_code_revision": public_plan["code_revision"],
            "dataset_revision": public_plan["dataset_revision"],
            "evaluator_python": public_plan["evaluator_environment"]["python"],
            "evaluator_options": public_plan["evaluator_options"],
            "boundaries": (
                "Same frozen parser runtime/options as invoice baselines; native "
                "evaluator and shared upstream table conversion, normalization off; "
                "all cases retained by dimension"
            ),
        },
    }
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "publication_state": (
            "Source evidence ready for author/editorial review; no public release authorized"
        ),
        "sources": list(sources.values()),
        "claims": claims,
        "contexts": contexts,
        "invoice": invoice_result,
        "public": public_result,
        "cells": cells,
        "audit": audit,
        "registry": registry,
        "selection_bias": selection_bias,
        "qualified_references": read_json(unit / "invoice-reference-checkpoint.json"),
        "extractbench": read_json(unit / "extractbench-contract-assessment.json"),
        "editorial": read_json(unit / "editorial-context.json"),
    }


def render(evidence: dict, template: str) -> tuple[str, str]:
    invoice, public = evidence["invoice"], evidence["public"]
    invoice_rows = [
        (
            "| Pipeline | Complete invoices | Correct fields | Matched / "
            "expected / predicted records | Record F1 |"
        ),
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name in ["pypdf", "pdfplumber"]:
        r = invoice[name]["task"]
        invoice_rows.append(
            f"| {name} | {r['document_success']}/{r['documents_expected']} | "
            f"{r['fields_correct']}/{r['fields_expected']} | {r['records_matched']} / "
            f"{r['records_expected']} / {r['records_predicted']} | {r['record_micro_f1']:.6f} |"
        )
    public_rows = [
        "| Pipeline | Native content faithfulness | Native table composite |",
        "| --- | ---: | ---: |",
    ]
    for name in ["pypdf", "pdfplumber"]:
        a, b = public[name]["text_content"], public[name]["table"]
        public_rows.append(
            f"| {name} | {a['mean']:.6f} ({a['scored_count']}/{a['planned_count']}) | "
            f"{b['mean']:.6f} ({b['scored_count']}/{b['planned_count']}) |"
        )
    cell_rows = [
        "| Source cell | Inputs | pypdf complete | pdfplumber complete |",
        "| --- | ---: | ---: | ---: |",
    ]
    for cell, row in evidence["cells"]["pypdf"].items():
        other = evidence["cells"]["pdfplumber"][cell]
        cell_rows.append(
            f"| {cell} | {row['documents_expected']} | {row['document_success']} | "
            f"{other['document_success']} |"
        )
    history_rows = ["| Retained family | Tier | Supported interpretation |", "| --- | --- | --- |"]
    for row in evidence["registry"]["artifacts"]:
        if row.get("story_annotation"):
            history_rows.append(
                f"| {row['story_annotation']['family']} | {row['evidence_tier']} | "
                f"{row['story_annotation']['supported_interpretation']} |"
            )
    q, audit = evidence["qualified_references"], evidence["audit"]
    full, chosen = evidence["selection_bias"]["full"], evidence["selection_bias"]["selected"]
    substitutions = {
        "invoice_table": "\n".join(invoice_rows),
        "public_table": "\n".join(public_rows),
        "cell_table": "\n".join(cell_rows),
        "history_table": "\n".join(history_rows),
        "documents": q["documents"],
        "pages": q["physical_pages"],
        "records": q["line_items"],
        "source_cells": len(q["source_layout_cells"]),
        "schemas": len(q["record_schemas"]),
        "failed_pairs": audit["failed_pair_count"],
        "failed_documents": audit["failed_document_count"],
        "disagreement_documents": len(audit["parser_disagreement_document_ids"]),
        "shared_failure_documents": len(audit["shared_failure_document_ids"]),
        "unsupported_pairs": audit["cause_pair_counts"]["unsupported_extractor_representation"],
        "party_association_pairs": audit["cause_pair_counts"][
            "lost_or_misassociated_parser_content"
        ],
        "retained_artifacts": evidence["registry"]["artifact_count"],
        "selected_documents": len(evidence["selection_bias"]["selected_ids"]),
        "full_pypdf_f1": f"{full['pypdf']['record_micro_f1']:.6f}",
        "full_pdfplumber_f1": f"{full['pdfplumber']['record_micro_f1']:.6f}",
        "selected_pypdf_f1": f"{chosen['pypdf']['record_micro_f1']:.6f}",
        "selected_pdfplumber_f1": f"{chosen['pdfplumber']['record_micro_f1']:.6f}",
    }
    context = evidence["contexts"]["invoice"]
    upstream = evidence["contexts"]["public"]
    substitutions["runtime_table"] = "\n".join(
        [
            "| Component | Frozen configuration |",
            "| --- | --- |",
            f"| Parser Python | {context['python']} |",
            f"| PDFsmith | Distribution {context['pdfsmith_distribution']}; "
            f"source {context['pdfsmith_source_version']} |",
            *[
                f"| {r['pipeline_id']} | Version "
                f"{context['backend_versions'][r['pipeline_id']]}; `{r['options']}` |"
                for r in context["pipelines"]
            ],
            f"| ParseBench code | `{upstream['upstream_code_revision']}` |",
            f"| Public dataset | `{upstream['dataset_revision']}` |",
            f"| Native evaluator Python | {upstream['evaluator_python']} |",
        ]
    )
    measured = {row["id"]: row["value"] for row in evidence["claims"]}
    substitutions.update(
        {
            "annotation_rows": f"{measured['parsebench-inventory-annotation_rows']:,}",
            "group_cases": f"{measured['parsebench-inventory-group_cases']:,}",
            "input_paths": f"{measured['parsebench-inventory-unique_input_paths']:,}",
            "content_identities": f"{measured['parsebench-inventory-unique_source_content_ids']:,}",
            "content_cases": public["pypdf"]["text_content"]["planned_count"],
            "table_cases": public["pypdf"]["table"]["planned_count"],
        }
    )
    report = Template(template).substitute(substitutions)
    appendix = "# Source-linked result appendix\n\n" + "\n\n".join(
        [
            substitutions["invoice_table"],
            substitutions["cell_table"],
            substitutions["public_table"],
            substitutions["history_table"],
            (
                "Each exported claim carries its source SHA256 and JSON pointer in "
                "claims.json. Native dimensions and complete-invoice scores measure "
                "different tasks."
            ),
        ]
    )
    return report, appendix


def validate_export(repo: Path, bundle: Path) -> dict:
    manifest = read_json(bundle / "manifest.json")
    required = {
        "claims.json",
        "technical-report.md",
        "appendix.md",
        "selection-bias.json",
        "integration-handoff.txt",
        "replay-protocol.txt",
    }
    if manifest["status"] != "complete" or required - manifest["files"].keys():
        raise ValueError("Report manifest omits required completed artifacts")
    for name, expected in manifest["files"].items():
        if digest(bounded(bundle, name)) != expected:
            raise ValueError("Generated report artifact changed")
    export = read_json(bundle / "claims.json")
    for record in export["sources"]:
        p = bounded(repo, record["path"])
        if digest(p) != record["sha256"]:
            raise ValueError("Report source is stale or changed")
    for row in export["claims"]:
        for item in [row, row.get("denominator")]:
            if item:
                s = item["evidence"]
                if digest(bounded(repo, s["path"])) != s["sha256"]:
                    raise ValueError("Claim evidence identity differs from source")
                if pointer(read_json(bounded(repo, s["path"])), s["pointer"]) != item["value"]:
                    raise ValueError("Exported claim differs from its source measurement")
    return export


def publish_report(repo: Path, unit: Path, output: Path) -> Path:
    evidence = collect(repo, unit)
    report, appendix = render(evidence, (unit / "technical-report.template.md").read_text())
    export = {
        key: evidence[key]
        for key in [
            "schema_version",
            "generated_at",
            "publication_state",
            "sources",
            "claims",
            "contexts",
            "editorial",
        ]
    }
    registry_source = next(s for s in export["sources"] if s["path"].endswith("/registry.json"))
    export["historical_tracks"] = [
        {
            "family": r["story_annotation"]["family"],
            "evidence_tier": r["evidence_tier"],
            "supported_interpretation": r["story_annotation"]["supported_interpretation"],
            "evidence": {**registry_source, "pointer": f"/artifacts/{index}"},
            "current_backend_identity": None,
        }
        for index, r in enumerate(evidence["registry"]["artifacts"])
        if r.get("story_annotation")
    ]
    output.mkdir(parents=True, exist_ok=True)
    identifier = uuid.uuid4().hex
    staging, final = output / (".incomplete-" + identifier), output / ("bundle-" + identifier)
    staging.mkdir()
    write_json_atomic(staging / "claims.json", export)
    write_json_atomic(staging / "selection-bias.json", evidence["selection_bias"])
    (staging / "technical-report.md").write_text(report)
    (staging / "appendix.md").write_text(appendix)
    shutil.copyfile(unit / "replay-protocol.txt", staging / "replay-protocol.txt")
    (staging / "integration-handoff.txt").write_text(
        "PDF-Bench: qualified invoice and native public-subset comparisons.\n"
        "Visitor task: decide whether public benchmark documents, task, grader and\n"
        "execution conditions fit the intended workflow. Reuse a relevant public\n"
        "subset when it fits; add internal evaluation for a consequential mismatch.\n"
        "claims.json carries paths, hashes, JSON pointers, denominators and context.\n"
        "Read technical-report.md, appendix.md and replay-protocol.txt.\n"
        "Synthetic invoice and native ParseBench scores measure different tasks.\n"
        "No universal parser winner or business-coverage percentage is established.\n"
        "PDF-Bench owns source evidence; editorial/website own synthesis/rendering.\n"
        "Stefan owns public release and paid-run authorization.\n"
        "No CMS edits, publication, deployment, release or paid calls performed.\n"
    )
    write_json_atomic(
        staging / "manifest.json",
        {
            "status": "complete",
            "files": {p.name: digest(p) for p in staging.iterdir() if p.is_file()},
        },
    )
    validate_export(repo, staging)
    staging.rename(final)
    write_json_atomic(
        output / "latest.json",
        {"bundle": final.name, "manifest_sha256": digest(final / "manifest.json")},
    )
    return final
