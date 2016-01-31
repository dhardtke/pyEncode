# Run a test server.
from app import app, socketio

# app.run(host="127.0.0.1", port=7000, debug=True)
socketio.run(app, host="0.0.0.0", port=7000, debug=True)
