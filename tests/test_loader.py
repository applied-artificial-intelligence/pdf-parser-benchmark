"""Tests for configuration loader with runtime resolution."""

import tempfile
from pathlib import Path

import pytest

from pdf_bench.config import (
    BenchmarkConfig,
    DocumentFilter,
    MetricConfig,
    OutputConfig,
    ParserConfig,
    save_config,
)
from pdf_bench.loader import (
    PARSER_REGISTRY,
    DocumentInfo,
    LoadedConfig,
    discover_documents,
    get_available_parsers,
    get_parser_info,
    load_benchmark_config,
    load_parsers,
)
from pdf_bench.systems import BaseParser
from pdf_bench.utils.metadata import DocumentMetadata, save_metadata


class TestParserRegistry:
    """Tests for parser registry."""

    def test_registry_not_empty(self) -> None:
        """Parser registry should contain implemented parsers."""
        assert len(PARSER_REGISTRY) > 0

    def test_registry_contains_expected_parsers(self) -> None:
        """Registry should contain all implemented parsers."""
        expected = {"pymupdf", "pdfplumber", "marker", "unstructured"}
        assert expected.issubset(set(PARSER_REGISTRY.keys()))

    def test_all_registry_values_are_classes(self) -> None:
        """All registry values should be classes."""
        for parser_class in PARSER_REGISTRY.values():
            assert isinstance(parser_class, type)

    def test_all_registry_classes_inherit_base_parser(self) -> None:
        """All parser classes should inherit from BaseParser."""
        for parser_class in PARSER_REGISTRY.values():
            assert issubclass(parser_class, BaseParser)


class TestGetAvailableParsers:
    """Tests for get_available_parsers function."""

    def test_returns_list(self) -> None:
        """Should return a list of parser IDs."""
        parsers = get_available_parsers()
        assert isinstance(parsers, list)
        assert all(isinstance(p, str) for p in parsers)

    def test_returns_all_registry_keys(self) -> None:
        """Should return all parser IDs from registry."""
        parsers = get_available_parsers()
        assert set(parsers) == set(PARSER_REGISTRY.keys())


class TestGetParserInfo:
    """Tests for get_parser_info function."""

    def test_valid_parser(self) -> None:
        """Should return info for valid parser."""
        info = get_parser_info("pymupdf")
        assert "id" in info
        assert "class" in info
        assert "name" in info
        assert info["id"] == "pymupdf"

    def test_invalid_parser(self) -> None:
        """Should raise ValueError for invalid parser."""
        with pytest.raises(ValueError, match="not found"):
            get_parser_info("nonexistent")


