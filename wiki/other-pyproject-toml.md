# Other — pyproject.toml

# RuFaS `pyproject.toml` — Project Configuration

## Purpose

The `pyproject.toml` file is the central configuration manifest for the **RuFaS** (Ruminant Farm Systems Model) package. It defines the build system, project metadata, runtime dependencies, optional feature sets, development tooling, and packaging rules. It is the single source of truth for how the project is built, installed, and linted/type-checked.

## Build System

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"
```

- **Backend**: `setuptools.build_meta` — the standard setuptools PEP 517 backend.
- **Isolated build requirements**: `setuptools>=68.0` and `wheel` are fetched into an isolated environment when building the package (e.g., via `pip install .` or `python -m build`).

## Project Metadata

```toml
[project]
name = "RuFaS"
version = "1.0.3"
description = "Ruminant Farm Systems Model"
readme = "README.md"
license = "GPL-3.0-only"
authors = [{"name" = "RuFaS Team", "email" = "contact@rufas.org"}]
requires-python = ">=3.12, <3.14"
```

| Field | Value | Notes |
|---|---|---|
| `name` | `RuFaS` | Distribution name; case-sensitive for import (`RUFAS`). |
| `version` | `1.0.3` | Current release. |
| `description` | Ruminant Farm Systems Model | One-line summary. |
| `readme` | `README.md` | Rendered on PyPI and used as long description. |
| `license` | `GPL-3.0-only` | SPDX identifier; the project is GPL-3.0-only licensed. |
| `authors` | RuFaS Team | Contact email for maintainers. |
| `requires-python` | `>=3.12, <3.14` | Supports Python 3.12 and 3.13 only. |

## Runtime Dependencies

```toml
dependencies = [
    "matplotlib>=3.10.0",
    "numpy==2.2.0",
    "pandas>=2.2.3",
    "scipy>=1.15.1",
    "typing_extensions>=4.12.2",
    "salib==1.5.1",
    "tqdm>=4.67.1",
    "deepdiff>=8.2.0",
    "psutil>=6.1.1",
    "numba>=0.61.0",
]
```

| Package | Constraint | Purpose in RuFaS |
|---|---|---|
| `matplotlib` | `>=3.10.0` | Plotting and visualization of model outputs. |
| `numpy` | `==2.2.0` | Core numerical array operations; pinned for reproducibility. |
| `pandas` | `>=2.2.3` | Tabular data handling for inputs and results. |
| `scipy` | `>=1.15.1` | Scientific computing (optimization, integration, stats). |
| `typing_extensions` | `>=4.12.2` | Backported typing features for Python 3.12/3.13. |
| `salib` | `==1.5.1` | Sensitivity analysis (Sobol, Morris, etc.). |
| `tqdm` | `>=4.67.1` | Progress bars for long-running simulations. |
| `deepdiff` | `>=8.2.0` | Deep comparison of model state/result structures. |
| `psutil` | `>=6.1.1` | System/process resource monitoring. |
| `numba` | `>=0.61.0` | JIT compilation for performance-critical loops. |

> **Note**: `numpy` and `salib` are pinned with `==` to guarantee numerical reproducibility across environments. The remaining packages use minimum-version constraints to allow patch updates.

## Optional Dependency Groups

### `build_docs` — Documentation Build

```toml
[project.optional-dependencies]
build_docs = [
    "sphinx==9.1.0",
    "sphinxawesome-theme>=5.3.2",
    "sphinxcontrib-mermaid>=2.0.1",
]
```

Used to build the project documentation site:

- **Sphinx** — documentation generator (pinned to 9.1.0).
- **sphinxawesome-theme** — custom theme for the docs.
- **sphinxcontrib-mermaid** — enables Mermaid diagrams inside Sphinx docs.

Install with: `pip install .[build_docs]`

### `dev` — Development Tooling

```toml
dev = [
    "black>=26.5.1",
    "flake8>=7.1.1",
    "mypy>=1.15.0",
    "coverage>=7.6.11",
    "pytest>=9.0.3",
    "pytest-mock>=3.14.0",
    "pytest-lazy-fixtures>=1.4.0",
    "freezegun>=1.5.1",
    "sphinx==9.1.0",
    "sphinxawesome-theme>=5.3.2",
    "sphinxcontrib-mermaid>=2.0.1",
]
```

The `dev` group is a superset of `build_docs` plus:

| Tool | Purpose |
|---|---|
| `black` | Code formatting (line length 120, see `[tool.black]`). |
| `flake8` | Linting. |
| `mypy` | Static type checking (strict mode, see `[tool.mypy]`). |
| `coverage` | Test coverage measurement. |
| `pytest` | Test runner. |
| `pytest-mock` | Mocking support for tests. |
| `pytest-lazy-fixtures` | Lazy fixture evaluation in parametrized tests. |
| `freezegun` | Time-travel control for tests involving dates/timestamps. |

Install with: `pip install .[dev]`

## Entry Point

```toml
[project.scripts]
rufas = "RUFAS.main:main"
```

Installing the package creates a console script named `rufas` that invokes the `main()` function from the `RUFAS.main` module. This is the command-line interface for running the model.

## Project URLs

```toml
[project.urls]
Homepage = "https://rufas.org"
Repository = "https://github.com/RuminantFarmSystems/RuFaS"
Documentation = "https://ruminantfarmsystems.github.io/RuFaS/"
```

## Tool Configuration

### `[tool.setuptools]`

```toml
[tool.setuptools]
packages = ["RUFAS"]
```

Explicitly declares the `RUFAS` package. Only this top-level package is included; subpackages must be listed explicitly or discovered via `find:` directives if added later.

### `[tool.black]`

```toml
[tool.black]
target-version = ["py312"]
line-length = 120
```

- Formats code targeting Python 3.12 syntax.
- Uses a 120-character line length (wider than Black's default 88).

### `[tool.mypy]`

```toml
[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
strict_optional = true
disallow_untyped_defs = true
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
show_column_numbers = true
strict = true
exclude = ['^(?!.*(?:RUFAS|tests|main\.py|setup\.py)).*']
```

- **`strict = true`** — enables all strict mypy checks.
- **`ignore_missing_imports = true`** — suppresses errors for third-party packages without type stubs.
- **`exclude`** — a negative lookahead regex that *keeps* `RUFAS`, `tests`, `main.py`, and `setup.py` in scope while excluding everything else. This ensures type checking is applied to the core package and tests only.

### `[tool.pytest.ini_options]`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

- Directs pytest to discover tests in the `tests/` directory.
- No custom markers or fixtures are declared here; those live in `tests/conftest.py` or test modules.

## Relationship to the Codebase

```
pyproject.toml
├── defines build/install → setuptools builds RUFAS package
├── defines CLI → rufas command → RUFAS.main:main
├── defines runtime deps → numpy, pandas, scipy, salib, numba, ...
├── defines dev deps → black, flake8, mypy, pytest, ...
└── configures tools → black, mypy, pytest
```

The file is the entry point for:

1. **Packaging** — `pip install .` builds and installs the `RUFAS` package.
2. **CLI** — the `rufas` console script is the primary user-facing interface.
3. **CI/CD** — CI pipelines typically run `pip install .[dev]`, then `black --check`, `flake8`, `mypy`, and `pytest`.
4. **Reproducibility** — pinned versions of `numpy` and `salib` ensure numerical results are stable across environments.

## Usage Examples

```bash
# Install the package with runtime dependencies
pip install .

# Install with development tooling
pip install -e .[dev]

# Install with documentation build dependencies
pip install .[build_docs]

# Run the model via the CLI
rufas --help

# Run tests
pytest

# Type-check the codebase
mypy RUFAS

# Format code
black RUFAS tests
```