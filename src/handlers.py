from flask import render_template, render_template_string, session, redirect, request, abort, make_response, jsonify
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from flask_wtf import csrf
from functools import wraps
from datetime import datetime
from random import randint
from jsonschema import validate, ValidationError

from src.shared import app, htmx, API_SECRET_PATH
from src.forms import LoginForm, CreateURLForm
from src.db.models import URLModel
from src.db.db import db
from src.db.util import gen_random_string
from src.schemas import create_url_schema

MAX_ID_SIZE = (2**63)-1

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

    csrf.generate_csrf()

    # get urls

    urls = db.session.query(URLModel).all()

    return render_template(
        "partials/main.j2" if htmx else "main.j2",
        urls=urls,
        url_form=CreateURLForm()
    )
    
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

@app.route("/<slug>")
def route_redirect(slug=None):
    
    url = db.session.query(URLModel).where(URLModel.slug == slug).first()
    if url == None:
        return abort(NotFound.code)

    # Update hits

    db.session.query(URLModel).where(URLModel.slug == slug).update({URLModel.hits: URLModel.hits + 1})
    db.session.commit()
    
    if url.opaque:
         return f"<script>window.location.replace('{url.url}')</script>"
    elif url.password != None:
        pass
    else:
        return redirect(url.url)

@app.route("/api/url/create", methods=["POST"])
def route_add():
    url_id: str = ""
    url_slug: str = ""
    url: str = ""

    # htmx (web interface) or JSON api

    if htmx:
    
        form: CreateURLForm = CreateURLForm()

        if not form.validate():
            
            resp = make_response(render_template("components/error_list.j2", errors=form.errors))
            resp.headers.add("HX-Reswap", "innerHTML")
            resp.headers.add("HX-Retarget", "#error-message")
            return resp
        
        url_slug = form.slug.data.strip()
        url = form.url.data

    else:
        
        try:
           validate(instance=request.json, schema=create_url_schema)
        except ValidationError:
            return abort(BadRequest.code)
        
        url_slug = str(request.json["slug"]).strip()
        url = request.json["url"]

    # generate ID

    url_id = randint(-MAX_ID_SIZE, MAX_ID_SIZE)

    while db.session.query(URLModel).where(URLModel.id == url_id).first() != None:
        url_id = randint(-MAX_ID_SIZE, MAX_ID_SIZE)

    if url_slug == "":
        url_slug = gen_random_string(4)

        while db.session.query(URLModel).where(URLModel.slug == url_slug).first() != None:
            url_slug = gen_random_string(4)
    else:

        if db.session.query(URLModel).where(URLModel.slug == url_slug).first() != None:
            resp = make_response(render_template("components/error_list.j2", errors={"slug_error" : ["Slug already in use"]}))
            resp.headers.add("HX-Reswap", "innerHTML")
            resp.headers.add("HX-Retarget", "#error-message")
            return resp
    
    db.session.add(
        URLModel(
            id=url_id,
            url=url,
            slug=url_slug,
        )
    )

    db.session.commit()

    if htmx:

        # get record as added to db

        latest = db.session.query(URLModel).order_by(URLModel.created.desc()).first()

        return render_template_string(
            """
            {%import "components/table_row.j2" as row %}

            {{ row.url_table_row(data) }}

            """,
            data=latest
        )

    else:
        return jsonify({"id" : url_id})

@app.route("/api/url/modify", methods=["PATCH"])
def route_modify():
    pass

@app.route("/api/url/delete", methods=["DELETE"])
def route_delete():
    pass

@app.route("/api/url/qr", methods=["GET"])
def route_gen_qr():
    pass