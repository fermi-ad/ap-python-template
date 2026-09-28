# DevPod and the development container

DevPod opens **your repository** in a development container in VS Code, so you can edit and test your application without installing its Python dependencies directly on your host. This is the supported way to use a common set of tools and reproduce the project's uv-based setup before maintainer-run integration. You may edit code outside DevPod, but your repository must remain installable and checkable with uv; a different editor or host environment does not change that requirement. Start with [Create a repository](quickstart.md#1-create-a-repository-from-the-template); after opening the workspace, return to the [rename step](quickstart.md#3-rename-the-project).

The [dev-container configuration](../.devcontainer/devcontainer.json) points to `adregistry.fnal.gov/dev-containers/ap-python:latest`, an **externally maintained development image**. Your repository's [`Dockerfile`](../Dockerfile) defines deployment images instead. You need access to pull the development image, but you do not need to build or maintain it. The configuration also adds an external desktop feature and runs `uv sync --dev --all-extras && uv run pre-commit install` at workspace start. The first sync needs access to the template's [ACSys Git dependency](../pyproject.toml). Keep the [project configuration and lockfile](development.md#stay-compatible-with-integration) usable by uv and check your changes locally; the maintained integration workflow runs separately on GitHub. The images used to deliver your app are described in [CI and deployment](deployment.md) and [Container usage](container.md).

## Install the host tools

1. Install [VS Code](https://code.visualstudio.com/download) and the **Dev Containers** extension. On Windows, also install the **WSL** extension.
2. Install [DevPod](https://devpod.sh/docs/getting-started/install#install-devpod).
3. Have a running Docker-compatible container engine that DevPod can use:
   - **macOS:** Install and start [OrbStack](https://orbstack.dev/download), then select DevPod's Docker provider.
   - **Windows:** Install WSL and Podman Desktop using the [Windows steps](#windows-host-setup) below.
   - **Linux:** Use a running Docker-compatible engine and select the Docker provider. The repository does not install a host engine.

### Windows host setup

In an elevated PowerShell terminal, install and update WSL (restart if prompted):

```powershell
wsl --install --no-distribution
wsl --update
```

Install [Podman Desktop for Windows](https://podman-desktop.io/downloads/windows), start it, and set up a Podman machine with WSL2 integration. Check that the Podman CLI works in PowerShell:

```powershell
podman version
```

## Start a workspace

1. In DevPod, create a workspace from **your new repository's URL** or its local clone.
2. Select the **Docker** provider. On Windows with Podman, the documented provider advanced settings are **Host** `tcp://127.0.0.1:2375` and **Docker Path** `podman`. This only works if your local Podman service is configured and running at that address; verify the host connection if DevPod cannot reach it. Do not expose an unauthenticated TCP endpoint to a network.
3. Select **VS Code** as the IDE and create/open the workspace. DevPod pulls the external development image and starts the container using the [descriptor](../.devcontainer/devcontainer.json). The first start may take longer while dependencies install. If it fails, read the startup logs and check access to the image and the ACSys Git source; you are not expected to fix the image itself.
4. In the VS Code workspace terminal, check the installed example command without connecting to ACSys:

   ```bash
   uv run ap-python-starter-kit --help
   ```

   If you already renamed the project, use the command under [`[project.scripts]`](../pyproject.toml) instead. If startup dependency installation failed, resolve the reported access/setup error before retrying `uv sync --dev --all-extras` and `uv run pre-commit install`.

Next, follow the [Quickstart rename and example check](quickstart.md#3-rename-the-project). Your own code, tests, and normal work belong in your new repository; the [development guide](development.md) covers that routine.

## Desktop access

The configured external `desktop-lite` feature offers a browser view of the **development container's desktop** on port `6080`. In VS Code's **Ports** panel, forward that port if needed and open its forwarded URL (typically `http://localhost:6080/`); select **Connect** if prompted. The [configuration](../.devcontainer/devcontainer.json) sets an empty desktop password, so keep the forwarded port local rather than publishing it.

To inspect the *template's optional PyQt example* in that desktop, run in the workspace terminal:

```bash
uv run ap-python-starter-kit --gui
```

After renaming, use your actual command name. The workspace startup installs all extras, including PyQt; if you are working outside that setup, install the extra with `uv sync --extra gui-pyqt`. This demo also tries to read ACSys, so it needs appropriate access. Your application can use another toolkit or run without a desktop. This development desktop runs in DevPod; for the browser-served Xpra delivery image, see [Make the template your application](application.md#make-the-template-your-application) and [CI and deployment](deployment.md).

## Windows troubleshooting

If DevPod reports `podman` is missing from `%PATH%`, check that `podman version` succeeds in the same Windows host environment DevPod uses. Update the user PATH if needed, then restart DevPod so it sees the change. If it cannot connect, verify that the local Podman service is running and matches the selected provider Host setting.

If VS Code reports `Bad owner or permissions on C:\\Users\\...\\.ssh\\config`, review your SSH access rules first, then repair your own SSH config permissions from PowerShell if appropriate:

```powershell
icacls "$env:USERPROFILE\.ssh\config" /setowner "$env:USERNAME"
icacls "$env:USERPROFILE\.ssh\config" /inheritance:r /grant:r "${env:USERNAME}:(F)"
```

Restart the affected workspace and host tools after resolving the host issue. Avoid removing existing host configuration without a backup.
