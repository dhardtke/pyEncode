from app import db
from app.models.file import File
from app.models.package import Package
from app.modules.mod_process.status_map import StatusMap
from tests import NoLoginBaseTestCase


class TestModList(NoLoginBaseTestCase):
    file1 = None
    file2 = None
    package = None

    def login(self, username, password):
        return self.client.post("/auth/login", data=dict(username=username, password=password), follow_redirects=False)

    def logout(self):
        return self.client.get("/auth/logout", follow_redirects=False)

    def setUp(self):
        super().setUp()

        # add some dummy data
        self.package = Package(queue=True, title="Dummy Package")
        db.session.add(self.package)
        # add a File that is processing
        self.file1 = File(filename="dummy.mkv", size=100 * 1024, status=StatusMap.processing.value)
        # add a File that is queued
        self.file2 = File(filename="dummy.mkv", size=100 * 1024, status=StatusMap.queued.value)
        db.session.add(self.file1, self.file2)
        self.package.files.append(self.file1)
        self.package.files.append(self.file2)
        db.session.commit()

        return

    def test_show(self):
        rv = self.client.get("/list/queue")
        self.assertIn(self.package.title, rv.data.decode("utf8"))
        self.assertIn(self.file1.filename, rv.data.decode("utf8"))

        rv = self.client.get("/list/collector")
        self.assertNotIn(self.package.title, rv.data.decode("utf8"))
        self.assertNotIn(self.file1.filename, rv.data.decode("utf8"))

        self.assert404(self.client.get("/list/invalid"))
        pass

    def test_move_package(self):
        # add Package
        package = Package(queue=True)
        db.session.add(package)
        # add File
        file = File(filename="dummy.mkv", size=100 * 1024)
        db.session.add(file)
        package.files.append(file)
        db.session.commit()

        self.client.post("/list/move_package", data=dict(package_id=package.id))
        self.assertFalse(Package.query.filter_by(id=package.id).first().queue)

        self.client.post("/list/move_package", data=dict(package_id=package.id))
        self.assertTrue(Package.query.filter_by(id=package.id).first().queue)

        self.assert404(self.client.post("/list/move_package", data=dict(package_id=-1)))
        return

    def test_restart_package(self):
        self.client.post("/list/restart_package", data=dict(package_id=self.package.id))
        self.assertEquals(File.query.filter_by(id=self.file1.id).first().status, StatusMap.queued.value)
        self.assertEquals(File.query.filter_by(id=self.file2.id).first().status, StatusMap.queued.value)
        return

    def test_restart_file(self):
        self.client.post("/list/restart_file", data=dict(file_id=self.file1.id))
        self.assertEquals(File.query.filter_by(id=self.file1.id).first().status, StatusMap.queued.value)

        self.client.post("/list/restart_file", data=dict(file_id=self.file2.id))
        self.assertEquals(File.query.filter_by(id=self.file2.id).first().status, StatusMap.queued.value)
        self.assert404(self.client.post("/list/restart_file", data=dict(file_id=-1)))
        return

    def test_delete_file(self):
        self.client.post("/list/delete_file", data=dict(file_id=self.file1.id))
        self.assertIsNone(File.query.filter_by(id=self.file1.id).first())
        self.assert404(self.client.post("/list/delete_file", data=dict(file_id=-1)))
        return

    def test_delete_package(self):
        self.client.post("/list/delete_package", data=dict(package_id=self.package.id))
        self.assertIsNone(Package.query.filter_by(id=self.package.id).first())
        self.assertIsNone(File.query.filter_by(id=self.file1.id).first())
        self.assertIsNone(File.query.filter_by(id=self.file2.id).first())

        self.assert404(self.client.post("/list/delete_package", data=dict(package_id=-1)))
        return

        # TODO more tests
