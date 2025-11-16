"""Tests for benchmark configuration schema and validation."""

import tempfile
from pathlib import Path

import pytest
import yaml

from pdf_bench.config import (
    VALID_CORPORA,
    VALID_FEATURES,
    VALID_METRICS,
    VALID_PARSERS,
    BenchmarkConfig,
    DocumentFilter,
    MetricConfig,
    OutputConfig,
    ParserConfig,
    load_config,
    save_config,
)


class TestDocumentFilter:
    """Tests for DocumentFilter class."""

    def test_empty_filter_valid(self) -> None:
        """Empty filter (no restrictions) should be valid."""
        filter_obj = DocumentFilter()
        filter_obj.validate()  # Should not raise

    def test_valid_corpora(self) -> None:
        """Valid corpora should pass validation."""
        filter_obj = DocumentFilter(corpora=["academic", "synthetic"])
        filter_obj.validate()  # Should not raise

    def test_invalid_corpus(self) -> None:
        """Invalid corpus should raise ValueError."""
        filter_obj = DocumentFilter(corpora=["invalid"])
        with pytest.raises(ValueError, match="Invalid corpus"):
            filter_obj.validate()

    def test_valid_domains(self) -> None:
        """Valid domains should pass validation."""
        filter_obj = DocumentFilter(domains=["arxiv", "gov-uk"])
        filter_obj.validate()  # Should not raise

    def test_invalid_domain(self) -> None:
        """Invalid domain should raise ValueError."""
        filter_obj = DocumentFilter(domains=["invalid"])
        with pytest.raises(ValueError, match="Invalid domain"):
            filter_obj.validate()

    def test_valid_features(self) -> None:
        """Valid features should pass validation."""
        filter_obj = DocumentFilter(features=["tables", "math", "code"])
        filter_obj.validate()  # Should not raise

    def test_invalid_feature(self) -> None:
        """Invalid feature should raise ValueError."""
        filter_obj = DocumentFilter(features=["invalid"])
        with pytest.raises(ValueError, match="Invalid feature"):
            filter_obj.validate()

    def test_max_documents_positive(self) -> None:
        """Positive max_documents should be valid."""
        filter_obj = DocumentFilter(max_documents=10)
        filter_obj.validate()  # Should not raise

    def test_max_documents_zero(self) -> None:
        """max_documents=0 should raise ValueError."""
        filter_obj = DocumentFilter(max_documents=0)
        with pytest.raises(ValueError, match="max_documents must be >= 1"):
            filter_obj.validate()

    def test_max_documents_negative(self) -> None:
        """Negative max_documents should raise ValueError."""
        filter_obj = DocumentFilter(max_documents=-5)
        with pytest.raises(ValueError, match="max_documents must be >= 1"):
            filter_obj.validate()

    def test_doc_id_lists(self) -> None:
        """Document ID include/exclude lists should be valid."""
        filter_obj = DocumentFilter(
            include_doc_ids=["doc1", "doc2"], exclude_doc_ids=["doc3", "doc4"]
        )
        filter_obj.validate()  # Should not raise


class TestMetricConfig:
    """Tests for MetricConfig class."""

    def test_valid_metrics(self) -> None:
        """Valid metrics should pass validation."""
        config = MetricConfig(metrics=["edit_distance", "chrf++", "teds"])
        config.validate()  # Should not raise

    def test_empty_metrics(self) -> None:
        """Empty metrics list should raise ValueError."""
        config = MetricConfig(metrics=[])
        with pytest.raises(ValueError, match="At least one metric must be specified"):
            config.validate()

    def test_invalid_metric(self) -> None:
        """Invalid metric should raise ValueError."""
        config = MetricConfig(metrics=["invalid_metric"])
        with pytest.raises(ValueError, match="Invalid metric"):
            config.validate()

    def test_aggregate_flag(self) -> None:
        """Aggregate flag should be configurable."""
        config = MetricConfig(metrics=["edit_distance"], aggregate=False)
        config.validate()  # Should not raise
        assert config.aggregate is False


