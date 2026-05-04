# Hashed Maze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import re
from PySide6.QtCore import QTimer

from src.utils.resource_path import resource_path
class SettingsMixin:
    def _get_settings(self: "MainWindow"):
        sql = "SELECT search_field, sort_by, logoff_time, color_scheme FROM settings WHERE rowid = 1"
        result = self.state.db.fetch_one(sql)
        
        if result:
            self.state.ui.search_field = result["search_field"]
            self.state.ui.search_order = result["sort_by"]
            self.state.ui.logoff_time =  result["logoff_time"]
            self.state.ui.color_scheme =  result["color_scheme"]
            self.set_value_search_variable(result["search_field"])
            self.cbxDefaultFieldSearch.setCurrentText(result["search_field"])
            self.cbxDefaultFieldOrder.setCurrentText(result["sort_by"])
            self.cbxLogoffTime.setCurrentText('-' if result["logoff_time"] == 0 else str(result["logoff_time"]))
            self.cbxColorScheme.setCurrentText(result["color_scheme"])
            return
        
        self.state.ui.search_field = "all fields"
        self.state.ui.search_order = "url"
        self.state.ui.color_scheme = "tokio_night"

    def _set_settings(self: "MainWindow", settings: dict | None = None) -> bool:
        if settings is None:
            settings = {"search_field":"user", "sort_by":"url", "logoff_time":"300000", "color_scheme":"tokio_night"}

        cols = ", ".join([f"{key} = ?" for key in settings])
        sql = f"UPDATE settings SET {cols}"
        values = tuple(settings.values())

        try:
            self.state.db.execute(sql, tuple(values))
            self.state.ui.logoff_time = settings.get("logoff_time")
            return True
        except Exception as e:
            return False

    def _feedback_settings(self: "MainWindow", success: bool):
        if success:
            self.lblSettings.setStyleSheet("color: rgb(20, 182, 71);")
            self.lblSettings.setText("Settings saved")
        else:
            self.lblSettings.setStyleSheet("color: rgb(220, 50, 50);")
            self.lblSettings.setText("Error saving settings")
        
        QTimer.singleShot(5000, lambda: self.lblSettings.setStyleSheet("color: rgb(160, 160, 160);"))

    def on_change_search_order(self: "MainWindow"):
        column = self.cbxDefaultFieldOrder.currentText().replace(' ','_')
        self.state.ui.search_order = column        

        result = re.sub(r'(?<=ordered by )\S+', f'{column})', self.lblSearchBy.text())

        self.lblSearchBy.setText(result)
        
        # save settings
        self._feedback_settings(self._set_settings(self._get_current_settings()))

    def on_change_search_field(self: "MainWindow"):
        column = self.cbxDefaultFieldSearch.currentText()
        self.state.ui.search_field = column

        result = re.sub(r'(?<=search by )[^(]+', f'{column} ', self.lblSearchBy.text())
        self.lblSearchBy.setText(result)

        result = re.sub(r'(?<=search by ).+', column, self.edtSearch.placeholderText())
        self.edtSearch.setPlaceholderText(result)

        # save settings
        self._feedback_settings(self._set_settings(self._get_current_settings()))

    def on_change_color_scheme(self: "MainWindow"):
        self.state.ui.color_scheme = self.cbxColorScheme.currentText()

        # save settings
        self._feedback_settings(self._set_settings(self._get_current_settings()))
        self._apply_color_scheme()
    
    def _get_current_settings(self: "MainWindow") -> dict:
        return {
            "search_field": self.cbxDefaultFieldSearch.currentText(),
            "sort_by": self.cbxDefaultFieldOrder.currentText(),
            "logoff_time": int(self.cbxLogoffTime.currentText()) if self.cbxLogoffTime.currentText() != '-' else 0,
            "color_scheme": self.cbxColorScheme.currentText(),            
        }

    def _apply_color_scheme(self: "MainWindow") -> None:
        self.setStyleSheet(self._get_color_scheme_qss())
    
    def _get_color_scheme_qss(self: "MainWindow") -> str:
        schemes = {
            "tokio_night": "src/styles/tokio_night.qss",
            "catppuccin_mocha": "src/styles/catppuccin_mocha.qss",
            "dracula": "src/styles/dracula.qss",
            "nord": "src/styles/nord.qss",
            "gruvbox": "src/styles/gruvbox.qss",
            "one_dark": "src/styles/one_dark.qss",
        }

        path = schemes.get(self.state.ui.color_scheme)

        if path:
            with open(resource_path(path)) as f:
                return f.read()
        return ""
