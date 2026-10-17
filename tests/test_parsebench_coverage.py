import hashlib
import json
from pathlib import Path

import pytest
from reportlab.pdfgen.canvas import Canvas

from pdf_bench.parsebench_coverage import acquire_population, classify, inspect_source


def source(tmp_path: Path) -> tuple[Path, dict]:
    path = tmp_path / "invoice.pdf"
    canvas = Canvas(str(path))
    canvas.drawString(50, 700, "Insurance annual report: financial statements and cash flows")
    canvas.showPage()
    canvas.save()
    data = path.read_bytes()
    return path, {
        "path": "docs/text/invoice.pdf",
        "oid": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
        "size": len(data),
    }


def test_family_candidates_use_document_content_and_leave_unidentified_sources_unknown(tmp_path):
    path, asset = source(tmp_path)
    row = inspect_source(path, asset, ["text_content"], [])
    assert row["page_count"] == 1
    assert "financial_reporting" in row["family_classification"]["candidates"]
    assert "insurance" in row["family_classification"]["candidates"]
    assert "transactional_records" not in row["family_classification"]["candidates"]
    assert row["original_document_identity"] is None
    assert classify("")["status"] == "unknown"


def test_changed_pdf_bytes_cannot_reuse_pinned_coverage_identity(tmp_path):
    path, asset = source(tmp_path)
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="pinned identity"):
        inspect_source(path, asset, ["text_content"], [])


def test_omitted_source_does_not_publish_incomplete_full_coverage(tmp_path):
    snapshot = tmp_path / "snapshot.json"
    inventory = tmp_path / "inventory.json"
    output = tmp_path / "coverage.json"
    snapshot.write_text(json.dumps({"assets": {}}))
    inventory.write_text(
        json.dumps({"cases": [], "totals": {"group_cases": 1, "unique_input_paths": 1}})
    )
    output.write_text("previous valid inventory")
    with pytest.raises(ValueError, match="membership"):
        acquire_population(snapshot, inventory, tmp_path / "cache", output)
    assert output.read_text() == "previous valid inventory"