class TestLoadParsers:
    """Tests for load_parsers function."""

    def test_load_single_parser(self) -> None:
        """Should load a single parser."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        parsers = load_parsers(config)
        assert len(parsers) == 1
        assert parsers[0].name == "pymupdf"

    def test_load_multiple_parsers(self) -> None:
        """Should load multiple parsers."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf", "pdfplumber"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        parsers = load_parsers(config)
        assert len(parsers) == 2
        assert {p.name for p in parsers} == {"pymupdf", "pdfplumber"}

    def test_load_all_parsers_when_empty(self) -> None:
        """Should load all available parsers when list is empty."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=[]),  # Empty = all
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        parsers = load_parsers(config)
        assert len(parsers) == len(PARSER_REGISTRY)

    def test_load_parser_with_options(self) -> None:
        """Should pass options to parser constructor."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(
                parsers=["unstructured"],
                parser_options={"unstructured": {"strategy": "fast"}},
            ),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        parsers = load_parsers(config)
        assert len(parsers) == 1
        # Parser should be instantiated with options

    def test_invalid_parser_raises_error(self) -> None:
        """Should raise ValueError for invalid parser ID."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["nonexistent"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        with pytest.raises(ValueError, match="not found in registry"):
            load_parsers(config)


class TestDiscoverDocuments:
    """Tests for discover_documents function."""

    def test_nonexistent_corpus_dir(self) -> None:
        """Should raise FileNotFoundError for nonexistent directory."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="nonexistent",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        with pytest.raises(FileNotFoundError):
            discover_documents(Path("/nonexistent/path"), config)

    def test_corpus_dir_is_file(self) -> None:
        """Should raise ValueError if corpus_dir is a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file instead of directory
            file_path = Path(tmpdir) / "not_a_dir"
            file_path.write_text("test", encoding="utf-8")

            config = BenchmarkConfig(
                name="Test",
                description="Test",
                corpus_dir=str(file_path),
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=["pymupdf"]),
                metric_config=MetricConfig(metrics=["edit_distance"]),
                output_config=OutputConfig(),
            )

            with pytest.raises(ValueError, match="not a directory"):
                discover_documents(file_path, config)

    def test_discover_synthetic_corpus(self) -> None:
        """Should discover documents from synthetic corpus."""
        corpus_dir = Path("corpus")
        if not corpus_dir.exists():
            pytest.skip("Corpus directory not found")

        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(corpora=["synthetic"]),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        documents = discover_documents(corpus_dir, config)
        assert len(documents) > 0
        assert all(isinstance(d, DocumentInfo) for d in documents)
        assert all(d.metadata.corpus == "synthetic" for d in documents)

    def test_corpus_filter(self) -> None:
        """Should filter by corpus."""
        corpus_dir = Path("corpus")
        if not corpus_dir.exists():
            pytest.skip("Corpus directory not found")

        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(corpora=["synthetic"]),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        documents = discover_documents(corpus_dir, config)
        # All should be synthetic
        assert all(d.metadata.corpus == "synthetic" for d in documents)

    def test_feature_filter(self) -> None:
        """Should filter by features."""
        corpus_dir = Path("corpus")
        if not corpus_dir.exists():
            pytest.skip("Corpus directory not found")

        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(features=["tables"]),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        documents = discover_documents(corpus_dir, config)
        # All should have tables feature
        assert all("tables" in d.metadata.features for d in documents)

    def test_max_documents_limit(self) -> None:
        """Should respect max_documents limit."""
        corpus_dir = Path("corpus")
        if not corpus_dir.exists():
            pytest.skip("Corpus directory not found")

        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(corpora=["synthetic"], max_documents=2),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        documents = discover_documents(corpus_dir, config)
        assert len(documents) <= 2

    def test_no_documents_raises_error(self) -> None:
        """Should raise ValueError if no documents match filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty corpus directory
            corpus_dir = Path(tmpdir)

            config = BenchmarkConfig(
                name="Test",
                description="Test",
                corpus_dir=str(corpus_dir),
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=["pymupdf"]),
                metric_config=MetricConfig(metrics=["edit_distance"]),
                output_config=OutputConfig(),
            )

            with pytest.raises(ValueError, match="No documents found"):
                discover_documents(corpus_dir, config)


