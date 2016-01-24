from flask import Blueprint, render_template
from flask.ext.login import login_required
from flask.ext.babel import gettext as _

from mod_process.process_repository import ProcessRepository

mod_index = Blueprint("mod_index", __name__)


@mod_index.route("/")
@login_required
def index():
    return render_template("index.html", js_name="index.js", css_name="index.css", title=_("Overview"))


@mod_index.route("/toggle", methods=["POST"])
@login_required
def toggle_encoding_active():
    ProcessRepository.set_encoding_active(not ProcessRepository.encoding_active)
    return ""
