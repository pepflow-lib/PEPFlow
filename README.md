<div align="center">
<h1 align="center">
  <img width="45" alt="PEPflow logo" src="docs/assets/pepflow-logo.svg">
  PEPFlow: Performance <br />  Estimation Problem Workflow
</h1>


[![CI](https://github.com/pepflow-lib/pepflow/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pepflow-lib/pepflow/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Pypi](https://img.shields.io/pypi/v/pepflow.svg?logo=python&logoColor=white&label=PyPI&color=fcbc2c)](https://pypi.org/project/pepflow/)
</div>


<span style="color:#6B4497; font-weight:bold">PEPFlow</span> builds on the Performance Estimation Problem (PEP) framework, a powerful approach for analyzing the convergence of optimization algorithms. PEP formulates performance guarantees of an algorithm into tractable optimization problems and helps provide analytical proofs of convergence. <span style="color:#6B4497; font-weight:bold">PEPFlow</span> streamlines the entire PEP workflow:

1. Express the algorithm in a mathematical-like syntax
2. Formulate Primal/Dual PEP
3. Numerically verify convergence rate
4. Manipulate Primal/Dual PEP via interactive dashboard
5. Find analytical proofs using PEPFlow and SymPy symbolic engine jointly
6. Verify analytical proofs using PEPFlow and SymPy symbolic engine jointly

<span style="color:#6B4497; font-weight:bold">PEPFlow</span> offers the following key features for building a systematic and interactive <span style="color:red; font-weight:bold">workflow</span>

- Automated process for setting up and solving Primal/Dual PEPs;
- Interactive dashboard to explore and search exact relaxations of Primal PEPs;
- Interactive dashboard to numerically verify dual variable values of Dual PEPs;
- Direct access to key mathematical objects for deriving and verifying analytical proofs in symbols.


## Development Guide

We use `uv` to manage the packages and python environments. To start 

```bash
uv sync; source .venv/bin/activate;
```

In windows, use `.venv\Scripts\activate` instead.

### Lint & Testing
We use `ruff` to do the format and lint and `isort` to do the import ordering.

```bash
ruff format;
ruff check .;
isort .;
```

We use `pytest` framework to do the test. To run all unit tests, run the following command:

```bash
pytest -s -vv pepflow
```

We have a convenient script to above
```bash
scripts/check.sh [format|lint|typecheck|test]
```
See the script for the options.

### Build doc website

Install the required library (one-time) and `pandoc` in order to build ipynb.
```bash
uv pip install -r docs/requirements.txt
```

To build the website, run
```bash
scripts/build_doc.sh [--serve-only]
```
The argument `--serve-only` is optional for hosting the website locally.


## Pre-Release Notice

This library is still in the pre-alpha phase. We are releasing the code early due to ongoing disputes. On November 11, an email was sent to the PEPFlow team as well as a group of researchers, accusing plagiarism and stating no citation on previous work. Credit and context are provided in our workshop paper submitted in August 2025, which will soon be released on OpenReview. See this original paragraph in the following screenshot:

![screenshot](docs/assets/screenshot.png)

While we have complied with the citation request, we find the ungrounded accusation of plagiarism directed at a pre-alpha release to be unwarranted and not in the spirit of open, collaborative research.


