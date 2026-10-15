"""Create source-fact labels beside frozen PDF pages for qualification review."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pdf_bench.invoice_references import digest, validate_reference_bundle
from pdf_bench.persistence import write_json_atomic


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--rendered", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_reference_bundle(args.bundle)
    rendered = json.loads(args.rendered.read_bytes())
    if rendered["bundle_manifest_sha256"] != digest(args.bundle / "manifest.json"):
        raise ValueError("Render snapshot mismatch")
    if args.output.exists():
        raise FileExistsError("Use a new inspection-sheet location")
    args.output.mkdir(parents=True)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    pages = []
    for doc in rendered["documents"]:
        reference = json.loads(
            (args.bundle / "references" / f"{doc['document_id']}.json").read_bytes()
        )
        for page in doc["pages"]:
            pages.append((doc, reference, page))
    records = []
    for offset in range(0, len(pages), 4):
        sheet = Image.new("RGB", (1600, 2400), "white")
        draw = ImageDraw.Draw(sheet)
        members = []
        for index, (doc, reference, page) in enumerate(pages[offset : offset + 4]):
            left, top = index % 2 * 800, index // 2 * 1200
            row = next(d for d in manifest["documents"] if d["document_id"] == doc["document_id"])
            fields = reference["fields"]
            label = (
                f"{doc['document_id']}, page {page['page']}; "
                f"{row['template_style']}/{row['complexity']}"
            )
            draw.text((left + 8, top + 5), label, font=font, fill="black")
            draw.text(
                (left + 8, top + 24),
                f"Source: {fields['vendor']}; {fields['invoice_number']}",
                font=font,
                fill="black",
            )
            draw.text(
                (left + 8, top + 43),
                f"Due {fields['due_date']}; total {reference['surfaces']['grand_total']}; "
                f"records {len(reference['records'])}",
                font=font,
                fill="black",
            )
            path = args.rendered.parent / page["image"]
            if digest(path) != page["sha256"]:
                raise ValueError("Source review image changed")
            image = Image.open(path).convert("RGB")
            image.thumbnail((780, 1110))
            sheet.paste(image, (left + (800 - image.width) // 2, top + 75))
            members.append(
                {
                    "document_id": doc["document_id"],
                    "page": page["page"],
                    "image_sha256": page["sha256"],
                }
            )
        path = args.output / f"sheet-{offset // 4 + 1:02d}.png"
        sheet.save(path)
        records.append({"sheet": path.name, "sha256": digest(path), "pages": members})
    write_json_atomic(
        args.output / "sheets.json",
        {"render_manifest_sha256": digest(args.rendered), "sheets": records},
    )
    print(f"{len(pages)} pages in {len(records)} sheets: {args.output}")


if __name__ == "__main__":
    main()
