from flask import (
    render_template,
    render_template_string,
    session,
    redirect,
    request,
    abort,
    make_response,
    jsonify,
    send_file,
)
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized
from flask_wtf import csrf
from functools import wraps
from datetime import datetime
from random import randint
from jsonschema import validate, ValidationError
from argon2 import PasswordHasher
from argon2.exceptions import HashingError, VerifyMismatchError
import qrcode
from io import BytesIO
import os
import uuid

from src.shared import app, htmx, API_SECRET_PATH, PW_BIN_PATH
from src.forms import LoginForm, CreateURLForm, EditURLForm, ChangePasswordForm
from src.db.models import URLModel
from src.db.db import db
from src.db.util import gen_random_string
from src.schemas import create_url_schema

MAX_ID_SIZE = (2**63) - 1


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "Authorization" in request.headers:

            with open(API_SECRET_PATH) as fi:
                token = fi.read()

                if request.headers["Authorization"].split()[1] != token:
                    return abort(Unauthorized.code)

        else:

            if "authenticated" not in session or "time" not in session:
                return redirect("/admin/login")
            else:
                if datetime.now().timestamp() - int(session["time"]) >= 3600:
                    session.clear()

                    return redirect("/admin/login")

        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def route_login():

    csrf.generate_csrf()
    form: LoginForm = LoginForm()

    if request.method == "GET":
        if "authenticated" in session:  # lazy way of checking login
            return redirect("/admin/main")
        else:
            return render_template(
                "partials/login.j2" if htmx else "login.j2", form=form
            )
    elif request.method == "POST":

        if not htmx:
            return abort(BadRequest.code)

        if not form.validate():
            return render_template("partials/login.j2", form=form)

        resp = make_response("")
        resp.headers["HX-Location"] = (
            '{"path":"/admin/main", "target":"#content-block"}'
        )

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
        "partials/main.j2" if htmx else "main.j2", urls=urls, url_form=CreateURLForm()
    )


@app.route("/admin/logout", methods=["POST"])
@login_required
def route_logout():
    if not htmx:
        return abort(400)

    session.clear()

    resp = make_response("")
    resp.headers["HX-Redirect"] = "/admin/login"

    return resp


@app.route("/admin/settings")
@login_required
def route_settings():

    csrf.generate_csrf()

    form: ChangePasswordForm = ChangePasswordForm()

    return render_template("partials/settings.j2" if htmx else "settings.j2", form=form)


@app.route("/<slug>")
def route_redirect(slug=None):

    url = db.session.query(URLModel).where(URLModel.slug == slug, URLModel.enabled).first()
    if url == None:
        return abort(NotFound.code)

    # Update hits

    db.session.query(URLModel).where(URLModel.slug == slug).update(
        {URLModel.hits: URLModel.hits + 1}
    )
    db.session.commit()

    if url.opaque:
        return f"<script>window.location.replace('{url.url}')</script>"
    elif url.password != None:
        if "pw" not in request.args:
            resp = make_response(
                render_template_string(
                    f"<p>This is a password protected URL. Please add <code>?pw=****</code> (replace **** with the password) to the end of the URL to access.</p>"
                )
            )
            resp.status_code = Unauthorized.code

            return resp
        
        # hash password and compare
        
        try:
            hasher = PasswordHasher()
            hasher.verify(url.password, request.args["pw"])
        except VerifyMismatchError:
            resp = make_response(
                render_template_string(
                    f"<p>Incorrect password supplied.</p>"
                )
            )
            resp.status_code = 401

            return resp
        
        return redirect(url.url)

    else:
        return redirect(url.url)


@app.route("/api/url/create", methods=["POST"])
@login_required
def route_add():
    url_id: str = ""
    url_slug: str = ""
    url: str = ""

    # htmx (web interface) or JSON api

    if htmx:

        form: CreateURLForm = CreateURLForm()

        if not form.validate():

            resp = make_response(
                render_template("components/error_list.j2", errors=form.errors)
            )
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

        while (
            db.session.query(URLModel).where(URLModel.slug == url_slug).first() != None
        ):
            url_slug = gen_random_string(4)
    else:

        if db.session.query(URLModel).where(URLModel.slug == url_slug).first() != None:
            resp = make_response(
                render_template(
                    "components/error_list.j2",
                    errors={"slug_error": ["Slug already in use"]},
                )
            )
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

        last_added = (
            db.session.query(URLModel).order_by(URLModel.created.desc()).first()
        )

        return render_template_string(
            """
            {%import "components/table_row.j2" as row %}

            {{ row.url_table_row(data) }}

            """,
            data=last_added,
        )

    else:
        return jsonify({"id": url_id})


@app.route("/ui/edit/<url_id>", methods=["GET"])
@login_required
def route_ui_edit(url_id=None):
    url = db.session.query(URLModel).where(URLModel.id == url_id).first()

    if url == None:
        return abort(NotFound.code)

    if not htmx:
        return abort(BadRequest.code)

    csrf.generate_csrf()

    form: EditURLForm = EditURLForm(
        id=url.id, url=url.url, slug=url.slug, enabled=url.enabled, opaque=url.opaque
    )

    return render_template_string(
        """
            {% import "components/table_row.j2" as tr %}

            {{ tr.edit_url_row(form, hits, pw_set, errors) }}
            """,
        form=form,
        hits=url.hits,
        pw_set=url.password == None,
        errors=form.errors,
    )


