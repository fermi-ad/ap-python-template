from __future__ import annotations

import argparse
import asyncio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="__template-module__",
        description="CLI entry point for __template_project_name__.",
    )
    parser.add_argument(
        "--device",
        default="G:SCTIME@P,15H",
        help="ACSys device/request string to query (demo default: SCTIME at 15Hz).",
    )
    return parser


async def _acsys_demo(device: str) -> int:
    # Import lazily so the template CLI still works in environments
    # where ACSys isn't reachable.
    import acsys
    import acsys.dpm

    async def run(con) -> None:
        async with acsys.dpm.DPMContext(con) as dpm:
            await dpm.add_entry(0, device)
            await dpm.start()

            # Print a few readings and exit.
            count = 0
            async for evt in dpm:
                if evt.is_reading_for(0):
                    print(evt)
                    count += 1
                    if count >= 5:
                        return

    # `acsys.run_client` manages the asyncio loop internally, but we keep
    # this async wrapper to make unit-testing and CLI control cleaner.
    acsys.run_client(run)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    return asyncio.run(_acsys_demo(args.device))


if __name__ == "__main__":
    raise SystemExit(main())
