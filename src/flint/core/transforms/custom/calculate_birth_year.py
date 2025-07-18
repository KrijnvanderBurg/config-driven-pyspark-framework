"""
Calculate birth year transform function.

This module provides a transformation function that calculates a person's birth year
based on their age and the current year.
"""

from collections.abc import Callable

from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, lit

from flint.core.transform import Function, TransformFunctionRegistry
from flint.models.transforms.custom.model_calculate_birth_year import CalculateBirthYearFunctionModel


@TransformFunctionRegistry.register("calculate_birth_year")
class CalculateBirthYearFunction(Function[CalculateBirthYearFunctionModel]):
    """Function that calculates birth year based on age and current year.

    This transform function takes a person's age from a specified column
    and calculates their approximate birth year by subtracting the age
    from the current year. The result is added as a new column to the DataFrame.

    The function is configured using a CalculateBirthYearFunctionModel that
    specifies which columns to use and any additional parameters.

    Attributes:
        model: Configuration model specifying input/output columns and parameters
        model_cls: The concrete model class used for configuration
        data_registry: Shared registry for accessing and storing DataFrames

    Example:
        ```json
        {
            "function": "calculate_birth_year",
            "arguments": {
                "age_column": "age",
                "birth_year_column": "birth_year",
                "current_year": 2025
            }
        }
        ```
    """

    model_cls: type[CalculateBirthYearFunctionModel] = CalculateBirthYearFunctionModel

    def transform(self) -> Callable:
        """Apply the birth year calculation transformation to the DataFrame.

        This method subtracts a person's age from the current year to estimate
        their birth year. It creates a new column with the calculated birth year
        while preserving all existing columns.

        The calculation uses the age column and current year specified in the model.

        Returns:
            A callable function that performs the birth year calculation when
            applied to a DataFrame

        Examples:
            Consider the following DataFrame schema:

                    ```
                    root
                    |-- name: string (nullable = true)
                    |-- age: integer (nullable = true)
                    ```

                    Applying the 'calculate_birth_year' function:

        ```
                    {
                        "function": "calculate_birth_year",
                        "arguments": {
                            "current_year": 2025,
                            "age_column": "age",
                            "birth_year_column": "birth_year"
                        }
                    }
                    ```

                    The resulting DataFrame schema will be:

                    ```
                    root
                    |-- name: string (nullable = true)
                    |-- age: integer (nullable = true)
                    |-- birth_year: integer (nullable = true)
                    ```
        """

        def __f(df: DataFrame) -> DataFrame:
            args = self.model.arguments  # Type is CalculateBirthYearFunctionModel.Args

            # Create the birth year column by subtracting age from current year
            # Convert the subtraction to use literal for the current year
            return df.withColumn(args.birth_year_column, lit(args.current_year) - col(args.age_column))

        return __f
