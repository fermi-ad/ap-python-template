"""Host-side checks for Docker workspace startup; no Docker daemon or mount is needed."""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from scripts.rename_project import TARGET_FILES

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_HELPER = REPO_ROOT / "docker" / "create-workspace.sh"


@pytest.fixture
def workspace(tmp_path: Path) -> Generator[tuple[Path, Path, dict[str, str], Path]]:
    """Stub the mount and remove test storage after each test, including failures."""
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    helper = tmp_path / "create-workspace.sh"
    original = WORKSPACE_HELPER.read_text(encoding="utf-8")
    assert "STORAGE_ROOT=/mnt/storage\n" in original
    helper.write_text(
        original.replace(
            "STORAGE_ROOT=/mnt/storage", f"STORAGE_ROOT={shlex.quote(str(storage_root))}", 1
        ),
        encoding="utf-8",
    )

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    mountpoint = bin_dir / "mountpoint"
    mountpoint.write_text('#!/bin/sh\nexit "${MOUNTPOINT_STATUS:-0}"\n', encoding="utf-8")
    mountpoint.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "HOSTNAME": "test-host",
        "MOUNTPOINT_STATUS": "0",
    }
    try:
        yield helper, storage_root, env, bin_dir
    finally:
        shutil.rmtree(storage_root)


def source_helper(helper: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", 'source "$1" && printf "%s\\n" "$JOB_DIR"', "bash", str(helper)],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_unmounted_storage_fails(workspace: tuple[Path, Path, dict[str, str], Path]) -> None:
    helper, storage_root, env, _ = workspace
    result = source_helper(helper, {**env, "MOUNTPOINT_STATUS": "1"})

    assert result.returncode != 0
    assert "is not a mounted volume" in result.stderr
    assert not (storage_root / "ap-python-starter-kit").exists()


def test_unwritable_storage_fails(workspace: tuple[Path, Path, dict[str, str], Path]) -> None:
    helper, storage_root, env, bin_dir = workspace
    # Simulate a denied write rather than chmod: permission checks are unreliable as root.
    (bin_dir / "mktemp").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    (bin_dir / "mktemp").chmod(0o755)

    result = source_helper(helper, env)

    assert result.returncode != 0
    assert "is not writable" in result.stderr
    assert list((storage_root / "ap-python-starter-kit").iterdir()) == []


def test_job_directory_location_and_name(
    workspace: tuple[Path, Path, dict[str, str], Path],
) -> None:
    helper, storage_root, env, _ = workspace
    result = source_helper(helper, env)

    assert result.returncode == 0, result.stderr
    job_dir = Path(result.stdout.strip())
    assert job_dir.parent == storage_root / "ap-python-starter-kit"
    assert re.fullmatch(r"\d{8}_\d{6}_test-host", job_dir.name)
    # The shell has exited; the runtime helper must not remove completed jobs.
    assert job_dir.is_dir()


def test_concurrent_starts_get_distinct_directories(
    workspace: tuple[Path, Path, dict[str, str], Path],
) -> None:
    helper, storage_root, env, bin_dir = workspace
    # The helper distinguishes concurrent starts on different hosts. Starts
    # on the same host in the same second share a directory by design.
    date = bin_dir / "date"
    date.write_text('#!/bin/sh\nprintf "%s\\n" "20260102_030405_${HOSTNAME}"\n', encoding="utf-8")
    date.chmod(0o755)
    hosts = ["test-host-a", "test-host-b"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda host: source_helper(helper, {**env, "HOSTNAME": host}), hosts)
        )

    assert all(result.returncode == 0 for result in results), results
    job_dirs = [Path(result.stdout.strip()) for result in results]
    assert {path.name for path in job_dirs} == {f"20260102_030405_{host}" for host in hosts}
    assert all(path.parent == storage_root / "ap-python-starter-kit" for path in job_dirs)
    assert all(path.is_dir() for path in job_dirs)


def test_helper_refuses_direct_execution(
    workspace: tuple[Path, Path, dict[str, str], Path],
) -> None:
    helper, _, env, _ = workspace
    result = subprocess.run(
        ["bash", str(helper)], env=env, text=True, capture_output=True, check=False
    )

    assert result.returncode != 0
    assert "source" in result.stderr.lower()


@pytest.mark.parametrize("target", ["run", "run-gui"])
def test_make_dry_run_uses_absolute_mount_source(target: str) -> None:
    assert shutil.which("make"), "make is required to check Docker targets"
    result = subprocess.run(
        ["make", "-n", target], cwd=REPO_ROOT, text=True, capture_output=True, check=False
    )

    assert result.returncode == 0, result.stderr
    assert "docker run" in result.stdout
    assert f"--mount type=bind,source={REPO_ROOT / 'mount'},target=/mnt/storage" in result.stdout


def test_rename_script_docker_targets_exist() -> None:
    docker_targets = {name for name in TARGET_FILES if name.startswith("docker/")}
    assert {"docker/create-workspace.sh", "docker/start-cli.sh", "docker/start-gui.sh"} <= (
        docker_targets
    )
    assert all((REPO_ROOT / name).is_file() for name in docker_targets)
