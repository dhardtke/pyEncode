import logging
import os
from logging.handlers import RotatingFileHandler

from app import app

# create LOG_FILE if necessary
if not os.path.isfile(app.config["LOG_FILE"]):
    open(app.config["LOG_FILE"], "a").close()

handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=1 * 1024 * 1024, backupCount=app.config["LOG_COUNT"])

formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s", "%d.%m.%Y %H:%M:%S")

handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
