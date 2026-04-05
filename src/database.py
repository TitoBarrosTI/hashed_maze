import os
from contextlib import contextmanager
import sqlite3
from typing import Any, Generator

class SQLiteDB:
    def __init__(self, db_path: str):
        # dir_name = os.path.dirname(db_path)
        self.db_path = db_path

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            yield conn
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"error on bank: {e}") from e
        finally:
            conn.close()

    def initialize(self) -> None:
        ddl = """
            CREATE TABLE IF NOT EXISTS credentials (
                id        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                user      TEXT(256) NOT NULL,
                url       TEXT NOT NULL,
                notes     TEXT,
                created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                ciphertext TEXT,
                salt      TEXT,
                nonce     TEXT
            );

            CREATE TABLE IF NOT EXISTS hash (
                mkhash     BLOB NOT NULL,
                salt       TEXT NOT NULL,
                created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
            );
        """
        with self._get_connection() as conn:
            conn.executescript(ddl)
            conn.commit()

    def execute(self, sql, params: tuple = ()) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
    
    def insert(self, table, data: dict):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))

        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self._get_connection() as conn:
            conn.execute(sql, tuple(data.values()))
            conn.commit()

    def update(self, table, data: dict, where: str, params: tuple):
        with self._get_connection() as conn:
            set_clause = ", ".join([f"{k}=?" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

            conn.execute(sql, tuple(data.values()) + params)
            conn.commit()

    def fetch_all(self, query, params: tuple = ()) -> list[dict] | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else None
    
    def fetch_one(self, query, params: tuple[Any, ...] = ()) -> dict | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row