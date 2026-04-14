from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class ACSysEvent(Protocol):
    def is_reading_for(self, index: int) -> bool: ...

    def __str__(self) -> str: ...


class ACSysConnection(Protocol):
    pass


def _run_with_dpm(device: str, on_event: Callable[[ACSysEvent], bool]) -> None:
    import acsys
    import acsys.dpm

    async def run(con: ACSysConnection) -> None:
        async with acsys.dpm.DPMContext(con) as dpm:
            await dpm.add_entry(0, device)
            await dpm.start()

            async for evt in dpm:
                if evt.is_reading_for(0) and on_event(evt):
                    return

    acsys.run_client(run)


def read_device(device: str, count: int = 5) -> list[str]:
    readings: list[str] = []

    def on_event(evt: ACSysEvent) -> bool:
        readings.append(str(evt))
        return len(readings) >= count

    _run_with_dpm(device, on_event)
    return readings


def stream_device(device: str, on_update: Callable[[str], bool]) -> None:
    def on_event(evt: ACSysEvent) -> bool:
        return on_update(str(evt))

    _run_with_dpm(device, on_event)
