from flask import Flask
import os

from src.shared import app, db
from src.db import init_db

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0", 
        port=8080, 
        debug=os.environ["DEBUG"].lower() == "true"
    )