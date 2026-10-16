"""
Benchmark configuration schema and utilities for PDF-Bench.

This module defines the structure and validation for benchmark configuration files
that control how benchmarks are run. Configuration is stored in YAML format and
includes document filters, parser selection, metric configuration, and output settings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# Valid parser identifiers - loaded dynamically from PARSER_REGISTRY
# This includes both pdfsmith-prefixed names and backward-compat aliases
def _get_valid_parsers() -> list[str]:
    """Get valid parser IDs from the registry (lazy load to avoid circular imports)."""
    try:
        from pdf_bench.loader import PARSER_ALIASES, PARSER_REGISTRY

        # Include both registry keys and backward-compat aliases
        return list(PARSER_REGISTRY.keys()) + list(PARSER_ALIASES.keys())
    except ImportError:
        # Fallback for when loader not available (e.g., during testing)
        return []


# Legacy list kept for reference - actual validation uses _get_valid_parsers()
_LEGACY_PARSERS = [
    # Open-source parsers (old names, now aliases)
    "pymupdf",
    "pymupdf4llm",
    "pdfplumber",
    "pypdf",
    "pypdf2",
    "pypdfium2",
    "pdfminer",
    "extractous",
    "unstructured",
    "marker",
    "docling",
    "kreuzberg",
    # Native parsers (not in pdfsmith)
    "tika",
    "marker_ollama",
    "landing_ai",
    # Commercial (old names)
    "aws_textract",
    "azure_document_intelligence",
    "google_document_ai",
    "databricks",
    "llamaparse",
    # Frontier LLMs (old names)
    "gemini_3_pro",
    "gemini_2_5_pro",
    "gemini_2_0_flash",
    "gpt_5_1",
    "gpt_4o",
    "gpt_4o_mini",
    "claude_sonnet_4_5",
    "claude_3_5_haiku",
]

# Valid metric identifiers
VALID_METRICS = [
    # Text metrics
    "edit_distance",
    "edit_similarity",
    "character_error_rate",
    "chrf++",
    # Structure metrics
    "tree_edit_distance",
    "tree_similarity",
    "element_f1",
    # Table metrics
    "teds",
    "teds_with_content",
    "cell_content_f1",
    "cell_accuracy",
    # Math metrics
    "latex_f1",
    "latex_accuracy",
]

# Valid corpora for filtering
VALID_CORPORA = ["academic", "business", "synthetic"]

# Valid domains for filtering
VALID_DOMAINS = {
    "academic": [
        "arxiv",
        # OmniDocBench domains
        "academic",
        "academic_literature",
        "book",
        "colorful_textbook",
        "education",
        "exam_paper",
        "handwritten",
        "magazine",
        "mixed",
        "news",
        "newspaper",
        "note",
        "PPT2PDF",
        "presentation",
        "research_report",
    ],
    "business": [
        "gov-uk",
        "sec-edgar",
        "legal",
        "invoices",
        "hr",
        "legal_contracts",
        "presentations",
    ],
    "synthetic": ["pandoc", "libreoffice", "tables", "lists", "multicolumn", "mixed"],
}

# Valid features for filtering
VALID_FEATURES = [
    "tables",
    "math",
    "figures",
    "code",
    "lists",
    "footnotes",
    "multi-column",
    "headers-footers",
]


@dataclass
class DocumentFilter:
    """
    Filters for selecting documents to include in benchmark.

    Fields:
        corpora: List of corpora to include (if empty, include all)
        domains: List of domains to include (if empty, include all)
        features: List of features documents must have (if empty, no feature filtering)
        exclude_doc_ids: List of specific document IDs to exclude
        include_doc_ids: List of specific document IDs to include (overrides other filters)
        max_documents: Maximum number of documents to include (if None, include all)
    """

    corpora: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    exclude_doc_ids: list[str] = field(default_factory=list)
    include_doc_ids: list[str] = field(default_factory=list)
    max_documents: int | None = None

    def validate(self) -> None:
        """
        Validate document filter configuration.

        Raises:
            ValueError: If any validation rule is violated
        """
        errors = []

        # Validate corpora
        for corpus in self.corpora:
            if corpus not in VALID_CORPORA:
                errors.append(f"Invalid corpus '{corpus}'. Valid corpora: {VALID_CORPORA}")

        # Validate domains
        for domain in self.domains:
            # Domain must be valid for at least one corpus
            valid = False
            for corpus_domains in VALID_DOMAINS.values():
                if domain in corpus_domains:
                    valid = True
                    break
            if not valid:
                all_domains = [d for domains in VALID_DOMAINS.values() for d in domains]
                errors.append(f"Invalid domain '{domain}'. Valid domains: {all_domains}")

        # Validate features
        for feature in self.features:
            if feature not in VALID_FEATURES:
                errors.append(f"Invalid feature '{feature}'. Valid features: {VALID_FEATURES}")

        # Validate max_documents
        if self.max_documents is not None and self.max_documents < 1:
            errors.append(f"max_documents must be >= 1, got {self.max_documents}")

        if errors:
            raise ValueError(
                f"DocumentFilter validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {error}" for error in errors)
            )


@dataclass
class MetricConfig:
    """
    Configuration for metrics to compute.

    Fields:
        metrics: List of metric identifiers to compute
        aggregate: Whether to compute aggregate scores across all documents
    """

    metrics: list[str] = field(default_factory=list)
    aggregate: bool = True

    def validate(self) -> None:
        """
        Validate metric configuration.

        Raises:
            ValueError: If any validation rule is violated
        """
        errors = []

        if not self.metrics:
            errors.append("At least one metric must be specified")

        for metric in self.metrics:
            if metric not in VALID_METRICS:
                errors.append(f"Invalid metric '{metric}'. Valid metrics: {VALID_METRICS}")

        if errors:
            raise ValueError(
                f"MetricConfig validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {error}" for error in errors)
            )


@dataclass
class ParserConfig:
    """
    Configuration for parsers to benchmark.

    Fields:
        parsers: List of parser identifiers to benchmark (if empty, use all available)
        parser_options: Optional per-parser configuration
            (e.g., {"unstructured": {"strategy": "fast"}})
    """

    parsers: list[str] = field(default_factory=list)
    parser_options: dict[str, dict[str, Any]] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate parser configuration.

        Raises:
            ValueError: If any validation rule is violated
        """
        errors = []
        valid_parsers = _get_valid_parsers()

        # Skip validation if registry not available (during initial import)
        if not valid_parsers:
            return

        for parser in self.parsers:
            if parser not in valid_parsers:
                errors.append(f"Invalid parser '{parser}'. Valid parsers: {valid_parsers}")

        # Validate parser_options keys match parsers
        for parser_name in self.parser_options.keys():
            if parser_name not in valid_parsers:
                errors.append(
                    f"Invalid parser in parser_options: '{parser_name}'. "
                    f"Valid parsers: {valid_parsers}"
                )

        if errors:
            raise ValueError(
                f"ParserConfig validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {error}" for error in errors)
            )


