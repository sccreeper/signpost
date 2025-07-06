from flask import Flask
from flask_htmx import HTMX

ROOT_PATH: str = "/var/lib/signpost"
DB_PATH: str = f"{ROOT_PATH}/database.db"
PW_BIN_PATH: str = f"{ROOT_PATH}/password.bin"
API_SECRET_PATH: str = f"{ROOT_PATH}/secret.txt"
DATA_VERSION_PATH: str = f"{ROOT_PATH}/data_version.txt"

CF_IP_HEADER: str = "CF-Connecting-IP"

app: Flask = Flask(__name__)
htmx: HTMX = HTMX()