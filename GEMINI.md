# PEPFlow Project Overview

PEPFlow (Performance Estimation Problem Workflow) is a Python framework designed to streamline the analysis of convergence for optimization algorithms using the Performance Estimation Problem (PEP) framework. It provides tools to express algorithms in a mathematical-like syntax, formulate Primal/Dual PEPs, numerically verify convergence rates, and find analytical proofs using a symbolic engine.

## Core Architecture

The project is structured into several key components:

- **`PEPBuilder` (`pepflow/pep.py`)**: The main interface for formulating and solving Primal and Dual PEPs.
- **`PEPContext` (`pepflow/pep_context.py`)**: Manages the state of a PEP, including registered functions, vectors, and scalars.
- **Mathematical Objects**:
    - **`Function` (`pepflow/function.py`)**: Represents functions (e.g., `SmoothConvexFunction`, `SmoothStronglyConvexFunction`) and manages their interpolation constraints.
    - **`Scalar` (`pepflow/scalar.py`)** and **`Vector` (`pepflow/vector.py`)**: Represent basic mathematical entities and their linear combinations.
    - **`Operator` (`pepflow/operator.py`)**: Represents operators used in optimization algorithms.
- **`ExpressionManager` (`pepflow/expression_manager.py`)**: Handles the evaluation and representation of complex expressions in terms of basis elements.
- **`Solver` (`pepflow/solver.py`)**: Interfaces with optimization solvers (primarily `cvxpy`) to solve the formulated PEPs.
- **Interactive Dashboards**: Located in `primal_interactive_constraint.py` and `dual_interactive_constraint.py`, these use `Dash` and `Plotly` to provide a visual interface for exploring PEP relaxations.

## Technical Stack

- **Language**: Python >= 3.10
- **Package Manager**: `uv`
- **Optimization**: `cvxpy`
- **Symbolic Math**: `sympy`
- **Visualization/UI**: `dash`, `plotly`, `matplotlib`
- **Testing**: `pytest`
- **Linting/Formatting**: `ruff`, `isort`

## Development Workflows

### Environment Setup
Use `uv` to manage the environment:
```bash
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Code Quality Checks
The project provides a unified script for quality checks:
- **Run all checks**: `scripts/check.sh`
- **Format code**: `scripts/check.sh format` (uses `isort` and `ruff format`)
- **Lint code**: `scripts/check.sh lint` (uses `ruff check --fix`)
- **Type check**: `scripts/check.sh typecheck` (uses `uvx ty check`)
- **Run tests**: `scripts/check.sh test` (uses `pytest`)

### Documentation
Documentation is built using Sphinx and can be found in the `docs/` directory.
- **Build docs**: `scripts/build_doc.sh`
- **Build and serve locally**: `scripts/build_doc.sh --serve`
- **Serve existing docs**: `scripts/build_doc.sh --serve-only`

### Testing Conventions
- Unit tests are located alongside source files (e.g., `pepflow/function_test.py`) or as standalone test files (e.g., `pepflow/e2e_test.py`).
- Use `pytest -s -vv pepflow` to run tests with verbose output.

## Key Files and Directories
- `pepflow/`: Core library source code.
- `docs/`: Sphinx documentation source and assets.
- `examples/`: Jupyter notebooks demonstrating various optimization algorithms (GD, AGM, PGM, DRS, etc.).
- `scripts/`: Utility scripts for development, building, and deployment.
- `pyproject.toml`: Project metadata, dependencies, and tool configurations.
