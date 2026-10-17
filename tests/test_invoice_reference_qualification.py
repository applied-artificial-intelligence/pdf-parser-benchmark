"""Guard source truth, exact rendition identity and atomic reference qualification."""

import copy
import json
import shutil
from pathlib import Path

import pytest
import yaml
from docx import Document

from pdf_bench.invoice_references import (
    extract_reference,
    prepare_references,
    qualify_references,
    render_reference_pages,
    validate_reference_bundle,
)

FIXTURES = Path(__file__).parent / "fixtures/invoice_sources"
DEV_IDS = tuple(f"invoice_{n:03d}" for n in range(1, 7))


def _review(bundle, rendered, target):
    manifest = validate_reference_bundle(bundle)
    decisions = []
    for row in manifest["documents"]:
        reference = json.loads((bundle / "references" / f"{row['document_id']}.json").read_text())
        assert not row["mechanical"]["missing_surface_keys"]
        decisions.append(
            {
                **{
                    k: row[k]
                    for k in [
                        "document_id",
                        "source_sha256",
                        "pdf_sha256",
                        "reference_sha256",
                        "protocol_sha256",
                    ]
                },
                "verdict": "eligible",
                "reviewed_pages": list(range(1, row["mechanical"]["pages"] + 1)),
                "layout_checked": True,
                "associations_checked": True,
                "observed_record_count": len(reference["records"]),
                "observed_headers": reference["source_headers"],
                "notes": (
                    "Retained fixtures visually inspected on October 15: source fields, row/column "
                    "roles, continuations and totals visible; no task-relevant clipping observed."
                ),
            }
        )
    target.write_text(
        json.dumps(
            {
                "reviewer": "Agent source-page review",
                "reviewed_at": "2026-10-15",
                "method": (
                    "Known retained fixture pages, visually reviewed before qualification tests"
                ),
                "documents": decisions,
            }
        )
    )
    return target


@pytest.fixture
def one_source(tmp_path):
    corpus = tmp_path / "corpus"
    for name in ["docx", "pdfs", "metadata"]:
        (corpus / name).mkdir(parents=True)
        suffix = {"docx": ".docx", "pdfs": ".pdf", "metadata": ".yaml"}[name]
        shutil.copyfile(
            FIXTURES / name / ("invoice_001" + suffix), corpus / name / ("invoice_001" + suffix)
        )
    return corpus


def test_source_fields_and_fractional_records_match_inspected_templates():
    expected = [
        ("INV-98034", "Cloud Cloud", "2025-09-20", "20684186.42", 10),
        ("INV-51883", "Standard Fabrication", "2025-12-12", "184646.74", 8),
        ("INV-43945", "Morgan LLP", "2025-08-21", "168795.3", 7),
        ("INV-22581", "Quantum IT Solutions", "2025-12-15", "93595.35", 4),
        ("INV-80900", "Summit Contractors", "2025-10-06", "134209.59", 5),
        ("INV-89478", "Quality Direct", "2025-12-15", "151539.78", 9),
    ]
    for doc_id, (number, vendor, due, total, count) in zip(DEV_IDS, expected, strict=True):
        reference = extract_reference(FIXTURES / "docx" / f"{doc_id}.docx")
        assert reference["fields"] == {
            "invoice_number": number,
            "vendor": vendor,
            "due_date": due,
            "grand_total": total,
            "currency_marker": "$",
        }
        assert len(reference["records"]) == count
    enterprise = extract_reference(FIXTURES / "docx/invoice_001.docx")
    assert enterprise["records"][0] == {
        "description": "Enterprise Plan - Annual",
        "quantity": "45.87",
        "unit": "subscription",
        "unit_price": "71834.13",
        "line_total": "3295031.54",
    }
    economy = extract_reference(FIXTURES / "docx/invoice_003.docx")
    assert economy["applicable_record_fields"] == ["description", "quantity", "line_total"]
    assert "$585.07/hour" in economy["records"][0]["description"]
    assert "unit_price" not in economy["records"][0]


def test_displayed_total_and_duplicate_source_rows_are_not_arithmetically_repaired(one_source):
    source = one_source / "docx/invoice_001.docx"
    doc = Document(source)
    doc.tables[1]._tbl.append(copy.deepcopy(doc.tables[1].rows[1]._tr))
    doc.tables[2].rows[-1].cells[1].text = "$1.23"
    doc.save(source)
    reference = extract_reference(source)
    assert reference["fields"]["grand_total"] == "1.23"
    assert len(reference["records"]) == 11
    assert reference["records"][0] == reference["records"][-1]


def test_reference_generation_ignores_wrong_metadata_and_old_extraction(one_source, tmp_path):
    metadata = one_source / "metadata/invoice_001.yaml"
    values = yaml.safe_load(metadata.read_text())
    values["vendor"]["name"] = "Wrong metadata vendor"
    values["total"] = 1.23
    metadata.write_text(yaml.safe_dump(values))
    old = one_source / "ground_truth"
    old.mkdir()
    (old / "invoice_001.md").write_text("Wrong parsed invoice with fabricated values")
    bundle = prepare_references(one_source, tmp_path / "refs", ("invoice_001",))
    reference = json.loads((bundle / "references/invoice_001.json").read_text())
    assert reference["fields"]["vendor"] == "Cloud Cloud"
    assert reference["fields"]["grand_total"] == "20684186.42"
    record = validate_reference_bundle(bundle)["documents"][0]
    assert record["metadata_cross_checks"]["vendor"] is False
    assert record["metadata_cross_checks"]["grand_total"] is False
    assert record["eligibility"] == "unqualified"


