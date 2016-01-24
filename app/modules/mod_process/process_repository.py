import os

from app import socketio, db, app
from app.library.formatters import formatted_file_data
from app.models.file import File
from app.models.package import Package
from mod_process.file_repository import FileRepository
from mod_process.status_map import StatusMap


class ProcessRepository:
    # this dict holds all the currently active processes as id-instance pairs
    # example: {1: <...>, 2: <...>, ...}
    processes = {}

    # this controls whether or not the encoding processing is active
    # notice: do not modify this directly, but use set_encoding_active()
    encoding_active = False

    # TODO auslagern in config
    parallel_processes = 1

    @staticmethod
    def set_encoding_active(new_state):
        ProcessRepository.encoding_active = new_state

        # fire event
        socketio.emit("active_changed", {"active": new_state})

        if ProcessRepository.encoding_active:
            # check if it's necessary to start new processes
            ProcessRepository.check_and_start_processes()

    @staticmethod
    def check_and_start_processes():
        while True:
            # grab next potential file to process
            file = FileRepository.get_queued_query().order_by(Package.position.asc(), File.position.asc()).first()

            if not ProcessRepository.encoding_active or file is None or ProcessRepository.count_processes_active() >= ProcessRepository.parallel_processes:
                break

            # start the Process
            from mod_process.process import Process
            process = Process(file)
            # add to "processes" dict
            ProcessRepository.processes[file.id] = process
            process.start()
            # update file.status in DB
            file.status = StatusMap.processing.value
            db.session.commit()

            # emit events
            file_data = formatted_file_data(file)
            socketio.emit("file_added", {"data": {"id": file.id, "filename": file_data["filename"]}})
            socketio.emit("file_started", {"data": {"count_active": ProcessRepository.count_processes_active(),
                                                    "count_queued": ProcessRepository.count_processes_queued()}})
            socketio.emit("file_progress", {"data": file_data})

    @staticmethod
    def count_processes_active():
        return len(ProcessRepository.processes)

    @staticmethod
    def count_processes_queued():
        return FileRepository.get_queued_query().count()

    @staticmethod
    def count_processes_total():
        # count all files that are in packages that are queued
        # return ProcessRepository.count_processes_active() + ProcessRepository.count_processes_queued()
        return Package.query.filter_by(queue=True).join(File).count()
        # TODO

    @staticmethod
    def add_process(file):
        pass

    # file_done() will be called whenever a Process is finished
    @staticmethod
    def file_done(file):
        # delete from "processes"
        ProcessRepository.processes.pop(file.id)
        # update status to "finished"
        db.session.query(File).filter_by(id=file.id).update({"status": StatusMap.finished.value})
        db.session.commit()

        # check if it's necessary to start new processes
        if ProcessRepository.encoding_active:
            ProcessRepository.check_and_start_processes()

        # notify client
        socketio.emit("file_done", {
            "data": {
                "id": file.id,
                "count_active": ProcessRepository.count_processes_active(),
                "count_queued": ProcessRepository.count_processes_queued(),
                "count_total": ProcessRepository.count_processes_total(),
            }
        })


# make functions available in jinja2
app.jinja_env.globals.update(count_processes_active=ProcessRepository.count_processes_active)
app.jinja_env.globals.update(count_processes_queued=ProcessRepository.count_processes_queued)
app.jinja_env.globals.update(count_processes_total=ProcessRepository.count_processes_total)
app.jinja_env.globals.update(encoding_active=lambda: ProcessRepository.encoding_active)