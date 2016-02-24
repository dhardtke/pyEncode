import os
import warnings
from configparser import ConfigParser

from flask import Flask, render_template, request, session
from flask.ext.assets import Environment
from flask.ext.babel import Babel
from flask.ext.compress import Compress
from flask.ext.login import current_user
from flask.ext.socketio import SocketIO, disconnect
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from webassets.loaders import PythonLoader as PythonAssetsLoader

from app import webassets

# all functions in this list will be executed when our app is ready
on_application_ready = []
# all functions in this list will be executed when a new client connects to socketio
on_socketio_connect = []

# Define the WSGI application object
app = Flask(__name__)

# load default configuration from app.config.production
app.config.from_object("app.config.production")
# and if PYENCODE_ADDITIONAL_CONFIG is given, load config from there too
additional_config = os.environ.get("PYENCODE_ADDITIONAL_CONFIG")
if additional_config:
    app.config.from_object(additional_config)

# initialize app specific config
CONFIG_FILE = os.path.join(app.config["DATA_PATH"], "config.ini")
config = ConfigParser()
if os.path.isfile(CONFIG_FILE):
    config.read(CONFIG_FILE)
else:
    warnings.warn("Loading fallback config - %s does not exist!" % CONFIG_FILE, RuntimeWarning)
    config.read_dict({
        "general": {
            "csrf_session_key": "secret",
            "secret_key": "secret",
            "parallel_processes": 1
        },
        "filemanager": {
            "show_resolution": False
        },
        "encoding": {
            "parameters": "-acodec aac -strict experimental -s 1280x720 -aspect = 1280:720 -preset slow -crf 22 -f matroska -vcodec libx265",
            "delete_old_file": False,
            "rename_enabled": False,
            "rename_search": "",
            "rename_replace": ""
        }
    })

app.config["CSRF_SESSION_KEY"] = config["general"]["csrf_session_key"]
app.config["SECRET_KEY"] = config["general"]["secret_key"]

assets = Environment(app)

# use app/static/compiled as output path for webassets' assets
assets.directory = os.path.abspath(app.root_path + os.sep + "static" + os.sep + "compiled")
assets.url = "/static/compiled"

# use app/static as load path for assets
assets.append_path(app.root_path + os.sep + "static", "static")

# load asset definitions from "static/webassets.py"
assets_loader = PythonAssetsLoader(webassets)
bundles = assets_loader.load_bundles()
for bundle in bundles:
    assets.register(bundle, bundles[bundle])

db = SQLAlchemy(app)
babel = Babel(app)
Compress(app)


@babel.localeselector
def get_locale():
    # try to guess the language from the user accept header the browser transmits. We support de/en.
    # The best match wins.
    if "language" not in session:
        if not current_user.is_authenticated:
            session["language"] = request.accept_languages.best_match(["en", "de"])
        else:
            session["language"] = current_user.language

    return session["language"]


socketio = SocketIO(app)


@socketio.on("connect")
def disconnect_anonymous():
    if not current_user.is_authenticated:
        disconnect()
        return

    for func in on_socketio_connect:
        func()

    return


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


# Register blueprint(s)
from app.modules.mod_index.controller import mod_index
from app.modules.mod_auth.controller import mod_auth
from app.modules.mod_list.controller import mod_list
from app.modules.mod_statusbar.controller import mod_statusbar
from app.modules.mod_filemanager.controller import mod_filemanager
from app.modules.mod_log.controller import mod_log

app.register_blueprint(mod_index)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_list)
app.register_blueprint(mod_statusbar)
app.register_blueprint(mod_filemanager)
app.register_blueprint(mod_log)


# enable foreign_keys for sqlite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Build the database
db.create_all()

# run all functions in ready_functions
for func in on_application_ready:
    func()
