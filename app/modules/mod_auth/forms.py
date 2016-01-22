# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, BooleanField
from wtforms.validators import DataRequired
from flask.ext.babel import gettext as _


class LoginForm(Form):
    username = StringField("Username", [DataRequired(message=_("Please provide a valid username."))])
    password = PasswordField("Password", [DataRequired(message=_("Please provide a valid password."))])
    remember = BooleanField("Remember")