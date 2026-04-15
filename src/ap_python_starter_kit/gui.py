from __future__ import annotations

import queue
import sys
import threading

from .acsys_client import stream_device


class MainWindow:
    def __init__(self, device: str) -> None:
        try:
            from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget
        except ImportError as exc:  # pragma: no cover - exercised in tests via `main`
            raise RuntimeError(
                "PyQt6 is not installed. Install the optional GUI dependencies with "
                "`uv sync --extra gui-pyqt`."
            ) from exc

        class _Window(QMainWindow):
            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle("ap-python-starter-kit - GUI demo")

                self._label = QLabel(f"Waiting for ACSys data from {device}...")
                self._label.setTextInteractionFlags(self._label.textInteractionFlags())

                root = QWidget()
                layout = QVBoxLayout(root)
                layout.addWidget(self._label)
                self.setCentralWidget(root)

            def update_text(self, text: str) -> None:
                self._label.setText(text)

        self._window = _Window()

    def resize(self, width: int, height: int) -> None:
        self._window.resize(width, height)

    def show(self) -> None:
        self._window.show()

    def update_text(self, text: str) -> None:
        self._window.update_text(text)


def run_gui(device: str) -> int:
    try:
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QApplication
    except ImportError as exc:
        raise RuntimeError(
            "PyQt6 is not installed. Install the optional GUI dependencies with "
            "`uv sync --extra gui-pyqt`."
        ) from exc

    updates: queue.Queue[str] = queue.Queue()
    stop = threading.Event()

    def run_stream() -> None:
        try:
            stream_device(device, lambda text: _queue_update(text, updates, stop))
        except Exception:
            updates.put("ACSys stream stopped (see logs for details).")

    thread = threading.Thread(target=run_stream, daemon=True)
    thread.start()

    app = QApplication(sys.argv)
    window = MainWindow(device)
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


def _queue_update(text: str, updates: queue.Queue[str], stop: threading.Event) -> bool:
    if stop.is_set():
        return True
    updates.put(text)
    return False
