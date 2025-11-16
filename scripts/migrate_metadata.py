#!/usr/bin/env python3
"""
Migrate corpus metadata files to standardized DocumentMetadata schema.

This script converts old metadata format to the new standard defined in
pdf_bench.utils.metadata.DocumentMetadata.
"""

from pathlib import Path
from typing import Any

import yaml

from pdf_bench.utils.metadata import DocumentMetadata, save_metadata


def convert_old_to_new(old_data: dict[str, Any], file_stem: str) -> DocumentMetadata:
    """
    Convert old metadata format to new DocumentMetadata schema.

    Args:
        old_data: Dictionary from old YAML file
        file_stem: Filename stem (e.g., "01_basic")

    Returns:
        DocumentMetadata instance with standardized fields
    """
    # Map old -> new required fields
    doc_id = old_data.get("document_id", file_stem)

    # Determine corpus from source_type or category
    corpus_value = old_data.get("source_type", old_data.get("category", "synthetic"))

    # Handle old "docx_generated" corpus -> should be synthetic/libreoffice
    if corpus_value == "docx_generated":
        corpus_value = "synthetic"
        domain = "libreoffice"
    else:
        # Determine domain from pdf_generation field
        pdf_gen = old_data.get("pdf_generation", "unknown")
        if pdf_gen == "pandoc":
            domain = "pandoc"
        elif pdf_gen == "libreoffice":
            domain = "libreoffice"
        else:
            # Default for synthetic
            domain = "pandoc"

    # Create synthetic source URL (GitHub reference)
    source_url = f"https://github.com/pdf-bench/corpus/synthetic/{file_stem}.md"

    # Extract features from old boolean format
    features = []
    old_features = old_data.get("features", {})
    if old_features.get("tables"):
        features.append("tables")
    if old_features.get("math"):
        features.append("math")
    if old_features.get("images"):
        features.append("figures")
    if old_features.get("code_blocks"):
        features.append("code")
    if old_features.get("ordered_lists") or old_features.get("unordered_lists"):
        features.append("lists")
    if old_features.get("multi_column"):
        features.append("multi-column")

    # Get optional fields
    title = old_data.get("title")
    authors = old_data.get("authors", [])
    license_info = old_data.get("license")
    notes = old_data.get("notes")
    created_date = old_data.get("created_date")

    # Create DocumentMetadata instance
    metadata = DocumentMetadata(
        doc_id=doc_id,
        source_url=source_url,
        corpus=corpus_value,
        domain=domain,
        title=title,
        authors=authors,
        publication_date=created_date,
        features=features,
        license=license_info,
        notes=notes,
    )

    return metadata


def migrate_corpus_metadata(corpus_dir: Path, dry_run: bool = False) -> None:
    """
    Migrate all metadata files in corpus directory.

    Args:
        corpus_dir: Path to corpus directory
        dry_run: If True, only print what would be done
    """
    migrated = 0
    skipped = 0

    for yaml_file in corpus_dir.glob("**/*.yaml"):
        # Skip non-document metadata
        if yaml_file.name in ["targets.yaml", "schema.yaml", "example_pandoc.yaml"]:
            print(f"⏭️  Skipping: {yaml_file.name}")
            skipped += 1
            continue

        # Load old metadata
        with open(yaml_file, encoding="utf-8") as f:
            old_data = yaml.safe_load(f)

        # Check if already migrated (has doc_id field)
        if "doc_id" in old_data and "source_url" in old_data:
            print(f"✅ Already migrated: {yaml_file.name}")
            skipped += 1
            continue

        # Convert to new format
        file_stem = yaml_file.stem
        try:
            new_metadata = convert_old_to_new(old_data, file_stem)

            if dry_run:
                print(f"🔄 Would migrate: {yaml_file.name}")
                print(f"   doc_id: {new_metadata.doc_id}")
                print(f"   corpus: {new_metadata.corpus}")
                print(f"   domain: {new_metadata.domain}")
                print(f"   features: {new_metadata.features}")
            else:
                # Save with new format
                save_metadata(new_metadata, yaml_file)
                print(f"✅ Migrated: {yaml_file.name} -> {new_metadata.doc_id}")

            migrated += 1

        except Exception as e:
            print(f"❌ Error migrating {yaml_file.name}: {e}")
            continue

    print("\n📊 Summary:")
    print(f"   Migrated: {migrated}")
    print(f"   Skipped: {skipped}")


if __name__ == "__main__":
    import sys

    corpus_path = Path("corpus")
    dry_run = "--dry-run" in sys.argv

    if not corpus_path.exists():
        print(f"❌ Corpus directory not found: {corpus_path}")
        sys.exit(1)

    print(f"{'🔍 DRY RUN - ' if dry_run else ''}Migrating metadata in {corpus_path}")
    print("─" * 60)

    migrate_corpus_metadata(corpus_path, dry_run=dry_run)

    if dry_run:
        print("\n💡 Run without --dry-run to actually migrate files")
