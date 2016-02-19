from flask.ext.testing import TestCase
import os

# tell the app instance to use the config values from app.config.testing
os.environ["PYENCODE_ADDITIONAL_CONFIG"] = "app.config.testing"

from app import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class NoLoginBaseTestCase(BaseTestCase):
    # disable @login_required for this test
    def create_app(self):
        _app = super().create_app()

        _app.config["LOGIN_DISABLED"] = True
        _app.login_manager.init_app(_app)
        return _app
