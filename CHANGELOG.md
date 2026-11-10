# Changelog

All notable changes to this template are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The template version is the `version` field in [`pyproject.toml`](pyproject.toml).

> **Created a project from this template?** This file describes changes to the *template*, not to your application. Use the migration guides below to bring template updates into your project, then replace this file with your own changelog if you like. Your project's `version` in `pyproject.toml` is yours to manage; it does not need to match the template version.

## 0.2.0

This release starts the changelog and versioning of the template. Later template changes will be recorded here with migration notes for projects created from earlier versions.

### Added

- `CHANGELOG.md` (this file) and template versioning, starting at `0.2.0`.
- `.python-version` pinning the local Python version to `3.12` for uv and other tools.
- Local storage mount for the container Make targets. `make run`, `make run-gui`, `make shell`, and `make shell-gui` now bind-mount a host directory at `/mnt/storage/ap-python-writable` and set `AP_WRITABLE_STORAGE_DIR`, imitating the persistent volume the [AP Python Launcher](https://ad-apps-internal.fnal.gov/ap-python/) provides.
  - The host directory defaults to `mount/<CONTAINER_NAME>/local` in the repository. Override it with `STORAGE_HOST_DIR=...`.
  - A new `make storage-dir` target creates the host directory and makes it world-writable, so the container user (UID 1000) can write to it whatever your host UID is. The run and shell targets depend on it.
- `mount/` added to `.gitignore`, so local storage directories are not committed.
- Docs: a new [Optional: local storage mount](docs/container.md#optional-local-storage-mount) section in `docs/container.md`, and more detail in [Persistent storage](docs/deployment.md#persistent-storage) about the working directory, log files, and file ownership.
- Docs: a new [View persisted files](docs/deployment.md#view-persisted-files) section explaining how to browse persisted data and logs outside a running launch at <https://ad-apps-internal.fnal.gov/ap-python/files/> (the trailing slash is required).
- README: a note that the **Use this template** button appears only for signed-in members of the [Fermi-AD organization](https://github.com/fermi-ad).

### Changed

- **Both container images now run from the writable storage directory.** The CLI image (previously `/app`) and the GUI/Xpra image (previously `/home/pyuser`) now use `/mnt/storage/ap-python-writable` as their `WORKDIR`. The image creates this directory and gives ownership to `pyuser:pygroup`. In the launcher, the persistent volume is mounted there, so relative paths resolve inside persistent storage.
- **GUI image logs are now persistent.** `docker/start.sh` writes `app.log` and `xpra.log` to the writable directory (`$AP_WRITABLE_STORAGE_DIR`, default `/mnt/storage/ap-python-writable`) instead of `/tmp`. They are kept after the launch ends and are not cleaned up automatically. `APP_LOG_FILE` and `XPRA_LOG_FILE` still override the paths.
- `docker/start.sh` now:
  - exits with an error if the writable directory is missing or not writable by the container user;
  - changes into that directory before starting Xpra, so the application starts there;
  - exports `AP_WRITABLE_STORAGE_DIR` so the application can find the directory the same way it does in the launcher.
- Xpra runtime directories (sockets and `chmod 700` directories) stay under `/tmp`; they do not belong on the shared volume.
- Docs (`docs/application.md`, `docs/deployment.md`) now recommend reading `AP_WRITABLE_STORAGE_DIR` explicitly rather than relying on the working directory.

### Migration guide: 0.1.0 → 0.2.0

These steps apply to projects created from the 0.1.0 template. Your project has probably been renamed with `make rename-project`, so wherever the template uses `ap-python-starter-kit` or `ap_python_starter_kit`, use your project's names instead. The easiest way to see each change is to compare the files below with the template repository at 0.2.0.

#### 1. Update the `Dockerfile`

In **both** runtime stages (the CLI stage and the Xpra/GUI stage), replace the old `WORKDIR` with:

```dockerfile
RUN mkdir -p /mnt/storage/ap-python-writable \
 && chown pyuser:pygroup /mnt/storage/ap-python-writable

WORKDIR /mnt/storage/ap-python-writable
```

- CLI stage: this replaces `WORKDIR /app`.
- GUI stage: this replaces `WORKDIR /home/pyuser` and the comment above it.

Keep the `RUN` before `USER pyuser:pygroup`, because it needs root to run `chown`.

#### 2. Update `docker/start.sh` (GUI image only)

1. Under "Application and logging settings," add the writable directory setting and change the log defaults:

   ```bash
   # Persistent writable directory (mounted by the launcher). The application runs
   # from here, and the logs below are written here by default.
   WRITABLE_DIR="${AP_WRITABLE_STORAGE_DIR:-/mnt/storage/ap-python-writable}"
   # Paths for Xpra and application logs.
   XPRA_LOG_FILE="${XPRA_LOG_FILE:-${WRITABLE_DIR}/xpra.log}"
   APP_LOG_FILE="${APP_LOG_FILE:-${WRITABLE_DIR}/app.log}"
   ```

2. After the configuration block (just before the `cleanup()` function), add the directory check and `cd`:

   ```bash
   if [ ! -d "${WRITABLE_DIR}" ] || [ ! -w "${WRITABLE_DIR}" ]; then
     echo "[start.sh] error: writable storage directory ${WRITABLE_DIR} is missing or not writable by $(id -un) (uid $(id -u))" >&2
     exit 1
   fi

   # Run the application (launched by Xpra) from the writable directory and let it
   # discover the location through the same variable the launcher provides.
   cd "${WRITABLE_DIR}"
   export AP_WRITABLE_STORAGE_DIR="${WRITABLE_DIR}"
   ```

   Leave your `APP_CMD` default unchanged.

#### 3. Update the `Makefile` (optional, recommended)

To test with local persistent storage the same way the launcher provides it:

1. After the `XPRA_BIND_HOST` setting, add:

   ```makefile
   # Local stand-in for the launcher's persistent volume. This host directory is
   # mounted at the same path the launcher uses; override STORAGE_HOST_DIR to change it.
   STORAGE_HOST_DIR ?= $(CURDIR)/mount/$(CONTAINER_NAME)/local
   STORAGE_CONTAINER_DIR := /mnt/storage/ap-python-writable
   DOCKER_STORAGE_ARGS = -v "$(STORAGE_HOST_DIR):$(STORAGE_CONTAINER_DIR)" -e AP_WRITABLE_STORAGE_DIR="$(STORAGE_CONTAINER_DIR)"
   ```

2. Add `storage-dir` to `.PHONY`, and add the target:

   ```makefile
   # Create the local storage directory. The container user (uid 1000) must be able
   # to write to it regardless of the host user's uid, so it is made world-writable.
   storage-dir:
   	@mkdir -p "$(STORAGE_HOST_DIR)"
   	@chmod a+rwx "$(STORAGE_HOST_DIR)" || echo "warning: could not chmod $(STORAGE_HOST_DIR); the container user (uid 1000) may be unable to write to it" >&2
   ```

3. Make `run`, `run-gui`, `shell`, and `shell-gui` depend on `storage-dir` (for example `run: storage-dir`), and add `$(DOCKER_STORAGE_ARGS)` to each of their `docker run` commands.

4. Optionally, add the `STORAGE_HOST_DIR` note to the `help` output.

Makefile recipe lines must start with a tab, not spaces.

#### 4. Update `.gitignore` and add `.python-version`

- Append to `.gitignore`:

  ```gitignore
  # Local mounted directories
  mount/
  ```

- Add a `.python-version` file containing `3.12`, unless your project already pins a different version.

#### 5. Check your application code

- **If your app writes files with relative paths**, they now go to `/mnt/storage/ap-python-writable` in the container. In the launcher, that means persistent storage instead of temporary storage. Check that this is what you want, and remember that persistent data is never cleaned up automatically.
- **If your app or users relied on `/home/pyuser` (GUI) or `/app` (CLI)** as the working directory, update those paths. For the GUI image, Xpra's file upload and download dialogs now open in the writable directory rather than the home directory.
- **If you read the GUI logs from `/tmp/app.log` or `/tmp/xpra.log`**, use `app.log` and `xpra.log` in the writable directory instead, or set `APP_LOG_FILE` / `XPRA_LOG_FILE` to keep the old paths. After a launch ends, you can read these logs in the launcher's [file browser](https://ad-apps-internal.fnal.gov/ap-python/files/) (keep the trailing slash).
- **For persistent data, read `AP_WRITABLE_STORAGE_DIR`** rather than relying on the working directory; see [Persistent storage](docs/deployment.md#persistent-storage).
- **If you run images with `docker run` yourself** and mount a directory at `/mnt/storage/ap-python-writable`, make sure UID 1000 can write to it. Otherwise the GUI image exits at startup with a "not writable" error.

#### 6. Update docs (optional)

If you kept the template's docs, update `docs/container.md`, `docs/deployment.md`, `docs/application.md`, and `README.md` to match the 0.2.0 template.

#### 7. Rebuild and verify

```bash
make build        # or: make build-gui
make run          # or: make run-gui
ls mount/*/local  # files your app writes (and, for the GUI image, app.log and xpra.log)
```

## 0.1.0

First version of the AP Python template: the initial work to set up a template repository for Fermilab Accelerator Division Python applications. It was not versioned or tagged at the time; `0.1.0` refers to the template state before this changelog was added.

### Added

- A Python 3.12+ uv project (`ap-python-starter-kit`) with a `src/` layout, an installed CLI entry point, and a committed `uv.lock`.
- An example application that reads devices through [ACSys](https://github.com/fermi-ad/acsys-python) (`acsys_client.py`, `main.py`), and an optional PyQt6 desktop window (`--gui`, `gui-pyqt` extra).
- `scripts/rename_project.py` (`make rename-project`) to rename the starter package, CLI command, Docker image names, and docs references to your project.
- pytest tests for the example app and rename script, Ruff linting and formatting, and pre-commit hooks.
- A multi-stage `Dockerfile` with two runtime targets: a CLI/headless image and a GUI image served to the browser through Xpra HTML (`docker/start.sh`).
- A `Makefile` with targets to sync, test, lint, format, build, run, and open shells in the images.
- DevPod and dev container configuration, with Fermilab Kerberos defaults.
- GitHub workflows that hand checks, image builds, and delivery to Harbor off to externally maintained reusable workflows, for deployment through the AP Python Launcher.
- Documentation: quickstart, DevPod, customizing the application, everyday development, container usage, CI and deployment (including persistent storage through `AP_WRITABLE_STORAGE_DIR`), Kerberos, and migrating an existing Python project.
