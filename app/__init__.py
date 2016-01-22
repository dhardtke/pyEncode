"""
TODOs:
- Web-API fuer kommunikation
- config
- i18n
- models
- websockets for js client
- auth (login/logout)
"""
import os

# Import flask and template operators
from flask import Flask, render_template, request

# Flask Extensions
from flask.ext.compress import Compress
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment
from flask.ext.babel import Babel

# Define the WSGI application object
app = Flask(__name__)
# load config from config.py
# TODO use YAML
app.config.from_object("config")

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
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


# Register blueprint(s)
from app.modules.mod_index.controller import mod_index
from app.modules.mod_auth.controller import mod_auth

app.register_blueprint(mod_index)
app.register_blueprint(mod_auth)

# Build the database
db.create_all()
