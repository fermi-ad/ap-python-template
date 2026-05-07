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
    - If on Windows, edit the advanced options to specify the "Host" as `tcp://127.0.0.1:2375`.
6. Select VS Code as your IDE
7. Click Create - the dev container will be pulled down and started for you, and VS Code should open
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

If your local machine is running Windows, you will need to have Windows Subsystem for Linux installed, with Podman installed there.

This guide uses **Podman in WSL** and exposes a **Docker-compatible API endpoint** to DevPod on Windows.

1. Run the following in a terminal with administrator rights (you may be asked to restart your machine)
    ```PowerShell
    wsl --install
    ```
    Ubuntu will be the default Linux distribution, and the remainder of this guide will target that.
2. Open the Start menu and type `wsl`. Run the WSL application.
3. You will be asked to set up a username and password in the Ubuntu instance. This has no bearing on your Windows environment. The user you set up will have administrator (sudo) permissions in the Ubuntu image.
4. Update the packages installed by running
    ```bash
    sudo apt update && sudo apt upgrade
    ```

##### Install Podman (in WSL Ubuntu)

5. Install Podman from Ubuntu's repositories:
    ```bash
    sudo apt install -y podman
    ```
6. Verify Podman is installed:
    ```bash
    podman version
    ```

##### Expose Podman's Docker-compatible API to DevPod (TCP 2375)

DevPod's "Docker" provider talks to a Docker-compatible API endpoint. Podman can provide this via its socket.

7. Enable and start the Podman socket:
    ```bash
    sudo systemctl enable --now podman.socket
    ```
8. Configure the socket to listen on `tcp://127.0.0.1:2375` (so DevPod on Windows can reach it).

    Create a systemd override for the socket:
    ```bash
    sudo systemctl edit podman.socket
    ```

    In the editor, add:
    ```ini
    [Socket]
    ListenStream=
    ListenStream=127.0.0.1:2375
    ```

    Note that both `ListenStream` lines are required.

    Then reload and restart:
    ```bash
    sudo systemctl daemon-reload && sudo systemctl restart podman.socket
    ```

9. Verify the socket is listening:
    ```bash
    sudo systemctl status podman.socket
    ```

10. In DevPod (Windows), select the Docker provider and set the Host to:

    `tcp://127.0.0.1:2375`

Note: If your environment blocks TCP listeners, you may need to adjust firewall / security tooling.

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
