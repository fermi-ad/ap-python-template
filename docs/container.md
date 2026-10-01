# Container usage

**Local image builds are optional.** Develop and test your app in the [shared DevPod workspace](devpod.md) using the [development checks](development.md), then follow [CI and deployment](deployment.md) for normal delivery. You do not need to build images or manage Harbor credentials; a fermi-ad admin grants access to new repositories as described in the deployment guide.

Use the commands here only to check container startup or troubleshoot an image-specific problem. They require a working Docker engine, access to the base images and dependencies, and a terminal at your repository root. These deployment images are separate from the DevPod development workspace and its desktop on port 6080. See [advanced image settings](#advanced-local-image-settings) only if the basic checks are insufficient.

A **CLI image** runs a command-line/headless program and prints output to its container logs. A **GUI image** uses Xpra to show a running desktop window in a browser; the app runs inside the container. The untouched template's CLI queries ACSys and its optional GUI uses PyQt6; both are examples you can customize. Use the `cli` workflow variant for a headless app or `gui-xpra` if your app needs browser access to a desktop window; see [CI and deployment](deployment.md#deploy-your-application-step-by-step).

## Optional: check your app in a local image

[`Dockerfile`](../Dockerfile) defines two deployable targets and their build stages:

| Target | Make command | Default image tag | What runs |
| --- | --- | --- | --- |
| `runtime` | [`make build`](../Makefile) | `ap-python-starter-kit` | CLI launcher, no browser service |
| `xpra-runtime` | [`make build-gui`](../Makefile) | `ap-python-starter-kit-gui` | PyQt GUI through Xpra's HTML5 client |

Choose **one** image for your app: run `make build` for the CLI target or `make build-gui` for the Xpra GUI target. The template's startup commands point to its example app; the rename script updates the original module names, but if you change the entry point, [update startup](application.md#replace-the-example-step-by-step) before building. The Xpra target uses an externally maintained base image. Both images require writable storage mounted at `/mnt/storage` when started through their normal entrypoints; see [Workspace storage](#workspace-storage). Local Make commands do **not** publish or deploy images; use [CI and deployment](deployment.md) for that.

## Optional: run the CLI image

```bash
make run
```

After building the CLI image, [`make run`](../Makefile) bind-mounts the current repository at `/mnt/storage`, creates a timestamped job directory, and starts the command-line app from there. The unmodified demo queries ACSys and prints five readings, so it needs ACSys access and any applicable site authentication. There is no browser port. The repository must be writable by the container's `pyuser` (UID 1000). If you changed the module rather than just its contents, check the [startup command](application.md#replace-the-example-step-by-step).

For a different CLI command in the container, see [advanced image settings](#advanced-local-image-settings). For day-to-day runs, use the [development workflow](development.md#a-normal-edit-and-check-cycle).

## Optional: run the browser-served GUI image

```bash
make run-gui
```

After building the GUI image, [`make run-gui`](../Makefile) bind-mounts the current repository at `/mnt/storage` and starts the Xpra desktop on `http://localhost:14500/`. Open that URL while the container runs. Xpra displays the app's window from the deployment container; the [development desktop](devpod.md#desktop-access) runs in DevPod. The repository must be writable by the container's `pyuser` (UID 1000); generated files are stored in the [job directory](#workspace-storage). **The default browser endpoint has no authentication and the Make target publishes the port on all host interfaces; do not expose it to an untrusted network.** See [Xpra security and a local-only binding](#xpra-lifecycle-and-security).

## Workspace storage

Both image entrypoints source [`docker/create-workspace.sh`](../docker/create-workspace.sh) before launching the app. It requires `/mnt/storage` to be a mount point and creates `/mnt/storage/ap-python-starter-kit/<timestamp>` using a timestamp formatted as `YYYY-MM-DDTHH:MM:SS.mmm` (the final part is milliseconds). It changes the process working directory to that job directory, so relative application output lands there. Renaming the project updates the app-name directory in the helper. Each container startup gets a timestamp-based directory; timestamps are not guaranteed unique under concurrent starts, and a restart can use a different directory. This is not a stable Kubernetes Job ID.

At deployment, mount the provisioned PVC at `/mnt/storage` and ensure the runtime user `pyuser` (UID 1000) can create the application directory and files there. The helper checks for the `mountpoint` command, verifies the mount point, creates the app directory, and tests that it can write there; startup fails if these checks fail. It does not verify *which* volume is mounted. The [`make run` and `make run-gui` recipes](../Makefile) use a bind mount of the current repository for local checks instead of a PVC, so their output is written into the repository under `ap-python-starter-kit/` (or the renamed project name). If your checkout is not writable by UID 1000, mount another writable directory with Docker directly. Opening a shell with `make shell` or `make shell-gui` bypasses the entrypoint and does not create a job directory.

## Advanced: local image settings

The CLI target uses AlmaLinux and installs the package without the optional PyQt extra, and starts via [`docker/start-cli.sh`](../docker/start-cli.sh). The GUI target uses the external `adregistry.fnal.gov/dev-containers/ap-python-xpra-base` image, installs the `gui-pyqt` extra, and starts via [`docker/start-gui.sh`](../docker/start-gui.sh). Builds need access to the selected base image and dependencies, including the template's [ACSys Git dependency](../pyproject.toml). [`make build-no-cache`](../Makefile) rebuilds only the CLI image without cache. You can set `IMAGE_NAME` or `IMAGE_NAME_GUI` for local image tags; [`make clean`](../Makefile) removes images under the selected tags.

**CLI launch command:** The CLI [`start-cli.sh`](../docker/start-cli.sh) runs a fixed module command. To run a different command in the built image, override the entrypoint explicitly:

```bash
docker run --rm --entrypoint python ap-python-starter-kit -m ap_python_starter_kit.main --help
```

Overriding the entrypoint as shown bypasses workspace setup. If the alternate command needs persistent storage, mount a writable volume at `/mnt/storage` and create/select a job directory explicitly, or adapt the CLI startup script.

The [`xpra-runtime` image](../Dockerfile) exposes port `14500`, has a health check against `http://localhost:14500/`, and runs as `pyuser`. The image's initial working directory is `/home/pyuser`, but [workspace setup](#workspace-storage) changes it to the job directory before Xpra and the app start. Its [startup script](../docker/start-gui.sh) defaults to `python -m ap_python_starter_kit.main --gui`. Xpra starts `openbox` and the configured application, writes the app and Xpra logs to `/tmp/app.log` and `/tmp/xpra.log` by default, and streams both logs to container stdout.

To select a different **host** port without changing the container's listening port:

```bash
make run-gui XPRA_PORT=16000
```

Then open `http://localhost:16000/`. `XPRA_PORT` changes the Docker port mapping only. The separate `XPRA_BIND_PORT` setting inside the startup script defaults to `14500`; if changed, update the mapping and health check accordingly. `XPRA_BIND_HOST` controls the address *inside* the container and defaults to all interfaces; binding only to container loopback may prevent Docker's published port from reaching Xpra.

The GUI [startup script](../docker/start-gui.sh) launches a fixed module command through Xpra. To change the command or its arguments, edit the script's `--start-child` command and rebuild the GUI image. [`make run-gui`](../Makefile) forwards `XPRA_BIND_HOST`; to override other Xpra settings locally, invoke Docker directly. The [application guide](application.md#replace-the-example-step-by-step) describes replacing the sample application.

### Xpra lifecycle and security

The [GUI startup script](../docker/start-gui.sh) supports these environment overrides (shown with defaults):

| Variable | Default | Purpose |
| --- | --- | --- |
| `XPRA_EXIT_WITH_CHILDREN` | `yes` | Request Xpra shutdown when its launched children exit. |
| `XPRA_EXIT_WITH_WINDOWS` | `yes` | Request shutdown when no application windows remain. |
| `XPRA_SERVER_IDLE_TIMEOUT` | `300` | Idle-server timeout in seconds. |

The startup script also accepts `APP_NAME` (Xpra session name, not the storage directory name), `XPRA_DISPLAY` (default `:100`), `XPRA_HTML` (default `on`), `XPRA_BIND_HOST` (default `0.0.0.0`), `XPRA_BIND_PORT` (default `14500`), and `XPRA_AUTH` (default `none`). It creates writable Xpra runtime directories under `/tmp` by default; see the [configuration block](../docker/start-gui.sh) for log and runtime-directory overrides. Persistent app output goes to the [job directory](#workspace-storage). It waits for the HTML endpoint to become ready and stops Xpra on container shutdown. These settings are script/runtime options, not additional `make` arguments unless explicitly forwarded by the recipe.

**Do not publish the default GUI port to an untrusted network.** Xpra defaults to `XPRA_AUTH=none` (no authentication), serves HTML, and listens on all container interfaces; the default [`make run-gui` port mapping](../Makefile) does not restrict the *host* interface. For local-only access, use an explicit loopback host-port binding instead of that `make` recipe, for example:

```bash
docker run --rm -p 127.0.0.1:14500:14500 \
  --mount "type=bind,source=$(pwd),target=/mnt/storage" \
  ap-python-starter-kit-gui
```

For a release, use the [provided deployment process](deployment.md); do not assume this local unauthenticated mapping is safe for other users. Xpra authentication is separate from [Kerberos configuration and runtime tickets](kerberos.md).

### Open an image shell

```bash
make shell
make shell-gui
```

These [Make targets](../Makefile) start disposable interactive containers with `/bin/bash` instead of the normal entrypoints; `make shell-gui` does **not** start Xpra. Image tags can be customized with `IMAGE_NAME` and `IMAGE_NAME_GUI`; `CONTAINER_NAME` controls the default name for `make run` (and its `-xpra` suffix for `make run-gui`), not the shell targets. For the CLI image's Kerberos packages and configuration, see [Kerberos defaults](kerberos.md).
