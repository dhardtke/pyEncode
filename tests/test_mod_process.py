import os

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

    @patch("app.modules.mod_process.process.Process.run_ffmpeg")
    @patch("app.modules.mod_process.process.Process.ffmpeg_probe_frame_count", return_value=10)
    def test_check_and_start_processes(self, mock_probe, mock_run):
        def mocked_run_ffmpeg(cmd, frame_count):
            yield {"return_code": -1, "eta": 1, "progress": 0, "bitrate": 0, "time": 0, "size": 0, "fps": 0}

        # mock run_ffmpeg()
        mock_run.side_effect = mocked_run_ffmpeg

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
        with patch("os.rename"):
            with patch("os.remove"):
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

    @staticmethod
    def test_file_done():
        with patch("os.rename") as m_rename:
            with patch("os.remove") as m_remove:
                # add fake_file to database in order to test renaming
                filename = "ThisIsAmazing.11.12.10.PyEncode.Is.The.Best.SEPARATOR.1080p.MP4-ABC.mp4"
                path = "/this/path/is/fake"
                fake_file = File(id=1, filename=path + os.sep + filename)
                fake_file.output_filename = filename + ".pyencode"
                db.session.add(fake_file)
                db.session.commit()

                # set options we want to test
                config["encoding"]["delete_old_file"] = "True"
                config["encoding"]["rename_enabled"] = "True"
                config["encoding"]["rename_search"] = r"(?P<head>.+)(?P<resolution>1080|720|2160)(?:p|P)\.(?P<tail>.+)\.(?P<extension>\w{3})"
                config["encoding"]["rename_replace"] = r"\g<head>720p.\g<tail>-selfmade.mkv"
                expected_filename = "ThisIsAmazing.11.12.10.PyEncode.Is.The.Best.SEPARATOR.720p.MP4-ABC-selfmade.mkv"

                ProcessRepository.processes[fake_file.id] = None
                ProcessRepository.file_done(fake_file)
                m_remove.assert_called_once_with(fake_file.filename)
                m_rename.assert_called_once_with(path + os.sep + fake_file.output_filename, path + os.sep + expected_filename)

        return

    def test_stop_process(self):
        # TODO
        pass

    def test_ffmpeg_probe_frame_count(self):
        # TODO
        pass
