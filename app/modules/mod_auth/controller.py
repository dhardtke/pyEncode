# Import flask dependencies
from flask import Blueprint, render_template, flash, request, url_for, redirect
from flask.ext.login import LoginManager, login_user, login_required, logout_user

from app import app
from app.forms.login_form import LoginForm
from .models import User

# configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
# TODO
login_manager.login_message = u"Bonvolu ensaluti por uzi tiun paĝon."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


mod_auth = Blueprint("auth", __name__, url_prefix="/auth")


@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User("", "", "")  # TODO
        login_user(user)

        flash("Logged in successfully.")

        next = request.args.get("next")

        return redirect(next or url_for("index"))

    return render_template("auth/login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
