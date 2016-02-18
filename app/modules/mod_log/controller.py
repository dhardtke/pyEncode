from flask import render_template, Blueprint
from flask.ext.login import login_required
from flask_babel import gettext as _

mod_log = Blueprint("mod_log", __name__, url_prefix="/log")


@login_required
@mod_log.route("/", methods=["GET"])
def log_page():
    return render_template("auth/login.html", title=_("Log"))
