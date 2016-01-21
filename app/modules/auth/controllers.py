# Import flask dependencies
from flask import Blueprint, render_template
from app.models.user import User

mod_auth = Blueprint("auth", __name__, url_prefix="/auth")


@mod_auth.route("/login")
def index():
    return render_template("index.html")
