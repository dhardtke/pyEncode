from flask.ext.login import UserMixin

from app import db
from app.models.base_model import BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    # relationships
    packages = db.relationship("Package", back_populates="user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
