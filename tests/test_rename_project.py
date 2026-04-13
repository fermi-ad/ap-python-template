from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.rename_project import (
    TEMPLATE_AUTHOR,
    TEMPLATE_CLI,
    TEMPLATE_DESC,
    TEMPLATE_MODULE,
    TEMPLATE_PROJECT,
    Replacements,
    _atomic_rename_context,
    _build_replacements,
    _parse_args,
    _rename_package_dir,
    _replace_in_text,
    _update_file,
    _validate_cli,
    _validate_identifier,
    _write_file_atomic,
    main,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repl() -> Replacements:
    return Replacements(
        project_name="my-project",
        module="my_project",
        description="A test project",
        author="Test Author",
        cli_name="my-project",
    )


@pytest.fixture()
def tmp_repo(tmp_path: Path, repl: Replacements) -> Path:
    """A minimal fake repo tree that mirrors what the script touches."""
    (tmp_path / "src" / TEMPLATE_MODULE).mkdir(parents=True)
    (tmp_path / "src" / TEMPLATE_MODULE / "__init__.py").write_text(
        f"# {TEMPLATE_PROJECT}\n", encoding="utf-8"
    )
    (tmp_path / "src" / TEMPLATE_MODULE / "main.py").write_text(
        f'"""Part of {TEMPLATE_PROJECT}."""\n', encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "{TEMPLATE_PROJECT}"\n'
        f'description = "{TEMPLATE_DESC}"\n'
        f'authors = [{{name = "{TEMPLATE_AUTHOR}"}}]\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        f"# {TEMPLATE_PROJECT}\n{TEMPLATE_DESC} by {TEMPLATE_AUTHOR}.\n",
        encoding="utf-8",
    )
    (tmp_path / ".git").mkdir()
    return tmp_path


# ---------------------------------------------------------------------------
# _validate_identifier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    ["my_module", "MyModule", "_private", "abc123", "A"],
)
def test_validate_identifier_valid(name: str) -> None:
    _validate_identifier(name)  # must not raise


@pytest.mark.parametrize(
    "name",
    ["", "123bad", "has-hyphen", "has space", "has.dot"],
)
def test_validate_identifier_invalid(name: str) -> None:
    with pytest.raises(SystemExit):
        _validate_identifier(name)


# ---------------------------------------------------------------------------
# _validate_cli
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    ["my-cli", "tool", "abc123", "a1-b2"],
)
def test_validate_cli_valid(name: str) -> None:
    _validate_cli(name)  # must not raise


@pytest.mark.parametrize(
    "name",
    ["", "MyCLI", "has_underscore", "-leading", "trailing-"],
)
def test_validate_cli_invalid(name: str) -> None:
    with pytest.raises(SystemExit):
        _validate_cli(name)


# ---------------------------------------------------------------------------
# _replace_in_text
# ---------------------------------------------------------------------------


def test_replace_in_text_all_placeholders(repl: Replacements) -> None:
    text = f"{TEMPLATE_PROJECT} {TEMPLATE_DESC} {TEMPLATE_AUTHOR} {TEMPLATE_MODULE} {TEMPLATE_CLI}"
    result = _replace_in_text(text, repl)
    assert repl.project_name in result
    assert repl.description in result
    assert repl.author in result
    assert repl.module in result
    assert repl.cli_name in result
    assert TEMPLATE_PROJECT not in result
    assert TEMPLATE_DESC not in result
    assert TEMPLATE_AUTHOR not in result
    # TEMPLATE_MODULE / TEMPLATE_CLI may overlap with repl values; check originals gone
    assert "ap_python_starter_kit" not in result
    assert "ap-python-starter-kit" not in result


def test_replace_in_text_no_placeholders(repl: Replacements) -> None:
    text = "nothing to replace here"
    assert _replace_in_text(text, repl) == text


def test_replace_in_text_partial(repl: Replacements) -> None:
    text = f"Hello {TEMPLATE_AUTHOR}!"
    result = _replace_in_text(text, repl)
    assert result == f"Hello {repl.author}!"


