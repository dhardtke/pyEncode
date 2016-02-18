import logging
import os
from logging.handlers import RotatingFileHandler

from app import DATA_PATH, app

LOG_FILE = os.path.join(DATA_PATH, "pyencode.log")
LOG_COUNT = 5

# create LOG_FILE if necessary
if not os.path.isfile(LOG_FILE):
    open(LOG_FILE, "a").close()

handler = RotatingFileHandler(LOG_FILE, maxBytes=1 * 1024 * 1024, backupCount=LOG_COUNT)

formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s", "%d.%m.%Y %H:%M:%S")

handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
