# Development Guide

Guide for contributing to and developing tourney-threads.

📖 **Also see [CONTRIBUTING.md](../CONTRIBUTING.md) for quick contribution guidelines.**

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Quality](#code-quality)
- [Making Changes](#making-changes)
- [CI/CD Pipeline](#cicd-pipeline)

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A text editor or IDE (VS Code recommended)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/chrisbirie/challonge-discord-thread-creator.git
cd challonge-discord-thread-creator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check that tests run
pytest

# Check that CLI works
tourney-threads --version
```

## Project Structure

```
tourney_threads/
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── docs/                    # Documentation
│   ├── INSTALLATION.md
│   ├── CONFIGURATION.md
│   ├── USAGE.md
│   ├── TEMPLATES.md
│   ├── DEVELOPMENT.md      # This file
│   └── TROUBLESHOOTING.md
├── src/
│   └── tourney_threads/
│       ├── __init__.py
│       ├── app.py          # Main application logic
│       └── version.py      # Version info
├── tests/
│   └── test_tourney_threads/
│       ├── api/            # API client tests
│       ├── config/         # Config tests
│       ├── discord_client/ # Discord tests
│       ├── e2e/            # End-to-end tests
│       ├── integration/    # Integration tests
│       └── utils/          # Utility tests
├── config.example.yaml     # Example config
├── pyproject.toml          # Project metadata and tool configs
├── requirements.txt        # Production dependencies
└── README.md               # Main documentation
```

### Key Files

- **[src/tourney_threads/app.py](../src/tourney_threads/app.py)**: Main application with all logic
- **[pyproject.toml](../pyproject.toml)**: Package metadata, dependencies, tool configurations
- **[.github/workflows/ci.yml](../.github/workflows/ci.yml)**: GitHub Actions CI/CD pipeline
- **[tests/](../tests/)**: Comprehensive test suite

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=tourney_threads --cov-report=html
```

View coverage report:
```bash
# On Windows:
start htmlcov\index.html

# On macOS:
open htmlcov/index.html

# On Linux:
xdg-open htmlcov/index.html
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_tourney_threads/api
pytest tests/test_tourney_threads/config
pytest tests/test_tourney_threads/discord_client
pytest tests/test_tourney_threads/utils

# Integration tests
pytest tests/test_tourney_threads/integration

# End-to-end tests
pytest tests/test_tourney_threads/e2e
```

### Run Specific Test Files

```bash
pytest tests/test_tourney_threads/config/test_config.py
pytest tests/test_tourney_threads/e2e/test_e2e_workflow.py -v
```

### Run Tests with Debug Output

```bash
pytest -v -s
pytest --log-cli-level=DEBUG
```

## Code Quality

The project uses several tools to maintain code quality. All are configured in [pyproject.toml](../pyproject.toml).

### Formatting

**Black** - Code formatter
```bash
# Check formatting
black --check src tests

# Auto-format
black src tests
```

**isort** - Import sorting
```bash
# Check imports
isort --check-only src tests

# Auto-sort
isort src tests
```

### Linting

**Ruff** - Fast Python linter
```bash
# Lint code
ruff check src tests

# Auto-fix issues
ruff check --fix src tests
```

### Type Checking

**MyPy** - Static type checker
```bash
mypy src
```

### Security

**Bandit** - Security issue scanner
```bash
bandit -r src
```

**Safety** - Dependency vulnerability scanner
```bash
safety check
```

### Run All Checks

```bash
# Formatting
black --check src tests
isort --check-only src tests

# Linting
ruff check src tests

# Type checking
mypy src

# Security
bandit -r src
safety check

# Tests
pytest --cov=tourney_threads
```

Or use Make (if Makefile exists):
```bash
make lint
make test
make security
```

## Making Changes

### Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes:**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes:**
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   black src tests
   ruff check src tests
   mypy src
   ```

4. **Commit:**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   # Then create pull request on GitHub
   ```

### Writing Tests

Tests should be placed in the appropriate directory under `tests/test_tourney_threads/`:

```python
# tests/test_tourney_threads/api/test_new_feature.py
import pytest

def test_my_new_feature():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

### Test Guidelines

1. **Use descriptive names**: `test_config_loads_oauth_credentials`
2. **Test one thing**: Each test should verify one behavior
3. **Use fixtures**: For common setup (see [conftest.py](../tests/conftest.py))
4. **Mock external calls**: Don't make real API/Discord calls in tests
5. **Test edge cases**: Empty inputs, None, errors
6. **Aim for high coverage**: Target 95%+ code coverage

### Common Test Patterns

**Using fixtures:**
```python
def test_with_config(valid_config):
    """Uses valid_config fixture from conftest.py."""
    assert valid_config["oauth2"]["client_id"] == "test_client_id"
```

**Mocking API calls:**
```python
@pytest.mark.asyncio
async def test_api_call(mock_challonge_api):
    """Uses mock_challonge_api fixture."""
    result = await api.get_tournament("test")
    assert result is not None
```

**Testing exceptions:**
```python
def test_missing_config():
    with pytest.raises(KeyError):
        load_config("nonexistent.yaml")
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration. The pipeline runs on every pull request and push to main.

### Pipeline Jobs

Located in [.github/workflows/ci.yml](../.github/workflows/ci.yml):

1. **Code Quality** (`lint-and-format`)
   - Runs Black, isort, Ruff, MyPy
   - Fails if code doesn't meet standards

2. **Security** (`security`)
   - Runs Bandit, Safety
   - Checks for security vulnerabilities

3. **Tests** (`test`)
   - Runs on Python 3.10, 3.11, 3.12
   - Requires 95% coverage minimum
   - Uploads coverage reports

4. **Build** (`build`)
   - Builds Python package
   - Verifies package can be created

5. **Integration** (`integration-test`)
   - Runs integration and E2E tests
   - Validates full workflows

### Running CI Checks Locally

Before pushing, run the same checks CI will run:

```bash
# Code quality
black --check src tests
isort --check-only src tests
ruff check src tests
mypy src

# Security
bandit -r src
safety check

# Tests
pytest --cov=tourney_threads --cov-fail-under=95

# Build
python -m build
```

### CI Configuration

Key configurations in [pyproject.toml](../pyproject.toml):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "--cov=tourney_threads --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## Adding Dependencies

### Production Dependencies

Add to [pyproject.toml](../pyproject.toml) under `dependencies`:

```toml
dependencies = [
    "aiohttp>=3.9.0",
    "discord.py>=2.3.0",
    # New dependency
    "new-package>=1.0.0",
]
```

Then update:
```bash
pip install -e .
```

### Development Dependencies

Add to `dev` extras:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    # New dev dependency
    "new-dev-tool>=1.0.0",
]
```

Then update:
```bash
pip install -e ".[dev]"
```

## Code Style Guidelines

### General Principles

- **Readability over cleverness**: Clear code is better than clever code
- **Explicit over implicit**: Make intentions clear
- **Type hints**: Add type hints to function signatures
- **Docstrings**: Document public functions and classes

### Example

```python
from typing import Dict, List, Optional

async def get_matches(
    tournament_id: str,
    state: Optional[str] = None,
    page: int = 1,
) -> List[Dict[str, Any]]:
    """
    Fetch matches for a tournament.
    
    Args:
        tournament_id: The Challonge tournament identifier
        state: Optional match state filter (open, complete, all)
        page: Page number for pagination (default: 1)
        
    Returns:
        List of match dictionaries
        
    Raises:
        APIError: If the API request fails
    """
    # Implementation
    pass
```

### Formatting Rules

- **Line length**: 100 characters (Black default)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted with isort (stdlib, third-party, local)
- **Trailing commas**: In multi-line collections

## Releasing

### Version Bumping

Update version in [src/tourney_threads/version.py](../src/tourney_threads/version.py):

```python
__version__ = "0.2.0"  # Update this
```

### Creating a Release

1. **Update version**: Bump version in `version.py`
2. **Update changelog**: Document changes (if CHANGELOG.md exists)
3. **Commit**: `git commit -m "Bump version to 0.2.0"`
4. **Tag**: `git tag v0.2.0`
5. **Push**: `git push && git push --tags`
6. **GitHub Release**: Create release on GitHub

### Publishing to PyPI

```bash
# Build
python -m build

# Upload to TestPyPI (test first)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/chrisbirie/challonge-discord-thread-creator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chrisbirie/challonge-discord-thread-creator/discussions)
- **Docs**: Check other files in [docs/](.)

## See Also

- [README.md](../README.md) - Project overview
- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [USAGE.md](USAGE.md) - Usage examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
