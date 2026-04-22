# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License
from operator import truediv
import os
import re
import base64
import logging
from doctest import master
import sqlite3
from functools import partial

from PySide6.QtCore import Qt, QTimer, QSettings, QEvent, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap, QIcon, QWindowStateChangeEvent
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import (
    QApplication,
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

from src.config import db_path, APP_VERSION
from src.popup_hint import PopupHint
from src.crypt import CryptoVault, generate_random_password
from roundedframe import RoundedFrame
from src.utils.resource_path import resource_path
from src.utils.password_strength import calculate_force
from src.utils.dialogs import confirm_dialog
from src.core.state import app_state, AppState
from ui.helpers.animations import shake_widget
from src.popup_help import PopupHelp

# Resolve resource path for dev and PyInstaller (_MEIPASS) environments
Ui_MainWindow, BaseClass = loadUiType(resource_path("ui/forms/main_window_hashed_maze.ui"))  # type: ignore

class MainWindow(BaseClass, Ui_MainWindow):
    def __init__(self, app_state, parent=None):
        super().__init__()
        self.setupUi(self)
        self.state: AppState = app_state
        self.setFixedSize(self.size())
        self.pBar.setRange(0, 100)
        self.pBar.setTextVisible(False)
        self.lblCFGDatabaseDirectory.setText(db_path)
        self.lblVersion.setText(APP_VERSION)

        # hiding the column password
        self.treeCredentialsResponse.setColumnHidden(3, True)

        # decides which screen will be opened
        self._setup_initial_screen()

        # region ── popup_hint (resume)
        self._popup = PopupHint(dark_mode=True)
        self._last_item = None
        self._hide_timer = QTimer(singleShot=True)
        self._hide_timer.timeout.connect(self._popup.hide)
        self.treeCredentialsResponse.setMouseTracking(True)
        self.treeCredentialsResponse.viewport().installEventFilter(self)
        # endregion

        # region ── tree widget header adjusts
        header = self.treeCredentialsResponse.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        # endregion

        # signal/slot connections
        # sitting editing status check ───────────────
        fields_in_form = [self.edtAccount, self.edtURL, self.edtPWD, self.edtPlainNotes]
        for f in fields_in_form:
            f.textChanged.connect(self.on_edit_fields)

        # region ── defining and creating actions in the search menu
        self.search_actions = {}
        menuSearch = QMenu(self)

        for name in ("all fields","created_at","user", "url", "notes"):
            act = menuSearch.addAction(name)
            act.triggered.connect(partial(self.set_value_search_variable, name))
            self.search_actions[name] = act  # Save the action by name

        self.search_actions["all fields"].trigger()

        self.btnSearchBy.setMenu(menuSearch)
        self.btnSearchBy.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btnSearch.clicked.connect(
            lambda: self.search_credential(self.state.ui.search_field, self.edtSearch.text(),self.state.ui.search_order)
        )

        self.edtSearch.returnPressed.connect(
            lambda: self.search_credential(self.state.ui.search_field, self.edtSearch.text(),self.state.ui.search_order)
        )
        # endregion 

        # sitting ordering search and field search by selected field
        self.cbxDefaultFieldSearch.activated.connect(self.on_change_search_field)
        self.cbxDefaultFieldOrder.activated.connect(self.on_change_search_order)

        # region ─ button tips
        self._help_search = PopupHelp(
            title="SEARCH",
            body="Use 'search by' to filter by a specific field\n"
                "(account, url, notes) or search across all fields.\n"
                "Type and press 'search' to find your credentials.",
            dark_mode=True,
        )

        self._help_credentials = PopupHelp(
            title="CREDENTIALS",
            body="Click any result above to load its data here.\n"
                "Edit the fields and press 'apply' to save changes.\n"
                "Use 'new' to create a fresh credential entry.",
            dark_mode=True,
        )

        self._help_general_config = PopupHelp(
            title="GENERAL CONFIGURATION",
            body="Define the default field for searches and how\n"
                "results are filtered. Changes apply immediately\n"
                "on the next search.",
            dark_mode=True,
        )

        self._help_manage_password = PopupHelp(
            title="MANAGE MASTER PASSWORD",
            body="To change your master password, enter your\n"
                "current password, then type and confirm\n"
                "the new one. All credentials will be\n"
                "re-encrypted automatically.",
            dark_mode=True,
        )

        self.btnHelpSearch.enterEvent = lambda e: self._help_search.show_near(self.btnHelpSearch)
        self.btnHelpSearch.leaveEvent = lambda e: self._help_search.close()

        self.btnHelpCredentials.enterEvent = lambda e: self._help_credentials.show_near(self.btnHelpCredentials)
        self.btnHelpCredentials.leaveEvent = lambda e: self._help_credentials.close()

        self.btnGeneralCFG.enterEvent = lambda e: self._help_general_config.show_near(self.btnGeneralCFG)
        self.btnGeneralCFG.leaveEvent = lambda e: self._help_general_config.close()

        self.btnManagerPWDCFG.enterEvent = lambda e: self._help_manage_password.show_near(self.btnManagerPWDCFG)
        self.btnManagerPWDCFG.leaveEvent = lambda e: self._help_manage_password.close()                        
        
        self.btnGenRandomPWD.clicked.connect(lambda e: self.edtPWD.setText(generate_random_password()))
        # endregion ─ button tips
        
        # endregion signal/slot connections

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
        self.btnSavePWD.clicked.connect(self.change_master_password)

        # region ── icons/images tasks
        self.tabWidget.setCurrentIndex(2)
        self.tabWidget.currentChanged.connect(self.update_icon)
        self.update_icon(self.tabWidget.currentIndex())
        self.btnShowPWD.setIcon(QIcon("static/icons/visibility_20.png"))
        self.btnApply.setIcon(QIcon("static/icons/apply_20.png"))
        self.lblBG.setPixmap(QPixmap("docs/screenshots/bgabout.jpg"))
        # endregion ── icons/images tasks

        self.btnLnkReportABug.clicked.connect(self.open_bug_report)
        self.btnLnkBuymeCoffee.clicked.connect(self.open_buy_me_a_coffee)
        self.btnClose.clicked.connect(self.on_close_clicked)

        # components config
        self.btnApply.setEnabled(False)
        self._get_settings()

    # region ── Crud methods ──────────────────────────────
    def search_credential(self, field, filter,order_col) -> None:
        try:
            if not field or not filter:
                return
            
            # mounting WHERE clause
            if field == "all fields":
                where = """WHERE user LIKE ? OR
                           url LIKE ? OR
                           notes LIKE ? OR
                           created_at LIKE ?                
                """ if filter else ""
                params = (f"%{filter}%", f"%{filter}%", f"%{filter}%", f"%{filter}%") if filter else ()
            else:
                where = f"WHERE {field} LIKE ?" if filter else ""            
                params = (f"%{filter}%",) if filter else ()

            sql = f"""
            SELECT id, user, url, ciphertext, 
                   salt, nonce, notes, created_at,
                   COUNT(*) OVER() AS total
            FROM credentials
            {where}
            ORDER BY {order_col or 'ROWID'} ASC
            """
            rows = self.state.db.fetch_all(sql, params)
            self.treeCredentialsResponse.clear()

            if not rows:
                self.lblResults.setText("-- no results --")
                return

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
        if table == 'credentials':
            if not self._required_fields_ok() or not self.state.crypto.decrypted_pass:
                return (False, "Fill in the required field")

            vault = CryptoVault.encrypt(self.state.crypto.decrypted_pass, self.edtPWD.text())

            data = {
                "user": self.edtAccount.text(),
                "url": self.edtURL.text(),
                "notes": self.edtPlainNotes.toPlainText(),
                "ciphertext": vault["ciphertext"],
                "salt": vault["salt"],
                "nonce": vault["nonce"],
            }
        elif table == "hash":
            if not self.edtNewPWDConfirm.text():
                return (False, "Fill in the required field")
            
            ash_login, salt, hash_b64, salt_b64 = CryptoVault.generate_hash_login(self.edtNewPWDConfirm.text())

            data = {
                "mkhash": hash_b64,
                "salt": salt_b64
            }

        try:
            if table == 'hash':
                cols = ", ".join([f"{key} = ?" for key in data.keys()])
                sql = f"UPDATE {table} SET {cols}"
                values = tuple(data.values())
            else:
                cols = ", ".join([f"{key} = ?" for key in data.keys()])
                sql = f"UPDATE {table} SET {cols} WHERE {where} = ?"
                values = list(data.values())
                values.append(str(self.state.ui.editing_id))

            self.state.db.execute(sql, tuple(values))

            self.btnSearch.click()
        except Exception as e:
            print(f"Error on update: {e}")

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
        if self.state.crypto.derived_key is None:
            return False, "Derived_key is None"
        
        try:
            if not self.state.crypto.decrypted_pass is None:
                vault = CryptoVault.encrypt(self.state.crypto.decrypted_pass, self.edtPWD.text())

            payload = {
                "user": self.edtAccount.text(),
                "url": self.edtURL.text(),
                "notes": self.edtPlainNotes.toPlainText(),
                "ciphertext": vault["ciphertext"],
                "salt": vault["salt"],
                "nonce": vault["nonce"],
            }

            new_id = self.state.db.insert(table, payload)
        except Exception as e:
            return False, f"Error on insert :{e}"

        self.clear_fields(self.fields_to_clean())
        self.state.ui.editing_id = new_id
        self.btnApply.setEnabled(False)
        self.btnCancel.setEnabled(False)
        self.on_action_finished()

        return True, "Inserted successfully"
    
    def load_data_row(self, mapping: dict, item, _) -> None:
        # visual feedback
        self.visual_feedback_on_record_status(1)
        self.state.ui.editing_id = item.data(0, Qt.ItemDataRole.UserRole) # flag edition
        data_items = item.data(1, Qt.ItemDataRole.UserRole)

        # Saving initial data received from treecredentials for rollback if editing is cancelled
        self.state.ui.initial_row_items = {
            k: item.text(i)
            for i, k in enumerate(["user","url","notes","ciphertext"])
        }

        for col_index, widget in mapping.items():
            # special condition for same component type (QLineEdit)
            if widget == self.edtPWD:
                if data_items:
                    ciphertext = data_items.get("ciphertext")
                    salt = data_items.get("salt")
                    nonce = data_items.get("nonce")
                    data_ = {"ciphertext": ciphertext, "salt": salt, "nonce": nonce}
                    
                    if self.state.crypto.derived_key is None:
                        return

                    if not self.state.crypto.decrypted_pass is None:
                     plaintext = CryptoVault.decrypt(self.state.crypto.decrypted_pass, data_)
                     
                    self.state.crypto.credential_plaintext = plaintext
                    widget.setText(str(plaintext))

                    # overwrite with plaintext
                    self.state.ui.initial_row_items["ciphertext"] = str(plaintext)
                continue
            
            value = item.text(col_index)

            if isinstance(widget, (QLineEdit, QLabel)):
                 widget.setText(str(value))
            elif isinstance(widget, QPlainTextEdit):
                widget.setPlainText(str(value))
            elif isinstance(widget, QListWidget):
                widget.clear()
                widget.addItems(str(value).splitlines())
    # endregion ── Crud methods ────────────────────────────

    # region ── Setup ─────────────────────────────────────
    def _setup_initial_screen(self):
        if CryptoVault.has_master_hash():
            from src.login_window_hashed_maze import LoginWindow
            self.login_or_hash = LoginWindow(self.state, parent=self)
        else:
            from src.master_pass_hashed_maze import MasterPass
            self.login_or_hash = MasterPass(app_state, parent=self)
        
        self.hide()

        if self.login_or_hash.exec():
            self.show()
        else:
            self.close()

    def _get_settings(self):
        sql = "SELECT search_field, sort_by FROM settings WHERE rowid = 1"
        result = self.state.db.fetch_one(sql)
        
        if result:
            self.state.ui.search_field = result["search_field"]
            self.state.ui.search_order = result["sort_by"]
            self.set_value_search_variable(result["search_field"])
            self.cbxDefaultFieldSearch.setCurrentText(result["search_field"])
            self.cbxDefaultFieldOrder.setCurrentText(result["sort_by"])
            return
        
        self.state.ui.search_field = "all fields"
        self.state.ui.search_order = "url"

    def _set_settings(self, settings: dict | None = None) -> bool:
        if settings is None:
            settings = {"search_field":"user", "sort_by":"url"}

        cols = ", ".join([f"{key} = ?" for key in settings])
        sql = f"UPDATE settings SET {cols}"
        values = tuple(settings.values())
        
        try:
            self.state.db.execute(sql, tuple(values))
            return True
        except Exception as e:
            return False

    def _feedback_settings(self, success: bool):
        if success:
            self.lblSettings.setStyleSheet("color: rgb(20, 182, 71);")
            self.lblSettings.setText("Settings saved")
        else:
            self.lblSettings.setStyleSheet("color: rgb(220, 50, 50);")
            self.lblSettings.setText("Error saving settings")        
    # endregion ── Setup ─────────────────────────────────────

    # region ── UI helpers ────────────────────────────────
    def update_icon(self, index) -> None:
        if index == 0:
            self.lblIconSearch.setPixmap(QPixmap("static/icons/database_search_40_clear_green"))            
        if index == 1:
            self.lblIconConfig.setPixmap(QPixmap("static/icons/settings_40_green.png"))
        if index == 2:
            self.lblIconAbout.setPixmap(QPixmap("static/icons/about_40_green.png"))
    
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

    def visual_feedback_on_record_status(self, status = None):
        # receives integer or None (_editing_id)
        if not status:
            self.frmStatusEdition.set_status_colors(None)
        else:
            self.frmStatusEdition.set_status_colors("#b7d9b1", "#a3c9a0", "#92b68f")
    
    def set_value_search_variable(self, name) -> None:
        # after select option in context menu search
        self.state.ui.search_field = name
        self.edtSearch.clear()
        self.edtSearch.setPlaceholderText(f"search by {name}")
        self.edtSearch.setFocus()
        ordering = self.state.ui.search_order
        self.lblSearchBy.setText(f"search by {name} (ordered by {ordering if ordering else 'id'})")
    
    def verify_password_before_change(self, typed_password: str) -> bool:
        salt_bytes = base64.b64decode(self.state.crypto.salt_hash) # type: ignore
        try_key = CryptoVault.derive_key(typed_password, salt_bytes)
        db_hash_bytes = base64.b64decode(self.state.crypto.master_hash) # type: ignore
        return try_key == db_hash_bytes
    
    def _log(self, msg: str, color: Qt.GlobalColor = Qt.GlobalColor.green) -> None:
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
    # endregion UI helpers ────────────────────────────────

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
    # endregion ── Form state ────────────────────────────────

    # region ── Slot button ──────────────────────────────
    def on_click_new(self):
        # Store the value for rollback on cancel.
        self.state.ui.editing_id_before_cancel = self.state.ui.editing_id
        self.state.ui.editing_id = None  # flag edition (Single point of assignment to None)
        self.clear_fields(self.fields_to_clean())
        self.edtAccount.setFocus()
        # O lambda recebe o texto (*args) e o devolve na tupla de retorno
        self.handle_action_msg(lambda msg_input: (True, msg_input), "insert mode")
        self.btnApply.setEnabled(True)
        self.btnCancel.setEnabled(True)
        self.visual_feedback_on_record_status(1)
    
    def on_click_cancel(self):
        # restoring value of id
        self.state.ui.editing_id = self.state.ui.editing_id_before_cancel

        self.visual_feedback_on_record_status()
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

            value = self.state.ui.initial_row_items.get(keyName, "")
            
            if hasattr(widget, "setPlainText"):
                widget.setPlainText(value)
            else:
                # if it's ciphertext only and has listed items
                if key == 3 and self.state.ui.editing_id is not None:
                    value = self.state.crypto.credential_plaintext or ""
                widget.setText(value)
    
    def on_click_action(self, row_id: int, text: str, informative: str):
        if confirm_dialog(text, informative):
            self.state.db.execute("DELETE FROM credentials WHERE id = ?", (row_id,))
            self.search_credential(self.state.ui.search_field, self.edtSearch.text(),self.state.ui.search_order)
            self.btnSearch.click()
            self.clear_fields(self.fields_to_clean())
    
    def handle_action_on_save_record(self):
        if self.state.ui.editing_id is None:
            ok, msg = self.insert_record("credentials")
        else:
            ok, msg = self.update_record("credentials", "id")

        self.lblStatusEditionOrError.setText(msg)
        self.lblStatusEditionOrError.setStyleSheet(
            "color: rgb(127, 255, 0);" if ok else "color:silver;"
        )
    
    def handle_action_msg(self, func, *args):
        ok, msg = func(*args)

        self.visual_feedback_on_record_status(ok)
        self.lblStatusEditionOrError.setText(msg)
        self.lblStatusEditionOrError.setStyleSheet(
            "color: rgb(127, 255, 0);" if ok else "color:silver;"
        )
    
    def open_bug_report(self) -> None:
        QDesktopServices.openUrl(
            QUrl("https://github.com/TitoBarrosTI/hashed_maze/issues/new")
        )

    def open_buy_me_a_coffee(self) -> None:
        QDesktopServices.openUrl(
            QUrl("https://ko-fi.com/titobarrosti")
        )        
    
    def change_master_password(self):
        # getting/verifying current/new master password
        typed = self.edtCurrentPWD.text().strip()
        current = app_state.crypto.decrypted_pass
        
        if not typed:
            self.edtCurrentPWD.setFocus()
            shake_widget(self, self.edtCurrentPWD)
            self._log("Interrupted: current memory master password cannot be empty", Qt.GlobalColor.darkYellow)
            return

        if not current == typed:
            self.edtCurrentPWD.setFocus()
            shake_widget(self, self.edtCurrentPWD)
            self._log(f"Interrupted: typed password {typed} is not correct", Qt.GlobalColor.darkYellow)
            return
        
        # verifying new master password and confirmation
        new = self.edtNewPWD.text().strip()
        confirm = self.edtNewPWDConfirm.text().strip()

        if not new == confirm:
            shake_widget(self, self.edtNewPWD)
            shake_widget(self, self.edtNewPWDConfirm)
            self._log(f'Interrupted: new password {new} and confirm {confirm} is not equals', Qt.GlobalColor.darkYellow)
            return

        fields = {
            "current pwd": self.edtCurrentPWD,
            "new pwd": self.edtNewPWD,
            "confirm pwd": self.edtNewPWDConfirm,
        }

        for name, field in fields.items():
            if not field.text().strip():
                field.setFocus()
                shake_widget(self, field)
                self._log(f"Interrupted: field {name} cannot be empty", Qt.GlobalColor.darkYellow)
                break
        
        # re-encrypt all credentials with new password
        rows = self.state.db.fetch_all("SELECT id, ciphertext, salt, nonce, url FROM credentials")
        self._log(f"Found {len(rows)} credentials to re-encrypt...")
        logging.debug(f"Starting re-encryption for {len(rows)} credentials")
        
        row = None
        try:
            updates = []

            for i, row in enumerate(rows,1):
                self._log(f"Re-encrypting credential {i} of {len(rows)}...")
                data_ = {"ciphertext": row["ciphertext"], "salt": row["salt"], "nonce": row["nonce"]}
                plaintext = CryptoVault.decrypt(self.state.crypto.decrypted_pass, data_) # type: ignore
                new_vault = CryptoVault.encrypt(new, plaintext)
                updates.append((new_vault["ciphertext"], new_vault["salt"], new_vault["nonce"], row["id"]))
                logging.debug(f"Re-encrypted credential id={row['id']}")

            # new session
            self._log("Generating new session key...")
            hash_bytes, salt_bytes, hash_b64, salt_b64 = CryptoVault.generate_hash_login(new)

            # all atomic commiting
            with self.state.db.transaction() as conn:
                for upd in updates:
                    conn.execute("UPDATE credentials SET ciphertext=?, salt=?, nonce=? WHERE id=?", upd)
                self._log("Updating master hash...")
                conn.execute("UPDATE hash SET mkhash=?, salt=?", (hash_b64, salt_b64))

            self._log("Done. Master password changed successfully.", color=Qt.GlobalColor.green)

            # region (updating data to crypto state)
            app_state.crypto.salt_hash = salt_bytes
            app_state.crypto.master_hash = hash_b64
            app_state.crypto.decrypted_pass = new
            # endregion
        except Exception as e:
            if row:
                self._log(
                    f"Interrupted: {type(e).__name__} - id={row['id']} url={row['url']} "
                    f"| nonce={row['nonce'][:8]}... salt={row['salt'][:8]}...",
                    color=Qt.GlobalColor.red
            )
            else:
                self._log(f"Interrupted: {type(e).__name__}: {e!r}", color=Qt.GlobalColor.red)
            return

    def on_close_clicked(self) -> None:
        self.close()    
    
    def on_change_search_order(self):
        column = self.cbxDefaultFieldOrder.currentText().replace(' ','_')
        self.state.ui.search_order = column        

        result = re.sub(r'(?<=ordered by )\S+', f'{column})', self.lblSearchBy.text())

        self.lblSearchBy.setText(result)
        
        self._feedback_settings(self._set_settings({
            "search_field": self.cbxDefaultFieldSearch.currentText().replace(' ', '_'),
            "sort_by": self.cbxDefaultFieldOrder.currentText(),
        }))

    def on_change_search_field(self):
        column = self.cbxDefaultFieldSearch.currentText()
        self.state.ui.search_field = column

        result = re.sub(r'(?<=search by )[^(]+', f'{column} ', self.lblSearchBy.text())
        self.lblSearchBy.setText(result)

        result = re.sub(r'(?<=search by ).+', column, self.edtSearch.placeholderText())
        self.edtSearch.setPlaceholderText(result)

        self._feedback_settings(self._set_settings({
            "search_field": self.cbxDefaultFieldSearch.currentText(),
            "sort_by": self.cbxDefaultFieldOrder.currentText(),
        }))
    # endregion ── Slot button ──────────────────────────────
