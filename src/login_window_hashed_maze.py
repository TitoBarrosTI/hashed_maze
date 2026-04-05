# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import base64

from PySide6.QtGui import QWindowStateChangeEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import loadUiType
from PySide6.QtCore import Qt

from src.main_window_hashed_maze import MainWindow
from src.crypt import CryptoVault
from src.utils.resource_path import resource_path

# Resolve resource path for dev and PyInstaller (_MEIPASS) environments
Ui_MainWindow, BaseClass = loadUiType(resource_path("ui/login_window_hashed_maze.ui"))  # type: ignore

class LoginWindow(BaseClass,Ui_MainWindow):
    def __init__(self, master_hash, salt, parent=MainWindow):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())

        # signal/slot connections
        self.btnBox.button(self.btnBox.StandardButton.Ok).clicked.connect(self.handle_login)

    def handle_login(self):
        typed_hash = self.edtPWD.text()

        if self.login(typed_hash):
            self.accept()
            return
        
        self.lblMsg.setText("incorrect password or not typed.") 
        self.edtPWD.clear()
        self.edtPWD.setFocus()

    def login(self, typed_hash) -> bool:
        master = CryptoVault.get_master_hash()

        if master is None:
            print(f"any master returned")
            return False
        
        db_hash = master.hash
        db_salt = master.salt
        salt_bytes = base64.b64decode(db_salt)
        try_key = CryptoVault.derive_key(typed_hash, salt_bytes)
        db_hash_bytes = base64.b64decode(db_hash)
        
        if try_key == db_hash_bytes:
            return True
        else:
            return False
       
    # prevent windo maximization
    def changeEvent(self, event):
        if isinstance(event, QWindowStateChangeEvent):
            if self.windowState() & Qt.WindowState.WindowMaximized:
                self.setWindowState(Qt.WindowState.WindowNoState)
                return
        super().changeEvent(event)