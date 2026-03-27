# Container usage

This template includes a Docker-based workflow with:

- a **CLI-first** default image (smallest/safest)
- an **opt-in GUI (Xpra HTML)** image target for running a PyQt app in-container and viewing it in a browser

## Build (CLI)

```bash
make build
```

## Run (CLI default)

Runs the CLI module entrypoint configured in [`Dockerfile`](Dockerfile):

```bash
make run
```

## Run a custom CLI command

```bash
make run APP_CMD="python -m ap_python_starter_kit.main --name Container"
```

## Build (GUI / Xpra HTML)

Build the optional GUI image target (`xpra-runtime`) from [`Dockerfile`](Dockerfile:1):

```bash
make build-gui
```

## Run (GUI / Xpra HTML)

This runs a PyQt app inside the container and serves it via Xpra's built-in HTML client.

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
make run-gui APP_CMD="python /app/scaffolds/pyqt/app.py"
```

Security note:

- Xpra HTML is configured with `--auth=none` (no password). Do not expose this port publicly.

## Shell

```bash
make shell
make shell-gui
```
