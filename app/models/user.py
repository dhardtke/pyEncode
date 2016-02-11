from flask.ext.login import UserMixin

from app import db
from app.models.base_model import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean())
    language = db.Column(db.String(2))

    # relationships
    packages = db.relationship("Package", backref="user", cascade="all, delete-orphan")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

        self.active = True

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User %r>" % self.username
