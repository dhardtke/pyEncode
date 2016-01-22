# Import flask dependencies
from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user
from flask.ext.socketio import emit

from app import socketio

mod_index = Blueprint("mod_index", __name__)


@mod_index.route("/")
@login_required
def index():
    return render_template("index.html", js_name="index.js")


# TODO sollte status nicht woanders hin?
@socketio.on("status")
def status_message(message):
    if current_user.is_authenticated:
        emit("status", {"data": "TODO"})
    else:
        return False


@socketio.on("progress")
def progress_message(message):
    if current_user.is_authenticated:
        emit("progress", {"data": "TODO"})
    else:
        return False
