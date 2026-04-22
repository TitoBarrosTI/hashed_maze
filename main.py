# Hashed Maze
# Copyright (C) 2026 Tito de Barros Junior
# Lincensed under the MIT License


import signal
import sys

from src.setup import run_setup
signal.signal(signal.SIGINT, signal.SIG_IGN)
from PySide6.QtWidgets import QApplication
from src.main_window_hashed_maze import MainWindow
from src.core.single_instance import is_already_running
from src.utils.dialogs import info_dialog
from src.core.state import app_state, AppState

app = QApplication([])

if is_already_running():
    info_dialog("System already in operation. New instances are not allowed!",
                "This instance will be terminated.")
    sys.exit(0)

run_setup()

window = MainWindow(app_state)

app.exec()