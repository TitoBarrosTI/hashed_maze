import sys
import json
import struct
import sqlite3
import os
import logging
import socket
import traceback

# primeiríssima linha após os imports do stdlib
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.log")
logging.basicConfig(    
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.debug("bridge.py iniciado")

from src.config import db_path
from src.database import SQLiteDB
from src.crypt import CryptoVault

# 1. LOG configuration (Sasaved in C:\Hashed_Maze\debug.log)
# Since the script runs in the background, the log acts as its eyes and ears..
log_path = os.path.join(os.path.dirname(__file__), '..', 'debug.log')
logging.basicConfig(
    filename=log_path, 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_password_from_db(url):
    try:
        db = SQLiteDB(db_path)
        
        logging.info(f"Consultando banco para a URL: {url}")
        logging.debug(f"URL recebida para busca: repr={repr(url)}")

        # searching password based on URL sent by Edge
        sql = """
            SELECT ciphertext, salt, nonce FROM credentials 
            WHERE url LIKE ?
            OR ? LIKE url || '%'
            ORDER BY LENGTH(url) DESC
            LIMIT 1
        """
        row = db.fetch_one(sql,(f'%{url}%', url))
        
        if not row:
            return

        data_ = {"ciphertext": row['ciphertext'],
                 "salt": row['salt'],
                 "nonce": row['nonce']
        }

        master_password = get_master_password()
        if master_password is None:
            logging.error("The bridge could not obtain the master password.")
            return None
        
        return CryptoVault.decrypt(master_password, data_)
    except sqlite3.OperationalError as e:
        logging.error(f"Database operation failed: {e}")
        return None
    except RuntimeError as e:
        logging.error(f"Database connection error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error retrieving password: {e}")
        logging.debug(traceback.format_exc())
        return None
    
def listen():
    logging.info("--- Ponte HashedMaze Iniciada ---")
    
    try:
        while True:
            # Reading the message size from Edge (first 4 bytes)
            raw_length = sys.stdin.buffer.read(4)
            if not raw_length:
                logging.info("Conexão fechada pelo navegador.")
                break
            
            length = struct.unpack('I', raw_length)[0]
            
            # Reading the JSON content of the message
            # raw_data = sys.stdin.buffer.read(length).decode('utf-8')
            raw_data = read_full_message(length).decode('utf-8')
            message = json.loads(raw_data)
            logging.debug(f"Mensagem recebida: {message}")

            # If the extension asked for a password (action: "get")
            if message.get("action") == "get":
                senha_recuperada = get_password_from_db(message['url'])
                
                # Assembling the JSON response
                if senha_recuperada is None:
                    response_dict = {"status": "error", "reason": "app_locked"}
                else:
                    response_dict = {"status": "ok", "password": senha_recuperada}

                # response_dict = {"password": senha_recuperada}
                response_json = json.dumps(response_dict).encode('utf-8')
                
                # Sending back to Edge (Size + Content)
                sys.stdout.buffer.write(struct.pack('I', len(response_json)))
                sys.stdout.buffer.write(response_json)
                sys.stdout.buffer.flush()
                logging.debug(f"Resposta enviada com sucesso.")

    except Exception as e:
        logging.error(f"Erro crítico no loop de escuta: {str(e)}")

def read_full_message(n):
    data = b''
    while len(data) < n:
        chunk = sys.stdin.buffer.read(n - len(data))
        if not chunk:
            break
        data += chunk
    return data

def get_master_password():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5001))
        client.sendall(b"GET_MASTER_PASSWORD")
        response = client.recv(4096).decode().strip()
        client.close()

        if response.startswith("ERROR"):
            logging.error(response)
            return None
        return response
    except ConnectionRefusedError:
        logging.error("HashedMaze app is not running or user is not logged in.")
        return None    
    except Exception as e:
        logging.error(f"Failed to obtain the master password: {e}")
        return None

if __name__ == "__main__":
    import msvcrt
    import os
    # Força o stdin/stdout a ignorar conversões de texto do Windows
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    listen()