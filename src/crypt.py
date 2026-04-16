# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

import logging
import os
import base64

from hashlib import pbkdf2_hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hmac

from src.config import db_path
from src.database import SQLiteDB
from src.models import MasterKey

class CryptoVault:

    ITERATIONS = 200_000

    @staticmethod
    def derive_key(master_password: str, salt: bytes) -> bytes:
        return pbkdf2_hmac(
            "sha256",
            master_password.encode(),
            salt,
            CryptoVault.ITERATIONS,
            dklen=32
        )

    @staticmethod
    def encrypt(master_password: str, plaintext: str) -> dict:
        salt = os.urandom(16)
        key = CryptoVault.derive_key(master_password, salt)
        aes = AESGCM(key)
        nonce = os.urandom(12)

        ciphertext = aes.encrypt(
            nonce,
            plaintext.encode(),
            None
        )

        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode()            
        }

    @staticmethod
    def decrypt(master_password: str, data: dict) -> str:
        salt = base64.b64decode(data["salt"])
        nonce = base64.b64decode(data["nonce"])
        ciphertext = base64.b64decode(data["ciphertext"])
        key = CryptoVault.derive_key(master_password, salt)
        aes = AESGCM(key)
        return aes.decrypt(nonce, ciphertext, None).decode()   

    # @staticmethod
    # def generate_hash_login(master_password:str) -> tuple:
    #     salt = os.urandom(16)
    #     # your derive_key to generate the hash
    #     hash_login = CryptoVault.derive_key(master_password, salt)
    #     return base64.b64encode(hash_login).decode(), base64.b64encode(salt).decode()
    
    @staticmethod
    def generate_hash_login(master_password: str) -> tuple[bytes, bytes, str, str]:
        salt = os.urandom(16)
        hash_login = CryptoVault.derive_key(master_password, salt)

        hash_b64 = base64.b64encode(hash_login).decode()
        salt_b64 = base64.b64encode(salt).decode()

        return hash_login, salt, hash_b64, salt_b64

    @staticmethod
    def has_master_hash() -> bool | None:
        db = SQLiteDB(db_path)
        logging.debug(f"Database path: {db.db_path}")

        result = db.fetch_one("SELECT COUNT(*) as total FROM hash")
        return result is not None and result['total'] > 0
    
    @staticmethod
    def get_master_hash() -> MasterKey | None:
        db = SQLiteDB(db_path)
        result = db.fetch_one("SELECT mkhash, salt FROM hash LIMIT 1")
        if result:
            return MasterKey(hash=result['mkhash'], salt=result['salt'])
        return None

    # To check when attempting to access the app
    @staticmethod
    def hash_login_verify(typed_password, salt_db, hash_db):
        novo_hash = CryptoVault.derive_key(typed_password, salt_db)
        return hmac.compare_digest(novo_hash, hash_db)
    
def generate_random_password(width=15,numbers=True,symbols=True,capitalLetters=True) -> str:
    import secrets
    import string

    base = string.ascii_lowercase

    if width < 1:
        width = 15
    
    map = {
        "numbers": string.digits,
        "symbols": string.punctuation,
        "capitalLetters": string.ascii_uppercase
    }

    flags = {
        "numbers": bool(numbers),
        "symbols": bool(symbols),
        "capitalLetters": bool(capitalLetters)
    }
    
    chars = base + "".join(map[k] for k in flags if flags[k] is True)

    return ''.join(secrets.choice(chars) for _ in range(width))    
