# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from PySide6.QtCore import QByteArray
from PySide6.QtSvgWidgets import QSvgWidget

import threading
import base64
from PySide6.QtGui import QWindowStateChangeEvent, QIcon
from PySide6.QtWidgets import QWidget, QLineEdit
from PySide6.QtUiTools import loadUiType
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtSvgWidgets import QSvgWidget

from src.main_window_hashed_maze import MainWindow
from src.crypt import CryptoVault
from src.utils.resource_path import resource_path
from src.password_server import run_server
from src.core.state import app_state
from ui.helpers.animations import shake_widget

# Resolve resource path for dev and PyInstaller (_MEIPASS) environments
Ui_MainWindow, BaseClass = loadUiType(resource_path("ui/forms/login_window_hashed_maze.ui"))  # type: ignore

_MAX_LOGIN_ATTEMPTS = 3

_LOCK_SVG = b"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
     stroke="#1D9E75" stroke-width=".5" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
</svg>
"""
class LoginWindow(BaseClass,Ui_MainWindow):
    def __init__(self, app_state, parent=MainWindow):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.app_state = app_state
        self._attempts = 0

        #icon test
        self._setup_icon()
        self._setup_border_animation()

        # signal/slot connections
        self.btnBox.button(self.btnBox.StandardButton.Ok).clicked.connect(self.handle_login)
        self.btnShowPWD.clicked.connect(self.show_pwd)

        # icon/label tasks
        self.btnShowPWD.setIcon(QIcon("static/icons/visibility_20.png"))
        self.lblWarning.setVisible(False)
        self.lblMsg.setText('')

    # --- login logic ---

    def handle_login(self):
        typed_password = self.edtPWD.text()

        if self.login(typed_password):
            # start local IPC server to allow external components (e.g., extension) 
            # to retrieve the master password at runtime
            if not hasattr(self, "_server_started"):
                self._server_started = True
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()

            self.app_state.crypto.decrypted_pass = typed_password   # global uses
            self.accept()
            return
        
        self._attempts += 1
        remaining = _MAX_LOGIN_ATTEMPTS - self._attempts

        # Login attempt warnings
        warning_map = {
            2: ("The database will be wiped after three unsuccessful attempts", "rgb(233, 255, 38)"),
            1: ("** WARNING **\n Database will be deleted if this attempt is unsuccessful", "rgb(255, 122, 114)")
        }

        self.lblWarning.setVisible(remaining in warning_map)
        
        if remaining in warning_map:
            text, color = warning_map[remaining]
            self.lblWarning.setText(text)
            self.lblWarning.setStyleSheet(f"color: {color};")
            self.lblWarning.setVisible(True)
        
        # will delete database
        if remaining <= 0:
            self._wipe_and_reject()
            return
        
        self.lblMsg.setVisible(True)
        self.lblMsg.setText(f"Previous login attempt was unsuccessful, {remaining} attempts remaining.")
        shake_widget(self, self.edtPWD)
        self.edtPWD.clear()
        self.edtPWD.setFocus()

    def login(self, typed_password) -> bool:
        master = CryptoVault.get_master_hash()

        if master is None:
            return False
        
        salt_bytes = base64.b64decode(master.salt)
        try_key = CryptoVault.derive_key(typed_password, salt_bytes)
        db_hash_bytes = base64.b64decode(master.hash)
        
        if try_key == db_hash_bytes:
            self.app_state.crypto.master_hash = master.hash
            self.app_state.crypto.salt = master.salt
            self.app_state.crypto.decrypted_pass = typed_password
            self.app_state.crypto.derived_key = try_key
            # self.app_state.crypto.derived_key = typed_password
            return True
        
        return False
       
    def changeEvent(self, event):
        # prevent window maximization
        if isinstance(event, QWindowStateChangeEvent):
            if self.windowState() & Qt.WindowState.WindowMaximized:
                self.setWindowState(Qt.WindowState.WindowNoState)
                return
        super().changeEvent(event)

    def _wipe_and_reject(self):
        import os
        from src.config import db_path
        try:
            os.remove(db_path)
        except OSError:
            pass
        self.reject()

    def show_pwd(self):
        if self.edtPWD.echoMode() == QLineEdit.EchoMode.Password:
            self.edtPWD.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btnShowPWD.setIcon(QIcon("static/icons/visibility_off_20.png"))
        else:
            self.edtPWD.setEchoMode(QLineEdit.EchoMode.Password)
            self.btnShowPWD.setIcon(QIcon("static/icons/visibility_20.png"))

# --- icon ---

    def _setup_icon(self):
        size = 28
        x = self.lblIconPad.x() + (self.lblIconPad.width() - size) // 2
        y = self.lblIconPad.y() + (self.lblIconPad.height() - size) // 2

        self._svg = QSvgWidget(self.frame)
        self._svg.load(QByteArray(_LOCK_SVG))
        self._svg.setGeometry(x, y, size, size)
        self.lblIconPad.hide()    
    
    # --- border smooth pulse ---

    _BORDER_COLORS = [
        "#085041", "#0F6E56", "#1D9E75", "#5DCAA5", "#9FE1CB",
        "#5DCAA5", "#1D9E75", "#0F6E56",
    ]

    def _setup_border_animation(self):
        self._border_step = 0
        self._border_timer = QTimer(self)
        self._border_timer.setInterval(220)
        self._border_timer.timeout.connect(self._tick_border)
        self._border_timer.start()

    def _tick_border(self):
        color = self._BORDER_COLORS[self._border_step % len(self._BORDER_COLORS)]
        self.edtPWD.setStyleSheet(f"QLineEdit {{ border: 0.5px solid {color}; border-radius: 4px; }}")
        self._border_step += 1
