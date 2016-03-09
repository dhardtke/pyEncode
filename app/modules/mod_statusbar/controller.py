import html
import json
import os

from flask import Blueprint, request
from flask.ext.login import login_required, current_user

from app import db, socketio
from app.models.file import File
from app.models.package import Package
from app.modules.mod_process.process_repository import ProcessRepository
from app.modules.mod_process.status_map import StatusMap

mod_statusbar = Blueprint("mod_statusbar", __name__, url_prefix="/statusbar")


@mod_statusbar.route("/toggle", methods=["POST"])
@login_required
def toggle_encoding_active():
    """
    toggle the current encoding active status (from either True to False and vice-versa)
    :return: ""
    """

    ProcessRepository.set_encoding_active(not ProcessRepository.encoding_active)
    return ""


@mod_statusbar.route("/cancel", methods=["POST"])
@login_required
def cancel_processes():
    """
    cancel all currently running Processes and check for new processes
    :return: ""
    """

    ProcessRepository.cancel_all_processes()

    # after cancelling check if it's necessary to start new processes
    ProcessRepository.check_and_start_processes()
    return ""


@mod_statusbar.route("/add", methods=["POST"])
@login_required
def add_package():
    """
    add a new Package
    :return: "1"
    """

    i = 0
    paths = json.loads(request.form["paths"])
    for path in paths:
        paths[i] = html.unescape(path)
        path = paths[i]
        if not os.path.isfile(path):
            print(path + " does not exist..")
            return "not_existing"

        i += 1

    last_package = Package.query.filter_by(queue=True).order_by(Package.position.desc()).limit(1).first()
    if not last_package:
        position = 0
    else:
        position = last_package.position + 1

    package = Package(user=current_user, title=request.form["title"], queue=(request.form["queue"] == "1"),
                      position=position)
    db.session.add(package)

    file_pos = 0
    for path in paths:
        file = File(filename=path, size=os.path.getsize(path), status=StatusMap.queued.value, position=file_pos)
        package.files.append(file)
        file_pos += 1

    db.session.commit()

    # after adding, see if we have to start processes
    ProcessRepository.check_and_start_processes()
    return "1"
