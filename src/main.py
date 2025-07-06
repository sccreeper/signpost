import os
from flask_limiter import Limiter
from flask_compress import Compress
from flask import request

from src.shared import app, htmx, DB_PATH, CF_IP_HEADER
from src.db.db import db
from src.db import init_db

def get_real_ip() -> str:
    """Gets user IP. Some logic required to figure out if behind Cloudflare or not.

    Args:
        req (Request): The request object to be checked.

    Returns:
        str: Resulting IP
    """

    if CF_IP_HEADER in request.headers:
        return request.headers[CF_IP_HEADER]
    else:
        return request.remote_addr

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SECRET_KEY"] = os.environ["SECRET"]

limiter = Limiter(
    get_real_ip,
    default_limits=[f"{os.environ["RATE_LIMIT"]} per second"],
    storage_uri="memory://"
)

compress = Compress()

init_db()
db.init_app(app)

htmx.init_app(app)
compress.init_app(app)
limiter.init_app(app)

from src.handlers import *

if __name__ == "__main__":
    app.run(
        host="0.0.0.0", 
        port=8080, 
        debug=os.environ["DEBUG"].lower() == "true"
    )