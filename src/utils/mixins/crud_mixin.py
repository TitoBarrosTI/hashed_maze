# Hashed Maze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QListWidget,
    QTreeWidgetItem,
    QLineEdit,
    QPlainTextEdit,
    QLabel,
)
from functools import partial
import sqlite3

from src.crypt import CryptoVault

class CrudMixin:
    def search_credential(self: "MainWindow", field, filter, order_col, page: int = 0) -> None:
        try:
            self.state.ui.last_field = field
            self.state.ui.last_filter = filter
            self.state.ui.last_order = order_col

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

            self.state.ui.current_page = page
            offset = page * self.state.ui.page_size
            
            sql = f"""
            SELECT id, user, url, ciphertext, 
                   salt, nonce, notes, created_at,
                   COUNT(*) OVER() AS total
            FROM credentials
            {where}
            ORDER BY {order_col or 'ROWID'} ASC
            LIMIT {self.state.ui.page_size} OFFSET {offset}
            """

            rows = self.state.db.fetch_all(sql, params)
            self.treeCredentialsResponse.clear()

            if not rows:
                self.lblResults.setText("-- no results --")
                self.lblPagination.setText("0 of 0")
                self._update_pagination_buttons()
                return

            total_records = rows[0]["total"]
            self.state.ui.total_pages = -(-total_records // self.state.ui.page_size)  # ceil division
            
            self.lblResults.setText(f"results: {total_records}")
            self.lblPagination.setText(f"{page + 1} of {self.state.ui.total_pages}")            
            
            for row in rows:
                item = QTreeWidgetItem(self.treeCredentialsResponse)

                self.btnDeleteAction = QPushButton("delete")
                self.btnDeleteAction.setFixedSize(57, 22)
                self.btnDeleteAction.clicked.connect(
                    partial(
                        self.on_click_action,
                        int(row["id"]),
                        self.tr(f"Really wants delete this access account?"),
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
            
            self._update_pagination_buttons()

        except sqlite3.OperationalError as e:
            print("Operational error:", e)

        except sqlite3.IntegrityError as e:
            print("integrity error:", e)

        except sqlite3.Error as e:
            print("general SQLite error:", e)

    def update_record(self: "MainWindow", table: str, where: str):
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
    
    def insert_record(self: "MainWindow", table: str):
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
    
    def load_data_row(self: "MainWindow", mapping: dict, item, _) -> None:
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
    
    # region ── pagination commands ──────────────────────────────
    def _update_pagination_buttons(self: "MainWindow") -> None:
        at_first = self.state.ui.current_page == 0
        at_last = self.state.ui.current_page >= self.state.ui.total_pages - 1

        self.btnFirst.setEnabled(not at_first)
        self.btnGoBack.setEnabled(not at_first)
        self.btnGoForward.setEnabled(not at_last)
        self.btnLast.setEnabled(not at_last)
    
    def _go_first_page(self: "MainWindow") -> None:
        self.search_credential(
            self.state.ui.last_field,
            self.state.ui.last_filter,
            self.state.ui.last_order,
            page=0
        )

    def _go_prev_page(self: "MainWindow") -> None:
        self.search_credential(
            self.state.ui.last_field,
            self.state.ui.last_filter,
            self.state.ui.last_order,
            page=self.state.ui.current_page - 1
        )

    def _go_next_page(self: "MainWindow") -> None:
        self.search_credential(
            self.state.ui.last_field,
            self.state.ui.last_filter,
            self.state.ui.last_order,
            page=self.state.ui.current_page + 1
        )

    def _go_last_page(self: "MainWindow") -> None:
        self.search_credential(
            self.state.ui.last_field,
            self.state.ui.last_filter,
            self.state.ui.last_order,
            page=self.state.ui.total_pages - 1
        )
    # endregion ── pagination commands ──────────────────────────────