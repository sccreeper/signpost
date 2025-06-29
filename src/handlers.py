from flask import render_template, session, redirect, request, abort, make_response
from werkzeug.exceptions import BadRequest, Forbidden
from flask_wtf import csrf
from functools import wraps
from datetime import datetime

from src.shared import app, htmx, API_SECRET_PATH
from src.forms import LoginForm

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if "Authorization" in request.headers:
        
            with open(API_SECRET_PATH) as fi:
                token = fi.read()

                if request.headers["Authorization"].split()[1] != token:
                    return abort(Forbidden.code)

        else:
        
            if "authenticated" not in session or "time" not in session:
                return redirect("/admin/login")
            else:
                if datetime.now().timestamp() - int(session["time"]) >= 3600:
                    session["authenticated"] = False
                    session["time"] = 0

                    return redirect("/admin/login")
        
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/login", methods=["GET", "POST"])
def route_login():

    csrf.generate_csrf()
    form: LoginForm = LoginForm()

    if request.method == "GET":
        return render_template("partials/login.j2" if htmx else "login.j2", form=form)
    elif request.method == "POST":

        if not htmx:
            return abort(BadRequest.code)
        
        if not form.validate():
            return render_template("partials/login.j2", form=form)
        
        resp = make_response("")
        resp.headers["HX-Location"] = '{"path":"/admin/main", "target":"#content-block"}'

        session["authenticated"] = True
        session["time"] = datetime.now().timestamp()

        return resp


@app.route("/admin/main", methods=["GET"])
@login_required
def route_main():
    if htmx:
        return render_template("partials/main.j2")
    else:
        return render_template("main.j2")
    
@app.route("/admin/logout", methods=["POST"])
@login_required
def route_logout():
    if not htmx:
        return abort(400)

    session["authenticated"] = False
    session["time"] = 0

    resp = make_response("")
    resp.headers["HX-Redirect"] = "/admin/login"

    return resp

@app.route("/api/url/create", methods=["POST"])
def route_add():
    pass

@app.route("/api/url/modify", methods=["PATCH"])
def route_modify():
    pass

@app.route("/api/url/delete", methods=["DELETE"])
def route_delete():
    pass

@app.route("/api/url/qr", methods=["GET"])
def route_gen_qr():
    pass