class TestParserConfig:
    """Tests for ParserConfig class."""

    def test_empty_parsers_valid(self) -> None:
        """Empty parsers list (use all available) should be valid."""
        config = ParserConfig(parsers=[])
        config.validate()  # Should not raise

    def test_valid_parsers(self) -> None:
        """Valid parsers should pass validation."""
        config = ParserConfig(parsers=["pymupdf", "marker", "unstructured"])
        config.validate()  # Should not raise

    def test_invalid_parser(self) -> None:
        """Invalid parser should raise ValueError."""
        config = ParserConfig(parsers=["invalid_parser"])
        with pytest.raises(ValueError, match="Invalid parser"):
            config.validate()

    def test_parser_options(self) -> None:
        """Parser options should be valid."""
        config = ParserConfig(
            parsers=["unstructured"],
            parser_options={"unstructured": {"strategy": "fast"}},
        )
        config.validate()  # Should not raise

    def test_parser_options_invalid_parser(self) -> None:
        """Parser options for invalid parser should raise ValueError."""
        config = ParserConfig(parser_options={"invalid": {"key": "value"}})
        with pytest.raises(ValueError, match="Invalid parser in parser_options"):
            config.validate()


class TestOutputConfig:
    """Tests for OutputConfig class."""

    def test_defaults(self) -> None:
        """Default output configuration should be valid."""
        config = OutputConfig()
        config.validate()  # Should not raise
        assert config.results_dir == "results"
        assert config.save_format == "json"
        assert config.generate_report is True

    def test_valid_save_formats(self) -> None:
        """All valid save formats should pass validation."""
        for fmt in ["json", "csv", "both"]:
            config = OutputConfig(save_format=fmt)
            config.validate()  # Should not raise

    def test_invalid_save_format(self) -> None:
        """Invalid save format should raise ValueError."""
        config = OutputConfig(save_format="invalid")
        with pytest.raises(ValueError, match="save_format must be"):
            config.validate()

    def test_empty_results_dir(self) -> None:
        """Empty results_dir should raise ValueError."""
        config = OutputConfig(results_dir="")
        with pytest.raises(ValueError, match="results_dir cannot be empty"):
            config.validate()

    def test_report_path(self) -> None:
        """Custom report path should be valid."""
        config = OutputConfig(report_path="custom/path/report.html")
        config.validate()  # Should not raise


