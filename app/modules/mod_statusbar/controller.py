from flask import Blueprint
from flask.ext.login import login_required

from mod_process.process_repository import ProcessRepository

mod_statusbar = Blueprint("mod_statusbar", __name__, url_prefix="/statusbar")


@mod_statusbar.route("/toggle", methods=["POST"])
@login_required
def toggle_encoding_active():
    ProcessRepository.set_encoding_active(not ProcessRepository.encoding_active)
    return ""
