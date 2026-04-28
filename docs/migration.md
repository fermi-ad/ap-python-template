# Migrating an existing Python project

This guide will walk through the steps to take when pulling an existing Python project into the
AP Python ecosystem.

### Assumptions

This guide assumes your project uses `pip` as a package manager and `PyQt 5` as a GUI framework.
There will be sections dedicated to migrating from `pip` to `uv` and from `PyQt 5` to `PyQt 6`. 
Feel free to skip these if you're already set up with `uv` and `PyQt 6`. 

Included at the end of this guide are a few extra Quality-of-Life enhancements made to the original Auto Quad Centering application when testing out the migration process. They have to do with the application itself rather than the project configuration, so they may or may not have relevance in other applications.

## General migration steps

1. Construct a new repository for your migrated application from this template, using the "**Create a new repository**" button.
2. Ensure your AP Python development environment is set up. Follow [the guide](docs/devpod.md) for complete instructions.
3. Use the rename script (run `python3 scripts/rename_project.py` in the DevPod for your migrated project repository) to change the project package name.
Make it match the package name you use in your source project.

    For example, for Auto Quad Centering, the project name became `auto-quad-centering` and the package name was likewise `auto_quad_centering`.
4. Replace the contents of `src/<your package name>` with your existing Python code to be migrated.
5. If your source project used `pip`, follow the [`pip` to `uv` migration steps](#pip-to-uv-migration).
6. If your source project used `PyQt 5`, follow the [`PyQt 5` to `PyQt 6` migration steps](#pyqt-5-to-pyqt-6).

## `pip` to `uv` migration

`uv` and its dependencies are already installed in your DevPod environment. To build with `uv`, you'll simply need to let it know what Python packages your project depends on and where the entrypoint for your code is. This is configured in the `pyproject.toml` file at the root of the repository. The exact version of the dependencies used by `uv` when building your code will be recorded in the `uv.lock` file. 

Migration steps are as follows:

1. Copy the contents of your `requirements.txt` file to your clipboard
2. Locate the `[project]` section of the `pyproject.toml`, and paste the `requirements.txt` contents into the `dependencies` array.
    Modify the dependency entries so they are comma-delimited and each is surrounded by quotes.

    Example:
    
    `requirements.txt`
    ```txt
    numpy>=1.19.0
    pandas>=2.0.0
    matplotlib>=3.3.0
    ...
    ```
    becomes
    
    `pyproject.toml`
    ```toml
    ...
    [project]
    ...
    dependencies = [
        "acsys", 
        "acsys[settings]",
        "numpy>=1.19.0",
        "pandas>=2.0.0",
        "matplotlib>=3.3.0",
        ...
    ]
    ...
    ```
3. Refresh the `uv.lock` file by running `uv sync` in the command line
4. Rebuild the virtual environment by running `uv venv --clear` in the command line (this may take a minute to complete)
    - Be sure to run `source .venv/bin/activate` once the virtual environment has been rebuilt
    - Also run `uv run pre-commit install` to ensure the Git pre-commit hooks work correctly
5. (optional) You can delete your `requirements.txt`. All dependencies should now be handled via the `pyproject.toml` file. Use `uv add` and `uv remove` to update your dependencies from the command line, or edit the `dependencies` section of `pyproject.toml` directly.
    
    `uv --help` has a complete list of the commands available with `uv`. 

6. Update the project entrypoint in `pyproject.toml`

    By now, your `pyproject.toml` should have a section that looks like 
    ```toml
    ...
    [project.scripts]
    <kebab-case-project-name> = "<snake_case_package_name>.main:main"
    ...
    ```

    Update this section so the `.main:main` portion reflects the name and main function of the entry file for your project. For example, Auto Quad Centering has this section as 
    ```toml
    ...
    [project.scripts]
    auto-quad-centering = "auto_quad_centering.autocenter:main"
    ...
    ```
    This reflects that the main file for the project is `auto_quad_centering/autocenter.py`, and the entrypoint for that file is a function called `main()`.

## `PyQt 5` to `PyQt 6`

While the bulk of upgrading from PyQt 5 to PyQt 6 is simply a matter of updating your import statements (i.e., `from PyQt5 import ...` becoming `from PyQt6 import ...`), there are a couple breaking changes to be aware of.

- PyQt 6 demands fully-qualified enums, e.g. `Qt.AlignCenter` must now be `Qt.AlignmentFlag.AlignCenter`
- Any uses of PyQt 5's `exec_()` function must now use the standard `exec()` function from Python 3
- Various classes have moved to different modules (e.g. `QAction` and `QShortcut` are now in `QtGui` rather than `QtWidgets`)
- Some methods/APIs have changed (e.g. `QMouseEvent` now uses `.position()` instead of `.x()` and `.y()`)

For a deeper breakdown and migration guide, see [this article](https://www.pythonguis.com/faq/pyqt5-vs-pyqt6/).

## Auto Quad Centering addons

The following are some enhancements made to the original Auto Quad Centering application so it plays a little nicer with the Xpra runtime.

1. Added scrolling behavior to all tabs

    The Xpra runtime only exposes a certain amount of screen real estate. The original Auto Quad Centering app went off the screen by quite a bit, when first tested in the Xpra deployment. To resolve this, a `QScrollArea` was added to each of the tab widgets in the `ui` directory.

2. Added a Kerberos login dialog

    Auto Quad Centering requires the user to have an active Kerberos ticket to make settings to the accelerator. The original application assumed such a ticket would already be available in the host runtime. With the move to the remote Xpra environment, this is no longer a valid assumption. 

    A small username/password dialog was added to `ui/dialogs.py` that would be activated when the user selects to generate a new ticket. This allows the migrated app to leverage the preexisting code to generate a ticket in Kerberos from `auth/kerberos_manager.py`. 

3. Updated the file loading process to reflect the remote runtime

    The original application expected to be able to load files from the user's system. With the deployment to a remote Xpra instance, this is no longer a straightforward process. Users must first upload files to the Xpra runtime, and only then can the application access those files. The same is true, but in reverse, for files generated by the app. It writes the file to the Xpra runtime, and users must initiate the process in Xpra to download a file from the remote filesystem. 

    To help clarify this, some modifications were made to the file upload section in `ui/setup_tab.py`. There is now descriptive text to call out the new process.