from __future__ import annotations

import queue
import sys
import threading

import acsys
import acsys.dpm
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("__template_project_name__ - PyQt + ACSys")

        self._label = QLabel("Waiting for ACSys data...")
        self._label.setTextInteractionFlags(self._label.textInteractionFlags())

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(self._label)
        self.setCentralWidget(root)

    def update_text(self, text: str) -> None:
        self._label.setText(text)


async def _stream_device(
    con, device: str, updates: queue.Queue[str], stop: threading.Event
) -> None:
    async with acsys.dpm.DPMContext(con) as dpm:
        await dpm.add_entry(0, device)
        await dpm.start()

        async for evt in dpm:
            if stop.is_set():
                break
            if evt.is_reading_for(0):
                updates.put(str(evt))


def main() -> int:
    # Keep it dead-simple: stream SCTIME and show latest value.
    device = "G:SCTIME@P,15H"

    updates: queue.Queue[str] = queue.Queue()
    stop = threading.Event()

    def run_stream() -> None:
        try:
            acsys.run_client(lambda con: _stream_device(con, device, updates, stop))
        except Exception:
            # Show errors in the UI instead of crashing the app.
            updates.put("ACSys stream stopped (see container logs).")

    t = threading.Thread(target=run_stream, daemon=True)
    t.start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(720, 240)
    window.show()

    timer = QTimer()

    def pump_updates() -> None:
        latest = None
        while not updates.empty():
            latest = updates.get_nowait()
        if latest is not None:
            window.update_text(latest)

    timer.timeout.connect(pump_updates)
    timer.start(250)

    def on_about_to_quit() -> None:
        stop.set()

    app.aboutToQuit.connect(on_about_to_quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
