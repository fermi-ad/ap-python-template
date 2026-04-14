# DevPod

This repo includes a dev container descriptor at [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json).
It comes prebuilt with all the tools for building an application with Python 3.12 and `uv`.

## What you get

- Python 3.12 + `uv` in a workspace container
- Preconfigured command-line aliases:
  - `uv-sync` runs `uv sync`
  - `test` runs `uv run pytest`
  - `lint` runs `uv run ruff check .`
  - `format` runs `uv run ruff format .`
  - `run` runs `uv run ap-python-starter-kit` (or whatever you rename your project to)
    - If you rename the project without using the provided script, manually update your aliases and re-source your [`.bashrc`](.bashrc).
  - `rename` runs `python3 scripts/rename_project.py`
- A simple docs endpoint for browsing [`docs/`](docs/) via `python -m http.server` on port 8000
  - The alias `docs-serve` is also preconfigured

## Use

1. On your local machine, [install DevPod](https://devpod.sh/docs/getting-started/install).
2. Open DevPod and enter the URL of your project's GitHub repository, or point it to the local directory if you've already cloned the repo.
3. After the workspace starts, run the default build command, or run it manually:

   ```bash
   uv sync
   ```

4. Run tests:

   ```bash
   test
   ```

5. Run the CLI app:

   ```bash
   run
   ```

## Notes

- The template placeholders (`ap-python-starter-kit`, `ap_python_starter_kit`, and similar values) are expected to be replaced when you generate a real project from this template.
  - The provided `rename` command should do this for you.
  - After renaming, make sure the workspace user's [`.bashrc`](.bashrc) contains the correct alias values.
- This workspace intentionally uses a stock `uv` image for fast startup.
  - The repo's Docker-based workflow is still available in [`docs/container.md`](docs/container.md) for building runnable images and the optional browser-served GUI (Xpra HTML) target.
