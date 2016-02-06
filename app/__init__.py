import os
import warnings
from configparser import ConfigParser

# Import flask and template operators
from flask import Flask, render_template, request

# Flask Extensions
from flask.ext.compress import Compress
from flask.ext.socketio import SocketIO
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment
from flask.ext.babel import Babel

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.ini")
config = ConfigParser()

# Define the WSGI application object
def create_app():
    app = Flask(__name__)
    app.config["CSRF_ENABLED"] = True
    app.config["LANGUAGES"] = {
        "en": "English",
        "de": "Deutsch"
    }
    app.config["BASE_DIR"] = BASE_DIR
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.config["BASE_DIR"], "data", "app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["THREADS_PER_PAGE"] = 2  # TODO?

    # initialize app specific config
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
    return app


app = create_app()
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

# TODO async_mode, see https://stackoverflow.com/questions/35235797/socketio-emit-doesnt-work-when-interacting-using-popen-on-windows-in-a-thread
socketio = SocketIO(app)  # , async_mode="threading"


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config["LANGUAGES"].keys())


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
