from flask.ext.testing import TestCase

from app import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
        app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
        # disable CSRF checking when testing to allow form-validation testing
        app.config["WTF_CSRF_ENABLED"] = False
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
