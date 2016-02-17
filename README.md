pyEncode
============
[![Build Status](https://travis-ci.org/dhardtke/pyEncode.svg?branch=master)](https://travis-ci.org/dhardtke/pyEncode)

pyEncode is a wrapper for the audio and video processor ffmpeg (https://ffmpeg.org/).

**Warning: PyEncode is still in a very early stage and therefore only basic features are implemented!**

Requirements
============
pyEncode has been written to run with Python 3.5.x and above.

Installation
============
Run `pip install -r requirements.txt` in pyEncode's root directory to install all necessary third-party requirements.

Configuration
============
In order to use pyEncode it is recommended that you create your own config file inside the data directory.

Create a file called `config.ini` inside `data` with the following content:
```INI
[general]
csrf_session_key = secret
secret_key = secret
parallel_processes = 1

[filemanager]
show_resolution = False

[encoding]
parameters = -acodec aac -strict experimental -s 1280x720 -aspect 1280:720 -preset slow -crf 24 -f matroska -vcodec libx265
delete_old_file = False
rename_enabled = True
rename_search = (?P<head>.+)(?P<resolution>1080|720|2160)(?:p|P)\.(?P<tail>.+)\.(?P<extension>\w{3})
rename_replace = \g<head>720p.\g<tail>-pyencode.mkv
```

We advise you to change the `csrf_session_key` and `secret_key`.
If you wish, you can change the parameters that will be passed to `ffmpeg` by using the `parameters` key inside the config file.
Check out this site for info about all available options: https://ffmpeg.org/ffmpeg.html

Deployment
============
We recommend using `gunicorn` to run pyEncode:

Install `gunicorn` using `pip install gunicorn`.

Afterwards, you can use the `gunicorn.conf.py` that pyEncode comes with, or create your own.

Run `gunicorn -c gunicorn.conf.py app:app` to use `gunicorn.conf.py` that pyEncode comes with.

By default this configures gunicorn to use as many worker threads as the machine running pyEncode on CPUs have.

It also enables the daemon mode, so that when you start pyEncode, it is being detached into the background.

Development
============
Run `python run_dev.py` to start the socketio development server.

Running Tests
============
Run `python run_tests.py` in the root folder where the `app` subdirectory resides.