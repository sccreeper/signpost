from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    Field,
    StringField,
    URLField,
    HiddenField,
    BooleanField,
)
from wtforms.validators import DataRequired, ValidationError, URL
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.shared import PW_BIN_PATH


def _pw_validator(form: FlaskForm, field: Field):
    f = open(PW_BIN_PATH)
    pw_hash = f.read()
    f.close()

    try:
        ph = PasswordHasher()
        ph.verify(pw_hash, field.data)
    except VerifyMismatchError:
        raise ValidationError("Password incorrect")


class LoginForm(FlaskForm):
    pw = PasswordField(
        "Password: ",
        validators=[DataRequired("Please enter a password"), _pw_validator],
    )


class CreateURLForm(FlaskForm):
    url = URLField("URL: ", validators=[URL(), DataRequired("Please enter a URL")])
    slug = StringField("Slug (optional): ")


class EditURLForm(FlaskForm):
    id = HiddenField(validators=[DataRequired()])
    url = URLField(validators=[DataRequired()], render_kw={"placeholder": "URL"})
    slug = StringField(validators=[DataRequired()], render_kw={"placeholder": "Slug"})

    enabled = BooleanField()
    opaque = BooleanField()
    password = PasswordField(render_kw={"placeholder": "Password"})
