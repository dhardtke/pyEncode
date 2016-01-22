# Run a test server.
from app import app, socketio

# app.run(host="127.0.0.1", port=8080, debug=True)
socketio.run(app, port=8080)
