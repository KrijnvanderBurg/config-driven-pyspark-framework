"""Built-in transform functions for data manipulation.

This module contains concrete implementations of transformation functions
that can be used in the ingestion framework to manipulate data.

Each transform function is designed to perform a specific data operation
and is automatically registered with the TransformFunctionRegistry when imported.
This allows the functions to be referenced by name in configuration files.
"""

from . import cast, drop, dropduplicates, filter_, join, select, withcolumn
from .custom import calculate_birth_year, customer_orders

# Define __all__ to satisfy linters about "unused" imports
# These imports are actually used for their side effects (registering transforms)
__all__ = [
    # generic transforms
    "cast",
    "drop",
    "filter_",
    "join",
    "select",
    "withcolumn",
    "dropduplicates",
    # custom transforms
    "customer_orders",
    "calculate_birth_year",
]
