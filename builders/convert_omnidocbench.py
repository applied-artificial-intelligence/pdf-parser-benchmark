"""
Convert OmniDocBench dataset images to PDFs with ground truth markdown.

OmniDocBench provides page-level annotations with:
- Images (JPG) of document pages
- Layout detection annotations (text blocks, tables, figures, etc.)
- Text content for each element in reading order

This script:
1. Converts each image to a single-page PDF
2. Generates ground truth markdown from element annotations
3. Creates metadata files for each document
"""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import yaml

# External dependencies
try:
    from PIL import Image
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install pillow reportlab")
    exit(1)


def load_omnidocbench(json_path: Path) -> list[dict]:
    """Load the OmniDocBench JSON file."""
    with open(json_path) as f:
        return json.load(f)


def extract_document_id(image_path: str) -> tuple[str, int]:
    """Extract document stem and page number from image path.

    Examples:
        'eastmoney_59cde7e9...pdf_11.jpg' -> ('eastmoney_59cde7e9...pdf', 11)
        'PPT_1001115_eng_page_1.jpg' -> ('PPT_1001115_eng', 1)
        'yanbaopptmerge_yanbaoPPT_1015.jpg' -> ('yanbaopptmerge_yanbaoPPT_1015', 1)
    """
    # Remove .jpg/.png extension
    if image_path.endswith(".jpg"):
        base = image_path[:-4]
    elif image_path.endswith(".png"):
        base = image_path[:-4]
    else:
        base = image_path

    # Handle different naming patterns
    if "_page_" in base:
        # Pattern: PPT_xxx_page_N
        parts = base.rsplit("_page_", 1)
        try:
            return parts[0], int(parts[1])
        except ValueError:
            return base, 1

    # Pattern: xxx.pdf_N where N is a small number (page number)
    if ".pdf_" in base:
        parts = base.rsplit("_", 1)
        try:
            page_num = int(parts[1])
            if page_num < 1000:  # Reasonable page number
                return parts[0], page_num
        except ValueError:
            pass

    # Default: treat as single-page document
    return base, 1


def generate_ground_truth_markdown(page_data: dict) -> str:
    """Generate markdown from page annotations.

    Sorts elements by reading order and formats based on category type.
    """
    layout_dets = page_data.get("layout_dets", [])

    # Sort by order
    sorted_dets = sorted(
        [d for d in layout_dets if not d.get("ignore", False)],
        key=lambda x: x.get("order") if x.get("order") is not None else 999,
    )

    markdown_parts = []

    for det in sorted_dets:
        cat = det.get("category_type", "")
        text = det.get("text", "").strip()
        latex = det.get("latex", "")

        if not text and not latex:
            continue

        if cat == "title":
            markdown_parts.append(f"# {text}")
        elif cat == "figure_caption":
            markdown_parts.append(f"*{text}*")
        elif cat == "table_caption":
            markdown_parts.append(f"**{text}**")
        elif cat == "text_block":
            markdown_parts.append(text)
        elif cat == "table":
            # Tables may have LaTeX or text representation
            if latex:
                markdown_parts.append(f"```\n{latex}\n```")
            elif text:
                markdown_parts.append(text)
        elif cat == "equation":
            if latex:
                markdown_parts.append(f"${latex}$")
            elif text:
                markdown_parts.append(text)
        elif cat == "footnote":
            markdown_parts.append(f"[^1]: {text}")
        else:
            # Default: just include the text
            if text:
                markdown_parts.append(text)

    return "\n\n".join(markdown_parts)


def image_to_pdf(image_path: Path, pdf_path: Path):
    """Convert an image to a single-page PDF."""
    with Image.open(image_path) as img:
        # Get image dimensions
        img_width, img_height = img.size

        # Create PDF with same aspect ratio
        c = canvas.Canvas(str(pdf_path), pagesize=(img_width, img_height))
        c.drawImage(ImageReader(img), 0, 0, width=img_width, height=img_height)
        c.save()


def create_metadata(doc_id: str, page_info: dict, output_path: Path):
    """Create metadata YAML file for a document."""
    page_attr = page_info.get("page_attribute", {})

    metadata = {
        "doc_id": doc_id,
        "corpus": "academic",
        "domain": "mixed",  # OmniDocBench has diverse document types
        "source": "omnidocbench",
        "source_url": f"generated://omnidocbench/{doc_id}",
        "features": [],
        "data_source": page_attr.get("data_source", "unknown"),
        "language": page_attr.get("language", "unknown"),
        "layout": page_attr.get("layout", "unknown"),
    }

    # Add features based on content
    special_issues = page_attr.get("special_issue", [])
    if special_issues:
        metadata["special_issues"] = special_issues
        if "watermark" in special_issues:
            metadata["features"].append("watermark")
        if "stamp" in special_issues:
            metadata["features"].append("stamp")

    # Map data source to domain
    source_to_domain = {
        "PPT2PDF": "presentation",
        "exam_paper": "education",
        "book": "academic",
        "newspaper": "news",
        "magazine": "news",
        "colorful_textbook": "education",
        "academic_literature": "academic",
        "note": "handwritten",
        "research_report": "business",
    }
    metadata["domain"] = source_to_domain.get(page_attr.get("data_source", ""), "mixed")

    with open(output_path, "w") as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)


