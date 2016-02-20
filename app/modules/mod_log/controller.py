import os

from flask import render_template, Blueprint
from flask.ext.login import login_required
from flask_babel import gettext as _

from app import app

mod_log = Blueprint("mod_log", __name__, url_prefix="/log")


@login_required
@mod_log.route("/", methods=["GET"])
def log_page():
    # read all log files into one variable
    content = ""
    i = 0
    while i < app.config["LOG_COUNT"]:
        file = app.config["LOG_FILE"]

        # add suffix if necessary
        if i != 0:
            file += "." + str(i)
        i += 1

        # only read file if it exists
        if not os.path.isfile(file):
            continue

        with open(file, "r") as content_file:
            content += content_file.read()

    entries = []

    lines = content.split("\n")

    for i, line in enumerate(lines):
        # delete empty lines
        if len(line) == 0:
            del lines[i]
            continue

        line = line.strip()

        if not line[0].isnumeric():
            # this is definitely an exception line, because it does not start with a number
            # add it to the last item string
            entries[len(entries) - 1]["message"] += line + "\n\n"
            continue

        # separate date, time, the message is always the rest
        entry_date, entry_rest = line.split(" ", 1)
        entry_rest, entry_message = entry_rest.split("\t", 2)
        entry_time, entry_level = entry_rest.split(" ")

        entries.append({
            "date": entry_date,
            "time": entry_time,
            "level": entry_level,
            "message": entry_message.strip()
        })

    return render_template("log.html", entries=entries, title=_("Log"), css_name="log_css")
