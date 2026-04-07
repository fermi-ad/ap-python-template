# Quickstart

## 1) Create your project from this template

Replace all placeholders:

- `ap-python-starter-kit`
- `ap_python_starter_kit`
- `Python starter kit`
- `Template Maintainers`

## 2) Install dependencies

```bash
$ uv sync
```

## 3) Run the CLI app

By default the CLI runs an ACSys demo query (prints a few readings):

```bash
$ run
```

Override the device/request string:

```bash
$ run --device "G:SCTIME@P,15H"
```

## 4) Run tests and lint

```bash
$ test
$ lint
```

## 5) Optional: enable PyQt scaffold

The PyQt scaffold also shows a live ACSys reading (defaults to `G:SCTIME@P,15H`).

```bash
uv sync --extra gui-pyqt
uv run python scaffolds/pyqt/app.py
```