def convert_omnidocbench(
    source_dir: Path,
    output_dir: Path,
    max_docs: int | None = None,
    english_only: bool = False,
):
    """Convert OmniDocBench dataset to pdf-bench format.

    Args:
        source_dir: Directory containing OmniDocBench files
        output_dir: Output directory for converted corpus
        max_docs: Maximum number of documents to convert (None = all)
        english_only: Only include English documents
    """
    # Load JSON
    json_path = source_dir / "OmniDocBench.json"
    data = load_omnidocbench(json_path)
    print(f"Loaded {len(data)} pages from OmniDocBench")

    # Check which images are actually available (both JPG and PNG)
    images_dir = source_dir / "images"
    available_images = {f.name for f in images_dir.glob("*.jpg")}
    available_images.update(f.name for f in images_dir.glob("*.png"))
    print(f"Found {len(available_images)} available images (JPG + PNG)")

    # Group pages by document (only those with available images)
    docs = defaultdict(list)
    for page in data:
        img_path = page["page_info"]["image_path"]

        # Skip if image not available
        if img_path not in available_images:
            continue

        doc_stem, page_num = extract_document_id(img_path)

        # Apply English filter if requested
        if english_only:
            lang = page["page_info"].get("page_attribute", {}).get("language", "")
            if lang not in ["english", "English", "en"]:
                continue

        docs[doc_stem].append((page_num, page))

    print(f"Found {len(docs)} unique documents with available images")

    if max_docs:
        doc_stems = list(docs.keys())[:max_docs]
    else:
        doc_stems = list(docs.keys())

    # Create output directories
    pdfs_dir = output_dir / "pdfs"
    gt_dir = output_dir / "ground_truth"
    meta_dir = output_dir / "metadata"

    pdfs_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    for doc_stem in doc_stems:
        pages = sorted(docs[doc_stem], key=lambda x: x[0])

        # Generate short doc ID
        hashlib.md5(doc_stem.encode()).hexdigest()[:8]
        doc_id = f"omnidoc_{converted:03d}"

        # For now, convert only single-page documents (simplifies PDF conversion)
        # Multi-page would require merging PDFs
        if len(pages) == 1:
            page_num, page_data = pages[0]
            img_name = page_data["page_info"]["image_path"]
            img_path = source_dir / "images" / img_name

            if not img_path.exists():
                print(f"  Image not found: {img_path}")
                continue

            # Convert image to PDF
            pdf_path = pdfs_dir / f"{doc_id}.pdf"
            try:
                image_to_pdf(img_path, pdf_path)
            except Exception as e:
                print(f"  Failed to convert {img_name}: {e}")
                continue

            # Generate ground truth
            gt_markdown = generate_ground_truth_markdown(page_data)
            gt_path = gt_dir / f"{doc_id}.md"
            gt_path.write_text(gt_markdown, encoding="utf-8")

            # Create metadata
            meta_path = meta_dir / f"{doc_id}.yaml"
            create_metadata(doc_id, page_data["page_info"], meta_path)

            converted += 1
            if converted % 50 == 0:
                print(f"  Converted {converted} documents...")

    print(f"\nConversion complete: {converted} documents")

    # Create corpus metadata
    corpus_meta = {
        "name": "OmniDocBench",
        "description": "Academic document layout benchmark converted from OmniDocBench",
        "source": "https://huggingface.co/datasets/opendatalab/OmniDocBench",
        "document_count": converted,
        "ground_truth_type": "annotated_text_extraction",
    }
    with open(output_dir / "corpus_metadata.yaml", "w") as f:
        yaml.dump(corpus_meta, f)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert OmniDocBench to pdf-bench format")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("/home/stefan/projects/OmniDocBench_full"),
        help="OmniDocBench source directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("corpus/academic/omnidocbench"),
        help="Output directory for converted corpus",
    )
    parser.add_argument("--max-docs", type=int, default=None, help="Maximum documents to convert")
    parser.add_argument(
        "--english-only", action="store_true", help="Only include English documents"
    )

    args = parser.parse_args()

    convert_omnidocbench(
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        max_docs=args.max_docs,
        english_only=args.english_only,
    )
