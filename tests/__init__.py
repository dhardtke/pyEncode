from flask.ext.testing import TestCase

from app import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        # clear log file
        with open(app.config["LOG_FILE"], 'w'):
            pass
        # recreate the db
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
