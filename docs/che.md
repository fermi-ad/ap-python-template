# Eclipse Che / Dev Spaces

This repo includes an Eclipse Che devfile at [`.devfile.yaml`](../.devfile.yaml:1).

## What you get

- Python 3.12 + `uv` in a workspace container
- One-click commands for:
  - dependency sync (`uv sync`)
  - tests (`uv run pytest`)
  - lint/format (`uv run ruff ...`)
  - running the CLI entrypoint (`uv run __template-module__`)
- A simple docs endpoint for browsing `docs/` via `python -m http.server` (port 8000)

## Use

1. In Che/Dev Spaces, create a workspace from this repository.
2. Che will detect and use [`.devfile.yaml`](../.devfile.yaml:1).
3. After the workspace starts, run the default build command (or run manually):

   ```bash
   uv sync
   ```

4. Run tests:

   ```bash
   uv run pytest
   ```

5. Run the CLI app:

   ```bash
   uv run __template-module__
   ```

## Notes

- The template placeholders (`__template-module__`, `__template_module__`, etc.) are expected to be replaced when you generate a real project from this template. Update the devfile command [`.devfile.yaml`](../.devfile.yaml:1) `run` accordingly.
- This devfile intentionally uses a stock `uv` image for fast startup. The repo’s [Docker-based workflow](container.md:1) is still available for building runnable images and (optionally) GUI/Xpra targets.
