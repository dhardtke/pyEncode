from mock import patch

from app import socketio, app, db, config
from app.models.file import File
from app.models.package import Package
from app.modules.mod_process.process_repository import ProcessRepository
from app.modules.mod_process.status_map import StatusMap
from tests import BaseTestCase


class TestModProcess(BaseTestCase):
    socketio_client = None

    def setUp(self):
        super().setUp()

        self.socketio_client = socketio.test_client(app)
        ProcessRepository.set_encoding_active(False)
        self.socketio_client.queue.clear()

    def tearDown(self):
        super().tearDown()

        self.socketio_client.disconnect()

    # disable @login_required for this test
    def create_app(self):
        app = super().create_app()

        app.config["LOGIN_DISABLED"] = True
        app.login_manager.init_app(app)

        return app

    def test_set_encoding_active(self):
        # encoding_active should be False when creating app
        self.assertFalse(ProcessRepository.encoding_active)

        ProcessRepository.set_encoding_active(True)

        # ... and should be True now
        self.assertTrue(ProcessRepository.encoding_active)

        # test we received active_changed with the correct data
        received = self.socketio_client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["name"], "active_changed")
        self.assertEqual(received[0]["args"], [{"active": True}])

        return

    @patch("app.modules.mod_process.process.Process.run_avconv")
    @patch("app.modules.mod_process.process.Process.avconv_probe_frame_count", return_value=10)
    def test_check_and_start_processes(self, mock_probe, mock_run):
        def mocked_run_avconv(cmd, frame_count):
            yield {"return_code": -1, "eta": 1, "progress": 0, "bitrate": 0, "time": 0, "size": 0, "fps": 0}

        # mock run_avconv()
        mock_run.side_effect = mocked_run_avconv

        # add Package
        package = Package(queue=True)
        db.session.add(package)
        # add File
        file = File(status=StatusMap.queued.value, filename="dummy.mkv", size=100 * 1024)
        db.session.add(file)
        package.files.append(file)

        db.session.commit()

        # set parallel processes to 1
        config["general"]["parallel_processes"] = "1"

        # start processing
        ProcessRepository.set_encoding_active(True)

        self.assertTrue(mock_run.called)
        self.assertTrue(mock_run.call_count == 1)

        received = self.socketio_client.get_received()
        # there should have gotten one file_started and file_done event triggered
        self.assertEqual(len([x for x in received if x["name"] == "file_started"]), 1)
        self.assertEqual(len([x for x in received if x["name"] == "file_done"]), 1)

        # the status should be "finished" now
        # self.assertEqual(File.query.filter_by(id=file.id).first().status, StatusMap.finished.value)
        # print(File.query.filter_by(id=file.id).first().status)
        return

    def test_stop_process(self):
        # TODO
        pass
