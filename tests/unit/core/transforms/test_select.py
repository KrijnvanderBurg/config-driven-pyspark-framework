"""
Unit tests for the SelectFunction transform.
"""

from unittest.mock import MagicMock, patch

from pyspark.sql import DataFrame

from flint.core.transform import TransformFunctionRegistry
from flint.core.transforms.select import SelectFunction
from flint.models.transforms.model_select import SelectFunctionModel
from flint.types import DataFrameRegistry


class TestSelectFunction:
    """
    Unit tests for the SelectFunction class.
    """

    def test_registration(self) -> None:
        """Test that SelectFunction is registered correctly."""
        # Arrange
        registry = TransformFunctionRegistry()

        # Act
        function_class = registry.get("select")

        # Assert
        assert function_class == SelectFunction

    def test_initialization(self) -> None:
        """Test SelectFunction initialization."""
        # Arrange
        model = MagicMock(spec=SelectFunctionModel)
        model.function = "select"
        # Add mock arguments
        mock_args = MagicMock()
        mock_args.columns = ["col1", "col2"]
        model.arguments = mock_args

        # Act
        function = SelectFunction(model=model)

        # Assert
        assert function.model == model
        # Check that transform() returns a callable function
        assert callable(function.transform())

    @patch.object(SelectFunctionModel, "from_dict")
    def test_from_dict(self, mock_from_dict: MagicMock) -> None:
        """Test creating a SelectFunction from a dict."""
        # Arrange
        function_dict = {"function": "select", "arguments": {"columns": ["col1", "col2"]}}

        mock_model_cls = MagicMock(spec=SelectFunctionModel)
        mock_model_cls.function = "select"
        # Add mock arguments
        mock_args = MagicMock()
        mock_args.columns = ["col1", "col2"]
        mock_model_cls.arguments = mock_args
        mock_from_dict.return_value = mock_model_cls

        # Act
        function = SelectFunction.from_dict(function_dict)

        # Assert
        assert function.model == mock_model_cls
        mock_from_dict.assert_called_once_with(dict_=function_dict)

    def test_transform_function(self) -> None:
        """Test the transform function."""
        # Arrange
        args_mock = MagicMock()
        args_mock.columns = ["col1", "col2"]

        model = MagicMock(spec=SelectFunctionModel)
        model.function = "select"
        model.arguments = args_mock

        function = SelectFunction(model=model)

        # Create mock DataFrame
        mock_df = MagicMock(spec=DataFrame)
        mock_select_result = MagicMock(spec=DataFrame)
        mock_df.select.return_value = mock_select_result

        # Create mock DataFrameRegistry
        dataframe_registry = DataFrameRegistry()
        dataframe_registry["test_df"] = mock_df

        # Act
        transform_func = function.transform()
        result = transform_func(df=dataframe_registry["test_df"])

        # Assert
        mock_df.select.assert_called_once_with(*model.arguments.columns)
        assert result == mock_select_result  # Verify the return value

    def test_transform_integration(self) -> None:
        """Integration test for the transform function with real classes."""
        # Arrange
        function_dict = {"function": "select", "arguments": {"columns": ["col1", "col2"]}}

        # Act - Create function from dict and get transform callable
        function = SelectFunction.from_dict(function_dict)
        transform_func = function.transform()

        # Create mock DataFrame with proper select method
        mock_df = MagicMock()
        mock_select_result = MagicMock()
        mock_df.select.return_value = mock_select_result

        # Create DataFrameRegistry
        dataframe_registry = DataFrameRegistry()
        dataframe_registry["test_df"] = mock_df

        # Apply transform
        result = transform_func(df=dataframe_registry["test_df"])

        # Assert
        # 1. Verify select was called
        mock_df.select.assert_called_once()
        # 2. Verify the result is the transformed DataFrame
        assert result == mock_select_result
