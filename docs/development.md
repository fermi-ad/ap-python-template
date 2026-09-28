# Everyday development

Use this guide after the [Quickstart](quickstart.md) has helped you create, rename, and check your repository. Build **your own application** by customizing the sample ACSys/PyQt program as described in the [application guide](application.md#replace-the-example-step-by-step). Run the commands below in a terminal at the root of **your repository**. The [DevPod workspace](devpod.md) is the supported path to a common set of tools and a setup like the one used for integration; a manually prepared host environment needs Python 3.12+ and `uv` and must keep the same project checks working.

## A normal edit-and-check cycle

1. Create a working branch in your repository before making a change: `git switch -c my-change`. Edit the code under your renamed `src/` package and add or change tests in [`tests/`](../tests/). If you have not renamed yet, see the [Quickstart rename step](quickstart.md#3-rename-the-project).
2. Sync if you changed dependencies or the installed command, as described [below](#dependencies-and-environment). Run **your** app in the terminal to see what it does. The initial template command is `uv run ap-python-starter-kit --help`; after renaming, look up the command under `[project.scripts]` in [`pyproject.toml`](../pyproject.toml) and use that instead. The example's normal run queries ACSys and may fail without site access; `--help` does not query it. Once you replace the example, test the actual behavior of your own program.
3. Run tests and formatting/lint checks [below](#tests-and-code-quality). Fix failures and rerun them. Add tests for your replacement program alongside or in place of the sample tests.
4. Review `git status` and `git diff` to check what changed; stage the files you intend to commit with `git add`, then commit with `git commit -m "Describe my change"`. Pre-commit hooks may fix staged Python files automatically; review, restage, and commit again if needed. Push your branch and open a pull request when ready. Follow [CI and deployment](deployment.md) for how the provided workflows check PRs, request Harbor access, and deliver eligible changes to `main`. A PR alone does not deploy your app.

## Dependencies and environment

[`pyproject.toml`](../pyproject.toml) lists Python requirements, runtime dependencies, optional extras, the installed command, and the `dev` tools (pytest, Ruff, pre-commit, pytest-cov). [`uv.lock`](../uv.lock) records resolved dependency versions. The template includes `acsys` and `acsys[settings]` as runtime dependencies from the declared Git source; the optional `gui-pyqt` extra installs PyQt. Changing the demo query, CLI, or GUI does not itself require a dependency change. See the [application steps](application.md#replace-the-example-step-by-step) to adapt the starter code and add dependencies your app needs.

The [DevPod configuration](../.devcontainer/devcontainer.json) runs `uv sync --dev --all-extras` and installs pre-commit hooks when the workspace starts. To refresh your working environment after editing dependencies or renaming, run:

```bash
uv sync --dev
```

If your app keeps the optional sample PyQt extra and you need it outside DevPod's all-extras setup, run `uv sync --dev --extra gui-pyqt` instead. Syncing the template requires access to the ACSys Git source declared in [`pyproject.toml`](../pyproject.toml), even when you change the demo code. Review and commit changes to both [`pyproject.toml`](../pyproject.toml) and [`uv.lock`](../uv.lock) after dependency changes. The repository's [`make uv-sync`](../Makefile) is a shortcut for plain `uv sync`; it does not select the GUI extra.

## Stay compatible with integration

The [provided CI workflow](../.github/workflows/ci-cd.yaml) calls a reusable integration workflow maintained outside this repository. That workflow expects to invoke uv commands against **your repository**. Keep a valid [`pyproject.toml`](../pyproject.toml) with the correct package, installed command, and declared dependencies, and commit the corresponding [`uv.lock`](../uv.lock) after dependency changes. Keep your source package installable and the tests in [`tests/`](../tests/) runnable with `uv run pytest`; use the checks below before opening a PR. Do not replace the uv project with an environment that only works on your laptop or remove its configuration because DevPod already supplies tools.

DevPod runs `uv sync --dev --all-extras` at startup, so if you change dependencies or extras, make sure that sync still succeeds. A successful local check does not guarantee the externally maintained workflow will pass; read the actual PR results in GitHub Actions and fix any failures. You do not need to edit or maintain the reusable workflow or the common development image.

## Tests and code quality

[`tests/test_main.py`](../tests/test_main.py) currently mocks ACSys readings and checks the template's arguments and CLI/GUI dispatch; [`tests/test_rename_project.py`](../tests/test_rename_project.py) checks renaming. Replace or expand the application tests to cover what **your** program should do. For behavior that uses an external service, you can test with a fake or mock first; the supplied tests do not contact ACSys.

```bash
uv run pytest
uv run ruff format --check .
uv run ruff check .
```

`pytest` runs tests; the format check and Ruff lint command report issues without changing files. To apply formatting, use `uv run ruff format .`; to request automatic lint fixes, use `uv run ruff check --fix .`, then review the changes. The corresponding repository targets are [`make test`](../Makefile), [`make format`](../Makefile), and [`make lint`](../Makefile); `make format` **writes** formatting changes.

The [pre-commit configuration](../.pre-commit-config.yaml) runs Ruff fixes and formatting on staged Python files when you commit. DevPod installs the hooks at startup; in another environment, run `uv run pre-commit install` once. To check all tracked files yourself, run `uv run pre-commit run --all-files`. Hooks can edit code, so check `git status`, restage changes, and rerun your tests before committing if that happens.

Use the explicit `uv run` or [`Makefile`](../Makefile) commands here rather than assuming a bare `test`, `lint`, or `run` command exists. For local deployment-image tests (a separate step from editing in DevPod), see [Container usage](container.md). The maintained delivery process is in [CI and deployment](deployment.md), including the Harbor credential admin request and contacts.
