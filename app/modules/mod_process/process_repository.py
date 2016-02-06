from app import socketio, db, config
from app.library.formatters import formatted_file_data
from app.models.file import File
from app.models.package import Package
from app.modules.mod_process.file_repository import FileRepository
from app.modules.mod_process.status_map import StatusMap


class ProcessRepository:
    # this dict holds all the currently active processes as id-instance pairs
    # example: {1: <...>, 2: <...>, ...}
    processes = {}

    # this controls whether or not the encoding processing is active
    # notice: do not modify this directly, but use set_encoding_active()
    encoding_active = False

    @staticmethod
    def set_encoding_active(new_state):
        ProcessRepository.encoding_active = new_state

        # fire event
        socketio.emit("active_changed", {"active": new_state})

        # check if it's necessary to start new processes
        ProcessRepository.check_and_start_processes()

    @staticmethod
    def cancel_all_processes():
        for file_id in ProcessRepository.processes:
            # stop thread
            ProcessRepository.processes[file_id].stop()
            # update status
            file = File.query.filter_by(id=file_id).first()
            file.status = StatusMap.failed.value
            file.clear()
            db.session.commit()

            # emit file_done event
            socketio.emit("file_done", {"data": formatted_file_data(file)})

        # clear processes
        ProcessRepository.processes.clear()

        return

    @staticmethod
    def check_and_start_processes():
        while ProcessRepository.encoding_active:
            # grab next potential file to process
            file = FileRepository.get_queued_query().order_by(Package.position.asc(), File.position.asc()).first()

            if file is None or ProcessRepository.count_processes_active() >= config["general"].getint(
                    "parallel_processes"):
                break

            # update file.status in DB
            file.status = StatusMap.processing.value
            db.session.commit()

            # start the Process
            from app.modules.mod_process.process import Process
            process = Process(file)
            process.daemon = True

            # add to "processes" dict
            ProcessRepository.processes[file.id] = process

            process.start()

            # emit file_started event
            data = formatted_file_data(file)
            data["count_active"] = ProcessRepository.count_processes_active()
            data["count_queued"] = ProcessRepository.count_processes_queued()
            socketio.emit("file_started", {"data": data})

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

    # file_done() will be called whenever a Process is finished
    @staticmethod
    def file_done(file):
        # delete from "processes"
        ProcessRepository.processes.pop(file.id)

        # update status to "finished"
        db.session.query(File).filter_by(id=file.id).update(dict(status=StatusMap.finished.value))
        db.session.commit()

        # check if it's necessary to start new processes
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

        return

    @staticmethod
    def file_failed(file):
        # delete from "processes"
        ProcessRepository.processes.pop(file.id)

        # update status and set attributes to zero
        file = db.session.query(File).filter_by(id=file.id).first()
        file.status = StatusMap.failed.value
        file.clear()
        db.session.commit()

        # check if it's necessary to start new processes
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

        return

    @staticmethod
    def file_progress(file, info):
        info["id"] = file.id  # TODO nicer way of doing this

        socketio.emit("file_progress", {"data": info})
        return
