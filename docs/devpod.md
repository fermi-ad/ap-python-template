# DevPod

This repo includes a dev container descriptor at [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json). 
It comes prebuilt with all the tools for building an application with Python 3.12 and `uv`.

## What you get

- Python 3.12 + `uv` in a workspace container
- Preconfigured command-line aliases for:
  - dependency sync: `uv-sync` -> executes `uv sync`
  - tests: `test` -> executes `uv run pytest`
  - lint: `lint` -> executes `uv run ruff check .`
  - format: `format` -> executes `uv run ruff format .`
  - running the CLI entrypoint: `run` -> executes `uv run ap-python-starter-kit` (or whatever you rename your project to be)
    - Note that you will have to manually update your aliases and source the `.bashrc` file if you rename your project without using the provided script
  - renaming the project: `rename` -> executes `python3 scripts/rename_project.py`
- A simple docs endpoint for browsing `docs/` via `python -m http.server` (port 8000)
  - An alias for this is preconfigured as well: run `docs-serve`

## Use

1. On your local machine, [install DevPod](https://devpod.sh/docs/getting-started/install). 
2. Open DevPod and enter the URL of your project's GitHub repository (or the directory where the project lives on your local machine, if you've already cloned it).
3. After the workspace starts, run the default build command (or run manually):

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

- The template placeholders (`ap-python-starter-kit`, `ap_python_starter_kit`, etc.) are expected to be replaced when you generate a real project from this template. Be sure the container's `~/.bashrc` file has the correct alias.
  - The provided `rename` command should do this for you.
- This devfile intentionally uses a stock `uv` image for fast startup. The repo’s [Docker-based workflow](container.md:1) is still available for building runnable images and an optional GUI (Xpra HTML) target.
