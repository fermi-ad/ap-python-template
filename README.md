# ap-python-starter-kit

Python starter kit

A Python-first project template. The default path is a CLI app with optional, isolated PyQt scaffold support.

## Quickstart

1. Rename the template to your project:

   ```bash
   python3 scripts/rename_project.py
   ```

   (Non-interactive usage is also supported, see [`scripts/rename_project.py`](scripts/rename_project.py).)

2. Install dependencies:
   - `uv sync`
3. Run the CLI app:
   - `uv run my-project` (or your chosen `--cli-name`)

Detailed onboarding is in [`docs/quickstart.md`](docs/quickstart.md).

## Eclipse Che / Dev Spaces

This repo includes an Eclipse Che devfile at [`.devfile.yaml`](.devfile.yaml:1).

Docs: [`docs/che.md`](docs/che.md:1).

## Project Layout

```text
.
├── .devfile.yaml
├── .devcontainer/
├── .github/workflows/
├── docker/start.sh
├── docs/
├── scaffolds/pyqt/
├── src/ap_python_starter_kit/
├── tests/
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## Container and Che

- Container usage: [`docs/container.md`](docs/container.md)
- Eclipse Che usage: [`docs/che.md`](docs/che.md)

## Optional PyQt Scaffold

PyQt is intentionally isolated from the default template flow.

See [`docs/optional-pyqt.md`](docs/optional-pyqt.md) for setup and usage.
