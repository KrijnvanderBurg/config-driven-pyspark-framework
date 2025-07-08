<p align="center">
  <img src="docs/logo.svg" alt="Flint Logo" width="250"/>
</p>

<h1 align="center">Flint</h1>

<p align="center">
  <b>A lightweight, extensible framework for PySpark ETL pipelines</b>
</p>

<p align="center">
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/actions/workflows/ci.yml"><img src="https://github.com/krijnvanderburg/config-driven-pyspark-framework/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/actions/workflows/security.yml"><img src="https://github.com/krijnvanderburg/config-driven-pyspark-framework/actions/workflows/security.yml/badge.svg" alt="Security"></a>
  <a href="https://pypi.org/project/flint/"><img src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-informational" alt="Python Versions"></a>
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/blob/main/LICENSE"><img src="https://img.shields.io/github/license/krijnvanderburg/config-driven-pyspark-framework?style=flat-square" alt="License"></a>
  <a href="https://spark.apache.org/docs/latest/"><img src="https://img.shields.io/badge/spark-3.5.0+-lightgrey" alt="Apache Spark"></a>
  <a href="https://codecov.io/gh/krijnvanderburg/config-driven-pyspark-framework"><img src="https://codecov.io/gh/krijnvanderburg/config-driven-pyspark-framework/graph/badge.svg" alt="Coverage"></a>
</p>

<p align="center">
  <b>Built by Krijn van der Burg for the data engineering community</b>
</p>

<p align="center">
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/stargazers">⭐ Star this repo</a> •
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/issues">🐛 Report Issues</a> •
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/discussions">💬 Join Discussions</a>
</p>

<p align="center">
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/releases">📥 Releases (TBD)</a> •
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/blob/main/CHANGELOG.md">📝 Changelog (TBD)</a> •
  <a href="https://github.com/krijnvanderburg/config-driven-pyspark-framework/blob/main/CONTRIBUTING.md">🤝 Contributing</a>
</p>

---

## 🔍 Overview

**Flint is an intuitive barebones application framework for Apache Spark** that eliminates complex application setups and provides a configuration-driven approach. This is not a library you install and use, take the source code and extend the application with your implementations.

The core philosophy is simple: provide an barebones structure that lets teams easily create and share their own transformations. No complex abstractions—just a logical framework that makes PySpark development straightforward and maintainable.

Flint was designed to be **minimal yet powerful** - providing structural foundations while enabling your team to extend it with business-specific transforms.

### Build pipelines that are:

✅ **Maintainable** - Clear separation of application code and business logics.  
✅ **Standardized** - Consistent pipelines and patterns across your organization.  
✅ **Version-controlled** - More easily track changes by inspecting one config file.

Flint lets you focus on data transformations while handling the application structure complexities.


## ⚡ Quick Start

### Installation

```bash
git clone https://github.com/krijnvanderburg/config-driven-pyspark-framework.git
cd config-driven-pyspark-framework
code .                                   # shortcut for vscode
git submodule update --init --recursive  # recursive because of nested submodules
poetry install                           # install dependencies
```

## 🔍 Example: Customer Order Analysis

The included example demonstrates a real-world ETL pipeline:

- 📄 **Config**: `examples/job.json`
- 🏃 **Execution**: `python -m flint run --config-filepath examples/job.json`
- 📂 **Output**: `examples/customer_orders/output/`

Running this command executes a complete pipeline that showcases Flint's key capabilities:

- **Multi-format extraction**: Seamlessly reads from both CSV and JSON sources
  - Source options like delimiters and headers are configurable through the configuration file
  - Schema validation ensures data type safety and consistency across all sources

- **Flexible transformation chain**: Combines domain-specific and generic transforms
  - First uses a custom `customers_orders` transform to join datasets and filter orders > $100
  - Then applies the generic `select` transform to project only needed columns
  - Each transform function can be easily customized through its arguments

- **Configurable loading**: Writes results as CSV with customizable settings
  - Easily change to Parquet, Delta, or other formats by modifying `data_format`
  - Output mode (overwrite/append) controlled by a simple parameter

#### Configuration: examples/job.json

