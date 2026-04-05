# Hashed Maze
# Copyright (C) 2026 Tito de Barros Junior
# Lincensed under the MIT License

import signal
signal.signal(signal.SIGINT, signal.SIG_IGN)
from PySide6.QtWidgets import QApplication
from src.main_window_hashed_maze import MainWindow

app = QApplication([])

window = MainWindow()

app.exec()