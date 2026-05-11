# DevPod

This repo includes a dev container descriptor at [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json).
The workspace uses the external image referenced there, which is expected to provide Python 3.12 and `uv`.

## What you get

- Python 3.12 + `uv` in a workspace container
- The repository itself provides:
  - dependency management via `uv sync`
  - test and lint commands documented in [`Makefile`](Makefile)
  - project renaming via [`scripts/rename_project.py`](scripts/rename_project.py)
  - documentation content under [`docs/`](docs/)
- Some workspace images may also provide convenience shell aliases such as `test`, `lint`, `format`, `run`, or `docs-serve`
  - those conveniences come from the external image or workspace environment, not from files tracked in this repository
  - if those aliases are unavailable in your workspace, run the underlying commands directly instead

## Use

### Setup

1. Ensure [VS Code is set up](#vs-code). This includes installing some necessary extensions, listed in the instructions.
2. Prepare your machine
    - [Mac](#mac)
    - [Windows](#windows)
3. On your local machine, [install DevPod](https://devpod.sh/docs/getting-started/install#install-devpod).
4. Open DevPod and enter the URL of your project's GitHub repository, or point it to the local directory if you've already cloned the repo.
5. Select Docker as the "Provider"
    - If on Windows, edit the advanced options to specify the "Host" as `tcp://127.0.0.1:2375` and change "Docker Path" to "podman".
6. Select VS Code as your IDE
7. Click Create - the dev container will be pulled down and started for you, and VS Code should open
    - If you have trouble with this step on Windows, see [Troubleshooting DevPod on Windows](#troubleshooting-devpod-on-windows)
8. After the workspace starts, open a terminal in VS Code and run
    ```bash
    uv sync --dev --all-extras
    ```
9. Run tests
    ```bash
    uv run pytest
    ```
10. (Optional) Run the GUI
    1. [Set up access to the container's desktop](#ui-development-after-setup-is-complete)
    2. Run
        ```bash
        uv run ap-python-starter-kit
        ```

### Prerequisites

#### VS Code

1. [Install VS Code](https://code.visualstudio.com/download)
2. Open VS Code and navigate to the Extensions tab (icon looks like four squares, where the top-right square is rotated 45 degrees)
3. In the search bar at the top, type "Dev Containers" and install the extension from Microsoft
4. (Windows-only) Do the same as step 3, searching for and installing the "WSL" extension (also by Microsoft)

#### Mac

Mac users will run containers using the Docker-compatible [OrbStack](https://orbstack.dev/).

1. [Install OrbStack](https://orbstack.dev/download)
2. Start OrbStack by opening the app, or run in a terminal:
    ```bash
    orb start
    ```
3. During DevPod setup, follow the instructions for using Docker as your provider. OrbStack will be substituted by DevPod automatically.

#### Windows

If your local machine is running Windows, you will need to have Podman installed and set up to use Windows Subsystem for Linux as its unix runtime host.

1. Run the following in a terminal with administrator rights (you may be asked to restart your machine)
    ```PowerShell
    wsl --install --no-distribution
    ```
2. Ensure WSL has the latest kernel by running
    ```PowerShell
    wsl --update
    ```
3. Install Podman Desktop on Windows:
    - Download and install Podman Desktop: <https://podman-desktop.io/downloads/windows>
    - Open Podman Desktop after installing so it can finish first-time setup. It will walk you through creating a Podman Machine. Be sure to select the WSL2 integration during this step.
4. Verify Podman is installed:
    ```PowerShell
    podman version
    ```

### UI development (After setup is complete)

While building your app, you'll probably want to test out changes to the UI before deploying. In the container, this requires one preliminary step.

The development container comes with a minimal desktop overlay, in which your app will run when you kick it off. To see it, do the following:

1. In VS Code, go to the "Ports" tab of the bottom panel (toggle the panel with the appropriate button in the very top-right if it is not already visible)
2. Click the "Forward a Port" button
3. Type `6080` and hit Enter
4. If it doesn't open automatically, go to your web browser and navigate to `localhost:6080`
5. Click "Connect"

You're all set! Now when you run the app locally, it will come up in your web browser at `localhost:6080`.

## Notes

- The template placeholders (`ap-python-starter-kit`, `ap_python_starter_kit`, and similar values) are expected to be replaced when you generate a real project from this template.
  - The provided [`scripts/rename_project.py`](scripts/rename_project.py) command should do this for you.
- If your DevPod or dev container image defines shell aliases that reference the placeholder project name, update that environment after renaming the project.
- This workspace intentionally uses an external dev container image for fast startup.
  - The repo's Docker-based workflow is still available in [`docs/container.md`](docs/container.md) for building runnable images and the optional browser-served GUI (Xpra HTML) target.

### Troubleshooting DevPod on Windows

After applying any of these fixes, be sure to fully stop Podman and DevPod (making sure their icons are not still present in the taskbar hidden icons menu) restart them, and then create a new DevPod workspace from scratch (starting from [step 4](#setup) above)

#### `podman` binary not found in `%PATH%` during DevPod workspace build

Run in PowerShell to extend your path, replacing `[your user]` with your username:

```PowerShell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Users\[your user]\.local\bin", "User")
```

Also try deleting any pre-existing `C:\Users\[your user]\.docker` folder, as this may interfere with the Podman configuration.

#### VS Code fails to connect to running workspace with `Bad owner or permissions on C:\\Users\\[username]/.ssh/config` error in terminal

Run in PowerShell to set the correct permissions for the SSH config folder:

```PowerShell
icacls "$env:USERPROFILE\.ssh\config" /setowner "$env:USERNAME"
icacls "$env:USERPROFILE\.ssh\config" /inheritance:r /grant:r "${env:USERNAME}:(F)"
```
