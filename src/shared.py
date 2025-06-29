from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_htmx import HTMX
from flask_limiter import Limiter

ROOT_PATH: str = "/var/lib/signpost"
DB_PATH: str = f"{ROOT_PATH}/database.db"
PW_BIN_PATH: str = f"{ROOT_PATH}/password.bin"
API_SECRET_PATH: str = f"{ROOT_PATH}/secret.txt"
DATA_VERSION_PATH: str = f"{ROOT_PATH}/data_version.txt"

app: Flask = Flask(__name__)
db: SQLAlchemy = None
htmx: HTMX = HTMX()
# limiter: Limiter = Limiter()