```jsonc
{
    // EXTRACT: Read from multiple data sources with different formats
    "extracts": [
        {
            "name": "extract-customers",
            "data_format": "csv",                                  // CSV format for customers
            "location": "examples/customer_orders/customers.csv",
            "method": "batch",
            "options": {
                "delimiter": ",",
                "header": true,
                "inferSchema": false
            },
            "schema": "examples/customer_orders/customers_schema.json"
        },
        {
            "name": "extract-orders",
            "data_format": "json",                                 // JSON format for orders
            "location": "examples/customer_orders/orders.json",
            "method": "batch",
            "options": {},
            "schema": "examples/customer_orders/orders_schema.json"
        }
    ],

    // TRANSFORM: Apply business logic through transform functions
    "transforms": [
        {
            "name": "transform-join-orders",
            "upstream_name": "extract-customers",
            "functions": [
                // Use a custom transform to join datasets and filter for high-value orders
                { "function": "customers_orders", "arguments": {"amount_minimum": 100} },
                // Select only the fields we need for our report
                { "function": "select", "arguments": {"columns": ["name", "email", "signup_date", "order_id", "order_date", "amount"]} }
            ]
        }
    ],

    // LOAD: Write processed data to destination
    "loads": [
        {
            "name": "load-customer-orders",
            "upstream_name": "transform-join-orders",              // Use transformed data
            "data_format": "csv",                                  // Output as CSV
            "location": "examples/customer_orders/output",
            "method": "batch",
            "mode": "overwrite",                                   // Replace existing data
            "options": {
                "header": true
            }
        }
    ]
}
```

### Built-in Transformations

Flint includes ready-to-use generic transformations to jumpstart your development. These transformations can be configured directly through your JSON configuration files without writing any additional code.

#### Core Transformations

| Transform | Description | Example Usage |
|-----------|-------------|---------------|
| `select` | Select specific columns from a DataFrame | `{"function": "select", "arguments": {"columns": ["id", "name", "email"]}}` |
| `cast` | Convert columns to specified data types | `{"function": "cast", "arguments": {"columns": {"amount": "double", "date": "timestamp"}}}` |
| `drop` | Remove specified columns from a DataFrame | `{"function": "drop", "arguments": {"columns": ["temp_col", "unused_field"]}}` |
| `dropduplicates` | Remove duplicate rows based on specified columns | `{"function": "dropduplicates", "arguments": {"columns": ["id"]}}` |
| `filter` | Apply conditions to filter rows in a DataFrame | `{"function": "filter", "arguments": {"condition": "amount > 100"}}` |
| `join` | Combine DataFrames using specified join conditions | `{"function": "join", "arguments": {"other_df": "orders_df", "on": ["customer_id"], "how": "inner"}}` |
| `withcolumn` | Add or replace columns with computed values | `{"function": "withcolumn", "arguments": {"column_name": "full_name", "expression": "concat(first_name, ' ', last_name)"}}` |

#### Sample Domain-Specific Transformations

The following custom transformations are included to showcase how you can create your own domain-specific transformations:

| Transform | Description | Use Case |
|-----------|-------------|----------|
| `calculate_birth_year` | Calculate birth year based on age | Demonstrates simple field derivation based on existing fields |
| `customer_orders_bronze` | Join customer and order data with filtering | Shows how to combine multiple operations (join, filter, select) into a single reusable transform |