def test_source_gap_cannot_replace_prior_reference_snapshot(one_source, tmp_path):
    output = tmp_path / "refs"
    prepare_references(one_source, output, ("invoice_001",))
    before = (output / "latest-draft.json").read_bytes()
    with pytest.raises(ValueError, match="Reference gap"):
        prepare_references(one_source, output, ("invoice_001", "invoice_002"))
    assert (output / "latest-draft.json").read_bytes() == before
    with pytest.raises(ValueError, match="unique"):
        prepare_references(one_source, output, ("invoice_001", "invoice_001"))
    assert (output / "latest-draft.json").read_bytes() == before


def test_qualification_requires_all_pages_and_preserves_prior_valid_pointer(one_source, tmp_path):
    bundle = prepare_references(one_source, tmp_path / "drafts", ("invoice_001",))
    rendered = render_reference_pages(bundle, tmp_path / "renders")
    review = _review(bundle, rendered, tmp_path / "review.json")
    output = tmp_path / "qualified"
    qualified = qualify_references(bundle, rendered, review, output)
    assert (
        validate_reference_bundle(qualified, require_qualified=True)["documents"][0]["eligibility"]
        == "eligible"
    )
    before = (output / "latest-qualified.json").read_bytes()
    decisions = json.loads(review.read_text())
    decisions["documents"][0]["reviewed_pages"] = [1]
    review.write_text(json.dumps(decisions))
    with pytest.raises(ValueError, match="Every physical page"):
        qualify_references(bundle, rendered, review, output)
    assert (output / "latest-qualified.json").read_bytes() == before
    assert validate_reference_bundle(qualified, require_qualified=True)


def test_changed_qualified_pdf_cannot_reuse_its_previous_truth_decision(one_source, tmp_path):
    bundle = prepare_references(one_source, tmp_path / "drafts", ("invoice_001",))
    rendered = render_reference_pages(bundle, tmp_path / "renders")
    review = _review(bundle, rendered, tmp_path / "review.json")
    qualified = qualify_references(bundle, rendered, review, tmp_path / "qualified")
    source_pdf = qualified / "inputs/invoice_001.pdf"
    source_pdf.write_bytes(source_pdf.read_bytes() + b"\n% changed rendition\n")
    with pytest.raises(ValueError, match="hash/location mismatch"):
        validate_reference_bundle(qualified, require_qualified=True)


def test_failed_finalization_keeps_prior_qualified_references_intact(
    one_source, tmp_path, monkeypatch
):
    bundle = prepare_references(one_source, tmp_path / "drafts", ("invoice_001",))
    rendered = render_reference_pages(bundle, tmp_path / "renders")
    review = _review(bundle, rendered, tmp_path / "review.json")
    output = tmp_path / "qualified"
    qualified = qualify_references(bundle, rendered, review, output)
    before = (output / "latest-qualified.json").read_bytes()
    reference_before = (qualified / "references/invoice_001.json").read_bytes()
    copytree = shutil.copytree

    def corrupt_copy(source, target, *args, **kwargs):
        result = copytree(source, target, *args, **kwargs)
        if Path(source) == bundle:
            pdf = Path(target) / "inputs/invoice_001.pdf"
            pdf.write_bytes(pdf.read_bytes() + b"\n% failed finalization\n")
        return result

    monkeypatch.setattr(shutil, "copytree", corrupt_copy)
    with pytest.raises(ValueError, match="hash/location mismatch"):
        qualify_references(bundle, rendered, review, output)
    assert (output / "latest-qualified.json").read_bytes() == before
    assert (qualified / "references/invoice_001.json").read_bytes() == reference_before
    assert validate_reference_bundle(qualified, require_qualified=True)


def test_converter_total_change_is_detected_from_actual_rendered_output(one_source, tmp_path):
    from builders.build_docx import DocxBuilder

    source = one_source / "docx/invoice_001.docx"
    altered = tmp_path / "converter-input.docx"
    document = Document(source)
    document.tables[2].rows[-1].cells[1].text = "$1.23"
    document.save(altered)
    builder = DocxBuilder(tmp_path, tmp_path)
    wrong_pdf = builder.convert_to_pdf(altered)
    shutil.copyfile(wrong_pdf, one_source / "pdfs/invoice_001.pdf")
    bundle = prepare_references(one_source, tmp_path / "drafts", ("invoice_001",))
    manifest = validate_reference_bundle(bundle)
    assert "grand_total" in manifest["documents"][0]["mechanical"]["missing_surface_keys"]
    assert (
        json.loads((bundle / "references/invoice_001.json").read_text())["fields"]["grand_total"]
        == "20684186.42"
    )
    rendered = render_reference_pages(bundle, tmp_path / "renders")
    row = manifest["documents"][0]
    reference = json.loads((bundle / "references/invoice_001.json").read_text())
    decision = {
        **{
            k: row[k]
            for k in [
                "document_id",
                "source_sha256",
                "pdf_sha256",
                "reference_sha256",
                "protocol_sha256",
            ]
        },
        "verdict": "eligible",
        "reviewed_pages": list(range(1, row["mechanical"]["pages"] + 1)),
        "layout_checked": True,
        "associations_checked": True,
        "observed_record_count": 10,
        "observed_headers": reference["source_headers"],
        "notes": "An unsupported approval without a resolution must be rejected.",
    }
    review = tmp_path / "review.json"
    review.write_text(
        json.dumps(
            {
                "reviewer": "Negative control",
                "reviewed_at": "2026-10-15",
                "method": "Actual converter output with changed displayed total",
                "documents": [decision],
            }
        )
    )
    with pytest.raises(ValueError, match="text-presence miss"):
        qualify_references(bundle, rendered, review, tmp_path / "qualified")
    assert not (tmp_path / "qualified/latest-qualified.json").exists()
