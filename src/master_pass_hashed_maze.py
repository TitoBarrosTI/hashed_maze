# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import logging

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QPushButton, QWidget, QDialog, QApplication, QVBoxLayout,
                               QLineEdit, QLabel, QProgressBar)
# from PySide6.QtUiTools import loadUiType
from zxcvbn import zxcvbn
from PySide6.QtCore import QTimer, Qt

from src.core.state import app_state
from src.main_window_hashed_maze import MainWindow
from src.crypt import CryptoVault
from src.config import db_path
from src.database import SQLiteDB
from src.utils.resource_path import resource_path

from PySide6.QtWidgets import QWidget
from ui.forms.ui_master_pass import Ui_Form
BaseClass = QWidget

# Resolve resource path for dev and PyInstaller (_MEIPASS) environments
# Ui_MainWindow, BaseClass = loadUiType(resource_path("ui/forms/master_pass_hashed_maze.ui"))  # type: ignore

# class MasterPass(QDialog,Ui_MainWindow):
class MasterPass(QDialog,Ui_Form):
    def __init__(self, app_state, parent=MainWindow):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.state = app_state

        self.lblCFGDatabaseDirectory.setText(db_path)
        self.lblInstructions.setTextFormat(Qt.TextFormat.RichText)
        self.lblInstructions.setText("""
        <b>Create a strong password</b>
        <p style="margin-top:6px; margin-bottom:0">Use at least 12 characters — longer passwords are more secure.</p>
        <p style="margin-top:6px; margin-bottom:0">Avoid common patterns like 123456 or qwerty.</p>
        <p style="margin-top:6px; margin-bottom:0">Don't use personal details like your name or birth date.</p>
        <p style="margin-top:6px; margin-bottom:0">A good strategy is to combine random words or create a memorable phrase.</p>
        <p style="margin-top:6px; margin-bottom:0">Try mixing uppercase letters, lowercase letters, numbers, and symbols.</p>
        <p style="margin-top:6px; margin-bottom:0">Avoid reusing passwords across different accounts.</p>
        <p style="margin-top:6px; margin-bottom:0">Keep your password private and change it if you think it's been exposed.</p>
        """)

        # signal/slot connections
        self.btnAddMasterPass.clicked.connect(self.insert_master_pass)
        self.btnOk.clicked.connect(self.on_click_btn_ok)
        self.btnShowPWD.clicked.connect(self.show_pwd)

        # icons tasks
        self.btnShowPWD.setIcon(QIcon(resource_path("static/icons/visibility_20.png")))


        self.strength = PasswordStrengthController(
            self.edtMasterPass,
            self.pBar,
            self.lblMsg
        )

    def insert_master_pass(self):
        master_password = self.edtMasterPass.text()

        if not self.edtMasterPass.text():
            self.marquee = MarqueeController(
                self.lblMsg,
                "the master password field is empty, please correct it!",
                interval=100
            )
            return

        hash_login, salt_bytes, hash_b64, salt_b64 = CryptoVault.generate_hash_login(master_password)

        # setting updated data to crypto state
        self.state.crypto.decrypted_pass = master_password
        self.state.crypto.master_hash = hash_b64
        self.state.crypto.salt_hash = salt_bytes
        self.state.crypto.derived_key = hash_login.hex()

        data = {
            "mkhash": hash_b64,
            "salt": salt_b64
        }

        try:
            db = SQLiteDB(db_path)
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            sql = f"INSERT INTO hash ({cols}) VALUES({placeholders})"

            success, msg = db.execute(sql, (data['mkhash'], data['salt']))

            if not success:
                self.marquee = MarqueeController(
                    self.lblMsg,
                    "not registered master hash",
                    interval=100
                )

                logging.error(msg)
                return
            
            self.marquee = MarqueeController(
                self.lblMsg,
                "registered master hash",
                interval=100
            )

            from src.login_window_hashed_maze import LoginWindow
            self.login = LoginWindow(self.state, parent=self)
            
            if self.login.exec():
                self.accept()
            else:
                self.reject()
        except Exception as e:
            logging.debug(f"error on insert master pass: {e}")
            print(f'error on insert master pass: {e}')

    def on_click_btn_ok(self) -> None:
        self.has_master_hash = CryptoVault.has_master_hash()

        if self.has_master_hash:
            master_hash = CryptoVault.get_master_hash()
            MainWindow.db_hash = master_hash.hash
            MainWindow.db_salt = master_hash.salt
            self.accept()
        else:
            self.reject()

    def show_pwd(self):
        if self.edtMasterPass.echoMode() == QLineEdit.EchoMode.Password:
            self.edtMasterPass.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btnShowPWD.setIcon(QIcon(resource_path("static/icons/visibility_off_20.png")))
        else:
            self.edtMasterPass.setEchoMode(QLineEdit.EchoMode.Password)
            self.btnShowPWD.setIcon(QIcon(resource_path("static/icons/visibility_20.png")))

class MarqueeController:
    def __init__(self, widget, text, interval=100):
        self.widget = widget
        self.full_text = text + "   "
        self.pos = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text)
        self.timer.start(interval)

    def update_text(self):
        self.pos += 1
        if self.pos >= len(self.full_text):
            self.pos = 0

        display = self.full_text[self.pos:] + self.full_text[:self.pos]
        self.widget.setText(display)

class PasswordStrengthController:
    def __init__(self, p_lnEdt, p_pBar, p_lbl):
        self.edtMasterPass = p_lnEdt
        self.pBar = p_pBar
        self.lblMsg = p_lbl

        self.pBar.setRange(0, 100)
        self.pBar.setTextVisible(False)

        # signal/slot connections
        self.edtMasterPass.textChanged.connect(self.atualizar_forca_senha)

    def check_strength(self, text):
        if not text:
            self.bar.setValue(0)
            self.label.setText("")
            return

        result = zxcvbn(text)
        score = result["score"]

        self.label.setTextFormat(Qt.RichText)
        self.bar.setValue(score)

        texts = ["Muito fraca", "Fraca", "Média", "Boa", "Forte"]
        colors = ["#ff4d4d", "#ff944d", "#ffd24d", "#9acd32", "#2ecc71"]

        self.label.setText(texts[score])

        self.bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {colors[score]};
            }}
        """)

    def atualizar_forca_senha(self, pass_: str):
        forca = self.calculate_force(pass_)  # retorn 0-100
        self.pBar.setValue(forca)

        if forca == 0:
            cor = "transparent"  # no fill, track appears
        elif forca < 40:
            cor = "#e05252"  # red — weak
        elif forca < 70:
            cor = "#e0a832"  # yellow — medium
        else:
            cor = "#4caf50"  # green — strong

        self.pBar.setStyleSheet(f"""
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
        """)

    def calculate_force(self, pass_: str) -> int:
        if not pass_:
            return 0
        score = 0
        if len(pass_) >= 8:  score += 25
        if len(pass_) >= 12: score += 25
        if any(c.isupper() for c in pass_): score += 15
        if any(c.isdigit() for c in pass_): score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in pass_): score += 20
        return score
