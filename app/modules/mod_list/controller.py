from flask import Blueprint, render_template, abort, request
from flask.ext.babel import gettext as _
from flask.ext.login import login_required

from app import db
from app.library.formatters import human_size, filename_description
from app.models.file import File
from app.models.package import Package
from app.modules.mod_process.status_map import StatusMap
from app.modules.mod_process.process_repository import ProcessRepository

mod_list = Blueprint("mod_list", __name__, url_prefix="/list")


@mod_list.route("/<string:which>")
@login_required
def show(which):
    if which != "collector" and which != "queue":
        abort(404)

    queue = which == "queue"

    packages = Package.query.join(Package.files).filter(Package.queue == queue).options(
        db.contains_eager(Package.files)).order_by(Package.position.asc(), File.position.asc()).all()

    for package in packages:
        package.files_finished = 0
        package.size = 0

        for file in package.files:
            if file.status == StatusMap.finished.value:
                package.files_finished += 1

            package.size += file.size
            file.size = human_size(file.size)
            file.description = filename_description(file.filename)

        package.files_total = len(package.files)
        package.progress = round((package.files_finished / (package.files_total * 1.0) * 100))
        package.size = human_size(package.size)

    return render_template("list.html", packages=packages, StatusMap=StatusMap, js_name="list.js", css_name="list.css",
                           title=(_("Queue") if queue else _("Collector")))


@mod_list.route("/move_package", methods=["POST"])
@login_required
def move_package():
    package_id = request.form["package_id"]

    package = Package.query.filter_by(id=package_id).first()

    if not package:
        abort(404)

    package.queue = not package.queue
    db.session.commit()

    return ""


@mod_list.route("/restart_package", methods=["POST"])
@login_required
def restart_package():
    package_id = request.form["package_id"]

    package = Package.query.filter_by(id=package_id).first()
    if not package:
        abort(404)

    # cancel all currently running processes that belong to this package
    for file in package.files:
        if ProcessRepository.is_running(file.id):
            ProcessRepository.cancel_process(file.id)
        else:
            # clear progress, cancel_process() also does this
            file.clear()

        # set status of each file to "queued"
        file.status = StatusMap.queued.value

    db.session.commit()

    # check if it's necessary to start new processes
    ProcessRepository.check_and_start_processes()

    return ""


@mod_list.route("/restart_file", methods=["POST"])
@login_required
def restart_file():
    file_id = request.form["file_id"]

    file = File.query.filter_by(id=file_id).first()
    if not file:
        abort(404)

    if ProcessRepository.is_running(file.id):
        ProcessRepository.cancel_process(file.id)
    else:
        # clear progress, cancel_process() also does this
        file.clear()

    # set status of file to "queued"
    file.status = StatusMap.queued.value

    db.session.commit()

    return ""


@mod_list.route("/delete_package", methods=["POST"])
@login_required
def delete_package():
    package_id = request.form["package_id"]

    package = Package.query.filter_by(id=package_id).first()
    if not package:
        abort(404)

    # cancel all currently running processes that belong to this package
    for file in package.files:
        if ProcessRepository.is_running(file.id):
            ProcessRepository.cancel_process(file.id)

        # mark this file to be deleted (even though SQLAlchemy handles this already)
        db.session.delete(file)

    db.session.delete(package)
    db.session.commit()

    # check if it's necessary to start new processes
    ProcessRepository.check_and_start_processes()

    return ""


@mod_list.route("/delete_file", methods=["POST"])
@login_required
def delete_file():
    file_id = request.form["file_id"]
    file = File.query.filter_by(id=file_id).first()

    if not file:
        abort(404)

    # cancel the currently running processes that
    if ProcessRepository.is_running(file.id):
        ProcessRepository.cancel_process(file.id)

    db.session.delete(file)
    db.session.commit()

    # check if it's necessary to start new processes
    ProcessRepository.check_and_start_processes()

    return ""
