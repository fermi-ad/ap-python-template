# ap-python-starter-kit

Python starter kit

A Python-first project template with one installable application package that provides a default CLI experience and an optional PyQt GUI activated through the same launcher, plus built-in Kerberos-aware container support for `FNAL.GOV` environments.

## Quickstart

1. **Do not** clone this repo! Instead, click "**Use this template**" at the top right of its GitHub page, then click "**Create a new repository**" and complete the form to create a new repo using this template.

2. [Set up your development environment](docs/devpod.md)

3. Rename the template to make it your own project:

   ```bash
   python3 scripts/rename_project.py
   ```

4. Code away!

Detailed onboarding is in [`docs/quickstart.md`](docs/quickstart.md).

## DevPod / Dev Container

This repo includes a Dev Container descriptor file at [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json). It is recommended to [install DevPod](https://devpod.sh/docs/getting-started/install) so that you can take advantage of the prebuilt development environment it provides.

Read more about DevPod [here](https://devpod.sh/docs/what-is-devpod)

Full instructions: [`docs/devpod.md`](docs/devpod.md).

## Application Modes

The template ships as one installable package under [`src/ap_python_starter_kit/`](src/ap_python_starter_kit/) with a single console script, [`ap-python-starter-kit`](pyproject.toml:21).

- [`ap_python_starter_kit.main`](src/ap_python_starter_kit/main.py) provides the top-level launcher.
- [`ap_python_starter_kit.gui`](src/ap_python_starter_kit/gui.py) provides the optional PyQt GUI implementation invoked by the launcher when `--gui` is supplied.
- [`ap_python_starter_kit.acsys_client`](src/ap_python_starter_kit/acsys_client.py) contains shared ACSys helpers used by both CLI and GUI paths.

Run the default CLI behavior:

```bash
uv run ap-python-starter-kit
```

Run the CLI with an explicit device/request string:

```bash
uv run ap-python-starter-kit --device "G:SCTIME@P,15H"
```

Run the GUI through the same launcher after installing the optional GUI extra:

```bash
uv sync --extra gui-pyqt
uv run ap-python-starter-kit --gui --device "G:SCTIME@P,15H"
```

## Deployment Container

Once your app is ready to deploy, the template provides a multi-stage Docker setup with:

- a default CLI runtime image for launching [`ap_python_starter_kit.main`](src/ap_python_starter_kit/main.py)
- an Xpra-based GUI runtime image for serving the integrated PyQt app in a browser

Read more in [`docs/container.md`](docs/container.md).

The Dockerfile also contains additional internal build stages used to assemble those runtime images.

## FNAL Kerberos Defaults

This template assumes new applications will run in the `FNAL.GOV` Kerberos environment.

- The repository includes [`.kerberos/krb5.conf`](.kerberos/krb5.conf)
- The container copies that file into `/etc/krb5.conf` during build
- Kerberos runtime packages are installed by default in the base image

If a project needs a different Kerberos configuration, replace [`.kerberos/krb5.conf`](.kerberos/krb5.conf) or override `/etc/krb5.conf` in the deployment environment.

## Optional GUI Support

PyQt remains optional and is only installed when requested:

```bash
uv sync --extra gui-pyqt
```

The included GUI is intentionally minimal and demonstrative so downstream projects can replace it with their own application-specific interface while keeping the same package layout.

## CI/CD

This template comes preconfigured for Continuous Integration and Continuous Delivery. When opening a pull request, your code will automatically be checked for formatting errors and common coding pitfalls, verified to compile, and all tests will be run. A report of how much of the executable code is covered by the tests will be added to your pull request as well. The [`ci-cd.yaml`](.github/workflows/ci-cd.yaml) file contains values in the `env` section that you can configure to adjust the automated build slightly.

Upon merging changes in to the `main` branch, your application will be built and packaged into a container. The default deployment behavior is controlled by [`IMAGE_VARIANT`](.github/workflows/ci-cd.yaml:20) in [`.github/workflows/ci-cd.yaml`](.github/workflows/ci-cd.yaml). It is currently set to `gui-xpra`, which builds the browser-served GUI variant by default. If your application is intended as a headless service, or works better from the command line, change [`IMAGE_VARIANT`](.github/workflows/ci-cd.yaml:20) to `cli`.

Once the container is built, it will be pushed into Harbor at `adregistry.fnal.gov` so it can be deployed into the Kubernetes environment. Before images can be pushed to Harbor, a GitHub fermi-ad admin must add the appropriate GitHub App containing the AP Python Harbor secrets to your repository. Reach out to beau@fnal.gov or mariana@fnal.gov for this before you attempt to deploy.

To reiterate: **deployment will happen on every commit to the `main` branch.** If you do not want a new container being generated every time you make a change (e.g., if you're in the middle of implementing a new feature and want to do it in stages), the recommended approach is to create a "feature" branch that tracks your pending updates. Starting on `main`, the process would look something like this:

1. Run `git checkout -b <name of feature branch>` -> Creates a new branch based on `main` and checks out that branch
2. Run `git checkout -b <name of stage>` -> Creates a new branch based on your feature branch and checks out that branch
3. Make your series of edits
4. Run `git commit` and `git push` -> pushes changes to your "stage" branch
5. Open a pull request from your "stage" branch into your "feature" branch
   - This will run the automated integration workflow, to check for problems in the code. It will _not_ build or deploy a container to Harbor.
6. Merge into your feature branch
7. Repeat steps 2-6 until your feature branch has all the changes you want to make and is ready to be deployed
8. Open a pull request from your feature branch into `main` -> Runs the automated integration workflow one last time on all your changes together
9. Merge into `main` -> Constructs the new container for your application and delivers it to Harbor
   - Congrats! Your changes are now ready to be deployed.
