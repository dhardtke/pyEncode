# gunicorn WSGI server configuration
from os import environ


bind = "0.0.0.0:" + environ.get("PORT", "7000")
max_requests = 0  # disable automatic worker restarts
worker_class = "eventlet"
workers = 1  # this is important, see https://flask-socketio.readthedocs.org/en/latest/#gunicorn-web-server
daemon = True
pidfile = "pyencode.pid"