> **💡 Tip:** You can create your own custom transformations for specific business needs following the pattern shown in the [Extending with Custom Transforms](#-extending-with-custom-transforms) section.


## 📋 Configuration Reference

### Pipeline Structure

A Flint pipeline is defined by three core components in your configuration file:

```
Configuration
├── Extracts - Read data from source systems (CSV, JSON, Parquet, etc.)
├── Transforms - Apply business logic and data processing
└── Loads - Write results to destination systems
```

Each component has a standardized schema and connects through named references:

<details>
<summary><b>Extract Configuration</b></summary>

```jsonc
{
  "name": "extract-name",                    // Required: Unique identifier
  "method": "batch|stream",                  // Required: Processing method
  "data_format": "csv|json|parquet|...",     // Required: Source format
  "location": "path/to/source",              // Required: Source location
  "schema": "path/to/schema.json",           // Optional: Schema definition
  "options": {                               // Optional: PySpark reader options
    "header": true,
    "delimiter": ",",
    "inferSchema": false
  }
}
```

**Supported Formats:** CSV, JSON, Parquet, Avro, ORC, Text, JDBC, Delta (with appropriate dependencies)
</details>

<details>
<summary><b>Transform Configuration</b></summary>

```jsonc
{
  "name": "transform-name",                  // Required: Unique identifier
  "upstream_name": "previous-step-name",     // Required: Reference previous stage
  "functions": [                             // Required: List of transformations
    {
      "function": "transform-function-name", // Required: Registered function name
      "arguments": {                         // Required: Function-specific arguments
        "key1": "value1",
        "key2": "value2"
      }
    }
  ]
}
```

**Function Application:** Transformations are applied in sequence, with each function's output feeding into the next.
</details>

<details>
<summary><b>Load Configuration</b></summary>

```jsonc
{
  "name": "load-name",                       // Required: Unique identifier
  "upstream_name": "previous-step-name",     // Required: Reference previous stage
  "method": "batch|stream",                  // Required: Processing method
  "data_format": "csv|json|parquet|...",     // Required: Destination format
  "location": "path/to/destination",         // Required: Output location
  "mode": "overwrite|append|ignore|error",   // Required: Write mode
  "options": {}                              // Optional: PySpark writer options
}
```

**Modes explained:**
- `overwrite`: Replace existing data
- `append`: Add to existing data
- `ignore`: Ignore operation if data exists
- `error`: Fail if data already exists
</details>

### Environment variables
- Log level can be set by environment variable `FLINT_LOG_LEVEL`. If not present, then it will use `LOG_LEVEL`. If also not present, then it will default to `INFO`. Both env variables can be set to `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

## Architecture and flow

1. **Parse Configuration** → Validate and convert JSON/YAML configurations into typed models
2. **Initialize Components** → Set up extract, transform, and load objects based on configuration
3. **Execute Pipeline** → Process data through the configured workflow in sequence
4. **Monitor & Log** → Track execution progress and handle errors

#### Sequence Diagram
![Flint Data Flow](docs/sequence_diagram.png)

### Key Components

- **Registry System**: Central repository that manages registered components and data frames
- **Type Models**: Strongly-typed configuration models providing compile-time validation
- **Function Framework**: Plugin system for custom transformations
- **Execution Engine**: Coordinates the pipeline flow and handles dependencies

#### Class Diagram
![Class Diagram](docs/class_diagram.drawio.png)

- **Job**: Orchestrates the entire pipeline execution
- **Extract**: Reads data from various sources into DataFrames
- **Transform**: Applies business transform logic through registered functions
- **Load**: Writes processed data to destination

### Design Principles

- **Separation of Concerns**: Each component has a single, well-defined responsibility
- **Dependency Injection**: Components receive their dependencies rather than creating them
- **Plugin Architecture**: Extensions are registered with the framework without modifying core code
- **Configuration as Code**: All pipeline behavior is defined declaratively in configuration files

## 🧩 Extending with Custom Transforms

Flint's power comes from its extensibility. Create custom transformations to encapsulate your business logic. Let's look at a real example from Flint's codebase - the `select` transform:

### Step 1: Define the configuration model

```python
# src/flint/models/transforms/model_select.py

@dataclass
class SelectFunctionModel(FunctionModel):
    function: str
    arguments: "SelectFunctionModel.Args"

    @dataclass
    class Args:
        columns: list[Column]

    @classmethod
    def from_dict(cls, dict_: dict[str, Any]) -> Self:
        """Convert JSON configuration to typed model."""
        function_name = dict_[FUNCTION]
        arguments_dict = dict_[ARGUMENTS]
        
        columns = arguments_dict["columns"]
        arguments = cls.Args(columns=columns)
        
        return cls(function=function_name, arguments=arguments)
```

### Step 2: Create the transform function

```python
# src/flint/core/transforms/select.py

@TransformFunctionRegistry.register("select")
class SelectFunction(Function[SelectFunctionModel]):
    """Selects specified columns from a DataFrame."""
    model_cls = SelectFunctionModel

    def transform(self) -> Callable:
        """Returns a function that projects columns from a DataFrame."""
        def __f(df: DataFrame) -> DataFrame:
            return df.select(*self.model.arguments.columns)

        return __f
```

### Step 3: Use in your pipeline configuration

```jsonc
{
  "extracts": [
    // ...
  ],
  "transforms": [
    {
      "name": "transform-user-data",
      "upstream_name": "extract-users",
      "functions": [
        { "function": "select", "arguments": { "columns": ["user_id", "email", "signup_date"] } }
      ]
    }
  ],
  "loads": [
    // ...
  ]
}
```

> 🔍 **Best Practice**: Create transforms that are generic enough to be reusable but specific enough to encapsulate meaningful business logic.

### Building a Transform Library

As your team develops more custom transforms, you create a powerful library of reusable components:

1. **Domain-Specific Transforms**: Create transforms that encapsulate your business rules
2. **Industry-Specific Logic**: Build transforms tailored to your industry's specific needs
3. **Data Quality Rules**: Implement your organization's data quality standards

The registration system makes it easy to discover and use all available transforms in your configurations without modifying the core framework code.


## 🚀 Getting Help

- **Examples**: Explore working samples in the [examples/](examples/) directory
- **Documentation**: Refer to the [Configuration Reference](#-configuration-reference) section for detailed syntax
- **Community**: Ask questions and report issues on [GitHub Issues](https://github.com/krijnvanderburg/config-driven-pyspark-framework/issues)
- **Source Code**: Browse the implementation in the [src/flint](src/flint/) directory

## 🤝 Contributing

Contributions are welcome! Feel free to submit a pull request and message me.

## 📄 License

This project is licensed under the Creative Commons Attribution 4.0 International License (CC-BY-4.0) - see the [LICENSE](LICENSE) file for details.
