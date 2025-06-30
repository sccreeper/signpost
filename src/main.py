import os

from src.shared import app, htmx, DB_PATH
from src.db.db import db
from src.db import init_db

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SECRET_KEY"] = os.environ["SECRET"]

init_db()
db.init_app(app)
htmx.init_app(app)

from src.handlers import *

if __name__ == "__main__":
    app.run(
        host="0.0.0.0", 
        port=8080, 
        debug=os.environ["DEBUG"].lower() == "true"
    )