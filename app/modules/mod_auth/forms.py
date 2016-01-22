# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import Email, DataRequired
from flask.ext.babel import gettext as _


class LoginForm(Form):
    username = StringField("Username", [DataRequired(message=_("Please provide a valid username."))])
    password = PasswordField("Password", [DataRequired(message=_("Please provide a valid password."))])
