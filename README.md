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

After the first start pyEncode creates an initial admin user with the username `admin` and password `admin`.

Be sure to change these credentials after the first login!

Running pyEncode
============
You can run pyEncode using its `run.py` script:

```
nas@nas:/scripts/pyEncode$ ./run.py --help
usage: run.py [-h] [--debug] [--daemon] [--stop] [--restart] [--port PORT]
              [--host HOST]

optional arguments:
  -h, --help   show this help message and exit
  --debug      enable debug mode (default: False)

daemon:
  --daemon     run in daemon mode (default: False)
  --stop       stop if running in daemon mode (default: False)
  --restart    restart daemon (default: False)

net:
  --port PORT  port at which the web frontend is listening (default: 7000)
  --host HOST  host IP under which the web front end is listening (default:
               127.0.0.1)
nas@nas:/scripts/pyEncode$
```

Deployment
============
This section is still under development.

Running Tests
============
Run `python run_tests.py` in the root folder where the `app` subdirectory resides.