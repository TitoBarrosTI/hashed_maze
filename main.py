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
from src.core.state import app_state

app = QApplication([])

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QTranslator, QLocale
translator = QTranslator()
locale = QLocale.system().name()
_ = QCoreApplication.translate
# translator.load(f"translations/hashedmaze_{locale}.qm")
# # translator.load("translations/hashedmaze_pt_BR.qm")
# loaded = translator.load(f"translations/hashedmaze_{locale}.qm")
# # loaded = translator.load("translations/hashedmaze_pt_BR.qm")
# print(f"Carregou: {loaded}")

# app.installTranslator(translator)

ui_languages = QLocale.system().uiLanguages()

loaded = False
for lang in ui_languages:
    locale = lang.replace("-", "_")
    loaded = translator.load(f"translations/hashedmaze_{locale}.qm")
    if loaded:
        break

app.installTranslator(translator)


if is_already_running():
    info_dialog(_("main","System already in operation. New instances are not allowed!"),
                _("main","This instance will be terminated."))
    sys.exit(0)

run_setup()

window = MainWindow(app_state)

app.setQuitOnLastWindowClosed(False)
app.exec()