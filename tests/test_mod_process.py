from app import socketio, app
from tests import BaseTestCase
from app.modules.mod_process.process_repository import ProcessRepository


class TestModProcess(BaseTestCase):
    socketio_client = None

    def setUp(self):
        super().setUp()

        self.socketio_client = socketio.test_client(app)

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

        # TODO test mod_statusbar

        # ProcessRepository.parallel_processes = 1

        # TODO more tests