# ---------------------------------------------------------------------------
# _update_file
# ---------------------------------------------------------------------------


def test_update_file_modifies_content(tmp_path: Path, repl: Replacements) -> None:
    f = tmp_path / "sample.toml"
    f.write_text(f'name = "{TEMPLATE_PROJECT}"\n', encoding="utf-8")

    changed = _update_file(f, repl, check_only=False)

    assert changed is True
    assert f.read_text(encoding="utf-8") == f'name = "{repl.project_name}"\n'


def test_update_file_check_only_does_not_write(tmp_path: Path, repl: Replacements) -> None:
    f = tmp_path / "sample.toml"
    original = f'name = "{TEMPLATE_PROJECT}"\n'
    f.write_text(original, encoding="utf-8")

    changed = _update_file(f, repl, check_only=True)

    assert changed is True
    assert f.read_text(encoding="utf-8") == original  # untouched


def test_update_file_no_change(tmp_path: Path, repl: Replacements) -> None:
    f = tmp_path / "sample.toml"
    f.write_text('name = "unrelated"\n', encoding="utf-8")

    changed = _update_file(f, repl, check_only=False)

    assert changed is False


def test_update_file_skips_non_utf8(tmp_path: Path, repl: Replacements) -> None:
    f = tmp_path / "binary.bin"
    f.write_bytes(b"\xff\xfe binary blob")

    changed = _update_file(f, repl, check_only=False)

    assert changed is False


# ---------------------------------------------------------------------------
# _rename_package_dir
# ---------------------------------------------------------------------------


def test_rename_package_dir_renames(
    tmp_path: Path, repl: Replacements, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = tmp_path / "src"
    (src / TEMPLATE_MODULE).mkdir(parents=True)

    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_path)

    result = _rename_package_dir(repl, check_only=False)

    assert result is True
    assert not (src / TEMPLATE_MODULE).exists()
    assert (src / repl.module).exists()


def test_rename_package_dir_check_only(
    tmp_path: Path, repl: Replacements, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = tmp_path / "src"
    (src / TEMPLATE_MODULE).mkdir(parents=True)

    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_path)

    result = _rename_package_dir(repl, check_only=True)

    assert result is True
    # Source dir must still exist — nothing moved.
    assert (src / TEMPLATE_MODULE).exists()


def test_rename_package_dir_missing_src(
    tmp_path: Path, repl: Replacements, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_path)
    # src/TEMPLATE_MODULE does not exist
    result = _rename_package_dir(repl, check_only=False)
    assert result is False


def test_rename_package_dir_target_exists_raises(
    tmp_path: Path, repl: Replacements, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = tmp_path / "src"
    (src / TEMPLATE_MODULE).mkdir(parents=True)
    (src / repl.module).mkdir(parents=True)  # collision

    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_path)

    with pytest.raises(SystemExit):
        _rename_package_dir(repl, check_only=False)


# ---------------------------------------------------------------------------
# _parse_args
# ---------------------------------------------------------------------------


def test_parse_args_all_flags() -> None:
    ns = _parse_args(
        [
            "--project-name",
            "my-proj",
            "--module",
            "my_proj",
            "--author",
            "Alice",
            "--description",
            "My desc",
            "--cli-name",
            "my-proj",
        ]
    )
    assert ns.project_name == "my-proj"
    assert ns.module == "my_proj"
    assert ns.author == "Alice"
    assert ns.description == "My desc"
    assert ns.cli_name == "my-proj"
    assert ns.check is False


def test_parse_args_check_flag() -> None:
    ns = _parse_args(["--project-name", "x", "--module", "x", "--check"])
    assert ns.check is True


def test_parse_args_defaults() -> None:
    ns = _parse_args([])
    assert ns.project_name is None
    assert ns.module is None
    assert ns.description is None
    assert ns.author is None
    assert ns.cli_name is None


