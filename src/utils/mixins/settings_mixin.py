import re
from PySide6.QtCore import QTimer

class SettingsMixin:
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
        
        QTimer.singleShot(5000, lambda: self.lblSettings.setStyleSheet("color: rgb(160, 160, 160);"))

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