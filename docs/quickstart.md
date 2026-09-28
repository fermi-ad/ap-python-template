# Quickstart: make this template your application

This repository is a starting point, not the finished application. You will create **your own repository**, open a prepared development workspace, rename the package, check the included example, and then customize it with your code. The example CLI queries ACSys and has an optional PyQt window; those demo behaviors are not requirements. Use the provided [deployment guide](deployment.md) when you are ready to deliver your app through the maintained workflows.

Run the commands below in a terminal at the root of **your new repository**. [DevPod setup](devpod.md) is the supported way to use the common development tools and check the uv project before integration. You can write code elsewhere, but your repository must still support the maintainer-run integration workflow's uv-based installation and checks; see [Everyday development](development.md#stay-compatible-with-integration). Setting up a host Python environment yourself is an advanced alternative, not a different project setup.

## 1. Create a repository from the template

On the [template's GitHub page](https://github.com/fermi-ad/ap-python-template), select **Use this template → Create a new repository**. Choose a repository name and visibility, then create it. Copy the URL of your **new** repository. Do not develop by editing the original template repository.

## 2. Open your workspace

Follow [Start a DevPod workspace](devpod.md#start-a-workspace) using your new repository URL or a local clone of it. Open a VS Code terminal inside the workspace. Its [dev-container configuration](../.devcontainer/devcontainer.json) uses an externally maintained development image and installs the project dependencies on startup. If setup fails, check the workspace logs: the image and the template's [ACSys Git dependency](../pyproject.toml) must be accessible for the initial installation.

## 3. Rename the project

Before changing application code, run the renamer from the repository root:

```bash
python3 scripts/rename_project.py
```

In a terminal, enter your project name (for example, `my-project`), Python module name (`my_project`), author, description, and command name (`my-project`) when prompted. The module is the folder under `src/` that holds your Python code; the command is what you type to start the app. To preview a rename, or see all available options, run `python3 scripts/rename_project.py --help` and use its `--check` option together with the required naming options.

The script changes project configuration, the source package, tests, and some documentation. Review `git status` and the console command under [`[project.scripts]`](../pyproject.toml) before committing. **Current limitation:** the original project name and command name are the same text, so requesting a different `--cli-name` does not separately change the script entry. Edit that entry yourself if you need a different command. The renamer does not update every guide; examples and source links in the [application guide](application.md) and [development guide](development.md) still refer to the template names until you update them.

## 4. Refresh the installation and check the example

```bash
uv sync --dev
uv run my-project --help
```

Replace `my-project` with the command actually shown in your [`pyproject.toml`](../pyproject.toml). Re-syncing installs the renamed package. The help command is a safe sanity check: it does **not** connect to ACSys. If you have ACSys access and any required site authentication, you can also try the included CLI example:

```bash
uv run my-project
```

The **template example** requests `G:SCTIME@P,15H` and prints five readings. A failed live query does not necessarily mean your workspace is broken; it may simply lack ACSys connectivity or credentials. Do not treat this sample request as a requirement for your own program. The sample PyQt window is optional; see [desktop access](devpod.md#desktop-access) if you want to inspect it.

## 5. Replace the example with your application

Follow [Make the template your application](application.md#make-the-template-your-application): change the demo query, CLI arguments, and source code to suit your app, decide whether to keep any GUI, and keep the installed command and image startup settings pointing to **your** app. PyQt and Xpra are optional.

## 6. Test and prepare to deliver

After you edit code, run the tests and checks from the repository root:

```bash
uv run pytest
uv run ruff format --check .
uv run ruff check .
```

Update the example tests to test **your** program rather than only the template behavior. Keep the project's uv-based setup and tests working for integration; see [Everyday development](development.md#stay-compatible-with-integration) for the expected project layout and normal edit-and-check cycle. When your app is ready, follow [CI and deployment](deployment.md) for the branch, pull-request, image-choice, Harbor-access, and delivery steps.
