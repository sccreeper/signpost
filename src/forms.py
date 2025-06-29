from flask_wtf import FlaskForm
from wtforms import PasswordField, Field
from wtforms.validators import DataRequired, Length, ValidationError
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
    pw = PasswordField("Password: ", validators=[DataRequired("Please enter a password"), _pw_validator])