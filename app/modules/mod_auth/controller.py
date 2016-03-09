# Import flask dependencies
import hashlib

from flask import Blueprint, render_template, flash, request, url_for, redirect, abort, session
from flask.ext.babel import gettext as _
from flask.ext.login import login_user, login_required, logout_user, current_user

from app import db
from app.models.user import User
from app.modules.mod_auth.forms import LoginForm

mod_auth = Blueprint("mod_auth", __name__, url_prefix="/auth")


@mod_auth.route("/login", methods=["GET", "POST"])
def login():
    """
    show log in page or log in a User
    :return: the log in page or redirect to the index page
    """

    # don't allow login when User is logged in already
    if current_user.is_authenticated:
        return redirect(url_for("mod_index.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data,
                                    password=hashlib.sha256(form.password.data.encode("utf8")).hexdigest()).first()

        if user is not None:
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get("next") or url_for("mod_index.index"))
        else:
            flash(_("Invalid Username or Password. Please try again!"), "error")

    return render_template("auth/login.html", form=form, title=_("Login"))


@mod_auth.route("/logout")
@login_required
def logout():
    """
    logout the current User
    :return: redirect to login
    """
    logout_user()
    return redirect(url_for("mod_auth.login"))


@mod_auth.route("/lang/<string:language>")
def set_language(language):
    """
    set a new language as active for the currently logged in User
    :param language: the new language
    :return: redirect to referrer
    """

    if language in ("de", "en"):
        # only store language in database when the User is logged in
        if current_user.is_authenticated:
            current_user.language = language
            db.session.commit()

        session["language"] = language
        return redirect(request.referrer or url_for("mod_index.index"))
    else:
        abort(404)