@app.route("/api/url/modify", methods=["PATCH"])
@login_required
def route_modify():
    url_id: int = None
    new_slug: str = None
    new_url: str = None
    new_enabled: bool = None
    new_opaque: bool = None
    new_password: str = None

    if htmx:

        form: EditURLForm = EditURLForm()

        if not form.validate():
            return render_template_string(
                """
                {% import "components/table_row.j2" as tr %}

                {{ tr.edit_url_row(form, hits, pw_set, errors) }}
                """,
                form=form,
                hits=0,
                pw_set=form.password.data != "",
                errors=form.errors,
            )

        url_id = form.id.data
        new_slug = form.slug.data
        new_url = form.url.data
        new_enabled = form.enabled.data
        new_opaque = form.opaque.data
        new_password = (
            None
            if form.password.data == None or form.password.data.strip() == ""
            else form.password.data
        )

        if (
            db.session.query(URLModel)
            .where(URLModel.slug == new_slug, URLModel.id != url_id)
            .first()
            != None
        ):
            return render_template_string(
                """
                {% import "components/table_row.j2" as tr %}

                {{ tr.edit_url_row(form, hits, pw_set, errors) }}
                """,
                form=form,
                hits=0,
                pw_set=form.password.data != "",
                errors={"slug_error": ["Slug already in use"]},
            )

    else:

        try:
            validate(request.json)
        except ValidationError:
            return abort(BadRequest.code)

        url_id = request.json["id"]
        new_slug = request.json["new_values"]["slug"]
        new_url = request.json["new_values"]["url"]
        new_enabled = request.json["new_values"]["enabled"]
        new_opaque = request.json["new_values"]["opaque"]

        if request.json["new_values"]["password"].strip() == "":
            new_password = None
        else:
            new_password = request.json["new_values"]["password"]

        if db.session.query(URLModel).where(URLModel.id == url_id).first() == None:
            return abort(NotFound.code)

        if (
            db.session.query(URLModel)
            .where(URLModel.slug == new_slug, URLModel.id != url_id)
            .first()
            != None
        ):
            return abort(BadRequest.code)

    # Finally update data

    db.session.query(URLModel).where(URLModel.id == url_id).update(
        {
            URLModel.slug: new_slug,
            URLModel.url: new_url,
            URLModel.enabled: new_enabled,
            URLModel.opaque: new_opaque,
            URLModel.password: (
                PasswordHasher().hash(new_password) if new_password != None else None
            ),
            URLModel.modified: datetime.now(),
        }
    )

    db.session.commit()

    if htmx:
        last_modified = (
            db.session.query(URLModel).order_by(URLModel.modified.desc()).first()
        )

        return render_template_string(
            """
            {%import "components/table_row.j2" as row %}

            {{ row.url_table_row(data) }}

            """,
            data=last_modified,
        )
    else:
        return ""


@app.route("/api/url/delete/<url_id>", methods=["DELETE"])
@login_required
def route_delete(url_id=None):
    url = db.session.query(URLModel).where(URLModel.id == url_id).first()

    if url == None:
        return abort(404)

    db.session.delete(url)
    db.session.commit()

    return ""


@app.route("/api/url/qr/<url_id>", methods=["GET"])
@login_required
def route_gen_qr(url_id=None):

    url = db.session.query(URLModel).where(URLModel.id == url_id).first()

    if url == None:
        return abort(404)

    qr = qrcode.make(f"{os.environ['HOST']}/{url.slug}")
    buffer = BytesIO()
    qr.save(buffer)
    buffer.seek(0)

    return send_file(buffer, download_name=f"qr_{url.slug}.png", mimetype="image/png")


@app.route("/api/settings/change_password", methods=["POST"])
@login_required
def route_change_password():
    if not htmx:
        return abort(BadRequest.code)

    csrf.generate_csrf()

    form: ChangePasswordForm = ChangePasswordForm()

    if not form.validate():
        return render_template("partials/settings.j2", form=form)

    hasher = PasswordHasher()

    with open(PW_BIN_PATH, "w") as f:
        hash: str = ""

        try:
            hash = hasher.hash(form.new_password.data)
            f.write(hash)

            return render_template(
                "partials/settings.j2", form=form, status_message="Changed successfully"
            )
        except HashingError:
            return render_template(
                "partials/settings.j2",
                form=form,
                status_message="Unable to change password",
            )


@app.route("/api/settings/secret/view")
@login_required
def route_view_key():

    f = open(API_SECRET_PATH, "r")
    key = f.read()
    f.close()

    return render_template_string(f"API Key: {key}")

@app.route("/api/settings/secret/regenerate")
@login_required
def route_regen_key():

    new_secret = str(uuid.uuid4())

    f = open(API_SECRET_PATH, "w")
    f.write(new_secret)
    f.close()

    return render_template_string(f"API Key: {new_secret}")