# ---------------------------------------------------------------------------
# _build_replacements (non-interactive)
# ---------------------------------------------------------------------------


def test_build_replacements_valid() -> None:
    ns = _parse_args(
        [
            "--project-name",
            "cool-tool",
            "--module",
            "cool_tool",
            "--author",
            "Dev",
            "--description",
            "A cool tool",
        ]
    )
    repl = _build_replacements(ns)
    assert repl.project_name == "cool-tool"
    assert repl.module == "cool_tool"
    assert repl.cli_name == "cool-tool"  # derived from module


def test_build_replacements_explicit_cli_name() -> None:
    ns = _parse_args(
        [
            "--project-name",
            "cool-tool",
            "--module",
            "cool_tool",
            "--author",
            "Dev",
            "--description",
            "A cool tool",
            "--cli-name",
            "ct",
        ]
    )
    repl = _build_replacements(ns)
    assert repl.cli_name == "ct"


def test_build_replacements_missing_project_name_exits() -> None:
    ns = _parse_args(["--module", "my_mod", "--author", "A", "--description", "D"])
    with pytest.raises(SystemExit):
        _build_replacements(ns)


def test_build_replacements_missing_module_exits() -> None:
    ns = _parse_args(["--project-name", "p", "--author", "A", "--description", "D"])
    with pytest.raises(SystemExit):
        _build_replacements(ns)


def test_build_replacements_invalid_module_exits() -> None:
    ns = _parse_args(
        [
            "--project-name",
            "p",
            "--module",
            "bad-module",
            "--author",
            "A",
            "--description",
            "D",
        ]
    )
    with pytest.raises(SystemExit):
        _build_replacements(ns)


def test_build_replacements_invalid_cli_name_exits() -> None:
    ns = _parse_args(
        [
            "--project-name",
            "p",
            "--module",
            "my_mod",
            "--author",
            "A",
            "--description",
            "D",
            "--cli-name",
            "Bad_CLI",
        ]
    )
    with pytest.raises(SystemExit):
        _build_replacements(ns)


# ---------------------------------------------------------------------------
# main() integration — check mode
# ---------------------------------------------------------------------------


