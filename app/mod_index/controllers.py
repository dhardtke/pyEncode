# Import flask dependencies
from flask import Blueprint, render_template

mod_index = Blueprint('index', __name__)


@mod_index.route('/')
def index():
    return render_template("index.html")
