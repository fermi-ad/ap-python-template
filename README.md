# __template_project_name__

__template_description__

A Python-first project template. The default path is a CLI app with optional, isolated PyQt scaffold support.

## Quickstart

1. Replace placeholders:
   - `__template_project_name__`
   - `__template_module__`
   - `__template_description__`
   - `__template_author__`
2. Install dependencies:
   - `uv sync`
3. Run the CLI app:
   - `uv run __template-module__`

Detailed onboarding is in [`docs/quickstart.md`](docs/quickstart.md).

## Project Layout

```text
.
├── .devfile.yaml
├── .devcontainer/
├── .github/workflows/
├── docker/start.sh
├── docs/
├── scaffolds/pyqt/
├── src/__template_module__/
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
