# GitHub Actions CI/CD Pipeline

This directory contains the GitHub Actions workflows and reusable actions for the Flint project. The setup follows GitHub Actions best practices and mirrors the structure of the Azure DevOps pipeline templates.

## Structure

```
.github/
├── workflows/           # Main workflow files
│   ├── ci.yml          # Main CI pipeline
│   ├── release.yml     # Release and publishing
│   ├── docs.yml        # Documentation building and deployment
│   ├── security.yml    # Security scanning
│   └── dependency-update.yml # Automated dependency updates
├── actions/            # Reusable actions
│   ├── atomic/         # Individual tool actions
│   │   ├── poetry-install/
│   │   ├── poetry-build/
│   │   ├── pytest/
│   │   ├── black/
│   │   ├── isort/
│   │   ├── ruff-formatter/
│   │   ├── ruff-linter/
│   │   ├── pylint/
│   │   ├── flake8/
│   │   ├── mypy/
│   │   ├── pyright/
│   │   ├── bandit/
│   │   ├── semgrep/
│   │   ├── trufflehog/
│   │   ├── safety/
│   │   └── sphinx-build/
│   └── composite/      # Combinations of atomic actions
│       ├── python-formatters/
│       ├── python-linters/
│       ├── python-typechecking/
│       ├── python-security-1st-party/
│       └── python-security-3rd-party/
└── README.md           # This file
```

## Workflows

### CI Pipeline (`ci.yml`)
The main continuous integration pipeline that runs on:
- Push to `main` and `develop` branches
- Pull requests to `main` and `develop` branches
- Manual trigger with Python version selection

**Jobs:**
1. **Quality Assurance** - Code formatting, linting, and type checking
2. **Tests** - Runs tests across multiple Python versions (3.9-3.12)
3. **Security Scanning** - 1st and 3rd party vulnerability scanning
4. **Build** - Builds the Python package

### Release Pipeline (`release.yml`)
Handles package building and publishing:
- Triggered on GitHub releases
- Publishes to PyPI using trusted publishing
- Uploads artifacts to GitHub releases

### Documentation (`docs.yml`)
Builds and deploys documentation:
- Triggered on changes to docs or source code
- Builds Sphinx documentation
- Deploys to GitHub Pages

### Security Scanning (`security.yml`)
Comprehensive security scanning:
- Runs daily at 2 AM UTC
- Includes CodeQL analysis
- Scans dependencies and source code

### Dependency Updates (`dependency-update.yml`)
Automated dependency management:
- Runs weekly on Mondays
- Creates PR with updated dependencies
- Runs basic tests to verify updates

## Reusable Actions

### Atomic Actions
Individual tool actions that can be used independently:

- **poetry-install**: Install dependencies using Poetry
- **poetry-build**: Build Python package
- **pytest**: Run tests with coverage
- **black**: Code formatting with Black
- **isort**: Import sorting
- **ruff-formatter**: Code formatting with Ruff
- **ruff-linter**: Linting with Ruff
- **pylint**: Linting with Pylint
- **flake8**: Linting with Flake8
- **mypy**: Type checking with MyPy
- **pyright**: Type checking with Pyright
- **bandit**: Security scanning with Bandit
- **semgrep**: Security scanning with Semgrep
- **trufflehog**: Secret scanning
- **safety**: Dependency vulnerability scanning
- **sphinx-build**: Documentation building

### Composite Actions
High-level actions that combine multiple atomic actions:

- **python-formatters**: Runs Black, isort, and Ruff formatters
- **python-linters**: Runs Ruff, Pylint, and Flake8 linters
- **python-typechecking**: Runs MyPy and Pyright type checkers
- **python-security-1st-party**: Scans source code for security issues
- **python-security-3rd-party**: Scans dependencies for vulnerabilities

## Configuration

### Environment Variables
The workflows use these environment variables:
- `PYTHON_VERSION`: Default Python version (3.11)
- `PYTHON_SRC_DIRECTORY`: Source code directory (src)
- `PYTHON_TESTS_DIRECTORY`: Tests directory (tests)
- `PYTHON_PYPROJECT_FILEPATH`: Path to pyproject.toml

### Caching
Poetry dependencies are cached to speed up workflow execution:
- Cache key includes OS, Python version, and poetry.lock hash
- Separate caches for different Python versions

### Permissions
Workflows use minimal required permissions:
- `contents: read` for repository access
- `security-events: write` for security scanning
- `pages: write` for documentation deployment
- `id-token: write` for trusted publishing

## Usage

### Running Locally
You can test individual actions locally using the same commands they use:

```bash
# Install dependencies
poetry install

# Run formatters
poetry run black --check src
poetry run isort --check-only src
poetry run ruff format --check src

# Run linters
poetry run ruff check src
poetry run pylint src
poetry run flake8 src

# Run type checkers
poetry run mypy src
poetry run pyright src

# Run tests
poetry run pytest tests --cov=src

# Run security scans
poetry run bandit -r src
poetry run semgrep --config=auto src
```

### Customization
To customize the workflows:

1. **Modify tool configurations**: Update the config file paths in atomic actions
2. **Add new tools**: Create new atomic actions and add them to composite actions
3. **Change Python versions**: Update the matrix in the CI workflow
4. **Modify triggers**: Update the `on` sections in workflow files

### Secrets Required
For full functionality, configure these secrets:
- `PYPI_API_TOKEN`: For publishing to PyPI (if not using trusted publishing)
- `GITHUB_TOKEN`: Automatically provided by GitHub

## Best Practices Implemented

1. **Dependency Caching**: Speeds up workflow execution
2. **Matrix Builds**: Tests across multiple Python versions
3. **Fail Fast**: Quick feedback on failures
4. **Artifact Upload**: Preserves build artifacts and reports
5. **Security First**: Comprehensive security scanning
6. **Automated Updates**: Regular dependency updates
7. **Documentation**: Automated documentation building and deployment
8. **Trusted Publishing**: Secure package publishing without API keys

## Migration from Azure DevOps

This GitHub Actions setup provides equivalent functionality to the Azure DevOps templates:

| Azure DevOps Template | GitHub Actions Equivalent |
|----------------------|---------------------------|
| `atomic/python/*.yaml` | `.github/actions/atomic/*` |
| `composite/python/*.yaml` | `.github/actions/composite/*` |
| `solution/python/python-ci.yaml` | `.github/workflows/ci.yml` |
| `pipelines/flint.yaml` | `.github/workflows/ci.yml` |

The key differences:
- GitHub Actions uses YAML for both workflows and actions
- Caching is handled differently but more efficiently
- Security scanning integrates better with GitHub's security features
- Publishing uses trusted publishing instead of service connections
