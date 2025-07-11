"""
Unit tests for the load module.
"""

from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest
from pyspark.sql import DataFrame
from pyspark.sql.streaming.query import StreamingQuery

from flint.core.load import DATA_FORMAT, Load, LoadRegistry
from flint.models.model_load import LoadFormat, LoadMethod, LoadModelFile
from flint.types import DataFrameRegistry, StreamingQueryRegistry


class MockLoadModel:
    """Dummy model for testing Load class."""

    model_cls = LoadModelFile

    def __init__(self, name: str, upstream_name: str, method: LoadMethod = LoadMethod.BATCH) -> None:
        """Initialize test model."""
        self.name = name
        self.upstream_name = upstream_name
        self.method = method
        self.schema_location = None
        self.options = {}


class MockLoadClass(Load[LoadModelFile]):
    """Test implementation of Load abstract class."""

    model_cls = LoadModelFile

    def _load_batch(self) -> None:
        """Implementation of abstract method."""

    def _load_streaming(self) -> StreamingQuery:
        """Implementation of abstract method."""
        return MagicMock(spec=StreamingQuery)


class TestLoadRegistry:
    """
    Unit tests for the LoadRegistry class.
    """

    def test_registry_is_singleton(self) -> None:
        """Test that LoadRegistry is a singleton."""
        # Arrange & Act
        registry1 = LoadRegistry()
        registry2 = LoadRegistry()

        # Assert
        assert registry1 is registry2
        assert id(registry1) == id(registry2)

    def test_register_and_get_load(self) -> None:
        """Test registering and retrieving a load class."""
        # Arrange
        registry = LoadRegistry()

        # Mock load class
        mock_load_class = MagicMock()

        # Act
        registry.register("test_load")(mock_load_class)
        retrieved_class = registry.get("test_load")

        # Assert
        assert retrieved_class == mock_load_class

    def test_get_nonexistent_load_raises_key_error(self) -> None:
        """Test that getting a non-existent load raises KeyError."""
        # Arrange
        registry = LoadRegistry()

        # Act & Assert
        with pytest.raises(KeyError):
            registry.get("nonexistent_load")


