# Import flask dependencies
from flask import Blueprint, render_template
from flask.ext.login import login_required

mod_index = Blueprint("mod_index", __name__)


@mod_index.route("/")
@login_required
def index():
    return render_template("index.html")
