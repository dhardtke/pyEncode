from app import db
from app.models.base_model import BaseModel


class File(BaseModel):
    __tablename__ = "files"

    filename = db.Column(db.String(300))  # includes path!
    status = db.Column(db.Integer())
    size = db.Column(db.Integer())
    position = db.Column(db.Integer())

    # foreign keys
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"))

    ffmpeg_eta = db.Column(db.Float(), default=0)  # in seconds so the user can format it
    ffmpeg_progress = db.Column(db.Float(), default=0)
    ffmpeg_bitrate = db.Column(db.Float(), default=0)
    ffmpeg_time = db.Column(db.Integer(), default=0)
    ffmpeg_size = db.Column(db.Float(), default=0)
    ffmpeg_fps = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return "<File %r>" % self.id

    def clear(self):
        self.ffmpeg_progress = 0
        self.ffmpeg_eta = 0
        self.ffmpeg_bitrate = 0
        self.ffmpeg_time = 0
        self.ffmpeg_size = 0
        self.ffmpeg_fps = 0
