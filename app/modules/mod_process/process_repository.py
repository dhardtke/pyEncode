# TODO this one should control all the physical processes on the machine
import os

from flask.ext.login import current_user
from flask.ext.socketio import emit

from app import socketio, db, app
from app.library.formatters import human_time, human_size
from app.models.file import File
from app.models.package import Package
from mod_process.file_repository import FileRepository


class ProcessRepository:
    # this list holds all the currently active processes
    processes = []

    @staticmethod
    def set_encoding_active(new_state):
        # update User in database
        current_user.encoding_active = new_state
        db.session.commit()

        # fire event
        socketio.emit("active_changed", {"active": new_state})

        if ProcessRepository.encoding_active():
            # check if it's necessary to start new processes
            ProcessRepository.check_and_start_processes()

    @staticmethod
    def check_and_start_processes():
        while True:
            # grab next potential file to process
            file = FileRepository.get_queued_query().order_by(Package.position.asc(), File.position.asc()).first()

            if file is None or ProcessRepository.count_processes_active() >= int(current_user.parallel_processes):
                break

            # run avprobe / avconv by calling process.py with file.id as parameter
            """
            process = Popen(["python3", "process.py", str(dbFile.id)], shell=False, stdin=None, stdout=None, stderr=None,
                            close_fds=True)
            process.wait()
            """
            from mod_process.process import Process
            process = Process(file)
            ProcessRepository.processes.append(process)
            process.start()

            # emit events
            file_data = get_file_data(file)
            socketio.emit("file_added", {"data": {"id": file.id, "filename": file_data["filename"]}})
            socketio.emit("file_started", {"data": {"count_active": ProcessRepository.count_processes_active()}})
            emit("file_progress", {"data": file_data})
            #
            # TODO
            break

            # TODO hier die events hin, also file_progress, etc.
            # das ProcessRepository muss die threads starten und stoppen

    @staticmethod
    def encoding_active():
        return current_user.encoding_active

    @staticmethod
    def count_processes_active():
        return len(ProcessRepository.processes)

    @staticmethod
    def count_processes_total():
        return ProcessRepository.count_processes_active() + FileRepository.get_queued_query().count()

    def add_process(self, file):
        pass


# make functions available in jinja2
app.jinja_env.globals.update(count_processes_active=ProcessRepository.count_processes_active)
app.jinja_env.globals.update(count_processes_total=ProcessRepository.count_processes_total)
app.jinja_env.globals.update(encoding_active=ProcessRepository.encoding_active)

# check and start processes when starting app
if __name__ == "main":
    ProcessRepository.check_and_start_processes()


def get_file_data(file):
    return {
        "id": file.id,
        "progress": file.avconv_progress,
        "filename": os.path.basename(file.filename),  # show only filename, without path
        "bitrate": file.avconv_bitrate,
        "fps": file.avconv_fps,
        "size": human_size(file.size * 1024),  # in kB, calculate bytes and format via human_size() method
        "time": human_time(file.avconv_time),
        "eta": human_time(file.avconv_eta)
    }
