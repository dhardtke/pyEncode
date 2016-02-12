import os
import warnings
from configparser import ConfigParser

# Import flask and template operators
from flask import Flask, render_template, request, session

# Flask Extensions
from flask.ext.compress import Compress
from flask.ext.login import current_user
from flask.ext.socketio import SocketIO
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment
from flask.ext.babel import Babel

from sqlalchemy.engine import Engine
from sqlalchemy import event

# Define the WSGI application object
app = Flask(__name__)
app.config["CSRF_ENABLED"] = True
app.config["BASE_DIR"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.abspath(
    os.path.join(app.config["BASE_DIR"], "data", "app.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["THREADS_PER_PAGE"] = 2  # TODO?

# initialize app specific config
CONFIG_PATH = os.path.join(app.config["BASE_DIR"], "data", "config.ini")
config = ConfigParser()
if os.path.isfile(CONFIG_PATH):
    config.read(CONFIG_PATH)
else:
    warnings.warn("Loading fallback config - %s does not exist!" % CONFIG_PATH, RuntimeWarning)
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
            "acodec": "aac",
            "strict": "experimental",
            "s": "1280x720",
            "aspect": "1280:720",
            "preset": "slow",
            "crf": 22
        }
    })

app.config["CSRF_SESSION_KEY"] = config["general"]["csrf_session_key"]
app.config["SECRET_KEY"] = config["general"]["secret_key"]

assets = Environment(app)
# load asset definitions from "static/webassets.yml"
assets.from_yaml(app.root_path + os.sep + "static" + os.sep + "webassets.yml")

# use app/static/compiled as output path for webassets' assets
assets.directory = os.path.abspath(app.root_path + os.sep + "static" + os.sep + "compiled")
assets.url = "/static/compiled"

# use app/static as load path for assets
assets.append_path(app.root_path + os.sep + "static", "static")

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


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


# Register blueprint(s)
from app.modules.mod_index.controller import mod_index
from app.modules.mod_auth.controller import mod_auth
from app.modules.mod_list.controller import mod_list
from app.modules.mod_statusbar.controller import mod_statusbar
from app.modules.mod_filemanager.controller import mod_filemanager

app.register_blueprint(mod_index)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_list)
app.register_blueprint(mod_statusbar)
app.register_blueprint(mod_filemanager)


# enable foreign_keys for sqlite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Build the database
db.create_all()

# register common jinja2 functions
from app.modules.mod_process.process_repository import ProcessRepository

app.jinja_env.globals.update(count_processes_active=ProcessRepository.count_processes_active)
app.jinja_env.globals.update(count_processes_queued=ProcessRepository.count_processes_queued)
app.jinja_env.globals.update(count_processes_total=ProcessRepository.count_processes_total)
app.jinja_env.globals.update(encoding_active=lambda: ProcessRepository.encoding_active)


# run fail method when this Thread is still running and the program quits unexpectedly
# for sig in (signal.SIGABRT, signal.SIGBREAK, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
#    signal.signal(sig, ProcessRepository.file_failed(None))
# TODO!!
