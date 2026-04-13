from __future__ import annotations

from pathlib import Path

import pytest

from scripts.rename_project import (
    TEMPLATE_AUTHOR,
    TEMPLATE_CLI,
    TEMPLATE_DESC,
    TEMPLATE_MODULE,
    TEMPLATE_PROJECT,
    Replacements,
    _build_replacements,
    _parse_args,
    _rename_package_dir,
    _replace_in_text,
    _update_file,
    _validate_cli,
    _validate_identifier,
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
