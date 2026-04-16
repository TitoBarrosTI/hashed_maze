# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from src.database import SQLiteDB
from src.config import db_path
class CryptoState:
    def __init__(self):
        self.master_hash: str | None = None
        self.salt_hash: bytes | None = None
        self.derived_key: str | None = None
        self.decrypted_pass: str | None = None
        self.credential_plaintext: str | None = None

class UIState:
    def __init__(self):
        self.search_field: str | None = None
        self.current_id: int | None = None
        self.editing_id: int | None = None
        self.initial_row_items: dict = {}

class AppState:
    def __init__(self, db_path):
        # self.db = self.SQLiteDB(db_path)
        self.db = SQLiteDB(db_path)
        self.db.initialize()
        self.crypto = CryptoState()
        self.ui = UIState()

app_state = AppState(db_path)
