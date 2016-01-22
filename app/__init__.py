"""
TODOs:
- Web-API fuer kommunikation
- config
- i18n
- models
- websockets for js client
- auth (login/logout)
"""
# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object("config")

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


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
