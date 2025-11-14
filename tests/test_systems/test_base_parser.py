"""Unit tests for BaseParser abstract class.

This module tests the BaseParser interface to ensure that:
1. The abstract class cannot be instantiated directly
2. Concrete implementations must implement all abstract methods
3. The interface contract is enforced at runtime
4. Type checking works correctly with the abstract base
"""

from pathlib import Path

import pytest

from pdf_bench.systems.base_parser import BaseParser


class TestBaseParserAbstractness:
    """Test that BaseParser is properly abstract and cannot be instantiated."""

    def test_cannot_instantiate_base_parser_directly(self) -> None:
        """BaseParser should raise TypeError when instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseParser()  # type: ignore

    def test_missing_name_property_raises_error(self) -> None:
        """A class missing the name property should fail to instantiate."""

        class IncompleteParser1(BaseParser):
            @property
            def version(self) -> str:
                return "1.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteParser1()  # type: ignore

    def test_missing_version_property_raises_error(self) -> None:
        """A class missing the version property should fail to instantiate."""

        class IncompleteParser2(BaseParser):
            @property
            def name(self) -> str:
                return "test"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteParser2()  # type: ignore

    def test_missing_parse_method_raises_error(self) -> None:
        """A class missing the parse method should fail to instantiate."""

        class IncompleteParser3(BaseParser):
            @property
            def name(self) -> str:
                return "test"

            @property
            def version(self) -> str:
                return "1.0.0"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteParser3()  # type: ignore


class TestConcreteParserImplementation:
    """Test that properly implemented parsers work correctly."""

    @pytest.fixture
    def minimal_parser(self) -> BaseParser:
        """Create a minimal valid parser implementation for testing."""

        class MinimalParser(BaseParser):
            @property
            def name(self) -> str:
                return "minimal"

            @property
            def version(self) -> str:
                return "1.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                # Minimal implementation for testing
                output_path = output_dir / f"{pdf_path.stem}.md"
                return output_path

        return MinimalParser()

    def test_can_instantiate_complete_parser(self, minimal_parser: BaseParser) -> None:
        """A complete implementation should instantiate successfully."""
        assert isinstance(minimal_parser, BaseParser)

    def test_name_property_returns_string(self, minimal_parser: BaseParser) -> None:
        """The name property should return a string."""
        assert isinstance(minimal_parser.name, str)
        assert minimal_parser.name == "minimal"

    def test_version_property_returns_string(self, minimal_parser: BaseParser) -> None:
        """The version property should return a string."""
        assert isinstance(minimal_parser.version, str)
        assert minimal_parser.version == "1.0.0"

    def test_parse_method_accepts_paths(self, minimal_parser: BaseParser) -> None:
        """The parse method should accept Path objects."""
        pdf_path = Path("/tmp/test.pdf")
        output_dir = Path("/tmp/output")

        result = minimal_parser.parse(pdf_path, output_dir)

        assert isinstance(result, Path)
        assert result == Path("/tmp/output/test.md")

    def test_repr_includes_name_and_version(self, minimal_parser: BaseParser) -> None:
        """The __repr__ method should include name and version."""
        repr_str = repr(minimal_parser)

        assert "minimal" in repr_str
        assert "1.0.0" in repr_str
        assert "MinimalParser" in repr_str


class TestParserInterfaceContract:
    """Test the interface contract and type signatures."""

    @pytest.fixture
    def mock_parser(self) -> BaseParser:
        """Create a mock parser with various behaviors for testing."""

        class MockParser(BaseParser):
            def __init__(self, name_val: str = "mock", version_val: str = "2.0.0"):
                self._name = name_val
                self._version = version_val

            @property
            def name(self) -> str:
                return self._name

            @property
            def version(self) -> str:
                return self._version

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return output_dir / f"{pdf_path.stem}.md"

        return MockParser()

    def test_name_is_read_only_property(self, mock_parser: BaseParser) -> None:
        """The name property should be read-only (no setter)."""
        with pytest.raises(AttributeError):
            mock_parser.name = "changed"  # type: ignore

    def test_version_is_read_only_property(self, mock_parser: BaseParser) -> None:
        """The version property should be read-only (no setter)."""
        with pytest.raises(AttributeError):
            mock_parser.version = "changed"  # type: ignore

    def test_parse_returns_path_type(self, mock_parser: BaseParser) -> None:
        """The parse method should return a Path object."""
        result = mock_parser.parse(Path("test.pdf"), Path("/output"))

        assert isinstance(result, Path)

    def test_different_parsers_have_different_identities(self) -> None:
        """Different parser instances should be independent."""

        class Parser1(BaseParser):
            @property
            def name(self) -> str:
                return "parser1"

            @property
            def version(self) -> str:
                return "1.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output1.md")

        class Parser2(BaseParser):
            @property
            def name(self) -> str:
                return "parser2"

            @property
            def version(self) -> str:
                return "2.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output2.md")

        p1 = Parser1()
        p2 = Parser2()

        assert p1.name != p2.name
        assert p1.version != p2.version
        assert type(p1) is not type(p2)


class TestParserVersioningScenarios:
    """Test scenarios related to parser versioning."""

    def test_version_can_use_semantic_versioning(self) -> None:
        """Parser versions should support semantic versioning format."""

        class SemanticParser(BaseParser):
            @property
            def name(self) -> str:
                return "semantic"

            @property
            def version(self) -> str:
                return "1.2.3"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        parser = SemanticParser()
        assert parser.version == "1.2.3"

    def test_version_can_use_beta_tags(self) -> None:
        """Parser versions should support pre-release tags."""

        class BetaParser(BaseParser):
            @property
            def name(self) -> str:
                return "beta"

            @property
            def version(self) -> str:
                return "2.0.0-beta.1"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        parser = BetaParser()
        assert parser.version == "2.0.0-beta.1"

    def test_version_can_use_date_format(self) -> None:
        """Parser versions should support date-based versioning."""

        class DateParser(BaseParser):
            @property
            def name(self) -> str:
                return "dated"

            @property
            def version(self) -> str:
                return "2024.11.14"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        parser = DateParser()
        assert parser.version == "2024.11.14"


class TestParserNamingConventions:
    """Test various naming conventions for parsers."""

    def test_name_can_be_lowercase(self) -> None:
        """Parser names should work with lowercase."""

        class LowerParser(BaseParser):
            @property
            def name(self) -> str:
                return "lowercase"

            @property
            def version(self) -> str:
                return "1.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        parser = LowerParser()
        assert parser.name == "lowercase"

    def test_name_can_include_underscores(self) -> None:
        """Parser names should work with underscores."""

        class UnderscoreParser(BaseParser):
            @property
            def name(self) -> str:
                return "aws_textract"

            @property
            def version(self) -> str:
                return "1.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        parser = UnderscoreParser()
        assert parser.name == "aws_textract"

    def test_name_can_include_numbers(self) -> None:
        """Parser names should work with numbers."""

        class NumberParser(BaseParser):
            @property
            def name(self) -> str:
                return "parser2024"

            @property
            def version(self) -> str:
                return "1.0.0"

            def parse(self, pdf_path: Path, output_dir: Path) -> Path:
                return Path("output.md")

        parser = NumberParser()
        assert parser.name == "parser2024"
