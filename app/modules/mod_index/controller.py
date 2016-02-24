from flask import Blueprint, render_template
from flask.ext.babel import gettext as _
from flask.ext.login import login_required
# from flask.ext.socketio import emit

from app import socketio, on_socketio_connect
from app.library.formatters import formatted_file_data
from app.modules.mod_process.file_repository import FileRepository

mod_index = Blueprint("mod_index", __name__)


@mod_index.route("/")
@login_required
def index():
    return render_template("index.html", js_name="index_js", css_name="index_css", title=_("Overview"))


def add_processing_files():
    files = FileRepository.get_processing_query().all()

    for file in files:
        # emit the file_started event for *every* file that is currently being processed
        socketio.emit("file_started", {"data": formatted_file_data(file)})

    return


# add currently processing files whenever a client connects
on_socketio_connect.append(add_processing_files)
