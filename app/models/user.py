from flask.ext.login import UserMixin

from app import db
from app.models.base_model import BaseModel
from app.models.package import Package


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

        self.active = True

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User %r>" % self.username
