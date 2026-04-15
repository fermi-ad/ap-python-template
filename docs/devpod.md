# DevPod

This repo includes a dev container descriptor at [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json).
The workspace uses the external image referenced there, which is expected to provide Python 3.12 and `uv`.

## What you get

- Python 3.12 + `uv` in a workspace container
- The repository itself provides:
  - dependency management via `uv sync`
  - test and lint commands documented in [`Makefile`](Makefile)
  - project renaming via [`scripts/rename_project.py`](scripts/rename_project.py)
  - documentation content under [`docs/`](docs/)
- Some workspace images may also provide convenience shell aliases such as `test`, `lint`, `format`, `run`, or `docs-serve`
  - those conveniences come from the external image or workspace environment, not from files tracked in this repository
  - if those aliases are unavailable in your workspace, run the underlying commands directly instead

## Use

1. On your local machine, [install DevPod](https://devpod.sh/docs/getting-started/install).
2. Open DevPod and enter the URL of your project's GitHub repository, or point it to the local directory if you've already cloned the repo.
3. After the workspace starts, run the default build command, or run it manually:

   ```bash
   uv sync
   ```

4. Run tests:

   ```bash
   uv run pytest
   ```

5. Run the CLI app:

   ```bash
   uv run ap-python-starter-kit
   ```

## Notes

- The template placeholders (`ap-python-starter-kit`, `ap_python_starter_kit`, and similar values) are expected to be replaced when you generate a real project from this template.
  - The provided [`scripts/rename_project.py`](scripts/rename_project.py) command should do this for you.
- If your DevPod or dev container image defines shell aliases that reference the placeholder project name, update that environment after renaming the project.
- This workspace intentionally uses an external dev container image for fast startup.
  - The repo's Docker-based workflow is still available in [`docs/container.md`](docs/container.md) for building runnable images and the optional browser-served GUI (Xpra HTML) target.
