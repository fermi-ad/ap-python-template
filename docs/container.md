# Container usage

This template includes a Docker-based workflow with:

- a **CLI-first** default image (smallest/safest)
- an **opt-in GUI** image target for PyQt (host X server)
- an **opt-in Xpra HTML** deployment image target (AlmaLinux + Xpra)

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

## Build (GUI / PyQt)

Build the optional GUI image target (`runtime-gui`) from [`Dockerfile`](Dockerfile):

```bash
make build-gui
```

## Run (GUI / PyQt)

This uses your host X server (mounts `/tmp/.X11-unix`).

```bash
make run-gui
```

## Build (Xpra / HTML)

Build the optional Xpra image target (`xpra-runtime`) from [`Dockerfile`](Dockerfile):

```bash
make build-xpra
```

## Run (Xpra / HTML)

This runs a PyQt app inside the container and serves it via Xpra's built-in HTML client.

```bash
make run-xpra
```

Then open:

```text
http://localhost:14500/
```

Custom port:

```bash
make run-xpra XPRA_PORT=16000
```

Custom command:

```bash
make run-xpra APP_CMD="python /app/scaffolds/pyqt/app.py"
```

Security note:

- Xpra HTML is configured with `--auth=none` (no password). Do not expose this port publicly.

## Shell

```bash
make shell
make shell-gui
make shell-xpra
```
