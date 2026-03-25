# Container usage

This template includes a simple Docker-based workflow (CLI-first).

## Build

```bash
make build
```

## Run (default)

Runs the CLI module entrypoint configured in [`Dockerfile`](Dockerfile):

```bash
make run
```

## Run a custom command

```bash
make run APP_CMD="python -m __template_module__.main --name Container"
```

## Shell

```bash
make shell
```
