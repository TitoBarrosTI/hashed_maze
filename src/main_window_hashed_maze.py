# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from operator import truediv
import os
import re
import base64
import logging
from doctest import master
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
from src.utils.mixins.settings_mixin import SettingsMixin
from src.utils.mixins.crud_mixin import CrudMixin
from src.utils.mixins.helpers_mixin import HelpersMixin
from src.utils.mixins.security_mixin import SecurityMixin

# Resolve resource path for dev and PyInstaller (_MEIPASS) environments
Ui_MainWindow, BaseClass = loadUiType(resource_path("ui/forms/main_window_hashed_maze.ui"))  # type: ignore

class MainWindow(BaseClass, Ui_MainWindow, SettingsMixin, CrudMixin, SecurityMixin, HelpersMixin):
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
    # endregion ── Setup ─────────────────────────────────────

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

        # self.visual_feedback_on_record_status(None)
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
        
        self.visual_feedback_on_record_status(None)
    
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

    def on_close_clicked(self) -> None:
        self.close()    
    # endregion ── Slot button ──────────────────────────────