@dataclass
class OutputConfig:
    """
    Configuration for benchmark output and reporting.

    Fields:
        results_dir: Directory to save results (default: "results")
        save_format: Output format for results ("json", "csv", or "both")
        generate_report: Whether to generate HTML report
        report_path: Path to save HTML report (if None, auto-generate)
        save_predictions: Whether to save parser predictions to disk
        verbose: Whether to show detailed progress output
    """

    results_dir: str = "results"
    save_format: str = "json"
    generate_report: bool = True
    report_path: str | None = None
    save_predictions: bool = False
    verbose: bool = True

    def validate(self) -> None:
        """
        Validate output configuration.

        Raises:
            ValueError: If any validation rule is violated
        """
        errors = []

        if self.save_format not in ["json", "csv", "both"]:
            errors.append(f"save_format must be 'json', 'csv', or 'both', got '{self.save_format}'")

        if not self.results_dir:
            errors.append("results_dir cannot be empty")

        if errors:
            raise ValueError(
                f"OutputConfig validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {error}" for error in errors)
            )


@dataclass
class BenchmarkConfig:
    """
    Complete benchmark configuration.

    Fields:
        name: Human-readable benchmark name
        description: Benchmark description
        corpus_dir: Path to corpus directory
        document_filter: Filters for document selection
        parser_config: Parser configuration
        metric_config: Metric configuration
        output_config: Output and reporting configuration
        parallel_workers: Number of parallel workers (0 = auto, 1 = sequential)
    """

    name: str
    description: str
    corpus_dir: str
    document_filter: DocumentFilter
    parser_config: ParserConfig
    metric_config: MetricConfig
    output_config: OutputConfig
    parallel_workers: int = 0

    def validate(self) -> None:
        """
        Validate complete benchmark configuration.

        Raises:
            ValueError: If any validation rule is violated
        """
        errors = []

        # Required fields
        if not self.name:
            errors.append("name is required and cannot be empty")

        if not self.description:
            errors.append("description is required and cannot be empty")

        if not self.corpus_dir:
            errors.append("corpus_dir is required and cannot be empty")

        # Validate parallel_workers
        if self.parallel_workers < 0:
            errors.append(f"parallel_workers must be >= 0, got {self.parallel_workers}")

        if errors:
            raise ValueError(
                f"BenchmarkConfig validation failed with {len(errors)} error(s):\n"
                + "\n".join(f"  - {error}" for error in errors)
            )

        # Validate sub-configs
        self.document_filter.validate()
        self.parser_config.validate()
        self.metric_config.validate()
        self.output_config.validate()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary for YAML serialization.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "name": self.name,
            "description": self.description,
            "corpus_dir": self.corpus_dir,
            "document_filter": {
                "corpora": self.document_filter.corpora,
                "domains": self.document_filter.domains,
                "features": self.document_filter.features,
                "exclude_doc_ids": self.document_filter.exclude_doc_ids,
                "include_doc_ids": self.document_filter.include_doc_ids,
                "max_documents": self.document_filter.max_documents,
            },
            "parser_config": {
                "parsers": self.parser_config.parsers,
                "parser_options": self.parser_config.parser_options,
            },
            "metric_config": {
                "metrics": self.metric_config.metrics,
                "aggregate": self.metric_config.aggregate,
            },
            "output_config": {
                "results_dir": self.output_config.results_dir,
                "save_format": self.output_config.save_format,
                "generate_report": self.output_config.generate_report,
                "report_path": self.output_config.report_path,
                "save_predictions": self.output_config.save_predictions,
                "verbose": self.output_config.verbose,
            },
            "parallel_workers": self.parallel_workers,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BenchmarkConfig":
        """
        Create configuration instance from dictionary.

        Args:
            data: Dictionary with configuration fields

        Returns:
            BenchmarkConfig instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If validation fails
        """
        # Extract required fields
        try:
            name = data["name"]
            description = data["description"]
            corpus_dir = data["corpus_dir"]
        except KeyError as e:
            raise KeyError(f"Missing required field: {e}") from e

        # Parse document filter
        doc_filter_data = data.get("document_filter", {})
        document_filter = DocumentFilter(
            corpora=doc_filter_data.get("corpora", []),
            domains=doc_filter_data.get("domains", []),
            features=doc_filter_data.get("features", []),
            exclude_doc_ids=doc_filter_data.get("exclude_doc_ids", []),
            include_doc_ids=doc_filter_data.get("include_doc_ids", []),
            max_documents=doc_filter_data.get("max_documents"),
        )

        # Parse parser config
        parser_config_data = data.get("parser_config", {})
        parser_config = ParserConfig(
            parsers=parser_config_data.get("parsers", []),
            parser_options=parser_config_data.get("parser_options", {}),
        )

        # Parse metric config
        metric_config_data = data.get("metric_config", {})
        metric_config = MetricConfig(
            metrics=metric_config_data.get("metrics", []),
            aggregate=metric_config_data.get("aggregate", True),
        )

        # Parse output config
        output_config_data = data.get("output_config", {})
        output_config = OutputConfig(
            results_dir=output_config_data.get("results_dir", "results"),
            save_format=output_config_data.get("save_format", "json"),
            generate_report=output_config_data.get("generate_report", True),
            report_path=output_config_data.get("report_path"),
            save_predictions=output_config_data.get("save_predictions", False),
            verbose=output_config_data.get("verbose", True),
        )

        # Create instance
        config = cls(
            name=name,
            description=description,
            corpus_dir=corpus_dir,
            document_filter=document_filter,
            parser_config=parser_config,
            metric_config=metric_config,
            output_config=output_config,
            parallel_workers=data.get("parallel_workers", 0),
        )

        # Validate before returning
        config.validate()
        return config


def load_config(yaml_path: Path) -> BenchmarkConfig:
    """
    Load benchmark configuration from YAML file.

    Args:
        yaml_path: Path to YAML configuration file

    Returns:
        BenchmarkConfig instance

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
        KeyError: If required fields are missing
        ValueError: If validation fails
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML file {yaml_path}: {e}") from e

    if data is None:
        raise ValueError(f"Empty YAML file: {yaml_path}")

    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a dictionary, got {type(data)}")

    return BenchmarkConfig.from_dict(data)


def save_config(config: BenchmarkConfig, yaml_path: Path) -> None:
    """
    Save benchmark configuration to YAML file.

    Args:
        config: BenchmarkConfig instance to save
        yaml_path: Path to save YAML file

    Raises:
        ValueError: If configuration validation fails
        OSError: If file cannot be written
    """
    # Validate before saving
    config.validate()

    # Create parent directory if it doesn't exist
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict and save with nice formatting
    data = config.to_dict()

    try:
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,  # Preserve field order
                width=100,
            )
    except OSError as e:
        raise OSError(f"Failed to write configuration file {yaml_path}: {e}") from e
