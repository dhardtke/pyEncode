from flask import Blueprint, render_template, abort
from flask.ext.babel import gettext as _
from flask.ext.login import login_required

from app import db
from app.library.formatters import human_size, filename_description
from app.models.file import File
from app.models.package import Package
from mod_process.status_map import StatusMap

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
                           title=(_("Collector") if queue else _("Packages")))
