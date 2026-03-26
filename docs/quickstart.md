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

By default the CLI runs an ACSys demo query (prints a few readings):

```bash
uv run __template-module__
```

Override the device/request string:

```bash
uv run __template-module__ --device "G:SCTIME@P,15H"
```

## 4) Run tests and lint

```bash
uv run pytest
uv run ruff check .
```

## 5) Optional: enable PyQt scaffold

The PyQt scaffold also shows a live ACSys reading (defaults to `G:SCTIME@P,15H`).

```bash
uv sync --extra gui-pyqt
uv run python scaffolds/pyqt/app.py
```
