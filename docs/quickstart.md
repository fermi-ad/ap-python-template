# Quickstart

## 1) Create your project from this template

Replace all placeholders:

- `__template_project_name__`
- `__template_module__`
- `__template_description__`
- `__template_author__`

## 2) Install dependencies

```bash
uv sync
```

## 3) Run the CLI app

```bash
uv run __template-module__
uv run __template-module__ --name Developer
```

## 4) Run tests and lint

```bash
uv run pytest
uv run ruff check .
```

## 5) Optional: enable PyQt scaffold

```bash
uv sync --extra gui-pyqt
uv run python scaffolds/pyqt/app.py
```
