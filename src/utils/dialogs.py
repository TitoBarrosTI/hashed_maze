# Hashed Maze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from PySide6.QtWidgets import (QMessageBox)

def confirm_dialog(text: str, informative: str = "", title = "Hashed Maze — Password Vault") -> bool:
    msgBx = QMessageBox()
    msgBx.setText(text)
    msgBx.setWindowTitle(title)
    if informative:
        msgBx.setInformativeText(informative)
    msgBx.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msgBx.setDefaultButton(QMessageBox.StandardButton.No)
    return msgBx.exec() == QMessageBox.StandardButton.Yes

def info_dialog(text: str, informative: str = "", title = "Hashed Maze — Password Vault") -> None:
    msgBx = QMessageBox()
    msgBx.setText(text)
    msgBx.setWindowTitle(title)
    if informative:
        msgBx.setInformativeText(informative)
    msgBx.setStandardButtons(QMessageBox.StandardButton.Ok)
    
    msgBx.exec()