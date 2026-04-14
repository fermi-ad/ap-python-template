# Container usage

This template includes a Docker-based workflow with:

- a **CLI-first** default image for running the package launcher directly
- an **opt-in GUI (Xpra HTML)** image target for running the integrated PyQt app in-container and viewing it in a browser

## Image targets

The Dockerfile currently defines these documented runtime-oriented stages:

- `runtime`: the default CLI image used by [`make build`](Makefile) and [`make run`](Makefile)
- `xpra-runtime`: the browser-served GUI image used by [`make build-gui`](Makefile) and [`make run-gui`](Makefile)

## Build (CLI)

```bash
make build
```

## Run (CLI default)

Runs the fixed CLI entrypoint defined by the `runtime` stage in [`Dockerfile`](Dockerfile):

```bash
make run
```

At the moment, the CLI container starts `python -m ap_python_starter_kit.main` directly. Although [`Makefile`](Makefile) passes an `APP_CMD` environment variable into the container, the current `runtime` entrypoint does not consume it.

## Run a custom CLI command

The documented [`make run`](Makefile) path does **not** currently support overriding the CLI command via `APP_CMD`.

If you need to run a different CLI command locally, use the local `uv` workflow instead:

```bash
uv run ap-python-starter-kit --mode cli --device "G:SCTIME@P,15H"
```

If you need containerized custom CLI execution, update the `runtime` stage in [`Dockerfile`](Dockerfile) so its entrypoint evaluates `APP_CMD`.

## Build (GUI / Xpra HTML)

Build the optional GUI image target (`xpra-runtime`) from [`Dockerfile`](Dockerfile):

```bash
make build-gui
```

## Run (GUI / Xpra HTML)

This runs the integrated PyQt app inside the container and serves it through Xpra's built-in HTML client. This is the documented GUI deployment path for the template.

```bash
make run-gui
```

Then open:

```text
http://localhost:14500/
```

Custom port:

```bash
make run-gui XPRA_PORT=16000
```

Custom command:

```bash
make run-gui APP_CMD="python -m ap_python_starter_kit.gui"
```

For the Xpra image, `APP_CMD` is the supported way to replace the default GUI command that [`docker/start.sh`](docker/start.sh) launches.

Security note:

- Xpra HTML is configured with `--auth=none` (no password). Do not expose this port publicly.

## Shell

```bash
make shell
make shell-gui
```
