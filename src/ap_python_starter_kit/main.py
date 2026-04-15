from __future__ import annotations

import argparse

from .acsys_client import read_device

DEFAULT_DEVICE = "G:SCTIME@P,15H"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ap-python-starter-kit",
        description="Application entry point for ap-python-starter-kit.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the GUI instead of the default CLI demo.",
    )
    parser.add_argument(
        "--device",
        default=DEFAULT_DEVICE,
        help="ACSys device/request string to query (demo default: SCTIME at 15Hz).",
    )
    return parser


def run_cli(device: str) -> int:
    for reading in read_device(device):
        print(reading)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.gui:
        from .gui import run_gui

        return run_gui(args.device)

    return run_cli(args.device)


if __name__ == "__main__":
    raise SystemExit(main())
