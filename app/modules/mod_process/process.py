# this class / module serves as a wrapper for the avconv process
from threading import Thread

# see https://github.com/miguelgrinberg/Flask-SocketIO/issues/192
import subprocess
from eventlet.green.subprocess import Popen
from eventlet import sleep

from mod_process.process_repository import ProcessRepository


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file

    def run(self):
        # TODO
        sleep(1)
        # instance = Popen(["echo", "hallo"], stdout=subprocess.PIPE, shell=True)
        # print(instance.communicate())

        ProcessRepository.file_done(self.file)
