# this class / module serves as a wrapper for the avconv process
from threading import Thread
from time import sleep

from app import socketio
from mod_process.process_repository import ProcessRepository


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file

    def run(self):
        # TODO
        sleep(5)

        # done
        socketio.emit("file_done",
                      {"data": {"count_active": ProcessRepository.count_processes_active(), "id": self.file.id}})
