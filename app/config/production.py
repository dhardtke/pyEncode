import os

CSRF_ENABLED = True
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data")
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.abspath(os.path.join(DATA_PATH, "app.db"))
SQLALCHEMY_TRACK_MODIFICATIONS = False
THREADS_PER_PAGE = 1
LOG_FILE = os.path.join(DATA_PATH, "pyencode.log")
LOG_COUNT = 5