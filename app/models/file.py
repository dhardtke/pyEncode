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

    # relations
    package = db.relationship("Package", backref="files", cascade="all, delete-orphan", single_parent=True)

    avconv_eta = db.Column(db.Float(), default=0)  # in seconds so the user can format it
    avconv_progress = db.Column(db.Float(), default=0)
    avconv_bitrate = db.Column(db.Float(), default=0)
    avconv_time = db.Column(db.Integer(), default=0)
    avconv_size = db.Column(db.Float(), default=0)
    avconv_fps = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return "<File %r>" % self.id
