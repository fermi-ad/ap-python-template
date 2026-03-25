# Optional PyQt Scaffold

This scaffold is intentionally separate from the default CLI template path.

## Install extras

```bash
uv sync --extra gui-pyqt
```

## Run scaffold

```bash
uv run python scaffolds/pyqt/app.py
```

## Notes

- Keep GUI dependencies optional for template consumers.
- Copy scaffold code into your own module as needed.
