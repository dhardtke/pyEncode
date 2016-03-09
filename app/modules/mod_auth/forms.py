from flask.ext.wtf import Form
from wtforms import PasswordField, StringField, BooleanField
from wtforms.validators import DataRequired
from flask.ext.babel import lazy_gettext as _


class LoginForm(Form):
    username = StringField(_("Username"), [DataRequired(message=_("Please provide a valid username."))])
    password = PasswordField(_("Password"), [DataRequired(message=_("Please provide a valid password."))])
    remember = BooleanField(_("Remember"))
