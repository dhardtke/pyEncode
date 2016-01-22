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
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment
from flask.ext.babel import Babel, gettext

# Define the WSGI application object
app = Flask(__name__)
app.config.from_object("config")

assets = Environment(app)
db = SQLAlchemy(app)
babel = Babel(app)
assets.from_yaml(app.root_path + os.sep + "webassets.yml")


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

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
