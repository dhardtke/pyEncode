# Import flask dependencies
import os

from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user
from flask.ext.socketio import emit

from app import socketio
from app.library.helpers import human_size, human_time
from app.models.file import File

mod_index = Blueprint("mod_index", __name__)


@mod_index.route("/")
@login_required
def index():
    return render_template("index.html", js_name="index.js", css_name="index.css")


# emit event when file is finished
@mod_index.route("/test")
# TODO
def file_done():
    socketio.emit("file_done", {"data": {"id": 0}})
    return ""


# TODO sollte status nicht woanders hin?
@socketio.on("status")
def status_message(message):
    if current_user.is_authenticated:
        """data = {
            "download": current_user.encoding_active,
            "active": len(processes),
            "total": inject_currentlyTotal()["currentlyTotal"]
        }"""

        data = {
            "download": 0,
            "active": 0,
            "total": 0
        }

        emit("status", {"data": data})
    else:
        return False


@socketio.on("file_progress")
def progress_message(message):
    if current_user.is_authenticated:
        data = []
        files = File.query.join(File.package).filter_by(user_id=current_user.id).all()

        for file in files:
            try:
                data.append({
                    "progress": file.avconv_progress,
                    "filename": os.path.basename(file.filename),  # show only filename, without path
                    "bitrate": file.avconv_bitrate,
                    "fps": file.avconv_fps,
                    "size": human_size(file.size * 1024),  # in kB, calculate bytes and format via human_size() method
                    "time": human_time(file.avconv_time),
                    "eta": human_time(file.avconv_eta)
                })
            except TypeError:
                continue

        emit("file_progress", {"data": data})

    else:
        return False
