# Quickstart

## 1) Create your project from this template

Replace all placeholders:

- `ap-python-starter-kit`
- `ap_python_starter_kit`
- `Python starter kit`
- `Template Maintainers`

Or use the convenience script:

```bash
python3 scripts/rename_project.py
```

(Non-interactive usage is also supported; run `python3 scripts/rename_project.py -h` to see options.)

## 2) Install dependencies

```bash
uv sync
```

## 3) Run the app in CLI mode

By default the launcher runs an ACSys demo query and prints a few readings:

```bash
uv run ap-python-starter-kit
```

Override the device/request string:

```bash
uv run ap-python-starter-kit --device "G:SCTIME@P,15H"
```

Select the mode explicitly:

```bash
uv run ap-python-starter-kit --mode cli
```

## 4) Optional: enable the integrated PyQt GUI

The GUI uses the same shared ACSys client layer and shows a live ACSys reading.

```bash
uv sync --extra gui-pyqt
uv run ap-python-starter-kit --mode gui
```

Or launch the dedicated GUI script:

```bash
uv run ap-python-starter-kit-gui
```

## 5) Run tests and lint

```bash
uv run pytest
uv run ruff check .
```
