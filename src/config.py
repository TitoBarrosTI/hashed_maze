import os
from src.database import SQLiteDB

APP_VERSION = "1.1.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "hashedmazedb.db3")

db = SQLiteDB(db_path)