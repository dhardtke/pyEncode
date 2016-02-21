#!/usr/bin/env python3
import argparse
import os
import sys

from app.library.daemon import Daemon

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--debug", help="enable debug mode", action="store_true", default=False)

daemon_group = parser.add_argument_group("daemon")
daemon_group.add_argument("--daemon", help="run in daemon mode", action="store_true", default=False)
daemon_group.add_argument("--stop", help="stop if running in daemon mode", action="store_true", default=False)
daemon_group.add_argument("--restart", help="restart daemon", action="store_true", default=False)

web_frontend_group = parser.add_argument_group("net")
web_frontend_group.add_argument("--port", default=7000, help="port at which the web frontend is listening", type=int)
web_frontend_group.add_argument("--host", default="127.0.0.1",
                                help="host IP under which the web front end is listening")

args = parser.parse_args()
from app import app, socketio


class Application(Daemon):
    def start(self):
        if sys.platform == "win32":
            print("Sorry, but daemon mode is not supported under Windows!")
            sys.exit(1)

        super().start()
        return

    def run(self):
        socketio.run(app, host=args.host, port=args.port, debug=args.debug)


application = Application(os.path.join(app.config["DATA_PATH"], "pyencode.pid"))

if args.restart:
    application.restart()
elif args.stop:
    application.stop()
else:
    if args.daemon:
        application.start()
    else:
        # check if pyEncode is already running
        try:
            application.run()
        except OSError:
            sys.stderr.write("pyEncode is already running (maybe as daemon?)\n")
