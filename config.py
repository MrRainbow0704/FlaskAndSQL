from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 80
DEBUG = True
SQLITE_PATH = ROOT_DIR / "db.sqlite3"

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = None
MYSQL_DBNAME = "MyTestDatabase"