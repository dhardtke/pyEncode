# Import flask dependencies
from flask import Blueprint, render_template

mod_auth = Blueprint("auth", __name__, url_prefix="/auth")


@mod_auth.route("/login")
def index():
    return render_template("index.html")
