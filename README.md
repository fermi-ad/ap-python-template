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

## DevPod / Dev Container

This repo includes a Dev Container descriptor file at [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json). It is recommended to [install DevPod](https://devpod.sh/docs/getting-started/install) so that you can take advantage of the prebuilt development environment it provides. 

Read more about DevPod [here](https://devpod.sh/docs/what-is-devpod)

Docs: [`docs/devpod.md`](docs/devpod.md).

## Project Layout

```text
.
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

## Deployment Container
Once your app is ready to deploy, a container and Dockerfile have been provided for easy setup. Read more below:

- Container usage: [`docs/container.md`](docs/container.md)

## Optional PyQt Scaffold

PyQt is intentionally isolated from the default template flow.

See [`docs/optional-pyqt.md`](docs/optional-pyqt.md) for setup and usage.
