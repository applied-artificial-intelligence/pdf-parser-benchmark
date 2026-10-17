"""Rebuild source facts and reuse judgments only when inputs and rendered pixels match."""

import argparse
import json
import shutil
from pathlib import Path

from pdf_bench.invoice_references import (
    digest,
    prepare_references,
    qualify_references,
    render_reference_pages,
    validate_reference_bundle,
)
from pdf_bench.persistence import write_json_atomic


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work = Path(__file__).resolve().parent
    pointer = json.loads((work / "invoice-reference-evidence/latest-qualified.json").read_text())
    original = work / "invoice-reference-evidence" / pointer["bundle"]
    assert digest(original / "manifest.json") == pointer["manifest_sha256"]
    manifest = validate_reference_bundle(original, require_qualified=True)
    args.output.mkdir(parents=True, exist_ok=False)
    corpus = args.output / "corpus"
    for old, new in [("sources", "docx"), ("inputs", "pdfs"), ("metadata", "metadata")]:
        shutil.copytree(original / old, corpus / new)
    draft = prepare_references(corpus, args.output / "drafts", tuple(manifest["document_ids"]))
    replay = validate_reference_bundle(draft)
    for before, after in zip(manifest["documents"], replay["documents"], strict=True):
        for key in [
            "document_id",
            "source_sha256",
            "pdf_sha256",
            "reference_sha256",
            "protocol_sha256",
        ]:
            assert before[key] == after[key], (before["document_id"], key)
    rendered = render_reference_pages(draft, args.output / "renders")
    actual = json.loads(rendered.read_bytes())
    expected = json.loads((work / "invoice-render-artifacts.json").read_bytes())
    assert actual["documents"] == expected["documents"], "Pixels or source facts changed"
    qualified = qualify_references(
        draft, rendered, work / "invoice-rendition-review.json", args.output / "qualified"
    )
    final = validate_reference_bundle(qualified, require_qualified=True)
    write_json_atomic(
        args.output / "replay.json",
        {
            "status": "passed",
            "documents": len(final["documents"]),
            "pages": sum(len(d["pages"]) for d in actual["documents"]),
            "original_manifest_sha256": digest(original / "manifest.json"),
            "replayed_manifest_sha256": digest(qualified / "manifest.json"),
            "judgment_policy": (
                "Reuse earlier agent observations only for identical facts and pixels"
            ),
        },
    )
    print(f"References, all page pixels and eligibility reproduced: {qualified}")


if __name__ == "__main__":
    main()
