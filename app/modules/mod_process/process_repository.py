# TODO this one should control all the physical processes on the machine
from flask.ext.login import current_user

from app import socketio, db
from mod_process.file_repository import FileRepository


class ProcessRepository:
    # this list holds all the currently active processes
    processes = []

    def set_encoding_active(self, new_state):
        # update User in database
        current_user.encoding_active = new_state
        db.session.commit()

        # fire event
        socketio.emit("active_changed", {})

        if self.get_encoding_active():
            # check if it's necessary to start new processes
            pass

            # TODO hier die events hin, also file_progress, etc.
            # das ProcessRepository muss die threads starten und stoppen

    @staticmethod
    def get_encoding_active():
        return current_user.encoding_active

    @staticmethod
    def count_processes_active():
        return len(ProcessRepository.processes)

    @staticmethod
    def count_processes_total():
        return ProcessRepository.count_processes_active() + FileRepository.get_queued_query().count()

    def add_process(self, file):
        pass
