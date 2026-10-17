"""Generate immutable registry-backed historical evidence and a validated latest pointer."""

import argparse
from pathlib import Path

from pdf_bench.inventory import publish_registry

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data_exports/reconstruction"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--qualified-report", action="store_true")
    parser.add_argument(
        "--unit",
        type=Path,
        default=ROOT / ".workspace/work/2026-10-13-benchmark-rebuild",
    )
    args = parser.parse_args(argv)
    if args.qualified_report:
        from pdf_bench.reconstruction_report import publish_report

        bundle = publish_report(
            args.repo_root, args.unit, args.output_dir or args.unit / "report-evidence"
        )
        print(f"Completed qualified report bundle: {bundle}")
    else:
        output = args.output_dir or OUT_DIR
        pointer = publish_registry(args.repo_root, output)
        print(f"Completed registry bundle: {output / pointer['bundle']}")


if __name__ == "__main__":
    main()
