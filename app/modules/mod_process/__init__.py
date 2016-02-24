from app import on_application_ready, app


def register_jinja2_functions():
    # register common jinja2 functions
    from app.modules.mod_process.process_repository import ProcessRepository

    app.jinja_env.globals.update(count_processes_active=ProcessRepository.count_processes_active)
    app.jinja_env.globals.update(count_processes_queued=ProcessRepository.count_processes_queued)
    app.jinja_env.globals.update(count_processes_total=ProcessRepository.count_processes_total)
    app.jinja_env.globals.update(encoding_active=lambda: ProcessRepository.encoding_active)


on_application_ready.append(register_jinja2_functions)

# run fail method when this Thread is still running and the program quits unexpectedly
# for sig in (signal.SIGABRT, signal.SIGBREAK, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
#    signal.signal(sig, ProcessRepository.file_failed(None))
# TODO!!
