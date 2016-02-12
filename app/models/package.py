from app import db
from app.models.base_model import BaseModel


class Package(BaseModel):
    __tablename__ = "packages"

    title = db.Column(db.String(300))
    queue = db.Column(db.Boolean())
    position = db.Column(db.Integer(), default=0)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # relationships
    files = db.relationship("File", backref="package", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Package %r>" % self.id
