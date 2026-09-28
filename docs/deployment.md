# CI and deployment

This template comes with a [CI/CD workflow](../.github/workflows/ci-cd.yaml). You customize **your application** and choose an image type; the provided workflows run checks and handle image delivery. The included ACSys CLI and PyQt window are examples, not the application you are expected to deploy. Start with [Quickstart](quickstart.md) if you have not yet created and renamed your repository.

## Deploy your application, step by step

1. **Create and rename your repository.** Create a new repository from the template and follow the [Quickstart renaming instructions](quickstart.md#3-rename-the-project). Commit the rename and verify the installed command. On pushes, the [rename check](../.github/workflows/ci-cd.yaml) blocks delivery from a generated repository if `pyproject.toml` still contains the template distribution name `ap-python-starter-kit`. The workflow also skips delivery on its **first run** (run number 1, normally triggered when the repository is created); a later eligible push to `main` is needed.
2. **Customize the demo for your application.** Update the entry point, sample query, application code, tests, and (if using a GUI) its startup command so the resulting image launches *your* program rather than the sample readings or window. Add dependencies your app needs. Follow [Make the template your application](application.md#make-the-template-your-application) and [Container usage](container.md) for the relevant code and image startup settings. Test your application locally before merging.
3. **Choose CLI or GUI before merging.** In the top-level `env` of the [CI/CD workflow](../.github/workflows/ci-cd.yaml), leave `IMAGE_VARIANT: gui-xpra` for a browser-served Xpra/PyQt desktop application, or change it to `IMAGE_VARIANT: cli` for a command-line or headless application. The template defaults to `gui-xpra`; choose `cli` if your replacement app has no GUI. See [Container usage](container.md#images-and-build-targets-optional-local-builds) for the local CLI and GUI image targets. The maintained deployment workflow receives this choice as `image-variant`.
4. **Request Harbor access before attempting to deploy.** In a **newly generated repository**, a GitHub **fermi-ad admin must add the appropriate GitHub App containing the AP Python Harbor secrets to your repository before images can be pushed to Harbor**. Email or Slack **this group of people** and explicitly ask them to add that GitHub App to *your new repository* before you merge or push changes intended for deployment to `main`:

   - Connor Howington (chowingt@fnal.gov)
   - Jacob Curley (jcurley@fnal.gov)
   - Beau Harrison (beau@fnal.gov)
   - Mariana Gonzalez (mariana@fnal.gov)

   Include your repository URL so the admin knows where to grant access. You do **not** need to create or commit Harbor secrets yourself; the [delivery job](../.github/workflows/ci-cd.yaml) passes inherited secrets to the maintained workflow.
5. **Open a pull request and review the checks.** Work on a branch, push your changes, and open a PR into `main`. A PR runs the provided integration workflow; review its results in your repository's **Actions** tab and fix any failures. PRs do **not** publish an image or deploy the app. You can also open PRs between non-`main` branches while working in stages without invoking delivery.
6. **Merge to `main` when ready.** Merging a PR into `main` creates a push to `main`. A direct push to `main` has the same workflow trigger. The workflow runs integration and the rename check, then, when those jobs succeed and it is not workflow run number 1, calls the maintained deployment workflow to build and deliver the chosen image to Harbor (`adregistry.fnal.gov`). Each later qualifying push to `main` can repeat delivery, so keep unfinished work on branches.
7. **Check the outcome.** In your new repository on GitHub, open **Actions → Continuous Integration & Continuous Delivery** and inspect the run for the `main` push, especially the `delivery` job. After successful delivery, check the [AP Python Launcher](https://ad-apps-internal.fnal.gov/ap-python/) for your application. If the job fails or the app is missing from the launcher, share the run link with one of the admins above rather than adding secrets to your code.

## What this repository configures

The [local CI/CD workflow](../.github/workflows/ci-cd.yaml) triggers on PRs (to any branch) and pushes to `main`. Its `setup` job forwards the following top-level settings; you usually only need to select an image variant:

| Setting | Template value | What it controls |
| --- | --- | --- |
| `IMAGE_VARIANT` | `gui-xpra` | Sent as `image-variant` to the maintained deployment workflow; choose `cli` instead for no GUI support. |
| `SYSTEM_PACKAGES` | `libkrb5-dev` | Space-separated packages installed on the Actions host for integration, passed as `static-dependencies`; not the same as packages installed in the [Dockerfile](../Dockerfile). |
| `COV_EXCLUDE` | `tests/\|docs/\|examples/` | Pipe-separated paths passed as `coverage-exclude` to integration. |

On PRs, `integration` calls the maintained [`ap-python-integration.yaml`](https://github.com/fermi-ad/.github/blob/main/.github/workflows/ap-python-integration.yaml); delivery and the rename check do not run. On pushes to `main`, `integration` runs, `check-renamed` checks the original distribution name in [`pyproject.toml`](../pyproject.toml), and eligible `delivery` calls the maintained [`ap-python-deployment.yaml`](https://github.com/fermi-ad/.github/blob/main/.github/workflows/ap-python-deployment.yaml) with inherited secrets. The first-run guard is based on workflow **run number**, not a fresh-repository check.

This repository shows the triggers, prerequisites, forwarded options, and which reusable workflows are called; the maintained workflows outside this repository perform the actual integration checks and image delivery. The exact test reports, image tags, and any automatic launcher registration depend on those maintained workflows and the Actions run. The separate [template-usage notification workflow](../.github/workflows/notify-template-usage.yml) is not the application delivery job.
