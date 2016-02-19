import os
import tempfile
import atexit

SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
TESTING = True
DEBUG = False
PRESERVE_CONTEXT_ON_EXCEPTION = False
# disable CSRF checking when testing to allow form-validation testing
WTF_CSRF_ENABLED = False

# tempfile.mkstemp() returns a Tuple with 1. the handle and 2. the absolute path
tmpfile = tempfile.mkstemp("pyencode", "log")
LOG_FD = tmpfile[0]
LOG_FILE = tmpfile[1]
LOG_COUNT = 1


# remove the LOG_FILE when done with unit tests
def clean():
    from app import app
    handlers = app.logger.handlers[:]
    for handler in handlers:
        handler.close()
    os.close(LOG_FD)
    os.remove(LOG_FILE)

atexit.register(clean)
