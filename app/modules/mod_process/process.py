# this class / module serves as a wrapper for the avconv process
from threading import Thread


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file

    def run(self):
        # TODO
        pass