from app import ready_functions, app


def register_jinja2_functions():
    # register common jinja2 functions
    from app.modules.mod_process.process_repository import ProcessRepository

    app.jinja_env.globals.update(count_processes_active=ProcessRepository.count_processes_active)
    app.jinja_env.globals.update(count_processes_queued=ProcessRepository.count_processes_queued)
    app.jinja_env.globals.update(count_processes_total=ProcessRepository.count_processes_total)
    app.jinja_env.globals.update(encoding_active=lambda: ProcessRepository.encoding_active)

ready_functions.append(register_jinja2_functions)