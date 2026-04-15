from __future__ import annotations

from collections.abc import Sequence
from types import ModuleType, SimpleNamespace

import pytest

from ap_python_starter_kit import gui, main


def test_build_parser_accepts_device_flag() -> None:
    parser = main.build_parser()
    args = parser.parse_args(["--device", "G:SCTIME@P,15H"])
    assert args.device == "G:SCTIME@P,15H"
    assert args.gui is False


def test_build_parser_accepts_gui_flag() -> None:
    parser = main.build_parser()
    args = parser.parse_args(["--gui", "--device", "Z:TEST@I"])
    assert args.gui is True
    assert args.device == "Z:TEST@I"


def test_run_cli_prints_readings(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(main, "read_device", lambda device: [f"{device}-1", f"{device}-2"])

    result = main.run_cli("Z:TEST@I")

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.splitlines() == ["Z:TEST@I-1", "Z:TEST@I-2"]


def test_main_dispatches_to_gui(monkeypatch: pytest.MonkeyPatch) -> None:
    parser = SimpleNamespace(parse_args=lambda: SimpleNamespace(gui=True, device="G:GUI@I"))
    monkeypatch.setattr(main, "build_parser", lambda: parser)

    calls: list[str] = []

    def fake_run_gui(device: str) -> int:
        calls.append(device)
        return 17

    monkeypatch.setattr("ap_python_starter_kit.gui.run_gui", fake_run_gui)

    assert main.main() == 17
    assert calls == ["G:GUI@I"]


def test_main_dispatches_to_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    parser = SimpleNamespace(parse_args=lambda: SimpleNamespace(gui=False, device="G:CLI@I"))
    monkeypatch.setattr(main, "build_parser", lambda: parser)
    monkeypatch.setattr(main, "run_cli", lambda device: 23 if device == "G:CLI@I" else 1)

    assert main.main() == 23


def test_gui_main_raises_helpful_error_when_pyqt_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = __import__

    def fake_import(
        name: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        if name.startswith("PyQt6"):
            raise ImportError("missing PyQt6")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(RuntimeError, match="uv sync --extra gui-pyqt"):
        gui.run_gui(main.DEFAULT_DEVICE)
