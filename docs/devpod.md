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

1. Ensure [VS Code is set up](#vs-code)
2. Prepare your machine 
    - [Mac](#mac)
    - [Windows](#windows)
3. On your local machine, [install DevPod](https://devpod.sh/docs/getting-started/install#install-devpod).
4. Open DevPod and enter the URL of your project's GitHub repository, or point it to the local directory if you've already cloned the repo.
5. Select Docker as the "Provider"
    - If on Windows, edit the advanced options to specify the "Host" as `tcp://127.0.0.1:2375`
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
10. Run the CLI app
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

Mac users will require Docker to be installed. While Windows users can leverage Docker Engine to avoid licensing issues, Mac users will have to leverage an open-source alternative called [Colima](https://github.com/abiosoft/colima). 

1. Install Colima using [one of the provided methods](https://github.com/abiosoft/colima/blob/main/docs/INSTALL.md)
2. Start Colima using 
    ```bash
    colima start
    ```
3. During DevPod setup, follow the instructions for using Docker as your provider. Colima will be substituted by DevPod automatically.

#### Windows
If your local machine is running Windows, you will need to have Windows Subsystem for Linux installed, with Docker or some other pod management system installed there. Here are the steps to accomplish this:

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
5. Install needed packages for Docker
    ```bash
    sudo apt install ca-certificates curl gnupg lsb-release
    ```
6. Set up GPG for Docker authentication
    ```bash
    sudo mkdir -p /etc/apt/keyrings
    ```
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    ```
7. Configure GPG authentication 
    ```bash
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```
8. Install Docker Engine
    ```bash
    sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
    ```
9. Add your user to the `docker` group (prevents needing to use `sudo` for every Docker command)
    ```bash
    sudo usermod -aG docker $USER
    ```
10. Start Docker
    ```bash
    sudo systemctl enable --now docker
    ```
    ```bash
    sudo systemctl enable containerd
    ```
    Verify Docker is running
    ```bash
    sudo systemctl status docker
    ```
11. Configure Docker to be accessible to DevPod
    ```bash
    sudo systemctl edit --full docker.service
    ```
    This should open an editor. Look for 
    ```
    ...
    [Service]
    ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
    ...
    ```
    On the end of this line, add `-H tcp://127.0.0.1:2375`. The full entry should now read
    ```
    ...
    [Service]
    ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock -H tcp://127.0.0.1:2375
    ...
    ```
    Now run
    ```bash
    sudo systemctl daemon-reload && sudo systemctl restart docker.service
    ```

## Notes

- The template placeholders (`ap-python-starter-kit`, `ap_python_starter_kit`, and similar values) are expected to be replaced when you generate a real project from this template.
  - The provided [`scripts/rename_project.py`](scripts/rename_project.py) command should do this for you.
- If your DevPod or dev container image defines shell aliases that reference the placeholder project name, update that environment after renaming the project.
- This workspace intentionally uses an external dev container image for fast startup.
  - The repo's Docker-based workflow is still available in [`docs/container.md`](docs/container.md) for building runnable images and the optional browser-served GUI (Xpra HTML) target.
