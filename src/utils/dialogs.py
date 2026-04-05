# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from PySide6.QtWidgets import (QMessageBox)

def confirm_dialog(text: str, informative: str = "") -> bool:
    msgBx = QMessageBox()
    msgBx.setText(text)
    if informative:
        msgBx.setInformativeText(informative)
    msgBx.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msgBx.setDefaultButton(QMessageBox.StandardButton.No)
    return msgBx.exec() == QMessageBox.StandardButton.Yes