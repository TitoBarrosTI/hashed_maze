import os
from src.database import SQLiteDB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, "hashedmazedb.db3")
db_path = r"C:\Projetos\WEB\python\REPOSITORIO\hashed_maze\src\hashedmazedb.db3"

db = SQLiteDB(db_path)