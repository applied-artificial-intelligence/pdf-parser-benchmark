"""Inventory retained source structure without executing compared parsers or scoring."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import pymupdf
import yaml
from docx import Document
from docx.oxml.ns import qn

UNIT = Path(__file__).resolve().parent
CORPUS = UNIT.parents[2] / "corpus/business/invoices"
ITEM_HEADERS = {"Description", "Quantity", "Qty", "Unit", "Unit Price", "Rate", "Amount"}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory() -> dict:
    rows = []
    for number in range(1, 101):
        doc_id = f"invoice_{number:03d}"
        source = CORPUS / "docx" / f"{doc_id}.docx"
        pdf = CORPUS / "pdfs" / f"{doc_id}.pdf"
        metadata_path = CORPUS / "metadata" / f"{doc_id}.yaml"
        metadata = yaml.safe_load(metadata_path.read_text())
        document = Document(source)
        tables = []
        item_count = 0
        for table in document.tables:
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            is_items = "Description" in headers and set(headers) <= ITEM_HEADERS
            item_count += len(table.rows) - 1 if is_items else 0
            tables.append(
                {
                    "rows": len(table.rows),
                    "columns": len(table.columns),
                    "is_line_items": is_items,
                    "line_item_headers": headers if is_items else None,
                    "physical_cells": len(table._tbl.findall(f".//{qn('w:tc')}")),
                    "grid_spans": [
                        element.get(qn("w:val"))
                        for element in table._tbl.findall(f".//{qn('w:gridSpan')}")
                    ],
                    "vertical_merges": len(table._tbl.findall(f".//{qn('w:vMerge')}")),
                }
            )
        with pymupdf.open(pdf) as rendered:
            pages = len(rendered)
            pdf_metadata = {
                key: rendered.metadata.get(key)
                for key in ("producer", "creator", "creationDate", "modDate")
            }
        backup = CORPUS / "ground_truth_backup" / f"{doc_id}.md"
        current = CORPUS / "ground_truth" / f"{doc_id}.md"
        rows.append(
            {
                "document_id": doc_id,
                "source_sha256": file_hash(source),
                "pdf_sha256": file_hash(pdf),
                "metadata_sha256": file_hash(metadata_path),
                "reference_sha256": file_hash(current),
                "backup_reference_sha256": file_hash(backup),
                "template_style": metadata.get("template_style"),
                "complexity": metadata.get("complexity"),
                "region": metadata.get("region"),
                "pages": pages,
                "source_line_items": item_count,
                "metadata_line_items": metadata.get("line_item_count"),
                "tables": tables,
                "source_created": str(document.core_properties.created),
                "source_modified": str(document.core_properties.modified),
                "pdf_metadata": pdf_metadata,
            }
        )
    return {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "scope": "100 retained invoice IDs; source structure and PDF metadata only",
        "instruments": {name: version(name) for name in ("python-docx", "PyMuPDF", "PyYAML")},
        "limitations": [
            "Not reference qualification, semantic truth, or a scored parser comparison",
            "PDF/DOCX timestamps and producer strings cannot establish content identity",
            "Source table headers and metadata layout cells do not establish visual diversity",
            "PyMuPDF is an unscored inspection instrument, not either compared parser",
        ],
        "summary": {
            "documents": len(rows),
            "pages": sum(row["pages"] for row in rows),
            "page_counts": dict(sorted(Counter(row["pages"] for row in rows).items())),
            "template_complexity_cells": dict(
                sorted(
                    Counter(f"{row['template_style']}/{row['complexity']}" for row in rows).items()
                )
            ),
            "line_item_header_sets": dict(
                sorted(
                    Counter(
                        ", ".join(table["line_item_headers"])
                        for row in rows
                        for table in row["tables"]
                        if table["is_line_items"]
                    ).items()
                )
            ),
            "line_items": sum(row["source_line_items"] for row in rows),
            "source_metadata_count_disagreements": [
                row["document_id"]
                for row in rows
                if row["source_line_items"] != row["metadata_line_items"]
            ],
            "documents_with_merges": [
                row["document_id"]
                for row in rows
                if any(table["grid_spans"] or table["vertical_merges"] for table in row["tables"])
            ],
            "pdf_producers": dict(Counter(row["pdf_metadata"]["producer"] for row in rows)),
            "reference_directory_matches": sum(
                row["reference_sha256"] == row["backup_reference_sha256"] for row in rows
            ),
        },
        "documents": rows,
    }


if __name__ == "__main__":
    payload = inventory()
    destination = UNIT / "pre-run-source-inventory.json"
    if destination.exists():
        raise FileExistsError("Preserve the existing source inventory; choose a new version")
    serialized = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    temporary = destination.with_suffix(".preparing")
    try:
        temporary.write_text(serialized)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(json.dumps(payload["summary"], indent=2))
