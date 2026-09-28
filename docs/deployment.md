# CI and deployment

This template comes with a [CI/CD workflow](../.github/workflows/ci-cd.yaml). Customize the included ACSys CLI and PyQt window examples for **your application** and choose an image type; the provided workflows call externally maintained integration and delivery workflows. Keep your [uv project installable and checkable](development.md#stay-compatible-with-integration); use the common [DevPod workspace](devpod.md) to check it before opening a PR. You do not have to build images locally or manage the workflows or Harbor credentials. Start with [Quickstart](quickstart.md) if you have not yet created and renamed your repository.

## Deploy your application, step by step

1. **Create and rename your repository.** Follow the [Quickstart renaming instructions](quickstart.md#3-rename-the-project), commit the rename, and verify the installed command. Delivery will not proceed from a generated repository that still has the template name; the [workflow details](#advanced-workflow-settings-and-behavior) explain the check and first-run guard.
2. **Customize the demo for your application.** Update the example code and tests, add the dependencies your app needs, and check that the installed command runs your app. If you move or replace the entry point rather than editing its contents, update the appropriate image startup command too. Follow [Make the template your application](application.md#replace-the-example-step-by-step) and [Everyday development](development.md) to run your app and tests before merging; [Container usage](container.md) covers optional local image checks.
3. **Choose CLI or GUI before merging.** In the top-level settings of the [CI/CD workflow](../.github/workflows/ci-cd.yaml), leave `IMAGE_VARIANT: gui-xpra` for a browser-served desktop application, or change it to `IMAGE_VARIANT: cli` for a command-line or headless application. The template defaults to `gui-xpra`; choose `cli` if your app has no GUI. Local container builds are [optional](container.md).
4. **Request Harbor access before attempting to deploy.** In a **newly generated repository**, a GitHub **fermi-ad admin must add the appropriate GitHub App containing the AP Python Harbor secrets to your repository before images can be pushed to Harbor**. Email or Slack **this group of people** and explicitly ask them to add that GitHub App to *your new repository* before you merge or push changes intended for deployment to `main`:

   - Connor Howington (chowingt@fnal.gov)
   - Jacob Curley (jcurley@fnal.gov)
   - Beau Harrison (beau@fnal.gov)
   - Mariana Gonzalez (mariana@fnal.gov)

   Include your repository URL so the admin knows where to grant access. You do **not** need to create or commit Harbor secrets yourself; the [delivery job](../.github/workflows/ci-cd.yaml) passes inherited secrets to the maintained workflow.
5. **Open a pull request and review the checks.** Work on a branch, run the [local uv-based checks](development.md#tests-and-code-quality), push your changes, and open a PR into `main`. A PR calls the maintained integration workflow; review its results in your repository's **Actions** tab and fix any failures. PRs do **not** publish an image or deploy the app. You can also open PRs between non-`main` branches while working in stages without invoking delivery.
6. **Merge to `main` when ready.** A merge or direct push to `main` runs integration and the rename check. When the checks succeed and the push is eligible for delivery, the maintained deployment workflow builds and delivers the chosen image to Harbor (`adregistry.fnal.gov`). Later qualifying pushes to `main` can repeat delivery, so keep unfinished work on branches. See [workflow guards](#advanced-workflow-settings-and-behavior) if delivery is skipped.
7. **Check the outcome.** In your new repository on GitHub, open **Actions → Continuous Integration & Continuous Delivery** and inspect the run for the `main` push, especially the `delivery` job. After successful delivery, check the [AP Python Launcher](https://ad-apps-internal.fnal.gov/ap-python/) for your application. If the job fails or the app is missing from the launcher, share the run link with one of the admins above rather than adding secrets to your code.

## Advanced: workflow settings and behavior

The steps above cover normal delivery. The settings and guards below are for changing integration options or troubleshooting an Actions run; the reusable workflows and base images are maintained outside your repository.

The [local CI/CD workflow](../.github/workflows/ci-cd.yaml) triggers on PRs (to any branch) and pushes to `main`. Its `setup` job forwards the following top-level settings; you usually only need to select an image variant:

| Setting | Template value | What it controls |
| --- | --- | --- |
| `IMAGE_VARIANT` | `gui-xpra` | Sent as `image-variant` to the maintained deployment workflow; choose `cli` instead for no GUI support. |
| `SYSTEM_PACKAGES` | `libkrb5-dev` | Space-separated packages installed on the Actions host for integration, passed as `static-dependencies`; not the same as packages installed in the [Dockerfile](../Dockerfile). |
| `COV_EXCLUDE` | `tests/\|docs/\|examples/` | Pipe-separated paths passed as `coverage-exclude` to integration. |

On PRs, `integration` calls the maintained [`ap-python-integration.yaml`](https://github.com/fermi-ad/.github/blob/main/.github/workflows/ap-python-integration.yaml); delivery and the rename check do not run. On pushes to `main`, `integration` runs, `check-renamed` checks the original distribution name `ap-python-starter-kit` in [`pyproject.toml`](../pyproject.toml) for generated repositories, and eligible `delivery` calls the maintained [`ap-python-deployment.yaml`](https://github.com/fermi-ad/.github/blob/main/.github/workflows/ap-python-deployment.yaml) with inherited secrets. Delivery skips workflow run number 1 (normally triggered on repository creation); the guard is based on **run number**, not a fresh-repository check.

This repository shows the triggers, prerequisites, forwarded options, and which reusable workflows are called; the maintained workflows outside this repository perform the actual integration checks and image delivery. The exact test reports, image tags, and any automatic launcher registration depend on those maintained workflows and the Actions run. The [template-usage notification workflow](../.github/workflows/notify-template-usage.yml) reports template usage; application delivery runs through the CI/CD workflow.
