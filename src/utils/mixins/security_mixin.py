# MCacheBox
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from PySide6.QtCore import Qt, QTimer
import logging
from ui.helpers.animations import shake_widget

from src.crypt import CryptoVault
# from src.utils.mixins.helpers_mixin import HelpersMixin
# from utils.mixins import helpers_mixin

# class SecurityMixin(HelpersMixin):
class SecurityMixin():
    def verify_password_before_change(self: "MainWindow", typed_password: str) -> bool:
        salt_bytes = base64.b64decode(self.state.crypto.salt_hash) # type: ignore
        try_key = CryptoVault.derive_key(typed_password, salt_bytes)
        db_hash_bytes = base64.b64decode(self.state.crypto.master_hash) # type: ignore
        return try_key == db_hash_bytes
    
    def change_master_password(self: "MainWindow"):
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

    def auto_logoff(self):
        self.state.crypto.decrypted_pass = None
        self._do_login()
    
    def _reset_logoff_timer(self: "MainWindow"):
        if hasattr(self, '_logoff_timer'):
            self._logoff_timer.stop()
        self._logoff_timer = QTimer(self)
        self._logoff_timer.setSingleShot(True)
        self._logoff_timer.timeout.connect(self.auto_logoff)
        
        # only starts timer if value its above 0
        if self.state.ui.logoff_time != 0:
            self._logoff_timer.start(self.state.ui.logoff_time)

        # atualiza o display
        if not hasattr(self, '_countdown_timer'):
            self._countdown_timer = QTimer(self)
            self._countdown_timer.timeout.connect(self._update_countdown)
            self._countdown_timer.start(1000)

    def _update_countdown(self: "MainWindow"):
        if hasattr(self, '_logoff_timer'):
            remaining = self._logoff_timer.remainingTime() // 1000
            self.statusBar().showMessage(
                f"logoff in: {remaining}s" if self.state.ui.logoff_time != 0 else "auto-logoff disabled"
            )
