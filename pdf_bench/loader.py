"""
Configuration loader with runtime resolution for PDF-Bench.

This module extends the basic configuration loading from config.py with runtime
resolution of document paths and parser classes. It provides a complete, ready-to-use
configuration object for the benchmark runner.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pdf_bench.config import BenchmarkConfig, load_config
from pdf_bench.systems import BaseParser
from pdf_bench.systems.landing_ai_parser import LandingAIParser
from pdf_bench.systems.marker_ollama import MarkerOllamaParser
from pdf_bench.systems.pdfsmith_adapter import PdfsmithAdapter

# Native parsers (not available in pdfsmith)
from pdf_bench.systems.tika_parser import TikaParser
from pdf_bench.utils.metadata import DocumentMetadata, load_metadata

# Type alias for parser factories (class or callable returning parser)
ParserFactory = type[BaseParser] | Callable[[], BaseParser]

# Parser class registry mapping parser IDs to classes or factory functions
# Uses pdfsmith backends for most parsers, with native implementations for
# parsers not available in pdfsmith (tika, marker_ollama, landing_ai)
PARSER_REGISTRY: dict[str, ParserFactory] = {
    # ========== pdfsmith backends (open-source) ==========
    "pdfsmith-pypdf": lambda: PdfsmithAdapter("pypdf"),
    "pdfsmith-pdfplumber": lambda: PdfsmithAdapter("pdfplumber"),
    "pdfsmith-pymupdf": lambda: PdfsmithAdapter("pymupdf"),
    "pdfsmith-pymupdf4llm": lambda: PdfsmithAdapter("pymupdf4llm"),
    "pdfsmith-pdfminer": lambda: PdfsmithAdapter("pdfminer"),
    "pdfsmith-pypdfium2": lambda: PdfsmithAdapter("pypdfium2"),
    "pdfsmith-unstructured": lambda: PdfsmithAdapter("unstructured"),
    "pdfsmith-kreuzberg": lambda: PdfsmithAdapter("kreuzberg"),
    "pdfsmith-extractous": lambda: PdfsmithAdapter("extractous"),
    "pdfsmith-docling": lambda: PdfsmithAdapter("docling"),
    "pdfsmith-marker": lambda: PdfsmithAdapter("marker"),
    # ========== pdfsmith backends (commercial cloud OCR) ==========
    "pdfsmith-aws_textract": lambda: PdfsmithAdapter("aws_textract"),
    "pdfsmith-azure": lambda: PdfsmithAdapter("azure_document_intelligence"),
    "pdfsmith-google": lambda: PdfsmithAdapter("google_document_ai"),
    "pdfsmith-databricks": lambda: PdfsmithAdapter("databricks"),
    "pdfsmith-llamaparse": lambda: PdfsmithAdapter("llamaparse"),
    # ========== pdfsmith backends (frontier LLMs) ==========
    # Anthropic
    "pdfsmith-anthropic": lambda: PdfsmithAdapter("anthropic"),
    "pdfsmith-anthropic-haiku": lambda: PdfsmithAdapter("anthropic", model="claude-3-5-haiku"),
    "pdfsmith-anthropic-sonnet": lambda: PdfsmithAdapter("anthropic", model="claude-sonnet-4-5"),
    # OpenAI
    "pdfsmith-openai": lambda: PdfsmithAdapter("openai"),
    "pdfsmith-openai-mini": lambda: PdfsmithAdapter("openai", model="gpt-4o-mini"),
    "pdfsmith-openai-4o": lambda: PdfsmithAdapter("openai", model="gpt-4o"),
    "pdfsmith-openai-5": lambda: PdfsmithAdapter("openai", model="gpt-5.1"),
    # Gemini
    "pdfsmith-gemini": lambda: PdfsmithAdapter("gemini"),
    "pdfsmith-gemini-flash": lambda: PdfsmithAdapter("gemini", model="gemini-2.0-flash"),
    "pdfsmith-gemini-pro": lambda: PdfsmithAdapter("gemini", model="gemini-3-pro-preview"),
    # ========== Native parsers (not in pdfsmith) ==========
    "tika": TikaParser,
    "marker_ollama": MarkerOllamaParser,
    "landing_ai": LandingAIParser,  # type: ignore[dict-item]
}

# ========== Backward compatibility aliases ==========
# Map old parser names to new pdfsmith-prefixed names
PARSER_ALIASES: dict[str, str] = {
    # Open-source parsers
    "pypdf": "pdfsmith-pypdf",
    "pypdf2": "pdfsmith-pypdf",  # pypdf2 was merged into pypdf
    "pdfplumber": "pdfsmith-pdfplumber",
    "pymupdf": "pdfsmith-pymupdf",
    "pymupdf4llm": "pdfsmith-pymupdf4llm",
    "pdfminer": "pdfsmith-pdfminer",
    "pypdfium2": "pdfsmith-pypdfium2",
    "unstructured": "pdfsmith-unstructured",
    "kreuzberg": "pdfsmith-kreuzberg",
    "extractous": "pdfsmith-extractous",
    "docling": "pdfsmith-docling",
    "marker": "pdfsmith-marker",
    # Commercial cloud OCR
    "aws_textract": "pdfsmith-aws_textract",
    "azure_document_intelligence": "pdfsmith-azure",
    "google_document_ai": "pdfsmith-google",
    "databricks": "pdfsmith-databricks",
    "llamaparse": "pdfsmith-llamaparse",
    # Frontier LLM aliases (old names)
    "claude_3_5_haiku": "pdfsmith-anthropic-haiku",
    "claude_sonnet_4_5": "pdfsmith-anthropic-sonnet",
    "claude_3_opus": "pdfsmith-anthropic-sonnet",  # Map to sonnet as fallback
    "gpt_4o_mini": "pdfsmith-openai-mini",
    "gpt_4o": "pdfsmith-openai-4o",
    "gpt_5_1": "pdfsmith-openai-5",
    "gpt_4_turbo": "pdfsmith-openai-4o",  # Map to 4o as fallback
    "gemini_2_0_flash": "pdfsmith-gemini-flash",
    "gemini_2_5_flash": "pdfsmith-gemini-flash",
    "gemini_3_pro": "pdfsmith-gemini-pro",
    "gemini_2_5_pro": "pdfsmith-gemini-pro",
    "gemini_1_5_pro": "pdfsmith-gemini-pro",
    "gemini_1_5_flash": "pdfsmith-gemini-flash",
}

# Register aliases in PARSER_REGISTRY
for alias, target in PARSER_ALIASES.items():
    if alias not in PARSER_REGISTRY:  # Don't overwrite if already defined
        PARSER_REGISTRY[alias] = PARSER_REGISTRY[target]


# Supported image extensions for document inputs
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".webp", ".bmp"}

# Backends that support image inputs (subset of pdfsmith backends)
IMAGE_CAPABLE_BACKENDS = {
    # Open-source
    "pdfsmith-docling",
    "pdfsmith-kreuzberg",
    "pdfsmith-extractous",
    # Commercial APIs (all support images)
    "pdfsmith-aws_textract",
    "pdfsmith-azure",
    "pdfsmith-google",
    "pdfsmith-databricks",
    "pdfsmith-llamaparse",
    # LLM Vision APIs (all support images)
    "pdfsmith-anthropic",
    "pdfsmith-anthropic-haiku",
    "pdfsmith-anthropic-sonnet",
    "pdfsmith-openai",
    "pdfsmith-openai-mini",
    "pdfsmith-openai-4o",
    "pdfsmith-openai-5",
    "pdfsmith-gemini",
    "pdfsmith-gemini-flash",
    "pdfsmith-gemini-pro",
}


@dataclass
class DocumentInfo:
    """
    Information about a document in the benchmark.

    Fields:
        doc_id: Document identifier
        input_path: Absolute path to input file (PDF or image)
        ground_truth_path: Absolute path to ground truth Markdown file
        metadata: Document metadata (from YAML file)
        input_type: Type of input file ("pdf" or "image")
    """

    doc_id: str
    input_path: Path
    ground_truth_path: Path
    metadata: DocumentMetadata
    input_type: str = "pdf"

    @property
    def pdf_path(self) -> Path:
        """Backward compatibility: alias for input_path."""
        return self.input_path


@dataclass
class LoadedConfig:
    """
    Complete loaded configuration with resolved paths and parser instances.

    This is the runtime-ready version of BenchmarkConfig, with all paths
    resolved to absolute paths and parser classes instantiated.

    Fields:
        config: Original benchmark configuration
        documents: List of documents to benchmark (resolved paths)
        parser_instances: Instantiated parser objects ready to use
        results_dir: Absolute path to results directory
    """

    config: BenchmarkConfig
    documents: list[DocumentInfo]
    parser_instances: list[BaseParser]
    results_dir: Path

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"LoadedConfig(\n"
            f"  name={self.config.name!r},\n"
            f"  documents={len(self.documents)},\n"
            f"  parsers={[p.name for p in self.parser_instances]},\n"
            f"  results_dir={self.results_dir}\n"
            f")"
        )


def discover_documents(
    corpus_dir: Path,
    config: BenchmarkConfig,
) -> list[DocumentInfo]:
    """
    Discover and filter documents based on configuration.

    Args:
        corpus_dir: Absolute path to corpus directory
        config: Benchmark configuration with document filters

    Returns:
        List of DocumentInfo objects matching the filters

    Raises:
        FileNotFoundError: If corpus directory doesn't exist
        ValueError: If no documents match the filters
    """
    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    if not corpus_dir.is_dir():
        raise ValueError(f"Corpus path is not a directory: {corpus_dir}")

    documents = []
    filter_config = config.document_filter

    # If include_doc_ids is specified, only load those documents
    if filter_config.include_doc_ids:
        for doc_id in filter_config.include_doc_ids:
            # Try to find metadata file by searching all YAML files
            # and matching on doc_id field (not filename)
            found = False
            for yaml_file in corpus_dir.glob("**/*.yaml"):
                if yaml_file.name in ["targets.yaml", "schema.yaml"]:
                    continue

                try:
                    metadata = load_metadata(yaml_file)
                    if metadata.doc_id == doc_id:
                        # Found matching document
                        file_stem = yaml_file.stem

                        # Try multiple locations for PDF and ground truth files
                        # Pattern 1: Same directory as YAML (synthetic corpus)
                        pdf_path = yaml_file.parent / f"{file_stem}.pdf"
                        gt_path = yaml_file.parent / f"{file_stem}.md"

                        # Pattern 2: Sibling pdfs/ and ground_truth/ directories (business corpus)
                        if not pdf_path.exists():
                            corpus_root = yaml_file.parent.parent
                            pdf_path = corpus_root / "pdfs" / f"{file_stem}.pdf"
                            gt_path = corpus_root / "ground_truth" / f"{file_stem}.md"

                        # Pattern 3: Image input (OmniDocBench - images/ directory)
                        input_path = pdf_path
                        input_type = "pdf"
                        if not pdf_path.exists():
                            corpus_root = yaml_file.parent.parent
                            for ext in IMAGE_EXTENSIONS:
                                image_path = corpus_root / "images" / f"{file_stem}{ext}"
                                if image_path.exists():
                                    input_path = image_path
                                    input_type = "image"
                                    break
                            # Also check same directory for images
                            if input_type == "pdf":
                                for ext in IMAGE_EXTENSIONS:
                                    image_path = yaml_file.parent / f"{file_stem}{ext}"
                                    if image_path.exists():
                                        input_path = image_path
                                        input_type = "image"
                                        break

                        if input_path.exists() and gt_path.exists():
                            documents.append(
                                DocumentInfo(
                                    doc_id=doc_id,
                                    input_path=input_path,
                                    ground_truth_path=gt_path,
                                    metadata=metadata,
                                    input_type=input_type,
                                )
                            )
                            found = True
                            break
                except Exception:
                    continue

            # Skip if document not found (warn but don't fail)
            if not found:
                continue
    else:
        # Discover all documents and filter
        for metadata_path in corpus_dir.glob("**/*.yaml"):
            # Skip non-metadata YAML files
            if metadata_path.name in ["targets.yaml", "schema.yaml"]:
                continue

            try:
                metadata = load_metadata(metadata_path)
            except Exception:
                # Skip invalid metadata files
                continue

            # Apply corpus filter
            if filter_config.corpora and metadata.corpus not in filter_config.corpora:
                continue

            # Apply domain filter
            if filter_config.domains and metadata.domain not in filter_config.domains:
                continue

            # Apply feature filter (document must have ALL listed features)
            if filter_config.features:
                if not all(f in metadata.features for f in filter_config.features):
                    continue

            # Apply exclude filter
            if filter_config.exclude_doc_ids and metadata.doc_id in filter_config.exclude_doc_ids:
                continue

            # Get document paths - use metadata filename stem, not doc_id
            # (files are named like "01_basic.pdf" not "syn-basic-001.pdf")
            file_stem = metadata_path.stem  # e.g., "01_basic" from "01_basic.yaml"

            # Try multiple locations for PDF and ground truth files
            # Pattern 1: Same directory as YAML (synthetic corpus)
            pdf_path = metadata_path.parent / f"{file_stem}.pdf"
            gt_path = metadata_path.parent / f"{file_stem}.md"

            # Pattern 2: Sibling pdfs/ and ground_truth/ directories (business corpus)
            if not pdf_path.exists():
                corpus_root = metadata_path.parent.parent  # e.g., corpus/business/invoices
                pdf_path = corpus_root / "pdfs" / f"{file_stem}.pdf"
                gt_path = corpus_root / "ground_truth" / f"{file_stem}.md"

            # Determine input path and type (PDF or image)
            input_path = pdf_path
            input_type = "pdf"

            # Pattern 3: Image input (OmniDocBench - images/ directory)
            if not pdf_path.exists():
                corpus_root = metadata_path.parent.parent
                for ext in IMAGE_EXTENSIONS:
                    image_path = corpus_root / "images" / f"{file_stem}{ext}"
                    if image_path.exists():
                        input_path = image_path
                        input_type = "image"
                        break
                # Also check same directory for images
                if input_type == "pdf":
                    for ext in IMAGE_EXTENSIONS:
                        image_path = metadata_path.parent / f"{file_stem}{ext}"
                        if image_path.exists():
                            input_path = image_path
                            input_type = "image"
                            break

            # Verify files exist
            if not input_path.exists() or not gt_path.exists():
                continue

            # Use metadata's doc_id for identification
            doc_id = metadata.doc_id

            documents.append(
                DocumentInfo(
                    doc_id=doc_id,
                    input_path=input_path,
                    ground_truth_path=gt_path,
                    metadata=metadata,
                    input_type=input_type,
                )
            )

    # Apply max_documents limit if specified
    if filter_config.max_documents is not None and len(documents) > filter_config.max_documents:
        documents = documents[: filter_config.max_documents]

    if not documents:
        raise ValueError(
            "No documents found matching filter criteria. "
            "Check corpus_dir and document_filter settings."
        )

    return documents


def load_parsers(
    config: BenchmarkConfig,
) -> list[BaseParser]:
    """
    Load and instantiate parser classes based on configuration.

    Args:
        config: Benchmark configuration with parser settings

    Returns:
        List of instantiated parser objects

    Raises:
        ValueError: If parser not found in registry or instantiation fails
    """
    parser_instances = []

    # If no parsers specified, use all available
    parser_ids = config.parser_config.parsers
    if not parser_ids:
        parser_ids = list(PARSER_REGISTRY.keys())

    for parser_id in parser_ids:
        # Get parser class/factory from registry
        if parser_id not in PARSER_REGISTRY:
            raise ValueError(
                f"Parser '{parser_id}' not found in registry. "
                f"Available parsers: {list(PARSER_REGISTRY.keys())}"
            )

        parser_factory = PARSER_REGISTRY[parser_id]

        # Get parser-specific options if provided
        parser_options = config.parser_config.parser_options.get(parser_id, {})

        # Instantiate parser (factory function or class)
        try:
            if parser_options:
                # Pass options as keyword arguments
                parser_instance = parser_factory(**parser_options)
            else:
                # No options, use defaults (works for both classes and factory functions)
                parser_instance = parser_factory()

            parser_instances.append(parser_instance)
        except TypeError as e:
            raise ValueError(
                f"Failed to instantiate parser '{parser_id}' with options {parser_options}: {e}"
            ) from e

    return parser_instances


def load_benchmark_config(config_path: Path) -> LoadedConfig:
    """
    Load complete benchmark configuration with runtime resolution.

    This is the main entry point for loading a benchmark configuration.
    It loads the YAML config, validates it, resolves all document paths,
    and instantiates parser objects.

    Args:
        config_path: Path to benchmark configuration YAML file

    Returns:
        LoadedConfig with all paths resolved and parsers instantiated

    Raises:
        FileNotFoundError: If config file or corpus directory not found
        ValueError: If validation fails or no documents found
        yaml.YAMLError: If YAML parsing fails

    Example:
        >>> config = load_benchmark_config(Path("benchmarks/mvp_all.yaml"))
        >>> print(f"Loaded {len(config.documents)} documents")
        >>> print(f"Parsers: {[p.name for p in config.parser_instances]}")
    """
    # Load basic configuration from YAML
    config = load_config(config_path)

    # Resolve corpus directory to absolute path
    # If relative, resolve relative to config file location
    corpus_dir = Path(config.corpus_dir)
    if not corpus_dir.is_absolute():
        corpus_dir = (config_path.parent / corpus_dir).resolve()

    # Discover and filter documents
    documents = discover_documents(corpus_dir, config)

    # Load parser classes and instantiate
    parser_instances = load_parsers(config)

    # Resolve results directory to absolute path
    results_dir = Path(config.output_config.results_dir)
    if not results_dir.is_absolute():
        results_dir = (config_path.parent / results_dir).resolve()

    return LoadedConfig(
        config=config,
        documents=documents,
        parser_instances=parser_instances,
        results_dir=results_dir,
    )


def get_available_parsers() -> list[str]:
    """
    Get list of available parser IDs.

    Returns:
        List of parser IDs that can be used in configurations
    """
    return list(PARSER_REGISTRY.keys())


def get_parser_info(parser_id: str) -> dict[str, Any]:
    """
    Get information about a specific parser.

    Args:
        parser_id: Parser identifier

    Returns:
        Dictionary with parser information (name, class, etc.)

    Raises:
        ValueError: If parser not found
    """
    if parser_id not in PARSER_REGISTRY:
        raise ValueError(
            f"Parser '{parser_id}' not found. Available: {list(PARSER_REGISTRY.keys())}"
        )

    parser_class = PARSER_REGISTRY[parser_id]

    # Instantiate with defaults to get name/version
    try:
        instance = parser_class()
        return {
            "id": parser_id,
            "class": parser_class.__name__,
            "name": instance.name,
            "version": instance.version,
            "module": parser_class.__module__,
        }
    except Exception as e:
        return {
            "id": parser_id,
            "class": parser_class.__name__,
            "name": parser_id,
            "version": "unknown",
            "module": parser_class.__module__,
            "error": str(e),
        }
