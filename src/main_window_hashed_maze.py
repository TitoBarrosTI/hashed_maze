# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import os, sys, sqlite3
from functools import partial
# from typing import Any

from PySide6.QtCore import Qt, QTimer, QSettings, QEvent, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap, QIcon, QWindowStateChangeEvent
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QMenu,
    QListWidget,
    QMenu,
    QToolButton,
    QHeaderView,
    QTreeWidgetItem,
    QLineEdit,
    QPlainTextEdit,
    QLabel,
)

from src.config import db_path
from src.database import SQLiteDB
from src.popup_hint import PopupHint
from src.crypt import CryptoVault
from roundedframe import RoundedFrame
from src.utils.resource_path import resource_path
from src.utils.password_strength import calculate_force
from src.utils.dialogs import confirm_dialog

# Resolve resource path for dev and PyInstaller (_MEIPASS) environments
Ui_MainWindow, BaseClass = loadUiType(resource_path("ui/main_window_hashed_maze.ui"))  # type: ignore

class MainWindow(BaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.db = SQLiteDB(db_path)
        self.db.initialize()
        self.pBar.setRange(0, 100)
        self.pBar.setTextVisible(False)
        self.initial_row_items = {}
        self.search_field = None  # flag
        self.current_id: int | None = None
        self.master_hash = None
        self.salt = None
        self._editing_id: int | None = None
        self.lblCFGDatabaseDirectory.setText(db_path)

        self.btnApply: QPushButton

        # decides which screen will be opened
        self._setup_initial_screen()

        # popup_hint (resume)
        self._popup = PopupHint(dark_mode=True)
        self._last_item = None
        self._hide_timer = QTimer(singleShot=True)
        self._hide_timer.timeout.connect(self._popup.hide)
        self.treeCredentialsResponse.setMouseTracking(True)
        self.treeCredentialsResponse.viewport().installEventFilter(self)

        # tree widget header adjusts
        header = self.treeCredentialsResponse.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # signal/slot connections
        # region ─ sitting editing status check ───────────────
        fields_in_form = [self.edtAccount, self.edtURL, self.edtPWD, self.edtPlainNotes]
        for f in fields_in_form:
            f.textChanged.connect(self.on_edit_fields)

        # Defining and creating actions in the search menu
        self.search_actions = {}
        menuSearch = QMenu(self)

        for name in ("all fields","user", "url", "notes"):
            act = menuSearch.addAction(name)
            act.triggered.connect(partial(self.set_value_search_variable, name))
            self.search_actions[name] = act  # Save the action by name

        self.search_actions["all fields"].trigger()

        self.btnSearchBy.setMenu(menuSearch)
        self.btnSearchBy.setPopupMode(QToolButton.InstantPopup)
        self.btnSearch.clicked.connect(
            lambda: self.search_credential(self.search_field, self.edtSearch.text())
        )
        # endregion

        self.edtSearch.returnPressed.connect(
            lambda: self.search_credential(self.search_field, self.edtSearch.text())
        )

        # target fields for tree item data
        # (It must follow the same order as displayed in the TreeView.)
        self.mapping = {
            0: self.edtAccount,
            1: self.edtURL,
            2: self.edtPlainNotes,
            3: self.edtPWD,
        }

        self.treeCredentialsResponse.itemClicked.connect(
            partial(self.load_data_row, self.mapping)
        )
        self.btnApply.clicked.connect(self.handle_action_on_save_record)
        self.btnNew.clicked.connect(self.on_click_new)
        self.btnCancel.clicked.connect(self.on_click_cancel)
        self.edtPWD.textChanged.connect(self.update_password_force)
        self.btnShowPWD.clicked.connect(self.show_pwd)

        # icons works
        self.tabWidget.setCurrentIndex(2)
        self.tabWidget.currentChanged.connect(self.update_icon)
        self.update_icon(self.tabWidget.currentIndex())
        self.btnShowPWD.setIcon(QIcon("static/icons/visibility_20.png"))
        self.btnApply.setIcon(QIcon("static/icons/apply_20.png"))

        self.btnLnkReportABug.clicked.connect(self.open_bug_report)
        self.btnClose.clicked.connect(self.on_close_clicked)

        # components config
        self.btnApply.setEnabled(False)

    # region ── Crud methods ──────────────────────────────
    def search_credential(self, field, filter) -> None:
        try:
            if not field or not filter:
                return
            
            if field == "all fields":
                where = """WHERE user LIKE ? OR
                           url LIKE ? OR
                           notes LIKE ?                
                """ if filter else ""
                params = (f"%{filter}%", f"%{filter}%", f"%{filter}%") if filter else ()
            else:
                where = f"WHERE {field} LIKE ?" if filter else ""            
                params = (f"%{filter}%",) if filter else ()

            sql = f"""
            SELECT id, user, url, ciphertext, 
                   salt, nonce, notes, created_at,
                   COUNT(*) OVER() AS total
            FROM credentials
            {where}
            """
            rows = self.db.fetch_all(sql, params)
            self.treeCredentialsResponse.clear()

            if not rows:
                return

            # hiding the column password
            self.treeCredentialsResponse.setColumnHidden(3, True)

            self.lblResults.setText(f"results: {str(rows[0]["total"])}")
            
            for row in rows:
                item = QTreeWidgetItem(self.treeCredentialsResponse)

                self.btnDeleteAction = QPushButton("delete")
                self.btnDeleteAction.setFixedSize(57, 22)
                self.btnDeleteAction.clicked.connect(
                    partial(
                        self.on_click_action,
                        int(row["id"]),
                        f"Really wants delete this access account?",
                        f"id reference: {int(row['id'])}",
                    )
                )                
                self.treeCredentialsResponse.setItemWidget(
                    item, 5, self.btnDeleteAction
                )

                item.setText(0, str(row["user"]))
                item.setText(1, str(row["url"]))
                item.setText(2, str(row["notes"]))
                item.setText(3, str(row["ciphertext"]))
                item.setText(4, str(row["created_at"]))
                item.setData(0, Qt.ItemDataRole.UserRole, int(row["id"]))
                
                # all collumns of credentials in DataRole
                item.setData(
                    1,
                    Qt.ItemDataRole.UserRole,
                    {
                        "account": str(row["user"]),
                        "url": str(row["url"]),
                        "ciphertext": str(row["ciphertext"]),
                        "salt": str(row["salt"]),
                        "nonce": str(row["nonce"]),
                        "notes": str(row["notes"]),
                        "created_at": str(row["created_at"]),
                    },
                )

        except sqlite3.OperationalError as e:
            print("Operational error:", e)

        except sqlite3.IntegrityError as e:
            print("integrity error:", e)

        except sqlite3.Error as e:
            print("general SQLite error:", e)
    def update_record(self, table: str, where: str):
        if not self._required_fields_ok():
            return (False, "Fill in the required field")

        master_hash = CryptoVault.get_master_hash().hash
        vault = CryptoVault.encrypt(master_hash, self.edtPWD.text())

        data = {
            "user": self.edtAccount.text(),
            "url": self.edtURL.text(),
            "notes": self.edtPlainNotes.toPlainText(),
            "ciphertext": vault["ciphertext"],
            "salt": vault["salt"],
            "nonce": vault["nonce"],
        }

        try:
            cols = ", ".join([f"{key} = ?" for key in data.keys()])
            sql = f"UPDATE {table} SET {cols} WHERE {where} = ?"
            # join the values of DICT with WHERE param
            #.values() retrieves data in same order as the keys used above 
            # values = list(data.values()) + [self.current_id]
            values = list(data.values())
            values.append(self.current_id)

            self.db.execute(sql, tuple(values))

            self.btnSearch.click()
        except Exception as e:
            print(f"Error on update: {e}")

        self._editing_id = None  # flag edition
        self.btnApply.setEnabled(False)
        self.btnCancel.setEnabled(False)
        self.on_action_finished()

        return True, "Updated successfully"
    def insert_record(self, table: str):
        # obtaining inputs
        required_inputs = {
            "user": self.edtAccount.text().strip(),
            "url": self.edtURL.text().strip(),
            "ciphertext": self.edtPWD.text().strip(),
        }

        widget_map = {
            "user": self.edtAccount,
            "url": self.edtURL,
            "ciphertext": self.edtPWD,
        }

        # if not required inputs, fail
        for key, value in required_inputs.items():
            if not value:
                widget_map[key].setFocus()
                return False, f"*** {key.title()} is mandatory! ***"

        # generating encrypted password
        master_hash = CryptoVault.get_master_hash().hash
        vault = CryptoVault.encrypt(master_hash, self.edtPWD.text())

        payload = {
            "user": self.edtAccount.text(),
            "url": self.edtURL.text(),
            "notes": self.edtPlainNotes.toPlainText(),
            "ciphertext": vault["ciphertext"],
            "salt": vault["salt"],
            "nonce": vault["nonce"],
        }

        try:
            self.db.insert(table, payload)
        except Exception as e:
            print(f"Error on insert: {e}")

        self.clear_fields(self.fields_to_clean())
        self._editing_id = None  # flag edition
        self.btnApply.setEnabled(False)
        self.btnCancel.setEnabled(False)
        self.on_action_finished()

        return True, "Inserted successfully"
    def load_data_row(self, mapping: dict, item, _) -> None:
        # visual feedback
        self.record_status(1)
        self.current_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._editing_id = self.current_id  # flag edition
        data_items = item.data(1, Qt.ItemDataRole.UserRole)

        # Saving initial data received from treecredentials for rollback if editing is cancelled
        self.initial_row_items = {
            k: item.text(i)
            for i, k in enumerate(["user","url","notes","password"])
        }

        for col_index, widget in mapping.items():
            # special condition for same component type (QLineEdit)
            if widget == self.edtPWD:
                if data_items:
                    ciphertext = data_items.get("ciphertext")
                    salt = data_items.get("salt")
                    nonce = data_items.get("nonce")
                    data_ = {"ciphertext": ciphertext, "salt": salt, "nonce": nonce}
                    master_hash = CryptoVault.get_master_hash().hash
                    value_pass = CryptoVault.decrypt(master_hash, data_)
                    widget.setText(str(value_pass))
                continue
            
            value = item.text(col_index)            

            if isinstance(widget, (QLineEdit, QLabel)):
                 widget.setText(str(value))
            elif isinstance(widget, QPlainTextEdit):
                widget.setPlainText(str(value))
            elif isinstance(widget, QListWidget):
                widget.clear()
                widget.addItems(str(value).splitlines())
    # endregion

    # region ── Setup ─────────────────────────────────────
    def _setup_initial_screen(self):
        self.has_master_hash = CryptoVault.has_master_hash()

        if self.has_master_hash:
            from src.models import MasterKey

            self.master_hash = CryptoVault.get_master_hash()

            from src.login_window_hashed_maze import LoginWindow

            self.login_dialog = LoginWindow(self.master_hash, self.salt, parent=self)
            self.hide()

            # .exec() trava aqui até o login chamar self.accept() ou self.reject()
            if self.login_dialog.exec():
                self.show()
            else:
                self.close()
        else:
            from src.master_pass_hashed_maze import MasterPass

            self.master_pass_dialog = MasterPass(parent=self)
            self.hide()

            if self.master_pass_dialog.exec():
                self.show()
            else:
                self.close()
    # endregion

    # region ── UI helpers ────────────────────────────────
    def update_icon(self, index) -> None:
        if index == 0:
            self.lblIconSearch.setPixmap(QPixmap("static/icons/search_50.png"))
        if index == 1:
            self.lblIconConfig.setPixmap(QPixmap("static/icons/settings_50.png"))
        if index == 2:
            self.lblIconAbout.setPixmap(QPixmap("static/icons/about_50.png"))    
    def update_password_force(self, pass_: str):
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
    def show_pwd(self):
        if self.edtPWD.echoMode() == QLineEdit.EchoMode.Password:
            self.edtPWD.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btnShowPWD.setIcon(QIcon("static/icons/visibility_off_20.png"))
        else:
            self.edtPWD.setEchoMode(QLineEdit.EchoMode.Password)
            self.btnShowPWD.setIcon(QIcon("static/icons/visibility_20.png"))
    def record_status(self, status = None):
        # receives integer or None (_editing_id)
        if not status:
            self.frmStatusEdition.set_status_colors(None)
        else:
            self.frmStatusEdition.set_status_colors("#b7d9b1", "#a3c9a0", "#92b68f")
    # after select option in context menu search
    def set_value_search_variable(self, name) -> None:
        self.search_field = name
        self.edtSearch.clear()
        self.edtSearch.setPlaceholderText(f"search by {name}")
        self.edtSearch.setFocus()
        self.lblSearchBy.setText(f"searching by {name}")
    # endregion

    # region ── Qt overrides ──────────────────────────────
    def eventFilter(self, watched, event):
        if (
            watched is self.treeCredentialsResponse.viewport()
        ):  # <-- viewport, não a tree

            if event.type() == QEvent.Type.MouseMove:
                item = self.treeCredentialsResponse.itemAt(event.pos())

                if item and item is not self._last_item:
                    self._last_item = item
                    self._hide_timer.stop()
                    data = item.data(1, Qt.ItemDataRole.UserRole)
                    if data:
                        self._popup.set_content(data)
                        self._popup.show_near_cursor()

                elif not item:
                    self._hide_timer.start(250)
                    self._last_item = None

            elif event.type() == QEvent.Type.Leave:
                self._hide_timer.start(300)
                self._last_item = None

        return super().eventFilter(watched, event)
    # evitar maximizar a tela
    def changeEvent(self, event):
        if isinstance(event, QWindowStateChangeEvent):
            if self.windowState() & Qt.WindowState.WindowMaximized:
                self.setWindowState(Qt.WindowState.WindowNoState)
                return
        super().changeEvent(event)
    # endregion

    # region ── Form state ────────────────────────────────
    def clear_fields(self, lst_widgets: list[QWidget]) -> None:
        if not lst_widgets:
            return

        for w in lst_widgets:
            if isinstance(w, (QLineEdit, QPlainTextEdit)):
                w.clear()
    def fields_to_clean(self):
        return [self.edtAccount, self.edtURL, self.edtPWD, self.edtPlainNotes]
    def on_action_finished(self):
        # Volta para a cor padrão do sistema (cinza)
        self.frmStatusEdition.set_status_colors(None)
    def _required_fields_ok(self) -> bool:
        required = [self.edtAccount, self.edtURL, self.edtPWD]
        for w in required:
            if not w.text().strip():
                w.setFocus()
                return False
        return True
    def on_edit_fields(self):
        self.btnApply.setEnabled(True)
        self.btnCancel.setEnabled(True)
        self.handle_action_msg(lambda msg_input: (True, msg_input), "edit mode")
    # endregion

    # region ── Slot button ──────────────────────────────
    def on_click_new(self):
        self._editing_id = None  # flag edition
        self.clear_fields(self.fields_to_clean())
        self.edtAccount.setFocus()
        # O lambda recebe o texto (*args) e o devolve na tupla de retorno
        self.handle_action_msg(lambda msg_input: (True, msg_input), "insert mode")
        self.btnApply.setEnabled(True)
        self.btnCancel.setEnabled(True)
        self.record_status(1)
    def on_click_cancel(self):
        self.record_status()
        self.handle_action_msg(lambda msg_input: (False, msg_input), "view mode")
        self.btnApply.setEnabled(False)
        self.btnCancel.setEnabled(False)

        # restoring data before editing
        for key, widget in self.mapping.items():
            if key == 0:
                keyName = 'user'
            elif key == 1:
                keyName = 'url'
            elif key == 2:
                keyName = "notes"
            elif key == 3:
                keyName = "ciphertext"

            value = self.initial_row_items.get(keyName, "")
            
            if hasattr(widget, "setPlainText"):
                widget.setPlainText(value)
            else:
                widget.setText(value)
    def on_click_action(self, row_id: int, text: str, informative: str):
        if confirm_dialog(text, informative):
            self.db.execute("DELETE FROM credentials WHERE id = ?", (row_id,))
            self.search_credential(self.search_field, self.edtSearch.text())
            self.btnSearch.click()
            self.clear_fields(self.fields_to_clean())
    def handle_action_on_save_record(self):
        if self._editing_id is None:
            ok, msg = self.insert_record("credentials")
        else:
            ok, msg = self.update_record("credentials", "id")

        self.lblStatusEditionOrError.setText(msg)
        self.lblStatusEditionOrError.setStyleSheet(
            "color: rgb(127, 255, 0);" if ok else "color:silver;"
        )
    def handle_action_msg(self, func, *args):
        ok, msg = func(*args)

        self.record_status(ok)
        self.lblStatusEditionOrError.setText(msg)
        self.lblStatusEditionOrError.setStyleSheet(
            "color: rgb(127, 255, 0);" if ok else "color:silver;"
        )
    def open_bug_report(self) -> None:
        QDesktopServices.openUrl(
            QUrl("http://github.com/TitoBarrosTI/hashedmaze/issues/new")
        )
    def on_close_clicked(self) -> None:
        self.close()    
    # endregion