class TestLoadBenchmarkConfig:
    """Tests for load_benchmark_config function."""

    def test_load_example_config(self) -> None:
        """Should successfully load example config."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("Example config not found")

        loaded = load_benchmark_config(config_path)

        assert isinstance(loaded, LoadedConfig)
        assert isinstance(loaded.config, BenchmarkConfig)
        assert len(loaded.documents) > 0
        assert len(loaded.parser_instances) > 0
        assert loaded.results_dir.is_absolute()

    def test_loaded_config_str(self) -> None:
        """LoadedConfig string representation should be informative."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("Example config not found")

        loaded = load_benchmark_config(config_path)
        str_repr = str(loaded)

        assert "LoadedConfig" in str_repr
        assert loaded.config.name in str_repr
        assert str(len(loaded.documents)) in str_repr

    def test_relative_corpus_dir_resolved(self) -> None:
        """Relative corpus_dir should be resolved relative to config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create corpus directory
            corpus_dir = tmppath / "corpus" / "synthetic"
            corpus_dir.mkdir(parents=True)

            # Create a minimal document
            doc_id = "test_doc"
            metadata = DocumentMetadata(
                doc_id=doc_id,
                source_url="https://example.com/test.pdf",
                corpus="synthetic",
                domain="pandoc",
            )
            save_metadata(metadata, corpus_dir / f"{doc_id}.yaml")

            # Create dummy PDF and markdown
            (corpus_dir / f"{doc_id}.pdf").write_bytes(b"%PDF-1.4 test")
            (corpus_dir / f"{doc_id}.md").write_text("# Test", encoding="utf-8")

            # Create config with relative corpus_dir
            config = BenchmarkConfig(
                name="Test",
                description="Test",
                corpus_dir="corpus",  # Relative path
                document_filter=DocumentFilter(),
                parser_config=ParserConfig(parsers=["pymupdf"]),
                metric_config=MetricConfig(metrics=["edit_distance"]),
                output_config=OutputConfig(),
            )
            config_path = tmppath / "config.yaml"
            save_config(config, config_path)

            # Load and check corpus_dir was resolved
            loaded = load_benchmark_config(config_path)
            assert len(loaded.documents) == 1
            assert loaded.documents[0].pdf_path.is_absolute()
            assert loaded.documents[0].pdf_path.exists()

    def test_results_dir_resolved(self) -> None:
        """Results directory should be resolved to absolute path."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("Example config not found")

        loaded = load_benchmark_config(config_path)
        assert loaded.results_dir.is_absolute()

    def test_all_document_paths_absolute(self) -> None:
        """All document paths should be absolute."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("Example config not found")

        loaded = load_benchmark_config(config_path)

        for doc in loaded.documents:
            assert doc.pdf_path.is_absolute()
            assert doc.ground_truth_path.is_absolute()

    def test_all_document_files_exist(self) -> None:
        """All referenced document files should exist."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("Example config not found")

        loaded = load_benchmark_config(config_path)

        for doc in loaded.documents:
            assert doc.pdf_path.exists(), f"PDF not found: {doc.pdf_path}"
            assert doc.ground_truth_path.exists(), f"GT not found: {doc.ground_truth_path}"

    def test_parser_instances_match_config(self) -> None:
        """Parser instances should match configuration."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("Example config not found")

        loaded = load_benchmark_config(config_path)

        # Number of instances should match config
        expected_count = len(loaded.config.parser_config.parsers)
        if expected_count == 0:
            # Empty = all parsers
            expected_count = len(PARSER_REGISTRY)

        assert len(loaded.parser_instances) == expected_count

        # Each instance should be a BaseParser
        for parser in loaded.parser_instances:
            assert isinstance(parser, BaseParser)


class TestDocumentInfo:
    """Tests for DocumentInfo dataclass."""

    def test_creation(self) -> None:
        """Should create DocumentInfo with required fields."""
        metadata = DocumentMetadata(
            doc_id="test",
            source_url="https://example.com/test.pdf",
            corpus="synthetic",
            domain="pandoc",
        )

        doc_info = DocumentInfo(
            doc_id="test",
            pdf_path=Path("/path/to/test.pdf"),
            ground_truth_path=Path("/path/to/test.md"),
            metadata=metadata,
        )

        assert doc_info.doc_id == "test"
        assert doc_info.pdf_path == Path("/path/to/test.pdf")
        assert doc_info.ground_truth_path == Path("/path/to/test.md")
        assert doc_info.metadata.doc_id == "test"


class TestLoadedConfig:
    """Tests for LoadedConfig dataclass."""

    def test_str_representation(self) -> None:
        """String representation should be readable."""
        config = BenchmarkConfig(
            name="Test Benchmark",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        loaded = LoadedConfig(
            config=config,
            documents=[],
            parser_instances=[],
            results_dir=Path("/tmp/results"),
        )

        str_repr = str(loaded)
        assert "LoadedConfig" in str_repr
        assert "Test Benchmark" in str_repr
        assert "0" in str_repr  # 0 documents
        assert "/tmp/results" in str_repr


class TestIntegration:
    """Integration tests using real example configs."""

    def test_mvp_all_config(self) -> None:
        """Should load mvp_all.yaml config."""
        config_path = Path("benchmarks/mvp_all.yaml")
        if not config_path.exists():
            pytest.skip("mvp_all.yaml not found")

        loaded = load_benchmark_config(config_path)

        # Should have documents
        assert len(loaded.documents) > 0

        # Should have parsers
        assert len(loaded.parser_instances) > 0

        # All parsers should be valid
        for parser in loaded.parser_instances:
            assert parser.name
            assert parser.version

    def test_quick_test_config(self) -> None:
        """Should load quick_test.yaml config."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("quick_test.yaml not found")

        loaded = load_benchmark_config(config_path)

        # Should have limited documents (max_documents constraint)
        assert len(loaded.documents) <= 3

        # Should have limited parsers
        assert len(loaded.parser_instances) <= 2

    def test_tables_only_config(self) -> None:
        """Should load tables_only.yaml config."""
        config_path = Path("benchmarks/tables_only.yaml")
        if not config_path.exists():
            pytest.skip("tables_only.yaml not found")

        loaded = load_benchmark_config(config_path)

        # All documents should have tables feature
        for doc in loaded.documents:
            assert "tables" in doc.metadata.features

    def test_math_only_config(self) -> None:
        """Should load math_only.yaml config."""
        config_path = Path("benchmarks/math_only.yaml")
        if not config_path.exists():
            pytest.skip("math_only.yaml not found")

        loaded = load_benchmark_config(config_path)

        # All documents should have math feature
        for doc in loaded.documents:
            assert "math" in doc.metadata.features
