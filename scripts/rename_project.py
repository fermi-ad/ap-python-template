#!/usr/bin/env python3
"""Rename this template to a real project.

This script replaces the template placeholders:
- ap-python-starter-kit
- Python starter kit
- Template Maintainers
- ap_python_starter_kit (python package directory + import paths)
- ap-python-starter-kit (CLI script name)

It updates common project files and renames the src package directory.

Usage (interactive, recommended):
  python3 scripts/rename_project.py

Usage (non-interactive):
  python3 scripts/rename_project.py --project-name my-proj --module my_proj \
    --author "Your Name" --description "My project" [--cli-name my-proj]

Notes:
- Run from the repository root.
- This edits files in-place. Commit or stash before running.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASHRC_PATH = Path.home() / ".bashrc"


@dataclass(frozen=True)
class Replacements:
    project_name: str
    module: str
    description: str
    author: str
    cli_name: str


# These are the *starting values* in this repository. End-users run this script to
# rename them to their real project values.
TEMPLATE_PROJECT = "ap-python-starter-kit"
TEMPLATE_DESC = "Python starter kit"
TEMPLATE_AUTHOR = "Template Maintainers"
TEMPLATE_MODULE = "ap_python_starter_kit"
TEMPLATE_CLI = "ap-python-starter-kit"


TARGET_FILES = [
    ".devfile.yaml",
    "pyproject.toml",
    "Dockerfile",
    "docker/start.sh",
    "Makefile",
    "README.md",
    "docs/container.md",
    "docs/devpod.md",
    "docs/quickstart.md",
    "tests/test_main.py",
]


def _die(msg: str, code: int = 2) -> None:
    print(f"[rename_project] error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _validate_identifier(module: str) -> None:
    # Python package/module name must be a valid identifier and lowercase by convention.
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", module):
        _die(f"module must be a valid Python identifier (got: {module!r})")


def _validate_cli(cli_name: str) -> None:
    # Console script names are typically kebab-case.
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", cli_name):
        _die(f"cli-name must be kebab-case (got: {cli_name!r})")


def _prompt(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default


def _replace_in_text(text: str, repl: Replacements) -> str:
    return (
        text.replace(TEMPLATE_PROJECT, repl.project_name)
        .replace(TEMPLATE_DESC, repl.description)
        .replace(TEMPLATE_AUTHOR, repl.author)
        .replace(TEMPLATE_MODULE, repl.module)
        .replace(TEMPLATE_CLI, repl.cli_name)
    )


def _update_file(path: Path, repl: Replacements, *, check_only: bool) -> bool:
    # Most of the repo is UTF-8 text, but some environments may introduce files
    # with a different encoding. We treat those as non-targets instead of
    # crashing the rename.
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    updated = _replace_in_text(original, repl)
    if updated == original:
        return False
    if not check_only:
        path.write_text(updated, encoding="utf-8")
    return True


def _rename_package_dir(repl: Replacements, *, check_only: bool) -> bool:
    src_dir = REPO_ROOT / "src"
    old_dir = src_dir / TEMPLATE_MODULE
    new_dir = src_dir / repl.module

    if not old_dir.exists():
        return False

    if new_dir.exists():
        _die(f"target package dir already exists: {new_dir}")

    if check_only:
        return True

    shutil.move(str(old_dir), str(new_dir))
    return True


def _gather_files() -> list[Path]:
    files = [REPO_ROOT / p for p in TARGET_FILES]
    files.append(BASHRC_PATH)

    # Also update any files under src/<template_module>/ and docs/optional-pyqt.md if present.
    src_template = REPO_ROOT / "src" / TEMPLATE_MODULE
    if src_template.exists():
        files.extend([p for p in src_template.rglob("*") if p.is_file()])

    optional_pyqt = REPO_ROOT / "docs" / "optional-pyqt.md"
    if optional_pyqt.exists():
        files.append(optional_pyqt)

    # De-dupe while preserving order.
    seen: set[Path] = set()
    out: list[Path] = []
    for p in files:
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        out.append(p)
    return out


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-name", help="Distribution/repo name (e.g. my-project)")
    p.add_argument("--module", help="Python package name (e.g. my_project)")
    p.add_argument("--description", default=None, help="Project description")
    p.add_argument("--author", default=None, help="Author name")
    p.add_argument(
        "--cli-name",
        default=None,
        help="Console script name (kebab-case). Default: <module> with underscores -> hyphens",
    )
    p.add_argument("--check", action="store_true", help="Dry-run; print what would change")
    return p.parse_args(argv)


def _build_replacements(ns: argparse.Namespace) -> Replacements:
    any_provided = any([ns.project_name, ns.module, ns.description, ns.author, ns.cli_name])
    interactive = (not any_provided) and sys.stdin.isatty()

    project_name = ns.project_name
    module = ns.module

    description = ns.description
    author = ns.author
    cli_name = ns.cli_name

    if interactive:
        print("[rename_project] interactive mode")
        project_name = project_name or _prompt("Project/repo name (kebab-case)")
        module = module or _prompt("Python package name (snake_case)")
        author = author or _prompt("Author")
        description = description or _prompt("Description")

    if not project_name:
        _die("missing --project-name")
    if not module:
        _die("missing --module")
    if not author:
        _die("missing --author")
    if not description:
        _die("missing --description")

    _validate_identifier(module)

    default_cli = module.replace("_", "-")

    if interactive:
        cli_name = cli_name or _prompt("CLI command name", default_cli)

    description = "" if description is None else description
    author = "" if author is None else author
    cli_name = cli_name or default_cli

    _validate_cli(cli_name)

    return Replacements(
        project_name=project_name,
        module=module,
        description=description,
        author=author,
        cli_name=cli_name,
    )


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(sys.argv[1:] if argv is None else argv)
    repl = _build_replacements(ns)

    if Path.cwd().resolve() != REPO_ROOT:
        _die(f"run from repo root: {REPO_ROOT}")

    files = _gather_files()

    changed_files: list[Path] = []
    for f in files:
        if not f.exists() or f.is_dir():
            continue
        if _update_file(f, repl, check_only=ns.check):
            changed_files.append(f)

    renamed_pkg = _rename_package_dir(repl, check_only=ns.check)

    if ns.check:
        for f in changed_files:
            rel = BASHRC_PATH if f == BASHRC_PATH else f.relative_to(REPO_ROOT)
            print(f"[rename_project] would update: {rel}")
        if renamed_pkg:
            print(f"[rename_project] would rename: src/{TEMPLATE_MODULE}/ -> src/{repl.module}/")
        if not changed_files and not renamed_pkg:
            print("[rename_project] no changes detected")
        return 0

    for f in changed_files:
        if f == BASHRC_PATH:
            print(
                f"[rename_project] updated: {f} (run 'source ~/.bashrc' to apply CLI alias changes)"
            )
        else:
            rel = f.relative_to(REPO_ROOT)
            print(f"[rename_project] updated: {rel}")
    if renamed_pkg:
        print(f"[rename_project] renamed: src/{TEMPLATE_MODULE}/ -> src/{repl.module}/")

    if (REPO_ROOT / ".git").exists():
        print("[rename_project] done. Review changes and commit.")
    else:
        print("[rename_project] done.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
