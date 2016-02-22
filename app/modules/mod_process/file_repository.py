from app.models.file import File
from app.modules.mod_process.status_map import StatusMap


class FileRepository:
    @staticmethod
    def get_queued_query():
        return File.query.filter_by(status=StatusMap.queued.value).join(File.package).filter_by(queue=True)

    @staticmethod
    def get_processing_query():
        return File.query.filter_by(status=StatusMap.processing.value).join(File.package)
