# Import flask dependencies
from flask import Blueprint, render_template

mod_api = Blueprint("api", __name__, url_prefix="/api")


@mod_api.route("/")
def index():
    return render_template("index.html")
