# Getting Started

This page explains how to run Tau locally and work on the project.

## Requirements

Tau currently targets the Python version declared in `pyproject.toml` and uses `uv` for dependency management.

## Install dependencies

```bash
uv sync --dev --group docs
```

## Verify the CLI

```bash
uv run tau --version
```

Expected output:

```text
tau 0.1.0
```

## Run tests and checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

## Run the documentation site locally

```bash
uv run --group docs mkdocs serve
```

Then open:

```text
http://127.0.0.1:8000
```

## Build the documentation site

```bash
uv run --group docs mkdocs build
```

The generated static website is written to `site/`.

## Deployment

Documentation is deployed to GitHub Pages from the `main` branch using the workflow in:

```text
.github/workflows/docs.yml
```

The public site is configured for:

```text
https://alejandro-ao.github.io/tau/
```