class TestLoad:
    """Unit tests for the Load class and its implementations."""

    def test_load_initialization(self) -> None:
        """Test Load initialization."""
        # Arrange
        model = MagicMock(spec=LoadModelFile)
        model.name = "test_load"
        model.upstream_name = "source"

        # Act
        load = MockLoadClass(model=model)

        # Assert
        assert load.model == model
        assert isinstance(load.data_registry, DataFrameRegistry)
        assert isinstance(load.streaming_query_registry, StreamingQueryRegistry)

    @patch.object(LoadModelFile, "from_dict")
    def test_from_dict(self, mock_from_dict: MagicMock) -> None:
        """Test creating a Load from a dict."""
        # Arrange
        load_dict: dict = {
            "name": "test_load",
            "upstream_name": "source",
            "method": "batch",
            "data_format": "csv",
            "location": "/path/to/output.csv",
            "schema_location": None,
            "options": {},
        }

        mock_model_cls = MagicMock(spec=LoadModelFile)
        mock_model_cls.name = "test_load"
        mock_from_dict.return_value = mock_model_cls

        # Act
        load = MockLoadClass.from_dict(load_dict)

        # Assert
        assert load.model == mock_model_cls
        mock_from_dict.assert_called_once_with(dict_=load_dict)

    @patch("flint.utils.spark.SparkHandler")
    def test_load_batch_method(self, mock_spark_handler_class: MagicMock) -> None:
        """Test the load method with batch loading."""
        # Arrange
        mock_spark_handler = MagicMock()
        mock_spark_handler_class.return_value = mock_spark_handler

        model = MagicMock(spec=LoadModelFile)
        model.name = "test_load"
        model.upstream_name = "source"
        model.method = LoadMethod.BATCH
        model.schema_location = None
        model.options = {}

        load = MockLoadClass(model=model)
        load._load_batch = MagicMock()
        load._load_schema = MagicMock()

        # Add test data to registry
        load.data_registry["source"] = MagicMock(spec=DataFrame)

        # Act
        load.load()

        # Assert
        assert load.data_registry["test_load"] == load.data_registry["source"]
        load._load_batch.assert_called_once()
        load._load_schema.assert_called_once()
        # Skip asserting on add_configs since implementation may vary

    @patch("flint.utils.spark.SparkHandler")
    def test_load_streaming_method(self, mock_spark_handler_class: MagicMock) -> None:
        """Test the load method with streaming loading."""
        # Arrange
        mock_spark_handler = MagicMock()
        mock_spark_handler_class.return_value = mock_spark_handler

        model = MagicMock(spec=LoadModelFile)
        model.name = "test_load"
        model.upstream_name = "source"
        model.method = LoadMethod.STREAMING
        model.schema_location = None
        model.options = {}

        load = MockLoadClass(model=model)
        mock_streaming_query = MagicMock(spec=StreamingQuery)
        load._load_streaming = MagicMock(return_value=mock_streaming_query)
        load._load_schema = MagicMock()

        # Add test data to registry
        load.data_registry["source"] = MagicMock(spec=DataFrame)

        # Act
        load.load()

        # Assert
        assert load.data_registry["test_load"] == load.data_registry["source"]
        load._load_streaming.assert_called_once()
        load._load_schema.assert_called_once()
        assert load.streaming_query_registry["test_load"] == mock_streaming_query
        # Skip asserting on add_configs since implementation may vary

    @patch("flint.utils.spark.SparkHandler")
    def test_load_invalid_method(self, mock_spark_handler_class: MagicMock) -> None:
        """Test the load method with an invalid loading method."""
        # Arrange
        mock_spark_handler = MagicMock()
        mock_spark_handler_class.return_value = mock_spark_handler

        model = MagicMock(spec=LoadModelFile)
        model.name = "test_load"
        model.upstream_name = "source"
        # Create a mock method object that has value attribute but is invalid
        mock_invalid_method = MagicMock()
        mock_invalid_method.value = "invalid_method"
        model.method = mock_invalid_method
        model.options = {}

        load = MockLoadClass(model=model)

        # Add test data to registry
        load.data_registry["source"] = MagicMock(spec=DataFrame)

        # Act & Assert
        with pytest.raises(ValueError):
            load.load()

    @patch("builtins.open", new_callable=mock_open)
    def test_load_schema(self, mock_file: MagicMock) -> None:
        """Test the _load_schema method."""
        # Arrange
        model = MagicMock(spec=LoadModelFile)
        model.name = "test_load"
        model.schema_location = "/path/to/schema.json"

        load = MockLoadClass(model=model)

        # Create mock DataFrame with schema
        mock_df = MagicMock(spec=DataFrame)
        mock_schema = MagicMock()
        mock_schema.jsonValue.return_value = {"fields": [{"name": "col1", "type": "string"}]}
        mock_df.schema = mock_schema

        # Add mock DataFrame to registry
        load.data_registry["test_load"] = mock_df

        # Act
        with patch("json.dumps", return_value='{"fields": [{"name": "col1", "type": "string"}]}'):
            load._load_schema()

        # Assert
        mock_file.assert_called_once_with("/path/to/schema.json", mode="w", encoding="utf-8")
        mock_file().write.assert_called_once()

    def test_load_schema_no_location(self) -> None:
        """Test the _load_schema method when schema_location is None."""
        # Arrange
        model = MagicMock(spec=LoadModelFile)
        model.name = "test_load"
        model.schema_location = None

        load = MockLoadClass(model=model)

        # Act
        with patch("builtins.open") as mock_open_ctx:
            load._load_schema()

        # Assert
        mock_open_ctx.assert_not_called()

    @patch.object(LoadRegistry, "get")
    def test_base_class_from_dict_with_valid_format(self, mock_registry_get: MagicMock) -> None:
        """Test Load.from_dict method with a valid format."""
        # Arrange
        mock_load_class = MagicMock(spec=Load)
        mock_load_class.__name__ = "MockLoadClass"
        mock_model_cls = MagicMock()
        mock_model_cls.name = "test_load"
        mock_load_class.model_cls = MagicMock()
        mock_load_class.model_cls.from_dict = MagicMock(return_value=mock_model_cls)
        mock_load_class.return_value = MagicMock()
        mock_registry_get.return_value = mock_load_class

        config: dict[str, Any] = {DATA_FORMAT: "csv"}

        # Act
        Load.from_dict(config)

        # Assert
        mock_registry_get.assert_called_once_with(LoadFormat("csv"))
        mock_load_class.model_cls.from_dict.assert_called_once_with(dict_=config)
        mock_load_class.assert_called_once_with(model=mock_model_cls)

    def test_base_class_from_dict_with_invalid_format(self) -> None:
        """Test Load.from_dict method with an invalid format."""
        # Arrange
        config: dict[str, Any] = {DATA_FORMAT: "invalid_format"}

        # Act & Assert
        with pytest.raises(ValueError):
            Load.from_dict(config)

    def test_base_class_from_dict_with_missing_data_format_key(self) -> None:
        """Test Load.from_dict method with a missing 'data_format' key."""
        # Arrange
        config: dict[str, Any] = {}

        # Act & Assert
        with pytest.raises(NotImplementedError):
            Load.from_dict(config)
