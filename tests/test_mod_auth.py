import hashlib

from flask import url_for
from flask.ext.babel import gettext as _

from app import app, db
from app.models.user import User
from tests import BaseTestCase


class TestModAuth(BaseTestCase):
    def login(self, username, password):
        with app.test_request_context():
            return self.client.post(url_for("mod_auth.login"), data=dict(username=username, password=password),
                                    follow_redirects=False)

    def logout(self):
        with app.test_request_context():
            return self.client.get(url_for("mod_auth.logout"), follow_redirects=False)

    def test_login_logout(self):
        # rv = self.login("admin", "default")
        # assert 'You were logged in' in rv.data
        # rv = self.logout()
        # assert 'You were logged out' in rv.data
        rv = self.login("adminx", "default")
        self.assertIn(_("Invalid Username or Password. Please try again!"), rv.data.decode("utf8"))

        rv = self.login("", "")
        self.assertIn(_("Please provide a valid username."), rv.data.decode("utf8"))
        self.assertIn(_("Please provide a valid password."), rv.data.decode("utf8"))

        # create a real user
        user = User("admin", "webmaster@example.org", hashlib.sha256("password".encode("utf8")).hexdigest())
        db.session.add(user)
        db.session.commit()

        # try to login properly
        rv = self.login("admin", "password")
        with app.test_request_context():
            self.assertRedirects(rv, url_for("mod_index.index"))

        # try to logout
        rv = self.logout()
        with app.test_request_context():
            self.assertRedirects(rv, url_for("mod_auth.login"))

        # test @login_required decorator
        rv = self.client.get("/")
        # assert redirection
        self.assertStatus(rv, 302)
