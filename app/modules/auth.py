# Import flask dependencies
from flask import Blueprint, render_template
from flask.ext.login import LoginManager

from app import app
from app.models.user import User

# configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


mod_auth = Blueprint("auth", __name__, url_prefix="/auth")


@mod_auth.route("/login")
def login():
    return render_template("index.html")
