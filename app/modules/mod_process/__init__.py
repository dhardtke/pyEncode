import atexit

from app import on_application_ready, app
from mod_process.process_repository import ProcessRepository


def register_jinja2_functions():
    from app.modules.mod_process.process_repository import ProcessRepository

    app.jinja_env.globals.update(count_processes_active=ProcessRepository.count_processes_active)
    app.jinja_env.globals.update(count_processes_queued=ProcessRepository.count_processes_queued)
    app.jinja_env.globals.update(count_processes_total=ProcessRepository.count_processes_total)
    app.jinja_env.globals.update(encoding_active=lambda: ProcessRepository.encoding_active)


def fail_on_exit():
    ProcessRepository.cancel_all_processes()


# run fail method when this Thread is still running and the program quits unexpectedly
atexit.register(fail_on_exit)

# register common jinja2 functions
on_application_ready.append(register_jinja2_functions)
