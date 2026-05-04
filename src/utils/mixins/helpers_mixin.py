# Hashed Maze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
)

from src.utils.password_strength import calculate_force
from src.utils.resource_path import resource_path

class HelpersMixin:
    def update_icon(self: "MainWindow", index) -> None:
        if index == 0:
            self.lblIconSearch.setPixmap(QPixmap("static/icons/database_search_40_clear_green"))            
        if index == 1:
            self.lblIconConfig.setPixmap(QPixmap("static/icons/settings_40_green.png"))
        if index == 2:
            self.lblIconAbout.setPixmap(QPixmap("static/icons/about_40_green.png"))
    
    def update_password_force(self: "MainWindow", pass_: str):
        forca = calculate_force(pass_)  # retorn 0-100
        self.pBar.setValue(forca)

        if forca == 0:
            cor = "transparent"  # no fill, track appears
        elif forca < 40:
            cor = "#e05252"  # red — weak
        elif forca < 70:
            cor = "#e0a832"  # yellow — medium
        else:
            cor = "#4caf50"  # green — strong

        self.pBar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: #3a3a3a;
                border: none;
                border-radius: 3px;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {cor};
                border-radius: 3px;
            }}
        """
        )
    
    def show_pwd(self: "MainWindow"):
        if self.edtPWD.echoMode() == QLineEdit.EchoMode.Password:
            self.edtPWD.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btnShowPWD.setIcon(QIcon("static/icons/visibility_off_20.png"))
            QTimer.singleShot(10000,lambda: (
                self.edtPWD.setEchoMode(QLineEdit.EchoMode.Password),
                self.btnShowPWD.setIcon(QIcon(resource_path("static/icons/visibility_20.png")))
            ))
        else:
            self.edtPWD.setEchoMode(QLineEdit.EchoMode.Password)
            self.btnShowPWD.setIcon(QIcon(resource_path("static/icons/visibility_20.png")))

    def visual_feedback_on_record_status(self: "MainWindow", status = None):
        # receives integer or None (_editing_id)
        if status is None:
            # self.frmStatusEdition.set_status_colors("#1e1e1e", "#1e1e1e", "#1e1e1e")
            self.frmStatusEdition.set_status_colors("#222222","#1e1e1e", "#202020")
        else:
            self.frmStatusEdition.set_status_colors("#b7d9b1", "#a3c9a0", "#92b68f")
    
    def set_value_search_variable(self: "MainWindow", name) -> None:
        # after select option in context menu search
        self.state.ui.search_field = name
        self.edtSearch.clear()
        self.edtSearch.setPlaceholderText(f"search by {name}")
        self.edtSearch.setFocus()
        ordering = self.state.ui.search_order
        self.lblSearchBy.setText(f"search by {name} (ordered by {ordering if ordering else 'id'})")
  
    def _log(self: "MainWindow", msg: str, color: Qt.GlobalColor = Qt.GlobalColor.green) -> None:
        self.logMasterPWD.setReadOnly(True)
        
        # Fade out all previous lines
        cursor = self.logMasterPWD.textCursor()
        self.logMasterPWD.selectAll()
        
        fmt = self.logMasterPWD.currentCharFormat()
        fmt.setForeground(Qt.GlobalColor.darkGray)
        self.logMasterPWD.mergeCurrentCharFormat(fmt)
        
        # Move to the end and append a new line in default color
        cursor.movePosition(cursor.MoveOperation.End)
        self.logMasterPWD.setTextCursor(cursor)
        
        fmt.setForeground(color)
        self.logMasterPWD.setCurrentCharFormat(fmt)
        self.logMasterPWD.append(msg)
        
        # Force an immediate visual update
        QApplication.processEvents()