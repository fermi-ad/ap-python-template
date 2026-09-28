# AP Python Template

This Python 3.12+ repository is a **template for your own application**. Create a new repository from it, rename the starter package, and **customize the sample code and tests for your program**. The sample query and CLI use ACSys, which is included as a normal dependency; the PyQt6 window (`--gui`) is optional. Your app can use different libraries and does not need a GUI.

**Normal delivery uses the provided GitHub workflows.** You choose a CLI or browser-served Xpra GUI image for *your* app; the workflows delegate checks and delivery to externally maintained reusable workflows. You do **not** need to build images locally, manage Harbor credentials, or operate shared Docker/Harbor infrastructure. Before delivery from a new repository, ask a fermi-ad admin to attach the GitHub App with Harbor secrets to it. **See [CI and deployment: step-by-step instructions and Harbor access contacts](docs/deployment.md#deploy-your-application-step-by-step)** for the request, names, and email addresses.

## Start here

1. On the [template's GitHub page](https://github.com/fermi-ad/ap-python-template), select **Use this template → Create a new repository**. Develop in the repository you create.
2. Open your repository in DevPod using the [workspace setup guide](docs/devpod.md#start-a-workspace). Its development image is maintained externally and supplies the common tools used to check your app. Keep the project's uv configuration working so the maintainer-run integration workflow can install and check it; you do not maintain the image or the workflow.
3. In the workspace terminal, check the example command without connecting to ACSys:

   ```bash
   uv run ap-python-starter-kit --help
   ```

   If you have already renamed the project, use the command listed under `pyproject.toml`'s `[project.scripts]` instead. To try the sample CLI, run that command without `--help`; it requests five ACSys readings and needs connectivity and any applicable authentication. The optional `--gui` mode also uses ACSys. A failed live query may simply mean you lack connectivity or credentials.
4. Follow the [Quickstart](docs/quickstart.md) to rename and sync your project, then [replace the example with your application](docs/application.md#replace-the-example-step-by-step). Use the renamed command shown in your project's `pyproject.toml`, revise the tests, and use the [deployment steps](docs/deployment.md) when your app is ready.

## Guides

- [Quickstart](docs/quickstart.md) — create, rename, sync, and check your project.
- [DevPod and dev containers](docs/devpod.md) — workspace setup and development desktop.
- [Make the template your application](docs/application.md) — customize the starter CLI, tests, and optional GUI.
- [Everyday development](docs/development.md) — dependencies, tests, code quality, and keeping the project compatible with integration.
- [Container usage](docs/container.md) — optional local CLI and Xpra image checks and advanced settings.
- [CI and deployment](docs/deployment.md) — maintained workflow path, image choice, and Harbor GitHub App contacts.
- [Fermilab Kerberos defaults](docs/kerberos.md) — control-system authentication versus configuration and runtime tickets.
- [Migrating an existing Python project](docs/migration.md) — adapt existing code and dependencies.
