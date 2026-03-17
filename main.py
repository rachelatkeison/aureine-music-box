from __future__ import annotations
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from core.engine import MusicBoxEngine
from ui.app_window import AppWindow
from ui.styles import APP_QSS


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)

    engine = MusicBoxEngine()
    window = AppWindow(engine)
    window.show()

    timer = QTimer()
    timer.setInterval(40)
    timer.timeout.connect(window.tick)
    timer.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
