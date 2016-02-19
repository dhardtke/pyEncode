from app import app
from tests import NoLoginBaseTestCase


class TestModLog(NoLoginBaseTestCase):
    def test_log_page(self):
        rv = self.client.get("/log/")
        self.assertIn("The log file is empty.", rv.data.decode("utf8"))

        app.logger.debug("Hello World")
        rv = self.client.get("/log/")
        self.assertIn("Hello World", rv.data.decode("utf8"))
