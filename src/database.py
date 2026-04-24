# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from contextlib import contextmanager
import sqlite3
from typing import Any, Generator

class SQLiteDB:
    def __init__(self, db_path: str):
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

    @contextmanager 
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        with self._get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

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

            CREATE TABLE IF NOT EXISTS settings (
                search_field TEXT NOT NULL DEFAULT 'all fields'
                    CHECK(search_field IN('all fields','created_at','user','url','notes')),
                sort_by TEXT NOT NULL DEFAULT 'url'
                    CHECK(sort_by IN('created_at','user','url')),
                logoff_time INT NOT NULL DEFAULT 300000
                    CHECK (logoff_time = 0 OR logoff_time >= 120000),
                updated_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
            );
        """

        insert_settings = "INSERT OR IGNORE INTO settings (rowid) VALUES (1);"

        with self._get_connection() as conn:
            conn.executescript(ddl)
            conn.execute(insert_settings)
            conn.commit()

    def execute(self, sql, params: tuple = ()) -> tuple[bool, str]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()        
            return True, "Done. Inserted successfully."
        except Exception as e: 
            return False, f"Fail: Execution failed: {e}"
    
    def insert(self, table, data: dict):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))

        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self._get_connection() as conn:
            cursor = conn.execute(sql, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid

    def update(self, table, data: dict, where: str, params: tuple):
        with self._get_connection() as conn:
            set_clause = ", ".join([f"{k}=?" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"

            conn.execute(sql, tuple(data.values()) + params)
            conn.commit()

    def fetch_all(self, query, params: tuple = ()) -> list[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def fetch_one(self, query:str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row