import os

from flask.ext.babel import gettext as _
from mock import MagicMock

from tests import NoLoginBaseTestCase


class TestModFilemanager(NoLoginBaseTestCase):
    def test_filemanager(self):
        rv = self.client.get("/filemanager/")
        self.assertStatus(rv, 200)
        self.assertIn(_("File Manager"), rv.data.decode("utf8"))

        with self.assertRaises(FileNotFoundError):
            rv = self.client.get("/filemanager/invalidpath")

        os.listdir = MagicMock(return_value=["valid.mkv", "invalid.exe"])
        # mock os.stat
        # os.stat = MagicMock(return_value=type("", (), dict(st_size=0, st_mtime=0))())
        # TODO
        # rv = self.client.get("/filemanager/")
