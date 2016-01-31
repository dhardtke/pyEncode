pyEncode
============
[![wercker status](https://app.wercker.com/status/bb64a538d69c241f7b4c25c32b2d1a92/m "wercker status")](https://app.wercker.com/project/bykey/bb64a538d69c241f7b4c25c32b2d1a92)

pyEncode is a wrapper for the audio and video processor avconv (TODO link).

Requirements
============
pyEncode has been written to run with Python 3.5.x and avconv from libav.

Installation
============
Run `pip install -r requirements.txt` in pyEncode's root directory to install all necessary third-party requirements.

Afterwards, TODO...

Development
============
Run `python run_dev.py` to start the socketio development server.

Deployment
============
We recommend using `gunicorn` to run pyEncode:

Install `gunicorn` using `pip install gunicorn`. Afterwards, you can use the `gunicorn.conf.py` that pyEncode comes with, or create your own:

`gunicorn -c gunicorn.conf.py app:app`

Running Tests
============
Run `python run_tests.py` in the root folder where the `app` subdirectory resides.