from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("__template_project_name__ - PyQt Scaffold")
        self.setCentralWidget(QLabel("Optional PyQt scaffold is working."))


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(480, 200)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
