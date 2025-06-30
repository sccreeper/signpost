from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
import subprocess
from argon2 import PasswordHasher
import uuid

from src.shared import DATA_VERSION_PATH, DB_PATH, PW_BIN_PATH, API_SECRET_PATH
from src.db.models import BaseModel

def v0_migrate():
    # Initial version, i.e. no data

    engine = create_engine(f"sqlite:///{DB_PATH}")

    with Session(engine) as session:
        BaseModel.metadata.create_all(engine)
        session.commit()

    engine.dispose()

    version_f = open(DATA_VERSION_PATH, "w")
    version_f.write(str("0"))
    version_f.close()

    password_f = open(PW_BIN_PATH, "w")
    pw_hashed = PasswordHasher().hash("password")
    password_f.write(pw_hashed)
    password_f.close()

    api_secret_f = open(API_SECRET_PATH, "w")
    api_secret_f.write(str(uuid.uuid4()))
    api_secret_f.close()


def migrate(old_ver: int, cur_ver: int):

    while old_ver < cur_ver:
        match old_ver:
            case -1:
                v0_migrate()

        old_ver += 1

    f = open(DATA_VERSION_PATH, "w")
    f.write(str(cur_ver))
    f.close()

    subprocess.call(["reboot", "now"])


def init_db():

    if not os.path.exists(DATA_VERSION_PATH):
        migrate(-1, int(os.environ["DATA_VERSION"]))
    else:
        f = open(DATA_VERSION_PATH, "r")

        old_ver = int(f.read())
        cur_ver = int(os.environ["DATA_VERSION"])

        f.close()

        if old_ver != cur_ver:
            migrate(old_ver, cur_ver)

db: SQLAlchemy = SQLAlchemy(model_class=BaseModel)