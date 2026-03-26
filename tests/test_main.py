from __future__ import annotations

import sys

from ap_python_starter_kit.main import build_parser


def test_build_parser_accepts_device_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--device", "G:SCTIME@P,15H"])
    assert args.device == "G:SCTIME@P,15H"
