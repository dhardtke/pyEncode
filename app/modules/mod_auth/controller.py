# Import flask dependencies
import hashlib

from flask import Blueprint, render_template, flash, request, url_for, redirect
from flask.ext.babel import gettext as _
from flask.ext.login import LoginManager, login_user, login_required, logout_user, current_user

from app import app
from app.models.user import User
from .forms import LoginForm

# configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "mod_auth.login"
login_manager.login_message = _("You have to log in to access this page!")
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


mod_auth = Blueprint("mod_auth", __name__, url_prefix="/auth")


@mod_auth.route("/login", methods=["GET", "POST"])
def login():
    # don't allow login when User is logged in already
    if current_user.is_authenticated:
        return redirect(url_for("mod_index.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=hashlib.sha256(form.password.data.encode("utf8")).hexdigest()).first()

        if user is not None:
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get("next") or url_for("mod_index.index"))
        else:
            flash(_("Invalid Username or Password. Please try again!"), "error")

    return render_template("auth/login.html", form=form)


@mod_auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("mod_auth.login"))
