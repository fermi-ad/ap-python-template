from __future__ import annotations

import sys

from __template_module__.main import main


def test_main_default(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["__template-module__"])
    code = main()
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert "Hello, world from __template_project_name__!" == out


def test_main_custom_name(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["__template-module__", "--name", "Template"])
    code = main()
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert "Hello, Template from __template_project_name__!" == out
