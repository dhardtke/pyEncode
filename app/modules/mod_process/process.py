# this class / module serves as a wrapper for the ffmpeg process
import io
import math
import os
import re
import shlex
import subprocess
from collections import deque
from threading import Thread

import eventlet
from eventlet.green.subprocess import Popen

from app import db, config, app
from app.library.formatters import duration_to_seconds
from app.models.file import File
from app.modules.mod_process.process_repository import ProcessRepository

# we need to monkey patch the threading module, see http://eventlet.net/doc/patching.html
eventlet.monkey_patch(thread=True)

# the pattern to fetch meta information of the current progress
# to match a line like
# frame=44448 fps= 14 q=-0.0 Lsize=  247192kB time=00:30:53.95 bitrate=1092.3kbits/s speed=0.577x
PROGRESS_PATTERN = re.compile(r"frame=\s*(\d+) fps=\s*(.+) q=(.+) L?size=\s*(\d+)kB time=(.+) bitrate=\s*(.+)kbits/s(?:P speed=(.+)x)?")


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file
        self.active = True

    def run(self):
        """
        run the encoding
        """
        # probe file first
        frame_count = self.ffmpeg_probe_frame_count()

        if frame_count == -1:
            app.logger.debug("Probing of " + self.file.filename + " failed - aborting...")
            ProcessRepository.file_failed(self.file)
            return

        # app.logger.debug("Probing of " + file.filename + " successful.. frame count: " + str(frame_count))
        split_path = os.path.split(self.file.filename)
        path = split_path[0]
        original_filename = split_path[1]
        filename_noext = os.path.split(os.path.splitext(original_filename)[0])[1]
        # form output filename and store it in self.file for later use
        self.file.output_filename = filename_noext + ".pyencode"

        cmd = ["ffmpeg"]
        cmd.extend(["-i", self.file.filename])
        # add parameters from config
        cmd.extend(shlex.split(config.get("encoding", "parameters")))
        cmd.extend(["-y", path + os.sep + self.file.output_filename])

        app.logger.debug("Starting encoding of " + self.file.filename + " with %s" % " ".join(cmd))

        for info in self.run_ffmpeg(cmd, frame_count):
            if info["return_code"] != -1:
                app.logger.debug("Error occured while running ffmpeg. Last lines of output: ")
                app.logger.debug("\n".join(info["last_lines"]))
                ProcessRepository.file_failed(self.file)
                return

            # store information in database
            # convert kB to bytes
            info["ffmpeg_size"] *= 1024

            # we don't need the return_code anymore (and don't want to store it)
            info.pop("return_code")

            # update file in DB
            File.query.filter_by(id=self.file.id).update(info)
            db.session.commit()

            # update self.file
            for k in info:
                setattr(self.file, k, info[k])

            # tell ProcessRepository there's some progress going on
            ProcessRepository.file_progress(self.file)

        if self.active:
            ProcessRepository.file_done(self.file)

    def ffmpeg_probe_frame_count(self):
        """
        probe self.file and return frame count
        """
        instance = Popen(["ffprobe", self.file.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output = ""
        for line in instance.stderr:
            output += line.decode("utf8")

            # call sleep, see https://stackoverflow.com/questions/34599578/using-popen-in-a-thread-blocks-every-incoming-flask-socketio-request
            eventlet.sleep()

        fps_reg = re.findall(r"([0-9]*\.?[0-9]+) fps|tbr", output)
        if fps_reg is None:
            return -1

        fps = float(" ".join(fps_reg))

        duration = duration_to_seconds(re.findall(r"Duration: (.*?),", output)[0])

        # calculate the amount of frames for the calculation of progress
        frame_count = int(math.ceil(duration * float(fps)))

        return frame_count

    def stop(self):
        """
        stop this process
        """
        self.active = False

    def run_ffmpeg(self, cmd, frame_count):
        """
        run ffmpeg with given cmd arguments and a frame count
        :param cmd: the command line dictionary containing all the arguments
        :param frame_count: the amount of frames of this video, necessary for the progress calculation
        :return:
        """
        instance = Popen(map(str, cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reader = io.TextIOWrapper(instance.stderr, encoding="utf8")

        # these two variables are just needed for when the processing fails, see below
        last_lines = deque(maxlen=5)  # parameter determines how many lines to keep

        # oddly ffmpeg writes to stderr instead of stdout
        for line in reader:
            # kill ffmpeg when not being active anymore
            if not self.active:
                instance.kill()

            # call sleep, see https://stackoverflow.com/questions/34599578/using-popen-in-a-thread-blocks-every-incoming-flask-socketio-request
            eventlet.sleep()

            # append current line to last_lines
            last_lines.append(line)

            print(line)
            match = PROGRESS_PATTERN.match(line)

            # first few lines have no match
            if match:
                frame = int(match.group(1))  # current frame, needed for calculation of progress
                fps = float(match.group(2))  # needed for calculation of remaining time
                size = int(match.group(4))  # current size in kB
                time = duration_to_seconds(match.group(5))  # time already passed for converting, in seconds
                bitrate = float(match.group(6))  # in kbits/s
                progress = round((frame / float(frame_count)) * 100, 1)  # in %

                frames_remaining = frame_count - frame  # needed for eta
                eta = frames_remaining / fps if fps != 0 else -1  # in seconds

                yield {"return_code": -1, "ffmpeg_eta": eta, "ffmpeg_progress": progress, "ffmpeg_bitrate": bitrate,
                       "ffmpeg_time": time, "ffmpeg_size": size, "ffmpeg_fps": fps}

        return_code = instance.wait()
        if return_code != 0:
            yield {"return_code": return_code, "last_lines": last_lines}
