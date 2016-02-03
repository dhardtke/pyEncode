import datetime
import os
import string
from pathlib import Path

from flask import Blueprint, request, render_template
from flask.ext.babel import gettext as _
from flask.ext.login import login_required

from app import app
from app.library.extensions import allowed_extensions
from app.library.formatters import human_size

mod_filemanager = Blueprint("mod_filemanager", __name__, url_prefix="/filemanager")


@mod_filemanager.route("/", defaults={"path": "/"}, methods=["GET", "POST"])
@mod_filemanager.route("/<path:path>", methods=["GET", "POST"])
@login_required
def filemanager(path):
    # always prepend the root if we're not in it yet
    if path != "/" and os.name != "nt":
        path = "/" + path

    path_instance = Path(path)

    # build a breadcrumbs structure
    breadcrumbs = []
    if path == "/" or os.name == "nt":
        # on Windows we have this special "/" folder that shows a list of all drives
        breadcrumbs.append({"name": "/", "path": "/"})
    parents = path_instance.parents

    for parent in parents:
        # insert parent at position 1 (second item)
        pos = 0

        if os.name == "nt":
            pos = 1

        breadcrumbs.insert(pos, {"name": str(parent).replace("\\", "") if parent.name == "" else parent.name,
                                 "path": parent.as_posix()})

    # add the current path if we are not at root-level
    if str(path_instance) != os.path.normpath("/"):
        breadcrumbs.append(
            {"name": str(path_instance).replace("\\", "") if path_instance.name == "" else path_instance.name,
             "path": path_instance.as_posix()})

    if request.method == "POST":
        request_filter = request.form["filter"]
    else:
        request_filter = ""

    # the list of item rows that will be shown in the file manager's table
    items = []

    # on Windows only show the normal file/folder view when the path is not "/" (and testing is disabled)
    if app.testing or os.name != "nt" or path != "/":
        # grab a list of filenames using os.listdir, filter out all files that don't have
        # an extension from "allowed_extensions" or aren't dirs and process "request_filter"
        filename_list = sorted(filter(
            lambda file: (file.endswith(tuple(allowed_extensions)) or os.path.isdir(
                os.path.normpath(path + "/" + file))) and (
                             request_filter in file or request_filter.replace(" ", ".") in file), os.listdir(path)))

        for filename in filename_list:
            full_path = path_instance.joinpath(filename)

            try:
                is_file = full_path.is_file()
                stat = full_path.stat()
                timestamp = stat.st_mtime
                size = stat.st_size
            except PermissionError:
                continue

            items.append({
                "name": filename,
                "path": ("/" if not is_file and os.name == "nt" else "") + full_path.as_posix(),
                "type": ("file" if is_file else "folder"),
                "extension": os.path.splitext(filename)[1][1:],
                "size": (human_size(size) if is_file else "--"),
                "size_raw": size,
                "modified": datetime.datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S"),
                "modified_raw": timestamp
            })
    else:
        # show a list of drive letters
        available_drives = ["%s:" % d for d in string.ascii_uppercase if os.path.exists("%s:" % d)]

        for drive in available_drives:
            timestamp = os.path.getmtime(drive)

            items.append({
                "name": drive,
                "path": "/" + drive + "/",
                "type": "folder",
                "extension": "",
                "size": "--",
                "size_raw": 0,
                "modified": datetime.datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S"),
                "modified_raw": timestamp
            })

    # TODO config
    conf = {
        "general": {
            "show_resolution": "False"
        }
    }

    parent_path = path_instance.parent.as_posix()

    # this is only the case for the root on windows
    if os.name == "nt":
        if path == parent_path:
            parent_path = "/"
        else:
            parent_path = "/" + parent_path

    return render_template("filemanager.html", js_name="filemanager.js", css_name="filemanager.css", config=conf,
                           breadcrumbs=breadcrumbs, filter=request_filter, files=items, filemanager=True,
                           is_windows=os.name == "nt", parent_path=parent_path, path=path, title=_("File Manager"))
