"""Acquire the predeclared coverage sample and render source pages for inspection."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from pdf_bench.parsebench import download_source, sha256
from pdf_bench.persistence import write_json_atomic

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
CACHE = ROOT / "data_exports/parsebench/objects"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=WORK / "parsebench-snapshot.json")
    parser.add_argument(
        "--selection", type=Path, default=WORK / "parsebench-inspection-selection.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--renders", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.snapshot.read_text())
    selection = json.loads(args.selection.read_text())
    if args.output.exists() or args.renders.exists():
        raise ValueError("Inspection output locations must be new")
    args.renders.mkdir(parents=True)

    def fetch(item):
        return item, download_source(CACHE, manifest["assets"][item["path"]])

    with ThreadPoolExecutor(max_workers=4) as pool:
        sources = list(pool.map(fetch, selection["inputs"]))
    records = []
    thumbnails = []
    texts = []
    for index, (item, path) in enumerate(sources, 1):
        document = fitz.open(path)
        record = {
            "index": index,
            "source_path": item["path"],
            "selection_reason": item["reason"],
            "source_sha256": sha256(path.read_bytes()),
            "source_bytes": path.stat().st_size,
            "page_count": len(document),
            "pages": [],
        }
        for page_number, page in enumerate(document, 1):
            text = page.get_text()
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25), alpha=False)
            image_path = args.renders / f"{index:02d}-{page_number}.png"
            pixmap.save(image_path)
            record["pages"].append(
                {
                    "page": page_number,
                    "width_points": page.rect.width,
                    "height_points": page.rect.height,
                    "text_layer_characters": len(text),
                    "image_sha256": sha256(image_path.read_bytes()),
                    "image": image_path.relative_to(ROOT).as_posix(),
                }
            )
            thumbnails.append(
                (f"{index:02d} page {page_number}: {Path(item['path']).name}", image_path)
            )
            texts.append(f"\n{index:02d} {item['path']} page {page_number}\n{text[:3500]}\n")
        document.close()
        records.append(record)
    for offset in range(0, len(thumbnails), 4):
        sheet = Image.new("RGB", (1600, 2280), "white")
        draw = ImageDraw.Draw(sheet)
        for cell, (label, image_path) in enumerate(thumbnails[offset : offset + 4]):
            left, top = cell % 2 * 800, cell // 2 * 1140
            draw.text((left + 10, top + 8), label[:95], fill="black")
            thumbnail = Image.open(image_path).convert("RGB")
            thumbnail.thumbnail((780, 1100))
            sheet.paste(thumbnail, (left + (800 - thumbnail.width) // 2, top + 30))
        sheet.save(args.renders / f"sheet-{offset // 4 + 1:02d}.png")
    (args.renders / "text-layer-excerpts.txt").write_text("\n".join(texts))
    write_json_atomic(
        args.output,
        {
            "dataset_revision": manifest["dataset_revision"],
            "selection_sha256": sha256(args.selection.read_bytes()),
            "purpose": (
                "Unscored source inspection; text layers do not establish visible layout "
                "or task correctness."
            ),
            "inputs": records,
        },
    )
    print(f"Rendered {len(records)} inputs, {len(thumbnails)} pages; {args.renders}")


if __name__ == "__main__":
    main()