class TestBenchmarkConfig:
    """Tests for complete BenchmarkConfig class."""

    def test_minimal_valid_config(self) -> None:
        """Minimal valid configuration should pass validation."""
        config = BenchmarkConfig(
            name="Test Benchmark",
            description="Test description",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )
        config.validate()  # Should not raise

    def test_empty_name(self) -> None:
        """Empty name should raise ValueError."""
        config = BenchmarkConfig(
            name="",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )
        with pytest.raises(ValueError, match="name is required"):
            config.validate()

    def test_empty_description(self) -> None:
        """Empty description should raise ValueError."""
        config = BenchmarkConfig(
            name="Test",
            description="",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )
        with pytest.raises(ValueError, match="description is required"):
            config.validate()

    def test_empty_corpus_dir(self) -> None:
        """Empty corpus_dir should raise ValueError."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )
        with pytest.raises(ValueError, match="corpus_dir is required"):
            config.validate()

    def test_parallel_workers_negative(self) -> None:
        """Negative parallel_workers should raise ValueError."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
            parallel_workers=-1,
        )
        with pytest.raises(ValueError, match="parallel_workers must be >= 0"):
            config.validate()

    def test_parallel_workers_zero(self) -> None:
        """parallel_workers=0 (auto) should be valid."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
            parallel_workers=0,
        )
        config.validate()  # Should not raise

    def test_subconfig_validation(self) -> None:
        """Invalid sub-config should raise ValueError from parent."""
        config = BenchmarkConfig(
            name="Test",
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(features=["invalid"]),  # Invalid feature
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )
        with pytest.raises(ValueError, match="Invalid feature"):
            config.validate()


class TestConfigSerialization:
    """Tests for config to_dict/from_dict conversion."""

    def test_to_dict_complete(self) -> None:
        """to_dict should produce complete dictionary."""
        config = BenchmarkConfig(
            name="Test Benchmark",
            description="Test description",
            corpus_dir="corpus",
            document_filter=DocumentFilter(corpora=["synthetic"], max_documents=10),
            parser_config=ParserConfig(parsers=["pymupdf", "marker"]),
            metric_config=MetricConfig(metrics=["edit_distance", "chrf++"]),
            output_config=OutputConfig(save_format="both"),
            parallel_workers=4,
        )
        data = config.to_dict()

        assert data["name"] == "Test Benchmark"
        assert data["description"] == "Test description"
        assert data["corpus_dir"] == "corpus"
        assert data["document_filter"]["corpora"] == ["synthetic"]
        assert data["document_filter"]["max_documents"] == 10
        assert data["parser_config"]["parsers"] == ["pymupdf", "marker"]
        assert data["metric_config"]["metrics"] == ["edit_distance", "chrf++"]
        assert data["output_config"]["save_format"] == "both"
        assert data["parallel_workers"] == 4

    def test_from_dict_complete(self) -> None:
        """from_dict should reconstruct config from dictionary."""
        data = {
            "name": "Test Benchmark",
            "description": "Test description",
            "corpus_dir": "corpus",
            "document_filter": {"corpora": ["synthetic"], "max_documents": 10},
            "parser_config": {"parsers": ["pymupdf"]},
            "metric_config": {"metrics": ["edit_distance"]},
            "output_config": {"save_format": "json"},
            "parallel_workers": 2,
        }
        config = BenchmarkConfig.from_dict(data)

        assert config.name == "Test Benchmark"
        assert config.description == "Test description"
        assert config.corpus_dir == "corpus"
        assert config.document_filter.corpora == ["synthetic"]
        assert config.document_filter.max_documents == 10
        assert config.parser_config.parsers == ["pymupdf"]
        assert config.metric_config.metrics == ["edit_distance"]
        assert config.output_config.save_format == "json"
        assert config.parallel_workers == 2

    def test_from_dict_missing_required(self) -> None:
        """from_dict should raise KeyError for missing required fields."""
        data = {"name": "Test"}  # Missing description and corpus_dir
        with pytest.raises(KeyError, match="Missing required field"):
            BenchmarkConfig.from_dict(data)

    def test_round_trip(self) -> None:
        """to_dict -> from_dict should preserve config."""
        original = BenchmarkConfig(
            name="Test",
            description="Description",
            corpus_dir="corpus",
            document_filter=DocumentFilter(features=["tables"]),
            parser_config=ParserConfig(parsers=["marker"]),
            metric_config=MetricConfig(metrics=["teds", "latex_f1"]),
            output_config=OutputConfig(verbose=False),
        )
        data = original.to_dict()
        restored = BenchmarkConfig.from_dict(data)

        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.corpus_dir == original.corpus_dir
        assert restored.document_filter.features == original.document_filter.features
        assert restored.parser_config.parsers == original.parser_config.parsers
        assert restored.metric_config.metrics == original.metric_config.metrics
        assert restored.output_config.verbose == original.output_config.verbose


class TestConfigFileIO:
    """Tests for loading/saving config files."""

    def test_save_and_load(self) -> None:
        """Save config to file and load it back."""
        config = BenchmarkConfig(
            name="Test Benchmark",
            description="Test description",
            corpus_dir="corpus",
            document_filter=DocumentFilter(corpora=["synthetic"]),
            parser_config=ParserConfig(parsers=["pymupdf", "marker"]),
            metric_config=MetricConfig(metrics=["edit_distance", "chrf++"]),
            output_config=OutputConfig(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_config.yaml"

            # Save
            save_config(config, path)
            assert path.exists()

            # Load
            loaded = load_config(path)
            assert loaded.name == config.name
            assert loaded.description == config.description
            assert loaded.corpus_dir == config.corpus_dir
            assert loaded.parser_config.parsers == config.parser_config.parsers

    def test_load_nonexistent(self) -> None:
        """Loading nonexistent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/path/config.yaml"))

    def test_load_invalid_yaml(self) -> None:
        """Loading invalid YAML should raise YAMLError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.yaml"
            path.write_text("invalid: yaml: syntax: [[[", encoding="utf-8")

            with pytest.raises(yaml.YAMLError):
                load_config(path)

    def test_load_empty_file(self) -> None:
        """Loading empty YAML should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.yaml"
            path.write_text("", encoding="utf-8")

            with pytest.raises(ValueError, match="Empty YAML file"):
                load_config(path)

    def test_load_non_dict(self) -> None:
        """Loading YAML with non-dict root should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "list.yaml"
            path.write_text("- item1\n- item2\n", encoding="utf-8")

            with pytest.raises(ValueError, match="must contain a dictionary"):
                load_config(path)

    def test_save_invalid_config(self) -> None:
        """Saving invalid config should raise ValueError."""
        invalid_config = BenchmarkConfig(
            name="",  # Invalid: empty name
            description="Test",
            corpus_dir="corpus",
            document_filter=DocumentFilter(),
            parser_config=ParserConfig(parsers=["pymupdf"]),
            metric_config=MetricConfig(metrics=["edit_distance"]),
            output_config=OutputConfig(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.yaml"
            with pytest.raises(ValueError, match="name is required"):
                save_config(invalid_config, path)


class TestExampleConfigs:
    """Tests for example configuration files in benchmarks/ directory."""

    def test_mvp_all_yaml(self) -> None:
        """mvp_all.yaml should be valid and loadable."""
        config_path = Path("benchmarks/mvp_all.yaml")
        if not config_path.exists():
            pytest.skip("mvp_all.yaml not found")

        config = load_config(config_path)
        config.validate()  # Should not raise

        # Verify expected content
        assert "MVP" in config.name or "all" in config.name.lower()
        assert "synthetic" in config.document_filter.corpora
        assert len(config.parser_config.parsers) == 4  # All 4 parsers
        assert len(config.metric_config.metrics) >= 5  # Multiple metrics

    def test_quick_test_yaml(self) -> None:
        """quick_test.yaml should be valid and loadable."""
        config_path = Path("benchmarks/quick_test.yaml")
        if not config_path.exists():
            pytest.skip("quick_test.yaml not found")

        config = load_config(config_path)
        config.validate()  # Should not raise

        # Verify it's actually "quick"
        assert config.document_filter.max_documents is not None
        assert config.document_filter.max_documents <= 5
        assert len(config.parser_config.parsers) <= 2

    def test_tables_only_yaml(self) -> None:
        """tables_only.yaml should be valid and loadable."""
        config_path = Path("benchmarks/tables_only.yaml")
        if not config_path.exists():
            pytest.skip("tables_only.yaml not found")

        config = load_config(config_path)
        config.validate()  # Should not raise

        # Should filter for tables feature
        assert "tables" in config.document_filter.features
        # Should include table metrics
        assert any("teds" in m or "cell" in m for m in config.metric_config.metrics)

    def test_math_only_yaml(self) -> None:
        """math_only.yaml should be valid and loadable."""
        config_path = Path("benchmarks/math_only.yaml")
        if not config_path.exists():
            pytest.skip("math_only.yaml not found")

        config = load_config(config_path)
        config.validate()  # Should not raise

        # Should filter for math feature
        assert "math" in config.document_filter.features
        # Should include LaTeX metrics
        assert any("latex" in m for m in config.metric_config.metrics)


class TestConstantsCompleteness:
    """Tests to ensure constants are comprehensive and up-to-date."""

    def test_valid_parsers_matches_imports(self) -> None:
        """VALID_PARSERS should match available parser implementations."""
        # We have 4 parsers currently implemented
        implemented_parsers = {"pymupdf", "pdfplumber", "marker", "unstructured"}
        for parser in implemented_parsers:
            assert parser in VALID_PARSERS, f"Parser '{parser}' missing from VALID_PARSERS"

    def test_valid_metrics_comprehensive(self) -> None:
        """VALID_METRICS should include all metric types."""
        # Check we have metrics from each category
        assert any("edit" in m for m in VALID_METRICS), "Missing edit distance metrics"
        assert "chrf++" in VALID_METRICS, "Missing chrf++ metric"
        assert any("tree" in m for m in VALID_METRICS), "Missing tree metrics"
        assert "teds" in VALID_METRICS, "Missing TEDS metric"
        assert any("latex" in m for m in VALID_METRICS), "Missing LaTeX metrics"

    def test_valid_corpora_matches_metadata(self) -> None:
        """VALID_CORPORA should match metadata.py VALID_CORPORA."""
        # Both should define the same corpora
        assert set(VALID_CORPORA) == {"academic", "business", "synthetic"}

    def test_valid_features_matches_metadata(self) -> None:
        """VALID_FEATURES should match metadata.py VALID_FEATURES."""
        # Should include common features
        common_features = {"tables", "math", "figures", "code", "lists"}
        assert common_features.issubset(set(VALID_FEATURES))
