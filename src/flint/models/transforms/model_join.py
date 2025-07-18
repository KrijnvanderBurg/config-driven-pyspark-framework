"""Configuration model for the join transform function.

This module defines the data models used to configure join
transformations in the ingestion framework. It includes:

- JoinFunctionModel: Main configuration model for join operations
- Args nested class: Container for the join parameters

These models provide a type-safe interface for configuring joins
from configuration files or dictionaries.
"""

import logging
from dataclasses import dataclass
from typing import Any, Final, Self

from flint.exceptions import ConfigurationKeyError
from flint.models.model_transform import ARGUMENTS, FUNCTION, FunctionModel
from flint.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

# Constants for keys in the configuration dictionary
OTHER_UPSTREAM_NAME: Final[str] = "other_upstream_name"
ON: Final[str] = "on"
HOW: Final[str] = "how"


@dataclass
class JoinFunctionModel(FunctionModel):
    """Configuration model for join transform operations.

    This model defines the structure for configuring a join
    transformation, specifying the dataframes to join and how to join them.

    Attributes:
        function: The name of the function to be used (always "join")
        arguments: Container for the join parameters
    """

    function: str
    arguments: "JoinFunctionModel.Args"

    @dataclass
    class Args:
        """Arguments for join transform operations.

        Attributes:
            other_upstream_name: Name of the dataframe to join with the current dataframe
            on: Column(s) to join on. Can be a string for a single column or a list of strings for multiple columns
            how: Type of join to perform (inner, outer, left, right, etc.). Defaults to "inner"
        """

        other_upstream_name: str
        on: str | list[str]
        how: str = "inner"

    @classmethod
    def from_dict(cls, dict_: dict[str, Any]) -> Self:
        """Create a JoinFunctionModel instance from a dictionary.

        Args:
            dict_: The configuration dictionary.

        Returns:
            An initialized JoinFunctionModel instance

        Raises:
            ConfigurationKeyError: If required keys are missing from the dictionary
            ValueError: If the function name is not 'join'
            Exception: If there's an unexpected error during model creation
        """
        logger.debug("Creating JoinFunctionModel from dictionary: %s", dict_)

        try:
            function_name = dict_[FUNCTION]
            arguments_dict: dict = dict_[ARGUMENTS]
        except KeyError as e:
            raise ConfigurationKeyError(key=e.args[0], dict_=dict_) from e

        try:
            other_upstream_name = arguments_dict[OTHER_UPSTREAM_NAME]
            on = arguments_dict[ON]
            how = arguments_dict[HOW]

            logger.debug(
                "Parsed join function - name: %s, other_upstream: %s, on: %s, how: %s",
                function_name,
                other_upstream_name,
                on,
                how,
            )

            arguments = cls.Args(
                other_upstream_name=other_upstream_name,
                on=on,
                how=how,
            )
        except KeyError as e:
            raise ConfigurationKeyError(key=e.args[0], dict_=arguments_dict) from e

        model = cls(function=function_name, arguments=arguments)
        logger.info("Successfully created JoinFunctionModel - joining with %s on %s", other_upstream_name, on)
        return model
