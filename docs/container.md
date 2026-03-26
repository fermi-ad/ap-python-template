# Container usage

This template includes a Docker-based workflow with:

- a **CLI-first** default image (smallest/safest)
- an **opt-in GUI** image target for PyQt

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
make run APP_CMD="python -m __template_module__.main --name Container"
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

## Shell

```bash
make shell
make shell-gui
```
