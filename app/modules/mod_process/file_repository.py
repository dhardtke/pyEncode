from flask.ext.login import current_user

from app.models.file import File
from mod_process.status_map import StatusMap


class FileRepository:
    @staticmethod
    def get_queued_query():
        return File.query.filter_by(status=StatusMap.queued.value).join(File.package).filter_by(queue=True, user_id=current_user.id)
