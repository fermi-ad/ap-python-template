# Container usage

**Local image builds are optional.** Develop and test your app in the [shared DevPod workspace](devpod.md) using the [development checks](development.md), then follow [CI and deployment](deployment.md) for normal delivery. You do not need to build images or manage Harbor credentials; a fermi-ad admin grants access to new repositories as described in the deployment guide.

Use the commands here only to check container startup or troubleshoot an image-specific problem. They require a working Docker engine, access to the base images and dependencies, and a terminal at your repository root. These deployment images are separate from the DevPod development workspace and its desktop on port 6080. See [advanced image settings](#advanced-local-image-settings) only if the basic checks are insufficient.

A **CLI image** runs a command-line/headless program and prints output to its container logs; it does not provide a browser page. A **GUI image** uses Xpra to show a running desktop window in a browser: the app still runs in the container, not as a native website. The untouched template's CLI queries ACSys and its optional GUI uses PyQt6; both are examples you can customize. Use the `cli` workflow variant for a headless app or `gui-xpra` if your app needs this desktop access; see [CI and deployment](deployment.md#deploy-your-application-step-by-step).

## Optional: check your app in a local image

[`Dockerfile`](../Dockerfile) defines two deployable targets and their build stages:

| Target | Make command | Default image tag | What runs |
| --- | --- | --- | --- |
| `runtime` | [`make build`](../Makefile) | `ap-python-starter-kit` | CLI launcher, no browser service |
| `xpra-runtime` | [`make build-gui`](../Makefile) | `ap-python-starter-kit-gui` | PyQt GUI through Xpra's HTML5 client |

Choose **one** image for your app: run `make build` for the CLI target or `make build-gui` for the Xpra GUI target. The template's startup commands point to its example app; the rename script updates the original module names, but if you change the entry point, [update startup](application.md#replace-the-example-step-by-step) before building. The Xpra target uses an externally maintained base image. Local Make commands do **not** publish or deploy images; use [CI and deployment](deployment.md) for that.

## Optional: run the CLI image

```bash
make run
```

After building the CLI image, [`make run`](../Makefile) starts the command-line app. The unmodified demo queries ACSys and prints five readings, so it needs ACSys access and any applicable site authentication. There is no browser port. If you changed the module rather than just its contents, check the [startup command](application.md#replace-the-example-step-by-step).

For a different CLI command in the container, see [advanced image settings](#advanced-local-image-settings). For day-to-day runs, use the [development workflow](development.md#a-normal-edit-and-check-cycle).

## Optional: run the browser-served GUI image

```bash
make run-gui
```

After building the GUI image, [`make run-gui`](../Makefile) starts the Xpra desktop on `http://localhost:14500/`. Open that URL while the container runs. This is a browser view of the app's window in the container, **not** a web-native app or the [development desktop](devpod.md#desktop-access). **The default browser endpoint has no authentication and the Make target publishes the port on all host interfaces; do not expose it to an untrusted network.** See [Xpra security and a local-only binding](#xpra-lifecycle-and-security).

## Advanced: local image settings

The CLI target uses AlmaLinux and installs the package without the optional PyQt extra. The GUI target uses the external `adregistry.fnal.gov/dev-containers/ap-python-xpra-base` image, installs the `gui-pyqt` extra, and starts via [`docker/start.sh`](../docker/start.sh). Builds need access to the selected base image and dependencies, including the template's [ACSys Git dependency](../pyproject.toml). [`make build-no-cache`](../Makefile) rebuilds only the CLI image without cache. You can set `IMAGE_NAME` or `IMAGE_NAME_GUI` for local image tags; [`make clean`](../Makefile) removes images under the selected tags.

**CLI override limitation:** Although make passes `APP_CMD` as an environment variable if supplied, the CLI [`runtime` entrypoint](../Dockerfile) does not read it. To run a different command in the built image, override the entrypoint explicitly:

```bash
docker run --rm --entrypoint python ap-python-starter-kit -m ap_python_starter_kit.main --help
```

To make `APP_CMD` control the CLI image, change the entrypoint in your project; setting the environment variable alone is insufficient.

The [`xpra-runtime` image](../Dockerfile) exposes port `14500`, has a health check against `http://localhost:14500/`, and runs as `pyuser` in `/home/pyuser`. Its [startup script](../docker/start.sh) defaults to `python -m ap_python_starter_kit.main --gui`. Xpra starts `openbox` and the configured application, writes the app and Xpra logs to `/tmp/app.log` and `/tmp/xpra.log` by default, and streams both logs to container stdout.

To select a different **host** port without changing the container's listening port:

```bash
make run-gui XPRA_PORT=16000
```

Then open `http://localhost:16000/`. `XPRA_PORT` changes the Docker port mapping only. The separate `XPRA_BIND_PORT` setting inside the startup script defaults to `14500`; if changed, update the mapping and health check accordingly. `XPRA_BIND_HOST` controls the address *inside* the container and defaults to all interfaces; binding only to container loopback may prevent Docker's published port from reaching Xpra.

Unlike the CLI target, the GUI startup script **does** read `APP_CMD`. For example, to pass an application argument:

```bash
make run-gui APP_CMD="python -m ap_python_starter_kit.main --gui --device G:SCTIME@P,15H"
```

The script passes this value through a shell to Xpra's `--start-child`; keep overrides to trusted, properly quoted commands. For project-wide changes after renaming or replacing the app, edit the [script's default command](../docker/start.sh) and rebuild the GUI image. `make run-gui` forwards `APP_CMD` and `XPRA_BIND_HOST`, but not the script's other Xpra settings; for other local overrides use a direct Docker invocation. The [application guide](application.md#replace-the-example-step-by-step) describes replacing the sample application.

### Xpra lifecycle and security

The [startup script](../docker/start.sh) supports these environment overrides (shown with defaults):

| Variable | Default | Purpose |
| --- | --- | --- |
| `XPRA_EXIT_WITH_CHILDREN` | `yes` | Request Xpra shutdown when its launched children exit. |
| `XPRA_EXIT_WITH_WINDOWS` | `yes` | Request shutdown when no application windows remain. |
| `XPRA_SERVER_IDLE_TIMEOUT` | `300` | Idle-server timeout in seconds. |

The startup script also accepts `APP_NAME` (session name), `XPRA_DISPLAY` (default `:100`), `XPRA_HTML` (default `on`), `XPRA_BIND_HOST` (default `0.0.0.0`), `XPRA_BIND_PORT` (default `14500`), and `XPRA_AUTH` (default `none`). It creates writable runtime directories under `/tmp` by default; see the [configuration block](../docker/start.sh) for log and directory path overrides. It waits for the HTML endpoint to become ready and stops Xpra on container shutdown. These settings are script/runtime options, not additional make arguments unless explicitly forwarded by the recipe.

**Do not publish the default GUI port to an untrusted network.** Xpra defaults to `XPRA_AUTH=none` (no authentication), serves HTML, and listens on all container interfaces; the default [`make run-gui` port mapping](../Makefile) does not restrict the *host* interface. For local-only access, use an explicit loopback host-port binding instead of that make recipe, for example:

```bash
docker run --rm -p 127.0.0.1:14500:14500 ap-python-starter-kit-gui
```

For a release, use the [provided deployment process](deployment.md); do not assume this local unauthenticated mapping is safe for other users. Xpra authentication is separate from [Kerberos configuration and runtime tickets](kerberos.md).

### Open an image shell

```bash
make shell
make shell-gui
```

These [Make targets](../Makefile) start disposable interactive containers with `/bin/bash` instead of the normal entrypoints; `make shell-gui` does **not** start Xpra. Image tags can be customized with `IMAGE_NAME` and `IMAGE_NAME_GUI`; `CONTAINER_NAME` controls the default name for `make run` (and its `-xpra` suffix for `make run-gui`), not the shell targets. For the CLI image's Kerberos packages and configuration, see [Kerberos defaults](kerberos.md).