def test_main_check_mode(tmp_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    monkeypatch.chdir(tmp_repo)

    rc = main(
        [
            "--project-name",
            "my-project",
            "--module",
            "my_project",
            "--author",
            "Test Author",
            "--description",
            "A test project",
            "--check",
        ]
    )

    assert rc == 0
    # Files must be untouched in check mode.
    content = (tmp_repo / "pyproject.toml").read_text(encoding="utf-8")
    assert TEMPLATE_PROJECT in content


def test_main_applies_changes(tmp_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    monkeypatch.chdir(tmp_repo)

    rc = main(
        [
            "--project-name",
            "my-project",
            "--module",
            "my_project",
            "--author",
            "Test Author",
            "--description",
            "A test project",
        ]
    )

    assert rc == 0
    content = (tmp_repo / "pyproject.toml").read_text(encoding="utf-8")
    assert "my-project" in content
    assert TEMPLATE_PROJECT not in content


def test_main_renames_package_dir(tmp_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    monkeypatch.chdir(tmp_repo)

    main(
        [
            "--project-name",
            "my-project",
            "--module",
            "my_project",
            "--author",
            "Test Author",
            "--description",
            "A test project",
        ]
    )

    assert not (tmp_repo / "src" / TEMPLATE_MODULE).exists()
    assert (tmp_repo / "src" / "my_project").exists()


def test_main_fails_outside_repo_root(
    tmp_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    # cwd is a *different* directory
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)

    with pytest.raises(SystemExit):
        main(
            [
                "--project-name",
                "my-project",
                "--module",
                "my_project",
                "--author",
                "Test Author",
                "--description",
                "A test project",
            ]
        )


# ---------------------------------------------------------------------------
# _write_file_atomic
# ---------------------------------------------------------------------------


def test_write_file_atomic_writes_content(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    target.write_text("old", encoding="utf-8")

    _write_file_atomic(target, "new content")

    assert target.read_text(encoding="utf-8") == "new content"


def test_write_file_atomic_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "brand_new.txt"
    assert not target.exists()

    _write_file_atomic(target, "hello")

    assert target.read_text(encoding="utf-8") == "hello"


def test_write_file_atomic_no_temp_file_left_on_success(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"

    _write_file_atomic(target, "content")

    # The only file in tmp_path should be the target itself — no orphaned temp.
    remaining = list(tmp_path.iterdir())
    assert remaining == [target]


def test_write_file_atomic_cleans_up_temp_on_replace_failure(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"

    with patch("os.replace", side_effect=OSError("disk full")):
        with pytest.raises(OSError, match="disk full"):
            _write_file_atomic(target, "content")

    # No orphaned .rename_tmp_* file should remain.
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".rename_tmp_")]
    assert leftovers == []


def test_write_file_atomic_original_unchanged_when_replace_fails(tmp_path: Path) -> None:
    target = tmp_path / "original.txt"
    target.write_text("original", encoding="utf-8")

    with patch("os.replace", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            _write_file_atomic(target, "new")

    assert target.read_text(encoding="utf-8") == "original"


# ---------------------------------------------------------------------------
# _atomic_rename_context — file-content rollback
# ---------------------------------------------------------------------------


def test_atomic_rename_context_no_rollback_on_success(tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("original", encoding="utf-8")
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"

    with _atomic_rename_context([f], old_pkg, new_pkg):
        f.write_text("modified", encoding="utf-8")

    # Changes must persist after a clean exit.
    assert f.read_text(encoding="utf-8") == "modified"


def test_atomic_rename_context_restores_files_on_exception(tmp_path: Path) -> None:
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("aaa", encoding="utf-8")
    f2.write_text("bbb", encoding="utf-8")
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"

    with pytest.raises(RuntimeError):
        with _atomic_rename_context([f1, f2], old_pkg, new_pkg):
            f1.write_text("aaa-modified", encoding="utf-8")
            f2.write_text("bbb-modified", encoding="utf-8")
            raise RuntimeError("simulated failure")

    assert f1.read_text(encoding="utf-8") == "aaa"
    assert f2.read_text(encoding="utf-8") == "bbb"


def test_atomic_rename_context_restores_files_on_keyboard_interrupt(tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("original", encoding="utf-8")
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"

    with pytest.raises(KeyboardInterrupt):
        with _atomic_rename_context([f], old_pkg, new_pkg):
            f.write_text("modified", encoding="utf-8")
            raise KeyboardInterrupt

    assert f.read_text(encoding="utf-8") == "original"


def test_atomic_rename_context_skips_nonexistent_files(tmp_path: Path) -> None:
    existing = tmp_path / "exists.txt"
    existing.write_text("keep", encoding="utf-8")
    missing = tmp_path / "does_not_exist.txt"
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"

    # Passing a non-existent file must not raise during snapshot or rollback.
    with pytest.raises(RuntimeError):
        with _atomic_rename_context([existing, missing], old_pkg, new_pkg):
            existing.write_text("changed", encoding="utf-8")
            raise RuntimeError("fail")

    assert existing.read_text(encoding="utf-8") == "keep"
    assert not missing.exists()


# ---------------------------------------------------------------------------
# _atomic_rename_context — directory rollback
# ---------------------------------------------------------------------------


def test_atomic_rename_context_reverses_dir_rename_on_exception(tmp_path: Path) -> None:
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"
    old_pkg.mkdir()
    (old_pkg / "mod.py").write_text("# code", encoding="utf-8")

    with pytest.raises(RuntimeError):
        with _atomic_rename_context([], old_pkg, new_pkg):
            # Simulate the package directory rename that the script performs.
            import shutil

            shutil.move(str(old_pkg), str(new_pkg))
            raise RuntimeError("failure after dir rename")

    # Directory must be restored to its original name.
    assert old_pkg.exists()
    assert not new_pkg.exists()
    assert (old_pkg / "mod.py").exists()


def test_atomic_rename_context_does_not_undo_dir_if_not_moved(tmp_path: Path) -> None:
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"
    old_pkg.mkdir()

    # Raise without ever moving the directory.
    with pytest.raises(RuntimeError):
        with _atomic_rename_context([], old_pkg, new_pkg):
            raise RuntimeError("early failure")

    # The original directory must still exist, new one must not.
    assert old_pkg.exists()
    assert not new_pkg.exists()


def test_atomic_rename_context_dir_and_files_both_rolled_back(tmp_path: Path) -> None:
    f = tmp_path / "config.txt"
    f.write_text("original config", encoding="utf-8")
    old_pkg = tmp_path / "old_pkg"
    new_pkg = tmp_path / "new_pkg"
    old_pkg.mkdir()

    import shutil

    with pytest.raises(RuntimeError):
        with _atomic_rename_context([f], old_pkg, new_pkg):
            f.write_text("new config", encoding="utf-8")
            shutil.move(str(old_pkg), str(new_pkg))
            raise RuntimeError("fail after both changes")

    assert f.read_text(encoding="utf-8") == "original config"
    assert old_pkg.exists()
    assert not new_pkg.exists()


# ---------------------------------------------------------------------------
# main() — end-to-end rollback via _atomic_rename_context
# ---------------------------------------------------------------------------


def _main_args(tmp_repo: Path) -> list[str]:
    return [
        "--project-name",
        "my-project",
        "--module",
        "my_project",
        "--author",
        "Test Author",
        "--description",
        "A test project",
    ]


def test_main_rolls_back_files_on_write_error(
    tmp_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    monkeypatch.chdir(tmp_repo)

    original_toml = (tmp_repo / "pyproject.toml").read_text(encoding="utf-8")
    original_readme = (tmp_repo / "README.md").read_text(encoding="utf-8")

    call_count = 0

    real_write_file_atomic = _write_file_atomic

    def failing_write(path, content):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise OSError("simulated disk full")
        real_write_file_atomic(path, content)

    monkeypatch.setattr("scripts.rename_project._write_file_atomic", failing_write)

    with pytest.raises(OSError, match="simulated disk full"):
        main(_main_args(tmp_repo))

    # All files must be back to their original content.
    assert (tmp_repo / "pyproject.toml").read_text(encoding="utf-8") == original_toml
    assert (tmp_repo / "README.md").read_text(encoding="utf-8") == original_readme


def test_main_rolls_back_dir_rename_on_later_error(
    tmp_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    monkeypatch.chdir(tmp_repo)

    # Patch _write_file_atomic to succeed for all file writes, but inject a
    # failure *after* the package directory has already been renamed.
    real_rename_package_dir = _rename_package_dir

    def rename_then_fail(repl, *, check_only):
        real_rename_package_dir(repl, check_only=check_only)
        raise OSError("failure after dir rename")

    monkeypatch.setattr("scripts.rename_project._rename_package_dir", rename_then_fail)

    with pytest.raises(OSError, match="failure after dir rename"):
        main(_main_args(tmp_repo))

    # Package directory must have been rolled back to its original name.
    assert (tmp_repo / "src" / TEMPLATE_MODULE).exists()
    assert not (tmp_repo / "src" / "my_project").exists()


def test_main_successful_run_leaves_no_rollback_artifacts(
    tmp_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.rename_project.REPO_ROOT", tmp_repo)
    monkeypatch.chdir(tmp_repo)

    rc = main(_main_args(tmp_repo))

    assert rc == 0
    # No orphaned temp files anywhere in the repo.
    orphans = list(tmp_repo.rglob(".rename_tmp_*"))
    assert orphans == []
    # Changes must be present (not accidentally rolled back).
    content = (tmp_repo / "pyproject.toml").read_text(encoding="utf-8")
    assert "my-project" in content
    assert TEMPLATE_PROJECT not in content
